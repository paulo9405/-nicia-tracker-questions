"""
Comando: importa o banco mestre de questoes para o PostgreSQL.

Exemplos:
    python manage.py import_questions docs/15_BANCO_MESTRE_DE_QUESTOES.md
    python manage.py import_questions docs/15_BANCO_MESTRE_DE_QUESTOES.md --dry-run
    python manage.py import_questions docs/15_BANCO_MESTRE_DE_QUESTOES.md --strict

Idempotente: rodar duas vezes nao duplica questoes (ver QuestionImportService).
"""

from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.questions.models import Question
from apps.questions.services.import_service import QuestionImportService

_EXPECTED_QUESTION_COUNT = 800


class Command(BaseCommand):
    help = "Importa o banco mestre de questoes (markdown) para o banco de dados."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "path",
            type=str,
            help="Caminho do arquivo markdown (ex.: docs/15_BANCO_MESTRE_DE_QUESTOES.md).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Analisa e relata o que seria importado, sem gravar no banco.",
        )
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Encerra com erro (exit code != 0) se houver qualquer erro de parsing.",
        )

    def handle(self, *args, **options) -> None:
        path = Path(options["path"])
        if not path.exists():
            raise CommandError(f"Arquivo nao encontrado: {path}")

        dry_run = options["dry_run"]

        if not dry_run and Question.objects.count() >= _EXPECTED_QUESTION_COUNT:
            self.stdout.write("Banco de questões já importado — pulando.")
            return

        service = QuestionImportService()

        self.stdout.write(self.style.MIGRATE_HEADING(f"Importando: {path}"))
        if dry_run:
            self.stdout.write(self.style.WARNING("Modo dry-run: nada sera gravado."))

        report = service.import_from_file(str(path), dry_run=dry_run)

        if report.parse_errors:
            self.stdout.write(self.style.ERROR("Erros de parsing encontrados:"))
            for err in report.parse_errors[:50]:
                self.stdout.write(f"  - {err}")
            if len(report.parse_errors) > 50:
                self.stdout.write(f"  ... e mais {len(report.parse_errors) - 50} erros")
            if options["strict"]:
                raise CommandError("Importacao abortada (--strict).")
            return

        self.stdout.write(self.style.SUCCESS("Parsing OK."))
        self.stdout.write(f"  Criadas    : {report.created}")
        self.stdout.write(f"  Atualizadas: {report.updated}")
        self.stdout.write(f"  Inalteradas: {report.unchanged}")
        self.stdout.write(
            f"  Disciplinas: {', '.join(sorted(report.subjects_touched))}"
        )
        self.stdout.write(self.style.SUCCESS("Concluido."))
