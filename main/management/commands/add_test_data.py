from django.core.management.base import BaseCommand
from main.models import ProductCategory, Product
from decimal import Decimal

class Command(BaseCommand):
    help = '添加测试商品数据'

    def handle(self, *args, **kwargs):
        # 创建商品类别
        electronics = ProductCategory.objects.create(
            name='电子产品',
            description='包括手机、电脑、平板等电子设备'
        )

        clothing = ProductCategory.objects.create(
            name='服装服饰',
            description='包括男装、女装、童装等各类服装'
        )

        food = ProductCategory.objects.create(
            name='食品饮料',
            description='包括零食、饮料、生鲜等食品'
        )

        # 创建商品
        Product.objects.create(
            name='iPhone 15 Pro',
            description='最新款iPhone，搭载A17芯片，专业摄像系统',
            price=Decimal('8999.00'),
            category=electronics,
            stock=100,
            sales_count=50,
            is_active=True
        )

        Product.objects.create(
            name='MacBook Air M2',
            description='搭载M2芯片的轻薄笔记本，续航持久',
            price=Decimal('7999.00'),
            category=electronics,
            stock=50,
            sales_count=30,
            is_active=True
        )

        Product.objects.create(
            name='时尚连衣裙',
            description='2024春季新款，舒适面料，优雅设计',
            price=Decimal('299.00'),
            category=clothing,
            stock=200,
            sales_count=80,
            is_active=True
        )

        Product.objects.create(
            name='男士休闲西装',
            description='商务休闲两用，修身剪裁',
            price=Decimal('599.00'),
            category=clothing,
            stock=150,
            sales_count=40,
            is_active=True
        )

        Product.objects.create(
            name='进口巧克力礼盒',
            description='比利时进口巧克力，多种口味',
            price=Decimal('128.00'),
            category=food,
            stock=300,
            sales_count=150,
            is_active=True
        )

        Product.objects.create(
            name='有机水果礼盒',
            description='精选有机水果，营养美味',
            price=Decimal('199.00'),
            category=food,
            stock=100,
            sales_count=60,
            is_active=True
        )

        self.stdout.write(self.style.SUCCESS('测试数据添加成功！')) 