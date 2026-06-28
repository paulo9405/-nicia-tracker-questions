from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Profile, User


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Senha"}
        ),
    )
    password2 = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirme a senha"}
        ),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nome"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Sobrenome"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "E-mail"}
            ),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("As senhas não coincidem.")
        return cleaned


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "E-mail", "autofocus": True}
        ),
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Senha"}
        ),
    )


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        label="Nome",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        label="Sobrenome",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Profile
        fields = ["target_contest", "daily_goal", "study_level", "bio", "avatar"]
        widgets = {
            "target_contest": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: Médico Veterinário — Ponta Grossa 2026",
                }
            ),
            "daily_goal": forms.NumberInput(
                attrs={"class": "form-control", "min": 1, "max": 200}
            ),
            "study_level": forms.Select(attrs={"class": "form-select"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }
