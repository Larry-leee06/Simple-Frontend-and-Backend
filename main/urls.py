from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='/login/',
        redirect_field_name=None,
        template_name=None,
    ), name='logout'),
    path('logout/then-login/', RedirectView.as_view(url='/login/'), name='logout_then_login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('account-settings/', views.account_settings, name='account_settings'),
    path('change-avatar/', views.change_avatar, name='change_avatar'),
    path('article/post/', views.post_article, name='post_article'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
    path('article/<int:article_id>/like/', views.like_article, name='like_article'),
    path('article/<int:article_id>/comment/', views.post_comment, name='post_comment'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('upload_image/', views.upload_image, name='upload_image'),
    path('save_draft/', views.save_draft, name='save_draft'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/post/', views.post_product, name='post_product'),
    path('cart/', views.cart, name='cart'),
    path('api/cart/add/', views.add_to_cart, name='add_to_cart'),
    path('wishlist/', views.wishlist, name='wishlist'),
] 