"""
Valida o parser contra o arquivo real, sem depender de Django.

Uso:
    python scripts/validate_parse.py docs/15_BANCO_MESTRE_DE_QUESTOES.md
"""

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from apps.questions.importer.parser import BancoMestreParser  # noqa: E402


def main(path: str) -> int:
    result = BancoMestreParser().parse_file(path)

    print("=" * 60)
    print("RESULTADO DO PARSE")
    print("=" * 60)
    print(f"Total de questoes : {result.stats['total_questions']}")
    print(f"Total de secoes   : {result.stats['total_sections']}")
    print(f"Total de erros    : {result.stats['total_errors']}")
    print()

    per_section = Counter(q.section_index for q in result.questions)
    print("Questoes por secao:")
    for idx in sorted(per_section):
        title = next(q.section_title for q in result.questions if q.section_index == idx)
        src = next(q.source_file for q in result.questions if q.section_index == idx)
        print(f"  Secao {idx:2d} — {title:40s} {per_section[idx]:3d}  ({src})")
    print()

    with_ctx = sum(1 for q in result.questions if q.context_text)
    print(f"Questoes com texto-base (contexto): {with_ctx}")
    print()

    answer_dist = Counter(q.correct_letter for q in result.questions)
    print(f"Distribuicao de gabaritos: {dict(sorted(answer_dist.items()))}")
    print()

    if result.errors:
        print("ERROS:")
        for err in result.errors[:50]:
            print(f"  - {err}")
        if len(result.errors) > 50:
            print(f"  ... e mais {len(result.errors) - 50} erros")
        return 1

    print("OK — nenhum erro de parsing.")
    print()
    print("Amostra (primeira questao):")
    q = result.questions[0]
    print(f"  external_id : {q.external_id}")
    print(f"  enunciado   : {q.statement[:70]}...")
    for a in q.alternatives:
        mark = "X" if a.is_correct else " "
        print(f"    [{mark}] {a.letter}) {a.text[:60]}")
    print(f"  explicacao  : {q.explanation[:60]}")
    print(f"  ref. master : {q.master_ref}")
    print(f"  content_hash: {q.content_hash[:16]}...")
    return 0


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "docs/15_BANCO_MESTRE_DE_QUESTOES.md"
    raise SystemExit(main(target))
