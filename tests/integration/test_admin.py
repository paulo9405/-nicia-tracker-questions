"""
Smoke tests do Django admin (ferramenta de curadoria das questões).

Garantem que os ModelAdmin registrados na Fase 9 carregam sem erro — o admin
do User customizado (login por e-mail) é o ponto mais sensível.
"""

import pytest

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_logged(client):
    from apps.accounts.models import User

    admin = User.objects.create_superuser(
        email="admin@nicia.com", password="senha123segura"
    )
    client.force_login(admin)
    return client


@pytest.mark.parametrize(
    "url",
    [
        "/admin/",
        "/admin/questions/subject/",
        "/admin/questions/topic/",
        "/admin/questions/question/",
        "/admin/accounts/user/",
        "/admin/exams/quiz/",
        "/admin/exams/useranswer/",
    ],
)
def test_admin_changelist_carrega(admin_logged, url):
    assert admin_logged.get(url).status_code == 200


def test_admin_form_de_criacao_de_usuario_carrega(admin_logged):
    # add_fieldsets customizado (email + senhas) não deve quebrar.
    assert admin_logged.get("/admin/accounts/user/add/").status_code == 200
