"""
Populates StudyChapter.content from the 14 MASTER markdown files.

Extraction strategy:
  - Modules 1-9, 11, 13: parse ## N. numbered section headers
  - Module 10: parse # BLOCO N — headers
  - Modules 12, 14: parse # MÓDULO N — headers
  - Module 14 chapters 4-5: split MÓDULO 4 at ## Tecnologia subsection

Run:
  python manage.py populate_chapter_content
  python manage.py populate_chapter_content --dry-run
"""

import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.study_plan.models import StudyChapter, StudyModule

# (module_order, chapter_order): {'type': ..., 'sections': [...]}
CHAPTER_MAP = {
    # ── Module 1 — Saúde Única (## N. format, sections 1-11) ──────────
    (1, 1): {'type': 'numbered', 'sections': [1, 2]},
    (1, 2): {'type': 'numbered', 'sections': [3]},
    (1, 3): {'type': 'numbered', 'sections': [4]},
    (1, 4): {'type': 'numbered', 'sections': [5]},
    (1, 5): {'type': 'numbered', 'sections': [6]},
    (1, 6): {'type': 'numbered', 'sections': [7]},
    (1, 7): {'type': 'numbered', 'sections': [8, 9, 10, 11]},
    # ── Module 2 — Zoonoses e Vigilância (sections 2-18, §1 skipped) ──
    (2, 1): {'type': 'numbered', 'sections': [2, 3]},
    (2, 2): {'type': 'numbered', 'sections': [4]},
    (2, 3): {'type': 'numbered', 'sections': [5]},
    (2, 4): {'type': 'numbered', 'sections': [6]},
    (2, 5): {'type': 'numbered', 'sections': [7]},
    (2, 6): {'type': 'numbered', 'sections': [8]},
    (2, 7): {'type': 'numbered', 'sections': [9, 10]},
    (2, 8): {'type': 'numbered', 'sections': [11, 12]},
    (2, 9): {'type': 'numbered', 'sections': [13, 14]},
    (2, 10): {'type': 'numbered', 'sections': [15, 16, 17, 18]},
    # ── Module 3 — Segurança Alimentar (sections 2-17, §1 skipped) ────
    (3, 1): {'type': 'numbered', 'sections': [2]},
    (3, 2): {'type': 'numbered', 'sections': [3]},
    (3, 3): {'type': 'numbered', 'sections': [4, 5]},
    (3, 4): {'type': 'numbered', 'sections': [6]},
    (3, 5): {'type': 'numbered', 'sections': [7, 8]},
    (3, 6): {'type': 'numbered', 'sections': [9]},
    (3, 7): {'type': 'numbered', 'sections': [10]},
    (3, 8): {'type': 'numbered', 'sections': [11, 12]},
    (3, 9): {'type': 'numbered', 'sections': [13, 14, 15, 16, 17]},
    # ── Module 4 — Bem-Estar Animal (sections 1-16) ───────────────────
    (4, 1): {'type': 'numbered', 'sections': [1, 2, 3, 4]},
    (4, 2): {'type': 'numbered', 'sections': [5]},
    (4, 3): {'type': 'numbered', 'sections': [6, 7]},
    (4, 4): {'type': 'numbered', 'sections': [8, 9]},
    (4, 5): {'type': 'numbered', 'sections': [10]},
    (4, 6): {'type': 'numbered', 'sections': [11]},
    (4, 7): {'type': 'numbered', 'sections': [12, 13, 14, 15, 16]},
    # ── Module 5 — Medicina Veterinária do Coletivo (2-15, §1 skipped)
    (5, 1): {'type': 'numbered', 'sections': [2, 3]},
    (5, 2): {'type': 'numbered', 'sections': [4, 5]},
    (5, 3): {'type': 'numbered', 'sections': [6, 7]},
    (5, 4): {'type': 'numbered', 'sections': [8, 9]},
    (5, 5): {'type': 'numbered', 'sections': [10, 11, 12, 13, 14, 15]},
    # ── Module 6 — Fauna e Legislação Ambiental (2-17, §1 skipped) ───
    (6, 1): {'type': 'numbered', 'sections': [2, 3]},
    (6, 2): {'type': 'numbered', 'sections': [4]},
    (6, 3): {'type': 'numbered', 'sections': [5, 6]},
    (6, 4): {'type': 'numbered', 'sections': [7, 8]},
    (6, 5): {'type': 'numbered', 'sections': [9, 10]},
    (6, 6): {'type': 'numbered', 'sections': [11, 12, 13]},
    (6, 7): {'type': 'numbered', 'sections': [14, 15, 16, 17]},
    # ── Module 7 — Cirurgia, Anestesia e Contenção (1-30; 31-33 skipped)
    (7, 1): {'type': 'numbered', 'sections': [1, 2, 3, 4]},
    (7, 2): {'type': 'numbered', 'sections': [5, 6, 7]},
    (7, 3): {'type': 'numbered', 'sections': [8, 9]},
    (7, 4): {'type': 'numbered', 'sections': [10, 11, 12]},
    (7, 5): {'type': 'numbered', 'sections': [13, 14, 15, 16, 17]},
    (7, 6): {'type': 'numbered', 'sections': [18, 19, 20]},
    (7, 7): {'type': 'numbered', 'sections': [21, 22]},
    (7, 8): {'type': 'numbered', 'sections': [23, 24, 25]},
    (7, 9): {'type': 'numbered', 'sections': [26, 27, 28, 29, 30]},
    # ── Module 8 — Fisiologia e Reprodução (sections 1-14) ───────────
    (8, 1): {'type': 'numbered', 'sections': [1, 2]},
    (8, 2): {'type': 'numbered', 'sections': [3, 4]},
    (8, 3): {'type': 'numbered', 'sections': [5, 6]},
    (8, 4): {'type': 'numbered', 'sections': [7, 8]},
    (8, 5): {'type': 'numbered', 'sections': [9, 10, 11]},
    (8, 6): {'type': 'numbered', 'sections': [12, 13, 14]},
    # ── Module 9 — Lei Orgânica de Ponta Grossa (sections 1-20) ──────
    (9, 1): {'type': 'numbered', 'sections': [1, 2]},
    (9, 2): {'type': 'numbered', 'sections': [3, 4]},
    (9, 3): {'type': 'numbered', 'sections': [5, 6]},
    (9, 4): {'type': 'numbered', 'sections': [7, 8]},
    (9, 5): {'type': 'numbered', 'sections': [9, 10]},
    (9, 6): {'type': 'numbered', 'sections': [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]},
    # ── Module 10 — Revisão Final de Véspera (# BLOCO N — format) ────
    (10, 1): {'type': 'bloco', 'sections': [1]},
    (10, 2): {'type': 'bloco', 'sections': [2]},
    (10, 3): {'type': 'bloco', 'sections': [3]},
    (10, 4): {'type': 'bloco', 'sections': [4]},
    (10, 5): {'type': 'bloco', 'sections': [5]},
    (10, 6): {'type': 'bloco', 'sections': [6]},
    (10, 7): {'type': 'bloco', 'sections': [7]},
    (10, 8): {'type': 'bloco', 'sections': [8]},
    (10, 9): {'type': 'bloco', 'sections': [9]},
    # ── Module 11 — Língua Portuguesa (## N. format, sections 1-21) ──
    (11, 1): {'type': 'numbered', 'sections': [1, 2]},
    (11, 2): {'type': 'numbered', 'sections': [3, 4]},
    (11, 3): {'type': 'numbered', 'sections': [5, 6]},
    (11, 4): {'type': 'numbered', 'sections': [7, 8]},
    (11, 5): {'type': 'numbered', 'sections': [9, 10]},
    (11, 6): {'type': 'numbered', 'sections': [11, 12]},
    (11, 7): {'type': 'numbered', 'sections': [13, 14]},
    (11, 8): {'type': 'numbered', 'sections': [15, 16, 17]},
    (11, 9): {'type': 'numbered', 'sections': [18, 19, 20, 21]},
    # ── Module 12 — Informática (# MÓDULO N — format) ─────────────────
    (12, 1): {'type': 'modulo', 'sections': [1]},
    (12, 2): {'type': 'modulo', 'sections': [2, 3]},
    (12, 3): {'type': 'modulo', 'sections': [4, 6]},
    (12, 4): {'type': 'modulo', 'sections': [5]},
    (12, 5): {'type': 'modulo', 'sections': [7, 8]},
    # ── Module 13 — Matemática (## N. format, sections 1-17) ─────────
    (13, 1): {'type': 'numbered', 'sections': [1, 2, 3, 4]},
    (13, 2): {'type': 'numbered', 'sections': [5, 6, 7]},
    (13, 3): {'type': 'numbered', 'sections': [8, 9]},
    (13, 4): {'type': 'numbered', 'sections': [10, 11, 12, 13, 14, 15, 16, 17]},
    # ── Module 14 — Conhecimentos Gerais (# MÓDULO N — format) ────────
    (14, 1): {'type': 'modulo', 'sections': [1]},
    (14, 2): {'type': 'modulo', 'sections': [2]},
    (14, 3): {'type': 'modulo', 'sections': [3]},
    # Chapters 4-5 split MÓDULO 4 at ## Tecnologia subsection
    (14, 4): {'type': 'modulo_head', 'modulo_num': 4, 'split_before': '\n## Tecnologia'},
    (14, 5): {'type': 'modulo_tail', 'modulo_num': 4, 'split_at': '\n## Tecnologia'},
}


class Command(BaseCommand):
    help = 'Popula StudyChapter.content a partir dos arquivos MASTER em docs/'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria feito sem salvar nada',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        docs_dir = Path(settings.BASE_DIR) / 'docs'

        if dry_run:
            self.stdout.write(self.style.WARNING('=== DRY RUN — nada será salvo ===\n'))

        # Cache module objects and file contents
        modules = {m.order: m for m in StudyModule.objects.all()}
        file_cache: dict[int, str] = {}

        stats = {'populated': 0, 'skipped': 0, 'empty': 0, 'chars': []}

        for (mod_order, ch_order), config in sorted(CHAPTER_MAP.items()):
            module = modules.get(mod_order)
            if module is None:
                self.stderr.write(f'  Módulo {mod_order} não encontrado no banco.')
                stats['skipped'] += 1
                continue

            if mod_order not in file_cache:
                path = docs_dir / module.master_file
                if not path.exists():
                    self.stderr.write(f'  Arquivo não encontrado: {path}')
                    stats['skipped'] += 1
                    continue
                file_cache[mod_order] = path.read_text(encoding='utf-8')

            file_content = file_cache[mod_order]

            try:
                chapter = StudyChapter.objects.get(module=module, order=ch_order)
            except StudyChapter.DoesNotExist:
                self.stderr.write(f'  Capítulo {mod_order}/{ch_order} não encontrado.')
                stats['skipped'] += 1
                continue

            content = self._extract(file_content, config)

            if not content.strip():
                self.stderr.write(
                    self.style.WARNING(f'  ⚠ M{mod_order} Cap{ch_order}: conteúdo vazio!')
                )
                stats['empty'] += 1
                continue

            char_count = len(content)
            stats['chars'].append(char_count)
            label = f'M{mod_order:02d}/Ch{ch_order:02d} ({char_count:,} chars)'

            if not dry_run:
                chapter.content = content
                chapter.save(update_fields=['content'])
                self.stdout.write(f'  ✓ {label}')
            else:
                preview = content[:120].replace('\n', ' ')
                self.stdout.write(f'  ~ {label} — "{preview}…"')

            stats['populated'] += 1

        # Summary
        total = stats['populated'] + stats['skipped'] + stats['empty']
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'{"DRY RUN | " if dry_run else ""}Populados: {stats["populated"]} | '
            f'Pulados: {stats["skipped"]} | Vazios: {stats["empty"]} | Total: {total}'
        ))
        if stats['chars']:
            avg = sum(stats['chars']) // len(stats['chars'])
            self.stdout.write(
                f'Caracteres — total: {sum(stats["chars"]):,} | '
                f'média: {avg:,} | '
                f'mín: {min(stats["chars"]):,} | '
                f'máx: {max(stats["chars"]):,}'
            )

    # ──────────────────────────────────────────────────────────────────
    # Extraction helpers
    # ──────────────────────────────────────────────────────────────────

    def _extract(self, file_content: str, config: dict) -> str:
        t = config['type']
        if t == 'numbered':
            return self._numbered(file_content, config['sections'])
        if t == 'bloco':
            return self._bloco(file_content, config['sections'])
        if t == 'modulo':
            return self._modulo(file_content, config['sections'])
        if t == 'modulo_head':
            raw = self._modulo(file_content, [config['modulo_num']])
            idx = raw.find(config['split_before'])
            return raw[:idx].strip() if idx > 0 else raw
        if t == 'modulo_tail':
            raw = self._modulo(file_content, [config['modulo_num']])
            idx = raw.find(config['split_at'])
            return raw[idx:].strip() if idx > 0 else raw
        raise ValueError(f'Tipo de extração desconhecido: {t}')

    def _parse_sections(self, file_content: str, header_pattern: str) -> dict[int, str]:
        """Generic section parser. Returns {section_num: content_string}."""
        lines = file_content.split('\n')
        sections: dict[int, str] = {}
        current_num: int | None = None
        current_lines: list[str] = []

        for line in lines:
            m = re.match(header_pattern, line)
            if m:
                if current_num is not None:
                    sections[current_num] = '\n'.join(current_lines).rstrip()
                current_num = int(m.group(1))
                current_lines = [line]
            elif current_num is not None:
                current_lines.append(line)

        if current_num is not None:
            sections[current_num] = '\n'.join(current_lines).rstrip()

        return sections

    def _numbered(self, file_content: str, section_nums: list[int]) -> str:
        """Extract ## N. numbered sections."""
        sections = self._parse_sections(file_content, r'^## (\d+)\.')
        parts = [sections[n] for n in sorted(section_nums) if n in sections]
        return '\n\n'.join(parts)

    def _bloco(self, file_content: str, bloco_nums: list[int]) -> str:
        """Extract # BLOCO N — sections (Module 10)."""
        sections = self._parse_sections(file_content, r'^# BLOCO (\d+) ')
        parts = [sections[n] for n in sorted(bloco_nums) if n in sections]
        return '\n\n'.join(parts)

    def _modulo(self, file_content: str, modulo_nums: list[int]) -> str:
        """Extract # MÓDULO N — sections (Modules 12 and 14)."""
        sections = self._parse_sections(file_content, r'^# MÓDULO (\d+) ')
        parts = [sections[n] for n in modulo_nums if n in sections]
        return '\n\n'.join(parts)
