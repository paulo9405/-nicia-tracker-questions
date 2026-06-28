"""
Mapeamento de cada SECAO do banco mestre para a disciplina (Subject) do sistema.

`category` ("basic" | "specific") sera usada na Fase 8 (simulados) para montar a
distribuicao da prova: 5 Portugues + 5 Matematica + 5 Informatica +
5 Conhecimentos Gerais + 20 Especificas.

Observacao (ajuste de modelo descoberto na Fase 3): o Subject da Fase 2 ganha um
campo `category`. Veja a secao "Ajustes de modelo" na documentacao da fase.
"""

from __future__ import annotations

from dataclasses import dataclass

BASIC = "basic"
SPECIFIC = "specific"


@dataclass(frozen=True)
class SubjectMapping:
    section_index: int
    name: str
    slug: str
    category: str
    color: str


SUBJECT_MAP: dict[int, SubjectMapping] = {
    1: SubjectMapping(1, "Saúde Única", "saude-unica", SPECIFIC, "#2e7d32"),
    2: SubjectMapping(
        2, "Zoonoses e Vigilância", "zoonoses-vigilancia", SPECIFIC, "#388e3c"
    ),
    3: SubjectMapping(
        3, "Segurança Alimentar", "seguranca-alimentar", SPECIFIC, "#43a047"
    ),
    4: SubjectMapping(4, "Bem-Estar Animal", "bem-estar-animal", SPECIFIC, "#558b2f"),
    5: SubjectMapping(
        5,
        "Medicina Veterinária do Coletivo",
        "medicina-veterinaria-coletivo",
        SPECIFIC,
        "#689f38",
    ),
    6: SubjectMapping(
        6,
        "Fauna e Legislação Ambiental",
        "fauna-legislacao-ambiental",
        SPECIFIC,
        "#7cb342",
    ),
    7: SubjectMapping(
        7,
        "Cirurgia, Anestesia e Contenção",
        "cirurgia-anestesia-contencao",
        SPECIFIC,
        "#33691e",
    ),
    8: SubjectMapping(
        8, "Fisiologia e Reprodução", "fisiologia-reproducao", SPECIFIC, "#00695c"
    ),
    9: SubjectMapping(
        9,
        "Lei Orgânica de Ponta Grossa",
        "lei-organica-ponta-grossa",
        SPECIFIC,
        "#00838f",
    ),
    10: SubjectMapping(10, "Português", "portugues", BASIC, "#1565c0"),
    11: SubjectMapping(11, "Informática", "informatica", BASIC, "#6a1b9a"),
    12: SubjectMapping(12, "Matemática", "matematica", BASIC, "#c62828"),
    13: SubjectMapping(
        13, "Conhecimentos Gerais", "conhecimentos-gerais", BASIC, "#ef6c00"
    ),
}


def mapping_for(section_index: int) -> SubjectMapping:
    try:
        return SUBJECT_MAP[section_index]
    except KeyError as exc:
        raise ValueError(
            f"Secao {section_index} sem mapeamento de disciplina definido."
        ) from exc
