from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.django_db


class TestUserServiceRegister:
    def test_cria_usuario_com_email_como_username(self):
        from apps.accounts.forms import RegisterForm
        from apps.accounts.services.user_service import UserService

        data = {
            "first_name": "Nícia",
            "last_name": "Dijkinga",
            "email": "nicia@test.com",
            "password1": "Segura@2026",
            "password2": "Segura@2026",
        }
        form = RegisterForm(data=data)
        assert form.is_valid(), form.errors

        request = MagicMock()
        user = UserService.register(form, request)
        assert user.email == "nicia@test.com"
        assert user.username == "nicia@test.com"
        assert user.check_password("Segura@2026")

    def test_cria_profile_automaticamente(self):
        from apps.accounts.forms import RegisterForm
        from apps.accounts.services.user_service import UserService

        data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@test.com",
            "password1": "Segura@2026",
            "password2": "Segura@2026",
        }
        form = RegisterForm(data=data)
        assert form.is_valid(), form.errors

        request = MagicMock()
        user = UserService.register(form, request)
        assert hasattr(user, "profile")
        assert user.profile is not None

    def test_email_duplicado_invalida_form(self, user):
        from apps.accounts.forms import RegisterForm

        data = {
            "first_name": "Outra",
            "last_name": "Pessoa",
            "email": user.email,
            "password1": "Segura@2026",
            "password2": "Segura@2026",
        }
        form = RegisterForm(data=data)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_senhas_diferentes_invalida_form(self):
        from apps.accounts.forms import RegisterForm

        data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "novo@test.com",
            "password1": "Segura@2026",
            "password2": "DiferenteSenha",
        }
        form = RegisterForm(data=data)
        assert not form.is_valid()


class TestUserServiceUpdateProfile:
    def test_atualiza_perfil(self, user):
        from apps.accounts.forms import ProfileForm
        from apps.accounts.services.user_service import UserService

        data = {
            "first_name": "Nícia Editada",
            "last_name": "Dijkinga",
            "target_contest": "Médico Veterinário — PG 2026",
            "daily_goal": 20,
            "study_level": "intermediate",
            "bio": "",
        }
        form = ProfileForm(data=data, instance=user.profile)
        assert form.is_valid(), form.errors
        UserService.update_profile(user, form)

        user.refresh_from_db()
        assert user.first_name == "Nícia Editada"
        assert user.profile.target_contest == "Médico Veterinário — PG 2026"
        assert user.profile.daily_goal == 20
