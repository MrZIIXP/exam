from django import forms
from accounts.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .permissions import assygn_role


class RegisterForm(forms.ModelForm):
    username = forms.CharField(
        max_length=50,
        min_length=2,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'ALEXANDER',
            'class': 'w-full bg-transparent border-none border-b-2 border-outline-variant/20 py-3 text-on-surface font-medium placeholder:text-outline-variant/50 focus:ring-0 focus:border-primary transition-colors duration-300 dark:text-[#dae2fd] dark:focus:border-[#d72222] dark:placeholder:text-[#8c909f]/50',
            'autocomplete': 'off',
        }),
        help_text='От 2 до 50 символов'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'A.STERLING@PRECISION.COM',
            'class': 'w-full bg-transparent border-none border-b-2 border-outline-variant/20 py-3 text-on-surface font-medium placeholder:text-outline-variant/50 focus:ring-0 focus:border-primary transition-colors duration-300 dark:text-[#dae2fd] dark:focus:border-[#d72222] dark:placeholder:text-[#8c909f]/50',
            'autocomplete': 'email',
        })
    )
    
    password1 = forms.CharField(
        label='Пароль',
        max_length=128,
        min_length=6,
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••••••',
            'class': 'flex-1 bg-transparent border-none py-3 text-on-surface font-medium placeholder:text-outline-variant/50 focus:ring-0 dark:text-[#dae2fd] dark:placeholder:text-[#8c909f]/50',
            'autocomplete': 'new-password',
        }),
        help_text='Минимум 6 символов'
    )
    
    password2 = forms.CharField(
        label='Подтверждение пароля',
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••••••',
            'class': 'flex-1 bg-transparent border-none py-3 text-on-surface font-medium placeholder:text-outline-variant/50 focus:ring-0 dark:text-[#dae2fd] dark:placeholder:text-[#8c909f]/50',
            'autocomplete': 'new-password',
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        
        if not username:
            raise ValidationError('Пожалуйста, введите имя пользователя')
        
        if len(username) < 2:
            raise ValidationError('Имя должно содержать минимум 2 символа')
        
        if len(username) > 50:
            raise ValidationError('Имя не должно превышать 50 символов')
        
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        
        if not email:
            raise ValidationError('Пожалуйста, введите email')
        
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('Введите корректный email адрес')
        
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        
        return email
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1', '')
        
        if not password:
            raise ValidationError('Пожалуйста, введите пароль')
        
        if len(password) < 6:
            raise ValidationError('Пароль должен содержать минимум 6 символов')
        
        if len(password) > 128:
            raise ValidationError('Пароль не должен превышать 128 символов')
        
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError('Пароли не совпадают')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            assygn_role(user, 'User')
            self.save_m2m()
        return user


class LoginForm(forms.Form):    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'A.STERLING@PRECISION.COM',
            'class': 'w-full bg-transparent border-none border-b-2 border-outline-variant/20 py-3 text-on-surface font-medium placeholder:text-outline-variant/50 focus:ring-0 focus:border-primary transition-colors duration-300 dark:text-[#dae2fd] dark:focus:border-[#d72222] dark:placeholder:text-[#8c909f]/50',
            'autocomplete': 'email',
        })
    )
    
    password = forms.CharField(
        label='Пароль',
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••••••',
            'class': 'flex-1 bg-transparent border-none py-3 text-on-surface font-medium placeholder:text-outline-variant/50 focus:ring-0 dark:text-[#dae2fd] dark:placeholder:text-[#8c909f]/50',
            'autocomplete': 'current-password',
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        
        if not email:
            raise ValidationError('Пожалуйста, введите email')
        
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('Введите корректный email адрес')
        
        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        if not password:
            raise ValidationError('Пожалуйста, введите пароль')
        
        return password


class ForgotPasswordForm(forms.Form):    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'A.STERLING@PRECISION.COM',
            'class': 'w-full bg-transparent border-none border-b-2 border-outline-variant/20 py-3 text-on-surface font-medium placeholder:text-outline-variant/50 focus:ring-0 focus:border-primary transition-colors duration-300 dark:text-[#dae2fd] dark:focus:border-[#d72222] dark:placeholder:text-[#8c909f]/50',
            'autocomplete': 'email',
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        
        if not email:
            raise ValidationError('Пожалуйста, введите email')
        
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('Введите корректный email адрес')
        
        return email


class ResetPasswordForm(forms.Form):    
    password = forms.CharField(
        label='Новый пароль',
        max_length=128,
        min_length=6,
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••••••',
            'class': 'flex-1 bg-transparent border-none py-3 text-on-surface font-medium placeholder:text-outline-variant/50 focus:ring-0 dark:text-[#dae2fd] dark:placeholder:text-[#8c909f]/50',
            'autocomplete': 'new-password',
        }),
        help_text='Минимум 6 символов'
    )
    
    password_confirm = forms.CharField(
        label='Подтверждение пароля',
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••••••',
            'class': 'flex-1 bg-transparent border-none py-3 text-on-surface font-medium placeholder:text-outline-variant/50 focus:ring-0 dark:text-[#dae2fd] dark:placeholder:text-[#8c909f]/50',
            'autocomplete': 'new-password',
        })
    )
    
    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        
        if not password:
            raise ValidationError('Пожалуйста, введите пароль')
        
        if len(password) < 6:
            raise ValidationError('Пароль должен содержать минимум 6 символов')
        
        if len(password) > 128:
            raise ValidationError('Пароль не должен превышать 128 символов')
        
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError('Пароли не совпадают')
        
        return cleaned_data
