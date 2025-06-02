from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import Article, Comment, Product, Tag, ProductCategory, CartItem, WishlistItem, UserProfile
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils.text import slugify
from django.conf import settings
import os
import uuid
import json
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .serializers import ProductCategorySerializer, ProductSerializer, CartItemSerializer
from .forms import CustomUserCreationForm, UserProfileForm, AccountSettingsForm

def index(request):
    articles = Article.objects.filter(is_draft=False)
    products = Product.objects.all()[:5]  # 只显示5个商品
    
    paginator = Paginator(articles, 10)  # 每页显示10篇文章
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'index.html', {
        'page_obj': page_obj,
        'products': products,
    })

@login_required
def post_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        article_type = request.POST.get('article_type')
        tags = request.POST.get('tags')
        allow_comment = request.POST.get('allow_comment') == 'on'
        is_draft = request.POST.get('is_draft') == 'true'
        
        if title and content:
            article = Article.objects.create(
                title=title,
                content=content,
                author=request.user,
                article_type=article_type,
                tags=tags,
                allow_comment=allow_comment,
                is_draft=is_draft
            )
            
            # 处理封面图片
            if request.FILES.get('cover_image'):
                article.cover_image = request.FILES['cover_image']
                article.save()
            
            # 处理标签
            if tags:
                for tag_name in tags.split(','):
                    tag_name = tag_name.strip()
                    if tag_name:
                        tag, created = Tag.objects.get_or_create(name=tag_name)
            
            messages.success(request, '文章发布成功！' if not is_draft else '草稿保存成功！')
            return redirect('article_detail', article_id=article.id)
    
    return render(request, 'post_article.html')

@login_required
def post_product(request):
    """上传商品视图函数"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock', 0)
        category_id = request.POST.get('category')
        
        if name and description and price:
            # 创建商品对象
            product = Product(
                name=name,
                description=description,
                price=price,
                stock=stock,
                is_active=True,  # 默认上架
                publisher=request.user  # 添加发布者信息
            )
            
            # 处理分类
            if category_id:
                try:
                    category = ProductCategory.objects.get(id=category_id)
                    product.category = category
                except ProductCategory.DoesNotExist:
                    pass  # 分类不存在则不设置
            
            # 处理商品图片
            if request.FILES.get('image'):
                product.image = request.FILES['image']
            
            # 保存商品
            product.save()
            
            messages.success(request, '商品上传成功！')
            return redirect('product_detail', product_id=product.id)
    
    # 获取所有商品分类
    categories = ProductCategory.objects.all()
    
    return render(request, 'post_product.html', {
        'categories': categories,
    })

@login_required
@require_POST
def upload_image(request):
    if 'image' in request.FILES:
        image = request.FILES['image']
        # 生成唯一的文件名
        ext = os.path.splitext(image.name)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        
        # 保存图片
        filepath = os.path.join('article_images', filename)
        full_path = os.path.join(settings.MEDIA_ROOT, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        
        return JsonResponse({
            'url': os.path.join(settings.MEDIA_URL, filepath)
        })
    
    return JsonResponse({'error': '没有上传图片'}, status=400)

@login_required
@require_POST
def save_draft(request):
    try:
        # 添加is_draft参数调用post_article
        request.POST = request.POST.copy()
        request.POST['is_draft'] = 'true'
        return post_article(request)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def like_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.user in article.likes.all():
        article.likes.remove(request.user)
        liked = False
    else:
        article.likes.add(request.user)
        liked = True
    return JsonResponse({
        'liked': liked,
        'likes_count': article.likes.count()
    })

@login_required
@require_POST
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True
    return JsonResponse({
        'liked': liked,
        'likes_count': comment.likes.count()
    })

@login_required
@require_POST
def post_comment(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    content = request.POST.get('content')
    parent_id = request.POST.get('parent_id')
    
    if content:
        comment = Comment.objects.create(
            article=article,
            author=request.user,
            content=content,
            parent_id=parent_id if parent_id else None
        )
        messages.success(request, '评论发表成功！')
    return redirect('article_detail', article_id=article_id)

def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    # 增加浏览次数
    article.views_count += 1
    article.save()
    
    # 获取评论，包括回复
    comments = article.comments.filter(parent=None)
    
    return render(request, 'article_detail.html', {
        'article': article,
        'comments': comments,
    })

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功！')
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def product_list(request):
    category_id = request.GET.get('category')
    search_query = request.GET.get('q')
    sort = request.GET.get('sort', '-created_at')
    
    # 使用select_related减少数据库查询
    products = Product.objects.select_related('category')
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    if sort == 'price':
        products = products.order_by('price')
    elif sort == '-price':
        products = products.order_by('-price')
    elif sort == 'sales':
        products = products.order_by('-sales_count')
    else:
        products = products.order_by('-created_at')
    
    # 如果用户已登录，预先获取收藏状态
    if request.user.is_authenticated:
        wishlist_products = set(WishlistItem.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True))
        
        # 为每个商品添加收藏状态
        for product in products:
            product.is_in_wishlist = product.id in wishlist_products
    
    categories = ProductCategory.objects.all()
    
    paginator = Paginator(products, 12)  # 每页显示12个商品
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 获取购物车数量
    cart_count = CartItem.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    
    return render(request, 'product_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_id,
        'current_sort': sort,
        'search_query': search_query,
        'cart_count': cart_count,
    })

@login_required
def wishlist(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user).select_related('product')
    
    paginator = Paginator(wishlist_items, 12)  # 每页显示12个商品
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'wishlist.html', {
        'wishlist_items': page_obj,
        'page_obj': page_obj,
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # 直接在视图中获取相关商品，而不调用model的方法
    if product.category:
        related_products = Product.objects.filter(
            category=product.category, 
            is_active=True
        ).exclude(id=product.id)[:5]
    else:
        related_products = Product.objects.filter(
            is_active=True
        ).exclude(id=product.id)[:5]
    
    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related_products,
    })

@login_required
@require_POST
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        # 同时支持product_id和product两种参数名
        product_id = data.get('product_id') or data.get('product')
        quantity = int(data.get('quantity', 1))
        
        if not product_id:
            return JsonResponse({'success': False, 'error': '商品ID不能为空'})
        
        if quantity < 1:
            return JsonResponse({'success': False, 'error': '数量必须大于0'})
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': '商品不存在'})
        
        if product.stock < quantity:
            return JsonResponse({'success': False, 'error': '库存不足'})
        
        # 添加购物车逻辑
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            if cart_item.quantity > product.stock:
                return JsonResponse({'success': False, 'error': '超出库存数量'})
            cart_item.save()
        
        # 返回最新的购物车数量
        cart_count = CartItem.objects.filter(user=request.user).count()
        
        return JsonResponse({
            'success': True,
            'message': '成功加入购物车',
            'cart_count': cart_count
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': '无效的请求数据'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        category = self.request.query_params.get('category', None)
        if category is not None:
            queryset = queryset.filter(category_id=category)
        return queryset

    @action(detail=False, methods=['get'])
    def active(self, request):
        active_products = Product.objects.filter(is_active=True)
        serializer = self.get_serializer(active_products, many=True)
        return Response(serializer.data)

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related('product')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                if instance.user != request.user:
                    return Response(
                        {'error': '无权限删除此商品'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # 保存商品ID用于返回
                product_id = instance.product_id
                
                # 执行删除
                self.perform_destroy(instance)
                
                # 获取最新的购物车数据
                cart_items = CartItem.objects.filter(user=request.user)
                cart_count = cart_items.count()
                total_price = sum(item.total_price for item in cart_items)
                total_items = sum(item.quantity for item in cart_items)
                
                return Response({
                    'success': True,
                    'message': '商品已删除',
                    'cart_count': cart_count,
                    'total_price': float(total_price),
                    'total_items': total_items,
                    'deleted_product_id': product_id
                }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def update_quantity(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        
        try:
            cart_item = CartItem.objects.get(
                user=request.user,
                product_id=product_id
            )
            
            if quantity > cart_item.product.stock:
                return Response({
                    'error': '超出库存数量',
                    'current_quantity': cart_item.quantity
                }, status=status.HTTP_400_BAD_REQUEST)
            
            cart_item.quantity = quantity
            cart_item.save()
            
            return Response({
                'success': True,
                'quantity': cart_item.quantity,
                'total_price': float(cart_item.total_price)
            })
            
        except CartItem.DoesNotExist:
            return Response({
                'error': '购物车项不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def add_to_cart(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            
            if quantity > product.stock:
                return Response({
                    'error': '超出库存数量'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                if cart_item.quantity > product.stock:
                    return Response({
                        'error': '超出库存数量'
                    }, status=status.HTTP_400_BAD_REQUEST)
                cart_item.save()
            
            cart_count = CartItem.objects.filter(user=request.user).count()
            
            return Response({
                'success': True,
                'message': '成功加入购物车',
                'cart_count': cart_count
            })
            
        except Product.DoesNotExist:
            return Response({
                'error': '商品不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def cart_summary(self, request):
        cart_items = self.get_queryset()
        total_price = sum(item.total_price for item in cart_items)
        total_items = sum(item.quantity for item in cart_items)
        
        return Response({
            'total_price': float(total_price),
            'total_items': total_items,
            'items': self.get_serializer(cart_items, many=True).data
        })

class WishlistViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        product_id = request.data.get('product')
        try:
            product = Product.objects.get(id=product_id)
            wishlist_item = WishlistItem.objects.filter(
                user=request.user,
                product=product
            ).first()
            
            if wishlist_item:
                wishlist_item.delete()
                is_in_wishlist = False
            else:
                WishlistItem.objects.create(
                    user=request.user,
                    product=product
                )
                is_in_wishlist = True
            
            return Response({
                'is_in_wishlist': is_in_wishlist,
                'message': '已添加到收藏' if is_in_wishlist else '已取消收藏'
            })
        
        except Product.DoesNotExist:
            return Response(
                {'error': '商品不存在'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def batch_add(self, request):
        product_ids = request.data.get('products', [])
        created_items = []
        
        for product_id in product_ids:
            try:
                product = Product.objects.get(id=product_id)
                wishlist_item, created = WishlistItem.objects.get_or_create(
                    user=request.user,
                    product=product
                )
                if created:
                    created_items.append(wishlist_item)
            except Product.DoesNotExist:
                continue
        
        return Response({
            'message': f'成功添加{len(created_items)}个商品到收藏夹',
            'created_count': len(created_items)
        })

@login_required
def cart(request):
    """购物车页面"""
    # 添加缓存控制头
    response = render(request, 'cart.html', {
        'cart_items': CartItem.objects.filter(user=request.user).select_related('product'),
        'cart_count': CartItem.objects.filter(user=request.user).count(),
        'total_price': sum(item.total_price for item in CartItem.objects.filter(user=request.user)),
        'total_items': sum(item.quantity for item in CartItem.objects.filter(user=request.user)),
    })
    
    # 设置缓存控制头
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response

@login_required
def profile(request):
    user = request.user
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user.profile, user=user)
        if form.is_valid():
            form.save(user=user)
            messages.success(request, '个人资料已更新')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user.profile, user=user)
    
    return render(request, 'profile.html', {
        'form': form,
        'user': user,
    })

@login_required
def account_settings(request):
    user = request.user
    
    if request.method == 'POST':
        form = AccountSettingsForm(request.POST, user=user)
        
        if form.is_valid():
            # 处理密码修改
            current_password = form.cleaned_data.get('current_password')
            new_password = form.cleaned_data.get('new_password')
            
            if current_password and new_password:
                # 验证当前密码
                if user.check_password(current_password):
                    user.set_password(new_password)
                    user.save()
                    # 更新会话，避免用户被登出
                    update_session_auth_hash(request, user)
                    messages.success(request, '密码已成功修改')
                else:
                    messages.error(request, '当前密码不正确')
                    return render(request, 'account_settings.html', {'form': form})
            
            # 处理其他账户设置
            if hasattr(user, 'profile'):
                user.profile.theme_preference = form.cleaned_data.get('theme_preference', 'light')
                user.profile.save()
            
            messages.success(request, '账户设置已更新')
            return redirect('account_settings')
    else:
        form = AccountSettingsForm(user=user)
    
    return render(request, 'account_settings.html', {
        'form': form,
        'user': user,
    })

@login_required
def change_avatar(request):
    user = request.user
    
    if request.method == 'POST':
        if 'avatar' in request.FILES:
            # 获取上传的头像
            new_avatar = request.FILES['avatar']
            
            # 删除旧头像（如果存在）
            if user.profile.avatar:
                try:
                    # 保存旧头像路径
                    old_avatar_path = user.profile.avatar.path
                    # 清除头像字段
                    user.profile.avatar = None
                    user.profile.save()
                    # 删除文件
                    import os
                    if os.path.exists(old_avatar_path):
                        os.remove(old_avatar_path)
                except:
                    pass
            
            # 设置新头像
            user.profile.avatar = new_avatar
            user.profile.save()
            
            messages.success(request, '头像更新成功！')
            return redirect('change_avatar')
        else:
            messages.error(request, '请选择要上传的头像文件')
    
    return render(request, 'change_avatar.html', {
        'user': user,
    }) 