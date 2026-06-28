import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestRegisterView:
    url = reverse("accounts:register")

    def test_get_exibe_formulario(self, client):
        r = client.get(self.url)
        assert r.status_code == 200
        assert "form" in r.context

    def test_registro_valido_cria_usuario_e_redireciona(self, client):
        from apps.accounts.models import User

        data = {
            "first_name": "Nícia",
            "last_name": "Dijkinga",
            "email": "nova@test.com",
            "password1": "Segura@2026",
            "password2": "Segura@2026",
        }
        r = client.post(self.url, data)
        assert r.status_code == 302
        assert User.objects.filter(email="nova@test.com").exists()

    def test_usuario_autenticado_e_redirecionado(self, client_logged):
        r = client_logged.get(self.url)
        assert r.status_code == 302

    def test_email_duplicado_retorna_form_com_erro(self, client, user):
        data = {
            "first_name": "Outra",
            "last_name": "Pessoa",
            "email": user.email,
            "password1": "Segura@2026",
            "password2": "Segura@2026",
        }
        r = client.post(self.url, data)
        assert r.status_code == 200
        assert "email" in r.context["form"].errors


class TestLoginView:
    url = reverse("accounts:login")

    def test_get_exibe_formulario(self, client):
        r = client.get(self.url)
        assert r.status_code == 200

    def test_login_valido_redireciona(self, client, user):
        r = client.post(
            self.url, {"username": user.email, "password": "senha123segura"}
        )
        assert r.status_code == 302

    def test_credenciais_invalidas_retorna_form(self, client):
        r = client.post(self.url, {"username": "x@x.com", "password": "errada"})
        assert r.status_code == 200
        assert r.context["form"].errors


class TestLogoutView:
    url = reverse("accounts:logout")

    def test_get_exibe_confirmacao(self, client_logged):
        r = client_logged.get(self.url)
        assert r.status_code == 200

    def test_post_desloga_e_redireciona(self, client_logged):
        r = client_logged.post(self.url)
        assert r.status_code == 302
        assert r.url == reverse("accounts:login")

    def test_nao_autenticado_redireciona_para_login(self, client):
        r = client.get(self.url)
        assert r.status_code == 302


class TestProfileView:
    url = reverse("accounts:profile")

    def test_nao_autenticado_redireciona(self, client):
        r = client.get(self.url)
        assert r.status_code == 302

    def test_get_exibe_formulario(self, client_logged):
        r = client_logged.get(self.url)
        assert r.status_code == 200
        assert "form" in r.context

    def test_post_salva_e_redireciona(self, client_logged, user):
        data = {
            "first_name": "Nícia",
            "last_name": "Dijkinga",
            "target_contest": "MV Ponta Grossa 2026",
            "daily_goal": 15,
            "study_level": "intermediate",
            "bio": "",
        }
        r = client_logged.post(self.url, data)
        assert r.status_code == 302
        user.profile.refresh_from_db()
        assert user.profile.target_contest == "MV Ponta Grossa 2026"
