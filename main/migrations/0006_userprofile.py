from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0005_wishlistitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/', verbose_name='头像')),
                ('bio', models.TextField(blank=True, max_length=500, verbose_name='个人简介')),
                ('gender', models.CharField(blank=True, choices=[('M', '男'), ('F', '女'), ('O', '其他')], max_length=1, verbose_name='性别')),
                ('birthday', models.DateField(blank=True, null=True, verbose_name='生日')),
                ('location', models.CharField(blank=True, max_length=100, verbose_name='所在地')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='电话')),
                ('social_media', models.JSONField(blank=True, default=dict, null=True, verbose_name='社交媒体')),
                ('environmental_interests', models.TextField(blank=True, max_length=500, verbose_name='环保兴趣')),
                ('is_public', models.BooleanField(default=True, verbose_name='公开资料')),
                ('theme_preference', models.CharField(default='light', max_length=20, verbose_name='主题偏好')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '用户资料',
                'verbose_name_plural': '用户资料',
            },
        ),
    ] 