import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eco_community.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import Product

def update_product_publishers():
    """更新现有商品的发布者信息"""
    print("开始更新商品发布者信息...")
    
    # 获取一个管理员用户作为默认发布者
    try:
        default_publisher = User.objects.filter(is_superuser=True).first()
        if not default_publisher:
            default_publisher = User.objects.first()  # 如果没有超级用户，就用第一个用户
            
        if not default_publisher:
            print("错误: 系统中没有可用的用户作为默认发布者")
            return
            
        print(f"使用用户 '{default_publisher.username}' 作为默认发布者")
        
        # 获取所有没有发布者的商品
        products_without_publisher = Product.objects.filter(publisher__isnull=True)
        count = products_without_publisher.count()
        
        if count == 0:
            print("没有找到需要更新的商品")
            return
            
        print(f"找到 {count} 个没有发布者的商品")
        
        # 更新这些商品的发布者
        updated = products_without_publisher.update(publisher=default_publisher)
        
        print(f"成功更新了 {updated} 个商品的发布者信息")
        
    except Exception as e:
        print(f"更新过程中出错: {str(e)}")
        
if __name__ == "__main__":
    update_product_publishers() 