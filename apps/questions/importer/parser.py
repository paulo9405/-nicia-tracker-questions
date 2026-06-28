"""
Parser standalone (Python puro, sem Django) do BANCO MESTRE DE QUESTOES.

Projetado para o arquivo `15_BANCO_MESTRE_DE_QUESTOES.md`, cuja estrutura e:

    # SECAO N — TITULO
    ### NN questoes | Base: `arquivo_master.md`

    > Texto I para as questoes A a B:        (opcional — so em Portugues)
    >
    > *"...texto base..."*

    **1.** Enunciado da questao...
    A) alternativa A
    B) alternativa B
    C) alternativa C
    D) alternativa D

    ... (demais questoes) ...

    ---

    ### 🔑 GABARITO E COMENTARIOS — SECAO N
    | Q | Gab | Comentario resumido | Ref. MASTER |
    |---|-----|---------------------|-------------|
    | 1 | **D** | comentario... | 01 §3.1 |

    ---
    ---

Como o parser nao depende de Django, ele pode ser executado e testado
isoladamente contra o arquivo real (ver scripts/validate_parse.py).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path

# --------------------------------------------------------------------------- #
# Expressoes regulares (compiladas uma vez)
# --------------------------------------------------------------------------- #

RE_SECTION = re.compile(r"^#\s+SE[ÇC][ÃA]O\s+(\d+)\s*[—\-–]\s*(.+?)\s*$")
RE_SECTION_SUBTITLE = re.compile(
    r"^###\s+(\d+)\s+quest[õo]es\s*\|\s*Base:\s*`?(.+?)`?\s*$"
)
RE_GABARITO_HEADER = re.compile(r"^###\s+.*GABARITO E COMENT", re.IGNORECASE)
RE_QUESTION = re.compile(r"^\*\*(\d+)\.\*\*\s*(.*)$")
RE_ALTERNATIVE = re.compile(r"^([A-E])\)\s*(.*)$")
RE_BASE_TEXT = re.compile(
    r"^>\s*Texto\s+([IVXLCDM]+)\s+para\s+as\s+quest[õo]es\s+(\d+)\s+a\s+(\d+)\s*:",
    re.IGNORECASE,
)
RE_GABARITO_ROW = re.compile(
    r"^\|\s*(\d+)\s*\|\s*\*\*([A-E])\*\*\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|?\s*$"
)

VALID_LETTERS = ("A", "B", "C", "D")


# --------------------------------------------------------------------------- #
# Estruturas de dados do resultado
# --------------------------------------------------------------------------- #


@dataclass
class ParsedAlternative:
    letter: str
    text: str
    is_correct: bool = False


@dataclass
class ParsedQuestion:
    section_index: int
    section_title: str
    source_file: str
    number: int
    statement: str
    alternatives: list[ParsedAlternative] = field(default_factory=list)
    correct_letter: str | None = None
    explanation: str = ""
    master_ref: str = ""
    context_text: str | None = None

    @property
    def external_id(self) -> str:
        """Chave natural estavel: secao + numero da questao."""
        return f"banco-mestre-s{self.section_index:02d}-q{self.number:03d}"

    @property
    def content_hash(self) -> str:
        """Hash do conteudo relevante; muda se a questao for editada."""
        normalized = "|".join(
            [
                _normalize(self.statement),
                *[f"{a.letter}:{_normalize(a.text)}" for a in self.alternatives],
                f"correct:{self.correct_letter}",
                f"ctx:{_normalize(self.context_text or '')}",
            ]
        )
        return sha256(normalized.encode("utf-8")).hexdigest()


@dataclass
class ParseError:
    section_index: int
    question_number: int | None
    message: str

    def __str__(self) -> str:
        loc = f"secao {self.section_index}"
        if self.question_number is not None:
            loc += f", questao {self.question_number}"
        return f"[{loc}] {self.message}"


@dataclass
class ParseResult:
    questions: list[ParsedQuestion] = field(default_factory=list)
    errors: list[ParseError] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def stats(self) -> dict[str, int]:
        per_section: dict[int, int] = {}
        for q in self.questions:
            per_section[q.section_index] = per_section.get(q.section_index, 0) + 1
        return {
            "total_questions": len(self.questions),
            "total_sections": len(per_section),
            "total_errors": len(self.errors),
        }


# --------------------------------------------------------------------------- #
# Utilitarios
# --------------------------------------------------------------------------- #


def _normalize(text: str) -> str:
    """Normaliza texto para hashing/comparacao (lower, sem acento, sem espaco extra)."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", text).strip().lower()


def _roman_range(start: int, end: int) -> range:
    return range(start, end + 1)


# --------------------------------------------------------------------------- #
# Parser principal
# --------------------------------------------------------------------------- #


class BancoMestreParser:
    """Converte o markdown do banco mestre em ParsedQuestion."""

    def parse_file(self, path: str | Path) -> ParseResult:
        content = Path(path).read_text(encoding="utf-8")
        return self.parse_text(content)

    def parse_text(self, content: str) -> ParseResult:
        result = ParseResult()
        for block in self._split_sections(content):
            self._parse_section(block, result)
        return result

    # -- nivel: secao ------------------------------------------------------- #

    def _split_sections(self, content: str) -> list[list[str]]:
        """Quebra o documento em blocos de linhas, um por secao."""
        lines = content.splitlines()
        blocks: list[list[str]] = []
        current: list[str] | None = None
        for line in lines:
            if RE_SECTION.match(line):
                if current is not None:
                    blocks.append(current)
                current = [line]
            elif current is not None:
                current.append(line)
        if current is not None:
            blocks.append(current)
        return blocks

    def _parse_section(self, lines: list[str], result: ParseResult) -> None:
        header = RE_SECTION.match(lines[0])
        section_index = int(header.group(1))
        section_title = header.group(2).strip()

        source_file = ""
        gabarito_start = len(lines)
        for i, line in enumerate(lines[1:], start=1):
            sub = RE_SECTION_SUBTITLE.match(line)
            if sub and not source_file:
                source_file = sub.group(2).strip()
            if RE_GABARITO_HEADER.match(line):
                gabarito_start = i
                break

        body = lines[1:gabarito_start]
        gabarito_lines = lines[gabarito_start:]

        base_texts = self._parse_base_texts(body)
        questions = self._parse_questions(
            body, section_index, section_title, source_file, base_texts, result
        )
        gabarito = self._parse_gabarito(gabarito_lines, section_index, result)

        self._merge_gabarito(questions, gabarito, section_index, result)
        result.questions.extend(questions[number] for number in sorted(questions))

    # -- nivel: textos-base (Portugues) ------------------------------------ #

    def _parse_base_texts(self, body: list[str]) -> list[tuple[range, str]]:
        """Extrai blockquotes `> Texto N para as questoes A a B:` + conteudo."""
        texts: list[tuple[range, str]] = []
        i = 0
        while i < len(body):
            m = RE_BASE_TEXT.match(body[i])
            if not m:
                i += 1
                continue
            start, end = int(m.group(2)), int(m.group(3))
            collected: list[str] = []
            j = i + 1
            while j < len(body) and body[j].lstrip().startswith(">"):
                fragment = body[j].lstrip()[1:].strip().strip("*").strip('"').strip()
                if fragment:
                    collected.append(fragment)
                j += 1
            texts.append((_roman_range(start, end), " ".join(collected)))
            i = j
        return texts

    @staticmethod
    def _context_for(number: int, base_texts: list[tuple[range, str]]) -> str | None:
        for rng, text in base_texts:
            if number in rng:
                return text
        return None

    # -- nivel: questoes ---------------------------------------------------- #

    def _parse_questions(
        self,
        body: list[str],
        section_index: int,
        section_title: str,
        source_file: str,
        base_texts: list[tuple[range, str]],
        result: ParseResult,
    ) -> dict[int, ParsedQuestion]:
        questions: dict[int, ParsedQuestion] = {}
        current: ParsedQuestion | None = None
        current_alt: ParsedAlternative | None = None

        def close_current() -> None:
            nonlocal current, current_alt
            if current is not None:
                current.statement = current.statement.strip()
                questions[current.number] = current
            current = None
            current_alt = None

        for line in body:
            q_match = RE_QUESTION.match(line)
            if q_match:
                close_current()
                number = int(q_match.group(1))
                current = ParsedQuestion(
                    section_index=section_index,
                    section_title=section_title,
                    source_file=source_file,
                    number=number,
                    statement=q_match.group(2),
                    context_text=self._context_for(number, base_texts),
                )
                continue

            if current is None:
                continue

            alt_match = RE_ALTERNATIVE.match(line)
            if alt_match:
                letter = alt_match.group(1)
                current_alt = ParsedAlternative(letter=letter, text=alt_match.group(2))
                current.alternatives.append(current_alt)
                continue

            # Linha de continuacao (enunciado ou alternativa multi-linha).
            stripped = line.strip()
            if not stripped or stripped.startswith(">") or stripped.startswith("|"):
                continue
            if current_alt is not None:
                current_alt.text = f"{current_alt.text} {stripped}".strip()
            elif not current.alternatives:
                current.statement = f"{current.statement} {stripped}".strip()

        close_current()
        return questions

    # -- nivel: gabarito ---------------------------------------------------- #

    def _parse_gabarito(
        self, lines: list[str], section_index: int, result: ParseResult
    ) -> dict[int, tuple[str, str, str]]:
        """Retorna {numero: (letra, comentario, ref)}."""
        gabarito: dict[int, tuple[str, str, str]] = {}
        for line in lines:
            m = RE_GABARITO_ROW.match(line)
            if not m:
                continue
            number = int(m.group(1))
            letter = m.group(2)
            comment = m.group(3).strip()
            ref = m.group(4).strip()
            if number in gabarito:
                result.errors.append(
                    ParseError(section_index, number, "gabarito duplicado")
                )
            gabarito[number] = (letter, comment, ref)
        return gabarito

    def _merge_gabarito(
        self,
        questions: dict[int, ParsedQuestion],
        gabarito: dict[int, tuple[str, str, str]],
        section_index: int,
        result: ParseResult,
    ) -> None:
        for number, question in questions.items():
            entry = gabarito.get(number)
            if entry is None:
                result.errors.append(
                    ParseError(section_index, number, "sem gabarito correspondente")
                )
                continue
            letter, comment, ref = entry
            question.correct_letter = letter
            question.explanation = comment
            question.master_ref = ref
            for alt in question.alternatives:
                alt.is_correct = alt.letter == letter

        # Validacao estrutural de cada questao.
        for question in questions.values():
            self._validate_question(question, result)

        # Gabaritos orfaos (sem questao).
        for number in gabarito:
            if number not in questions:
                result.errors.append(
                    ParseError(section_index, number, "gabarito sem questao")
                )

    # -- validacao por questao --------------------------------------------- #

    def _validate_question(self, question: ParsedQuestion, result: ParseResult) -> None:
        si, n = question.section_index, question.number
        letters = [a.letter for a in question.alternatives]

        if len(question.alternatives) != 4:
            result.errors.append(
                ParseError(si, n, f"esperadas 4 alternativas, obtidas {len(letters)}")
            )
        if letters != list(VALID_LETTERS):
            result.errors.append(
                ParseError(si, n, f"alternativas fora do padrao A-D: {letters}")
            )
        if not question.statement:
            result.errors.append(ParseError(si, n, "enunciado vazio"))
        if any(not a.text for a in question.alternatives):
            result.errors.append(ParseError(si, n, "alternativa com texto vazio"))
        if question.correct_letter not in VALID_LETTERS:
            result.errors.append(
                ParseError(si, n, f"gabarito invalido: {question.correct_letter}")
            )
        correct_count = sum(1 for a in question.alternatives if a.is_correct)
        if correct_count != 1:
            result.errors.append(
                ParseError(si, n, f"esperada 1 correta, obtidas {correct_count}")
            )
