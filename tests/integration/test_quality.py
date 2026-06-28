"""
Testes de qualidade transversais (Fase 9).
"""

import pytest

pytestmark = pytest.mark.django_db


def test_mensagem_de_erro_renderiza_com_classe_bootstrap_danger(client_logged):
    """
    O nível ERROR do Django deve renderizar como `alert-danger` (Bootstrap),
    não `alert-error`. Sem MESSAGE_TAGS, o alerta sairia sem estilo vermelho.

    Com o banco de teste vazio (sem questões), iniciar um simulado dispara
    InsufficientQuestionsError → messages.error.
    """
    resp = client_logged.post("/questoes/simulado/", follow=True)
    assert resp.status_code == 200
    assert b"alert-danger" in resp.content
    assert b"alert-error" not in resp.content
