import pytest


@pytest.fixture
def user(db):
    from apps.accounts.models import User

    return User.objects.create_user(
        email="nicia@exemplo.com",
        password="senha123segura",
        first_name="Nícia",
        last_name="Dijkinga",
    )


@pytest.fixture
def client_logged(client, user):
    client.force_login(user)
    return client
