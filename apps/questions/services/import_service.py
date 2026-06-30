"""
Service de importacao: persiste o resultado do parser no banco, de forma
idempotente (reimportar nao duplica; conteudo editado e atualizado).

Depende dos models da Fase 2 (apps.questions.models):
    Subject(name, slug, category, color, is_active)
    Question(subject, external_id, content_hash, statement/text, context_text,
             explanation, source, board, is_active)
    Alternative(question, letter, text, is_correct)

Idempotencia:
    - external_id (ex.: "banco-mestre-s01-q001") e a chave natural estavel.
    - content_hash detecta edicoes; se mudou, a questao e suas alternativas
      sao reescritas dentro de uma transacao.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from django.db import transaction

from apps.questions.importer.mapping import mapping_for
from apps.questions.importer.parser import (
    BancoMestreParser,
    ParsedQuestion,
    ParseResult,
)
from apps.questions.models import Alternative, Question, Subject

# Banca organizadora do concurso (constante para todo o banco mestre).
DEFAULT_BOARD = "Instituto UniFil"


@dataclass
class ImportReport:
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    subjects_touched: set[str] = field(default_factory=set)
    parse_errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.parse_errors

    def as_dict(self) -> dict:
        return {
            "created": self.created,
            "updated": self.updated,
            "unchanged": self.unchanged,
            "subjects": sorted(self.subjects_touched),
            "parse_errors": self.parse_errors,
        }


class QuestionImportService:
    """Orquestra parse + persistencia idempotente do banco mestre."""

    def __init__(self, parser: BancoMestreParser | None = None) -> None:
        self.parser = parser or BancoMestreParser()

    # -- API publica -------------------------------------------------------- #

    def import_from_file(self, path: str, dry_run: bool = False) -> ImportReport:
        result = self.parser.parse_file(path)
        return self._persist(result, dry_run=dry_run)

    # -- persistencia ------------------------------------------------------- #

    def _persist(self, result: ParseResult, dry_run: bool) -> ImportReport:
        report = ImportReport(parse_errors=[str(e) for e in result.errors])

        # Falha rapido: nao importa nada se o parse apresentou qualquer erro.
        if not result.ok:
            return report

        if dry_run:
            # Simula sem tocar no banco: conta o que seria criado.
            self._simulate(result, report)
            return report

        subjects = self._ensure_subjects(result)
        for parsed in result.questions:
            subject = subjects[parsed.section_index]
            self._upsert_question(parsed, subject, report)
        return report

    def _simulate(self, result: ParseResult, report: ImportReport) -> None:
        existing = dict(Question.objects.values_list("external_id", "content_hash"))
        for parsed in result.questions:
            report.subjects_touched.add(mapping_for(parsed.section_index).slug)
            current_hash = existing.get(parsed.external_id)
            if current_hash is None:
                report.created += 1
            elif current_hash != parsed.content_hash:
                report.updated += 1
            else:
                report.unchanged += 1

    def _ensure_subjects(self, result: ParseResult) -> dict[int, Subject]:
        subjects: dict[int, Subject] = {}
        section_indexes = {q.section_index for q in result.questions}
        for idx in sorted(section_indexes):
            m = mapping_for(idx)
            subject, _ = Subject.objects.update_or_create(
                slug=m.slug,
                defaults={
                    "name": m.name,
                    "category": m.category,
                    "color": m.color,
                    "is_active": True,
                },
            )
            subjects[idx] = subject
        return subjects

    @transaction.atomic
    def _upsert_question(
        self, parsed: ParsedQuestion, subject: Subject, report: ImportReport
    ) -> None:
        report.subjects_touched.add(subject.slug)
        explanation = self._compose_explanation(parsed)

        existing = (
            Question.objects.filter(external_id=parsed.external_id)
            .select_for_update()
            .first()
        )

        if existing is None:
            question = Question.objects.create(
                subject=subject,
                external_id=parsed.external_id,
                content_hash=parsed.content_hash,
                text=parsed.statement,
                context_text=parsed.context_text,
                explanation=explanation,
                source=parsed.source_file,
                board=DEFAULT_BOARD,
                is_active=True,
            )
            self._write_alternatives(question, parsed)
            report.created += 1
            return

        if existing.content_hash == parsed.content_hash:
            report.unchanged += 1
            return

        # Conteudo mudou: atualiza questao e regrava alternativas.
        existing.subject = subject
        existing.content_hash = parsed.content_hash
        existing.text = parsed.statement
        existing.context_text = parsed.context_text
        existing.explanation = explanation
        existing.source = parsed.source_file
        existing.board = DEFAULT_BOARD
        existing.is_active = True
        existing.save()

        for alt in parsed.alternatives:
            existing.alternatives.filter(letter=alt.letter).update(
                text=alt.text,
                is_correct=alt.is_correct,
            )
        report.updated += 1

    @staticmethod
    def _write_alternatives(question: Question, parsed: ParsedQuestion) -> None:
        Alternative.objects.bulk_create(
            [
                Alternative(
                    question=question,
                    letter=alt.letter,
                    text=alt.text,
                    is_correct=alt.is_correct,
                )
                for alt in parsed.alternatives
            ]
        )

    @staticmethod
    def _compose_explanation(parsed: ParsedQuestion) -> str:
        if parsed.master_ref:
            return f"{parsed.explanation}\n\nRef.: {parsed.master_ref}".strip()
        return parsed.explanation.strip()
