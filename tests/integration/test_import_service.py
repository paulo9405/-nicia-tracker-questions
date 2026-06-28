"""
Testes de integracao do QuestionImportService (requerem banco + models da Fase 2).

Marcados com @pytest.mark.django_db; rodam quando o projeto Django estiver
scaffoldado (apps.questions.models). Validam idempotencia e atualizacao.
"""

import pytest

pytestmark = pytest.mark.django_db

FIXTURE = """\
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


@pytest.fixture
def md_file(tmp_path):
    f = tmp_path / "banco.md"
    f.write_text(FIXTURE, encoding="utf-8")
    return str(f)


def _import(path, **kwargs):
    from apps.questions.services.import_service import QuestionImportService

    return QuestionImportService().import_from_file(path, **kwargs)


def test_primeira_importacao_cria(md_file):
    from apps.questions.models import Alternative, Question, Subject

    report = _import(md_file)
    assert report.created == 1
    assert Question.objects.count() == 1
    assert Alternative.objects.filter(is_correct=True).count() == 1
    assert Subject.objects.get(slug="saude-unica").category == "specific"


def test_reimportacao_nao_duplica(md_file):
    from apps.questions.models import Question

    _import(md_file)
    report = _import(md_file)
    assert report.unchanged == 1
    assert report.created == 0
    assert Question.objects.count() == 1


def test_conteudo_editado_atualiza(md_file, tmp_path):
    from apps.questions.models import Question

    _import(md_file)
    editado = FIXTURE.replace("| 1 | **C** |", "| 1 | **A** |")
    f2 = tmp_path / "banco2.md"
    f2.write_text(editado, encoding="utf-8")

    report = _import(str(f2))
    assert report.updated == 1
    assert Question.objects.count() == 1
    q = Question.objects.get(external_id="banco-mestre-s01-q001")
    assert q.alternatives.get(is_correct=True).letter == "A"


def test_dry_run_nao_grava(md_file):
    from apps.questions.models import Question

    report = _import(md_file, dry_run=True)
    assert report.created == 1
    assert Question.objects.count() == 0
