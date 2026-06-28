"""
UserService — regra de negócio de usuários e perfis.
Views não manipulam models diretamente; tudo passa por aqui.
"""

from __future__ import annotations

from django.contrib.auth import login
from django.db import transaction
from django.http import HttpRequest

from apps.accounts.forms import RegisterForm
from apps.accounts.models import User


class UserService:

    @staticmethod
    @transaction.atomic
    def register(form: RegisterForm, request: HttpRequest) -> User:
        """
        Cria o User, faz hash da senha e faz login automático.
        O Profile é criado pelo signal post_save.
        """
        user = form.save(commit=False)
        user.username = form.cleaned_data["email"]
        user.set_password(form.cleaned_data["password1"])
        user.save()
        login(request, user)
        return user

    @staticmethod
    @transaction.atomic
    def update_profile(user: User, form) -> User:
        """Salva alterações de perfil e dos campos first_name/last_name do User."""
        profile = form.save(commit=False)
        profile.save()

        user.first_name = form.cleaned_data.get("first_name", user.first_name)
        user.last_name = form.cleaned_data.get("last_name", user.last_name)
        user.save(update_fields=["first_name", "last_name"])
        return user
