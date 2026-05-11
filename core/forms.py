from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

_INPUT_CLASS = (
    'w-full bg-[#0F0F1A] border border-[#2A2A45] focus:border-violet-500 '
    'focus:ring-1 focus:ring-violet-500 text-slate-100 placeholder-slate-500 '
    'rounded-lg px-4 py-2.5 text-sm transition-colors outline-none'
)


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'class': _INPUT_CLASS,
            'placeholder': 'seu@email.com',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': _INPUT_CLASS,
            'placeholder': '••••••••',
        })
    )

    error_messages = {
        'invalid_login': 'E-mail ou senha incorretos. Por favor, tente novamente.',
        'inactive': 'Esta conta está inativa.',
    }


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'class': _INPUT_CLASS,
            'placeholder': 'seu@email.com',
        })
    )
    name = forms.CharField(
        max_length=150,
        required=True,
        label='Nome completo',
        widget=forms.TextInput(attrs={
            'class': _INPUT_CLASS,
            'placeholder': 'João da Silva',
        })
    )
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': _INPUT_CLASS,
            'placeholder': '••••••••',
        })
    )
    password2 = forms.CharField(
        label='Confirme a senha',
        widget=forms.PasswordInput(attrs={
            'class': _INPUT_CLASS,
            'placeholder': '••••••••',
        })
    )

    class Meta:
        model = User
        fields = ['name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            del self.fields['username']
        self.error_messages = {
            'password_mismatch': 'As senhas não coincidem.',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está cadastrado.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']
        user.first_name = self.cleaned_data['name']
        if commit:
            user.save()
        return user
