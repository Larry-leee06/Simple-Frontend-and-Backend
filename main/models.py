from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from PIL import Image
import os
from django.db.models.signals import post_save
from django.dispatch import receiver

class Article(models.Model):
    ARTICLE_TYPES = [
        ('experience', '环保经验'),
        ('news', '环保新闻'),
        ('discussion', '话题讨论'),
    ]
    
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_articles', blank=True)
    article_type = models.CharField('文章类型', max_length=20, choices=ARTICLE_TYPES, default='experience')
    tags = models.CharField('标签', max_length=200, blank=True)
    cover_image = models.ImageField('封面图片', upload_to='article_covers/', null=True, blank=True)
    allow_comment = models.BooleanField('允许评论', default=True)
    is_draft = models.BooleanField('是否为草稿', default=False)
    views_count = models.PositiveIntegerField('浏览次数', default=0)
    
    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

    def get_tags_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments', verbose_name='文章')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='评论者')
    content = models.TextField('评论内容')
    created_at = models.DateTimeField('评论时间', default=timezone.now)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.author.username} 对 {self.article.title} 的评论'

class Tag(models.Model):
    name = models.CharField('标签名', max_length=50, unique=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class ProductCategory(models.Model):
    name = models.CharField('类别名称', max_length=100)
    description = models.TextField('类别描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '商品类别'
        verbose_name_plural = '商品类别'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField('商品名称', max_length=200)
    description = models.TextField('商品描述')
    price = models.DecimalField('价格', max_digits=10, decimal_places=2)
    image = models.ImageField('商品图片', upload_to='products/', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, verbose_name='商品类别')
    stock = models.PositiveIntegerField('库存', default=0)
    sales_count = models.PositiveIntegerField('销量', default=0)
    is_active = models.BooleanField('是否上架', default=True)
    publisher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='发布者', related_name='published_products')
    
    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

    def get_related_products(self):
        """获取相关商品（同一分类下的其他商品）"""
        if self.category:
            return Product.objects.filter(category=self.category, is_active=True).exclude(id=self.id)[:5]
        return Product.objects.filter(is_active=True).exclude(id=self.id)[:5]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.image:
            img = Image.open(self.image.path)
            
            # 设置最大尺寸
            max_size = (800, 800)
            
            # 如果图片超过最大尺寸，进行等比例缩放
            if img.height > max_size[1] or img.width > max_size[0]:
                output_size = max_size
                img.thumbnail(output_size)
                
                # 保存优化后的图片
                img.save(self.image.path, quality=85, optimize=True)

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    quantity = models.PositiveIntegerField('数量', default=1)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '购物车项'
        verbose_name_plural = '购物车项'
        unique_together = ['user', 'product']  # 同一用户的同一商品只能有一条记录
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username}的购物车 - {self.product.name}'

    @property
    def total_price(self):
        return self.quantity * self.product.price

class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '收藏项'
        verbose_name_plural = '收藏项'
        unique_together = ['user', 'product']  # 同一用户的同一商品只能收藏一次
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username}的收藏 - {self.product.name}'

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
        ('O', '其他'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)
    bio = models.TextField('个人简介', max_length=500, blank=True)
    gender = models.CharField('性别', max_length=1, choices=GENDER_CHOICES, blank=True)
    birthday = models.DateField('生日', null=True, blank=True)
    location = models.CharField('所在地', max_length=100, blank=True)
    phone = models.CharField('电话', max_length=20, blank=True)
    social_media = models.JSONField('社交媒体', default=dict, blank=True, null=True)
    environmental_interests = models.TextField('环保兴趣', max_length=500, blank=True)
    is_public = models.BooleanField('公开资料', default=True)
    theme_preference = models.CharField('主题偏好', max_length=20, default='light')
    
    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'
    
    def __str__(self):
        return f"{self.user.username}的资料"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.avatar:
            img = Image.open(self.avatar.path)
            
            # 设置头像最大尺寸
            max_size = (300, 300)
            
            # 如果图片超过最大尺寸，进行等比例缩放
            if img.height > max_size[1] or img.width > max_size[0]:
                output_size = max_size
                img.thumbnail(output_size)
                
                # 保存优化后的图片
                img.save(self.avatar.path, quality=85, optimize=True)

# 当创建User实例时自动创建关联的UserProfile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        # 先尝试访问profile，如果不存在则创建
        instance.profile
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)
    
    # 确保profile存在后再保存
    instance.profile.save() 