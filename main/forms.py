from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='必填。请输入有效的电子邮件地址。')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被注册')
        return email

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, label='姓', required=False)
    last_name = forms.CharField(max_length=30, label='名', required=False)
    email = forms.EmailField(max_length=254, label='电子邮件', required=True)
    
    class Meta:
        model = UserProfile
        fields = ('avatar', 'bio', 'gender', 'birthday', 'location', 'phone', 'environmental_interests', 'is_public')
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 3}),
            'environmental_interests': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'avatar': '头像',
            'bio': '个人简介',
            'gender': '性别',
            'birthday': '生日',
            'location': '所在地',
            'phone': '电话',
            'environmental_interests': '环保兴趣',
            'is_public': '公开资料',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
    
    def save(self, user=None, commit=True):
        profile = super(UserProfileForm, self).save(commit=False)
        if user:
            user.first_name = self.cleaned_data.get('first_name', '')
            user.last_name = self.cleaned_data.get('last_name', '')
            user.email = self.cleaned_data.get('email')
            if commit:
                user.save()
        if commit:
            profile.save()
        return profile

class AccountSettingsForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput(), label='当前密码', required=False)
    new_password = forms.CharField(widget=forms.PasswordInput(), label='新密码', required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label='确认新密码', required=False)
    
    email_notifications = forms.BooleanField(label='接收电子邮件通知', required=False)
    theme_preference = forms.ChoiceField(
        label='主题偏好',
        choices=[('light', '浅色'), ('dark', '深色')],
        widget=forms.RadioSelect,
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(AccountSettingsForm, self).__init__(*args, **kwargs)
        if user and hasattr(user, 'profile'):
            self.fields['theme_preference'].initial = user.profile.theme_preference
    
    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get('current_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and not current_password:
            self.add_error('current_password', '请输入当前密码')
        
        if new_password and new_password != confirm_password:
            self.add_error('confirm_password', '两次输入的密码不一致')
        
        return cleaned_data 