"""
Testes do parser do banco mestre (Python puro, sem Django).

Inclui um teste de fumaça contra o arquivo real, se ele estiver presente.
"""

from pathlib import Path

import pytest

from apps.questions.importer.parser import BancoMestreParser

REAL_FILE = Path(__file__).resolve().parents[2] / "docs" / "15_BANCO_MESTRE_DE_QUESTOES.md"

SECTION_FIXTURE = """\
# SEÇÃO 1 — SAÚDE ÚNICA
### 2 questões | Base: `01_SAUDE_UNICA_MASTER.md`

**1.** Enunciado da questão um?
A) Alternativa A.
B) Alternativa B.
C) Alternativa C.
D) Alternativa D.

**2.** Enunciado da questão dois?
A) Outra A.
B) Outra B.
C) Outra C.
D) Outra D.

---

### 🔑 GABARITO E COMENTÁRIOS — SEÇÃO 1

| Q | Gab | Comentário resumido | Ref. MASTER |
|---|-----|---------------------|-------------|
| 1 | **D** | Comentário um. | 01 §1.1 |
| 2 | **A** | Comentário dois. | 01 §1.2 |

---
---
"""

PORTUGUES_FIXTURE = """\
# SEÇÃO 10 — PORTUGUÊS
### 2 questões | Base: `11_PORTUGUES_CONCURSO_MASTER.md`

> Texto I para as questões 1 a 2:
>
> *"Um texto-base de exemplo para interpretação."*

**1.** Sobre o Texto I, é correto afirmar?
A) Errada.
B) Certa.
C) Errada.
D) Errada.

**2.** Outra sobre o Texto I?
A) Certa.
B) Errada.
C) Errada.
D) Errada.

---

### 🔑 GABARITO E COMENTÁRIOS — SEÇÃO 10 (PORTUGUÊS)

| Q | Gab | Comentário resumido | Ref. MASTER |
|---|-----|---------------------|-------------|
| 1 | **B** | ok. | 11 §1 |
| 2 | **A** | ok. | 11 §1 |
"""


class TestParserBasico:
    def test_extrai_duas_questoes(self):
        result = BancoMestreParser().parse_text(SECTION_FIXTURE)
        assert result.ok, result.errors
        assert result.stats["total_questions"] == 2

    def test_metadados_da_secao(self):
        q = BancoMestreParser().parse_text(SECTION_FIXTURE).questions[0]
        assert q.section_index == 1
        assert q.section_title == "SAÚDE ÚNICA"
        assert q.source_file == "01_SAUDE_UNICA_MASTER.md"
        assert q.number == 1

    def test_gabarito_marca_alternativa_correta(self):
        questions = BancoMestreParser().parse_text(SECTION_FIXTURE).questions
        q1 = questions[0]
        assert q1.correct_letter == "D"
        corretas = [a for a in q1.alternatives if a.is_correct]
        assert len(corretas) == 1 and corretas[0].letter == "D"

    def test_explicacao_e_ref(self):
        q = BancoMestreParser().parse_text(SECTION_FIXTURE).questions[0]
        assert q.explanation == "Comentário um."
        assert q.master_ref == "01 §1.1"

    def test_external_id_estavel(self):
        q = BancoMestreParser().parse_text(SECTION_FIXTURE).questions[0]
        assert q.external_id == "banco-mestre-s01-q001"

    def test_content_hash_muda_com_edicao(self):
        a = BancoMestreParser().parse_text(SECTION_FIXTURE).questions[0]
        editado = SECTION_FIXTURE.replace("Enunciado da questão um?", "Enunciado EDITADO?")
        b = BancoMestreParser().parse_text(editado).questions[0]
        assert a.content_hash != b.content_hash


class TestTextoBase:
    def test_contexto_associado_as_questoes(self):
        questions = BancoMestreParser().parse_text(PORTUGUES_FIXTURE).questions
        assert all("texto-base de exemplo" in (q.context_text or "") for q in questions)


class TestValidacoes:
    def test_questao_sem_gabarito_gera_erro(self):
        texto = SECTION_FIXTURE.replace("| 2 | **A** | Comentário dois. | 01 §1.2 |\n", "")
        result = BancoMestreParser().parse_text(texto)
        assert not result.ok
        assert any("sem gabarito" in str(e) for e in result.errors)

    def test_alternativa_faltando_gera_erro(self):
        texto = SECTION_FIXTURE.replace("D) Alternativa D.\n", "")
        result = BancoMestreParser().parse_text(texto)
        assert not result.ok
        assert any("4 alternativas" in str(e) for e in result.errors)


@pytest.mark.skipif(not REAL_FILE.exists(), reason="arquivo real ausente")
class TestArquivoReal:
    def test_oitocentas_questoes_sem_erro(self):
        result = BancoMestreParser().parse_file(REAL_FILE)
        assert result.ok, result.errors[:10]
        assert result.stats["total_questions"] == 800
        assert result.stats["total_sections"] == 13

    def test_todas_tem_quatro_alternativas_e_uma_correta(self):
        result = BancoMestreParser().parse_file(REAL_FILE)
        for q in result.questions:
            assert [a.letter for a in q.alternatives] == ["A", "B", "C", "D"]
            assert sum(a.is_correct for a in q.alternatives) == 1
