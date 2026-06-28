"""
Testes do management command `import_questions`.

Cobrem o ponto de entrada operacional: import normal, --dry-run, arquivo
inexistente e tratamento de erros de parsing (--strict vs relato silencioso).
"""

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

pytestmark = pytest.mark.django_db

FIXTURE_VALIDO = """\
# SEÇÃO 1 — SAÚDE ÚNICA
### 1 questões | Base: `01_SAUDE_UNICA_MASTER.md`

**1.** Enunciado?
A) A.
B) B.
C) C.
D) D.

---

### 🔑 GABARITO E COMENTÁRIOS — SEÇÃO 1

| Q | Gab | Comentário resumido | Ref. MASTER |
|---|-----|---------------------|-------------|
| 1 | **C** | Comentário. | 01 §1 |
"""

# Mesma questão, porém sem a linha de gabarito → gera erro de parsing.
FIXTURE_INVALIDO = """\
# SEÇÃO 1 — SAÚDE ÚNICA
### 1 questões | Base: `01_SAUDE_UNICA_MASTER.md`

**1.** Enunciado?
A) A.
B) B.
C) C.
D) D.

---

### 🔑 GABARITO E COMENTÁRIOS — SEÇÃO 1

| Q | Gab | Comentário resumido | Ref. MASTER |
|---|-----|---------------------|-------------|
"""


@pytest.fixture
def md_valido(tmp_path):
    f = tmp_path / "banco.md"
    f.write_text(FIXTURE_VALIDO, encoding="utf-8")
    return str(f)


@pytest.fixture
def md_invalido(tmp_path):
    f = tmp_path / "ruim.md"
    f.write_text(FIXTURE_INVALIDO, encoding="utf-8")
    return str(f)


def test_command_importa_questoes(md_valido):
    from apps.questions.models import Question

    call_command("import_questions", md_valido)
    assert Question.objects.count() == 1


def test_command_dry_run_nao_grava(md_valido):
    from apps.questions.models import Question

    call_command("import_questions", md_valido, "--dry-run")
    assert Question.objects.count() == 0


def test_command_arquivo_inexistente_levanta_erro():
    with pytest.raises(CommandError):
        call_command("import_questions", "/caminho/que/nao/existe.md")


def test_command_strict_aborta_quando_ha_erro_de_parsing(md_invalido):
    with pytest.raises(CommandError):
        call_command("import_questions", md_invalido, "--strict")


def test_command_sem_strict_relata_erro_sem_gravar(md_invalido):
    from apps.questions.models import Question

    call_command("import_questions", md_invalido)  # não levanta
    assert Question.objects.count() == 0
