"""
Management command: import_study_plan

Popula StudyModule e StudyChapter a partir do mapeamento explícito definido em
docs/STUDY_CONTENT_MAPPING.md (fonte de verdade para humanos) e replicado em
STUDY_PLAN_MAP abaixo (fonte de verdade para código).

Idempotente: rodar múltiplas vezes não duplica registros.
O conteúdo (chapter.content) não é preenchido aqui — será editado via admin
ou por um comando separado que extrai seções dos arquivos MASTER.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.questions.models import Subject
from apps.study_plan.models import StudyChapter, StudyModule


@dataclass
class ChapterDef:
    order: int
    title: str
    sections_source: str
    estimated_minutes: int
    tags: list[str]


@dataclass
class ModuleDef:
    order: int
    title: str
    slug: str
    master_file: str
    subject_slug: Optional[str]
    category: str
    study_phase: str
    estimated_hours: float
    icon: str
    description: str
    chapters: list[ChapterDef] = field(default_factory=list)


STUDY_PLAN_MAP: list[ModuleDef] = [
    ModuleDef(
        order=1,
        title="Saúde Única",
        slug="saude-unica",
        master_file="01_SAUDE_UNICA_MASTER.md",
        subject_slug="saude-unica",
        category="specific",
        study_phase="1",
        estimated_hours=8.0,
        icon="🌿",
        description="Fundamentos de One Health, resistência antimicrobiana e papel do médico veterinário na saúde pública.",
        chapters=[
            ChapterDef(1, "Conceitos Fundamentais de Saúde Pública", "§1, §2 (2.1–2.3)", 25, ["saude-publica", "saude-coletiva", "glossario"]),
            ChapterDef(2, "One Health — Conceito, Histórico e Princípios", "§3 (3.1–3.5)", 40, ["one-health", "ohhlep", "manhattan", "saude-unica"]),
            ChapterDef(3, "Relação Saúde Humana, Animal e Ambiental", "§4 (4.1–4.4)", 25, ["saude-ambiental", "cisticercose", "mudancas-climaticas"]),
            ChapterDef(4, "Zoonoses e Doenças Emergentes", "§5 (5.1–5.5)", 20, ["zoonoses", "doencas-emergentes", "guia-tripartite"]),
            ChapterDef(5, "Resistência Antimicrobiana e PAN-BR", "§6 (6.1–6.4)", 35, ["resistencia-antimicrobiana", "pan-br", "amr", "objetivos-estrategicos"]),
            ChapterDef(6, "Papel do Médico Veterinário na Saúde Única", "§7 (7.1–7.3)", 20, ["medico-veterinario", "saude-unica", "alimentos-seguros"]),
            ChapterDef(7, "Legislação, Tópicos Cobrados e Flashcards", "§8, §9, §10, §11", 20, ["legislacao", "saude-unica", "revisao"]),
        ],
    ),
    ModuleDef(
        order=2,
        title="Zoonoses e Vigilância",
        slug="zoonoses-vigilancia",
        master_file="02_ZOONOSES_VIGILANCIA_MASTER.md",
        subject_slug="zoonoses-vigilancia",
        category="specific",
        study_phase="1",
        estimated_hours=12.0,
        icon="🦟",
        description="Vigilância epidemiológica, notificação compulsória e as principais zoonoses cobradas em concursos.",
        chapters=[
            ChapterDef(1, "Vigilância Epidemiológica e Notificação Compulsória", "§2 (2.1–2.4), §3 (3.1–3.6)", 40, ["vigilancia-epidemiologica", "notificacao-compulsoria", "sinan", "portaria-mpa-19"]),
            ChapterDef(2, "Centros de Controle de Zoonoses (CCZ/UVZ)", "§4 (4.1–4.2)", 20, ["ccz", "uvz", "controle-zoonoses", "vetores"]),
            ChapterDef(3, "Raiva — Epidemiologia e Profilaxia", "§5 (5.1–5.4)", 40, ["raiva", "profilaxia-raiva", "ciclos-raiva", "pos-exposicao"]),
            ChapterDef(4, "Leishmaniose — Tegumentar e Visceral", "§6 (6.1–6.2)", 30, ["leishmaniose", "leishmaniose-tegumentar", "leishmaniose-visceral", "calazar"]),
            ChapterDef(5, "Leptospirose", "§7", 25, ["leptospirose"]),
            ChapterDef(6, "Toxoplasmose", "§8", 20, ["toxoplasmose"]),
            ChapterDef(7, "Brucelose e Tuberculose", "§9, §10", 30, ["brucelose", "tuberculose"]),
            ChapterDef(8, "Hantavirose e Febre Maculosa", "§11, §12", 25, ["hantavirose", "febre-maculosa"]),
            ChapterDef(9, "Animais Peçonhentos e Outras Zoonoses", "§13, §14 (14.1–14.7)", 30, ["animais-peconhentos", "teniase-cisticercose", "febre-amarela", "influenza-aviaria", "larva-migrans"]),
            ChapterDef(10, "Legislação, Tópicos Cobrados e Flashcards", "§15, §16, §17, §18", 20, ["legislacao", "zoonoses", "revisao"]),
        ],
    ),
    ModuleDef(
        order=3,
        title="Segurança Alimentar",
        slug="seguranca-alimentar",
        master_file="03_SEGURANCA_ALIMENTAR_MASTER.md",
        subject_slug="seguranca-alimentar",
        category="specific",
        study_phase="1",
        estimated_hours=10.0,
        icon="🍽️",
        description="BPF, RDC 216/275/724, padrões microbiológicos, APPCC e resíduos de serviços de saúde.",
        chapters=[
            ChapterDef(1, "BPF — Fundamentos e Multiplicação Microbiana", "§2 (2.1–2.3)", 30, ["boas-praticas", "bpf", "multiplicacao-microbiana", "contaminacao-cruzada"]),
            ChapterDef(2, "RDC 216/2004 — Serviços de Alimentação", "§3 (3.1–3.4)", 35, ["rdc-216", "temperatura", "higienizacao", "manipuladores"]),
            ChapterDef(3, "RDC 275/2002 — POPs e Lista de Verificação", "§4 (4.1–4.4), §5 (5.1–5.4)", 35, ["rdc-275", "pop", "lista-verificacao", "procedimentos-operacionais"]),
            ChapterDef(4, "APPCC — Análise de Perigos e PCCs", "§6 (6.1–6.3)", 25, ["appcc", "haccp", "ponto-critico", "sete-principios"]),
            ChapterDef(5, "Padrões Microbiológicos — Conceitos e RDC 724/2022", "§7 (7.1–7.4), §8 (8.1–8.3)", 35, ["padroes-microbiologicos", "rdc-724", "microrganismos"]),
            ChapterDef(6, "IN 161/2022 e IN 313/2024", "§9 (9.1–9.8)", 30, ["in-161", "in-313", "listeria", "criterios-microbiologicos"]),
            ChapterDef(7, "Interpretação de Resultados Microbiológicos", "§10 (10.1–10.5)", 30, ["plano-duas-classes", "plano-tres-classes", "amostra-representativa"]),
            ChapterDef(8, "Resíduos de Serviços de Saúde e RDC 222/2018", "§11 (11.1–11.6), §12 (12.1–12.4)", 35, ["rss", "rdc-222", "pgrss", "grupos-rss"]),
            ChapterDef(9, "Fiscalização, Legislação e Flashcards", "§13, §14, §15, §16, §17", 20, ["fiscalizacao", "legislacao", "seguranca-alimentar", "revisao"]),
        ],
    ),
    ModuleDef(
        order=4,
        title="Bem-Estar Animal",
        slug="bem-estar-animal",
        master_file="04_BEM_ESTAR_ANIMAL_MASTER.md",
        subject_slug="bem-estar-animal",
        category="specific",
        study_phase="1",
        estimated_hours=8.0,
        icon="🐾",
        description="Senciência, cinco liberdades, enriquecimento ambiental, maus-tratos e Lei Sansão.",
        chapters=[
            ChapterDef(1, "Conceitos de BEA, Senciência e Cinco Liberdades", "§1 (1.1–1.2), §2, §3, §4", 35, ["bem-estar-animal", "senciencia", "cinco-liberdades", "etologia"]),
            ChapterDef(2, "Indicadores de BEA e Welfare Quality", "§5 (5.1–5.4)", 25, ["indicadores-bea", "welfare-quality", "indicadores-comportamentais"]),
            ChapterDef(3, "Dor, Estresse e Cortisol", "§6 (6.1–6.2), §7 (7.1–7.2)", 25, ["dor", "estresse", "cortisol", "cascata-fisiologica"]),
            ChapterDef(4, "Enriquecimento Ambiental e Transporte Animal", "§8 (8.1–8.3), §9 (9.1–9.3)", 25, ["enriquecimento-ambiental", "transporte-animal", "boas-praticas"]),
            ChapterDef(5, "Abate Humanitário", "§10 (10.1–10.2)", 20, ["abate-humanitario", "insensibilizacao"]),
            ChapterDef(6, "Maus-Tratos — Art. 32 da Lei 9.605/98", "§11 (11.1–11.6)", 30, ["maus-tratos", "art-32", "lei-9605", "dolo-culpa"]),
            ChapterDef(7, "Lei Sansão, Legislação e Flashcards", "§12, §13 (13.1), §14, §15, §16", 25, ["lei-sansao", "tres-rs", "legislacao", "bem-estar-animal", "revisao"]),
        ],
    ),
    ModuleDef(
        order=5,
        title="Medicina Veterinária do Coletivo",
        slug="medicina-veterinaria-coletivo",
        master_file="05_MED_VET_COLETIVO_MASTER.md",
        subject_slug="medicina-veterinaria-coletivo",
        category="specific",
        study_phase="1",
        estimated_hours=8.0,
        icon="🏥",
        description="Guarda responsável, controle populacional, castração coletiva e políticas públicas para animais.",
        chapters=[
            ChapterDef(1, "MVC e Guarda Responsável", "§2 (2.1–2.2), §3", 30, ["medicina-coletiva", "guarda-responsavel", "nasf", "mudanca-paradigma"]),
            ChapterDef(2, "Controle Populacional e Manejo Ético", "§4 (4.1–4.6), §5 (5.1–5.3)", 35, ["controle-populacional", "manejo-etico", "oms-informe", "exterminio-ineficaz"]),
            ChapterDef(3, "Castração e Programas de Esterilização", "§6 (6.1–6.3), §7 (7.1–7.5)", 30, ["castracao", "esterilizacao", "res-cfmv-1596", "castracao-quimica-vedada"]),
            ChapterDef(4, "Abrigos, Adoção e Eutanásia", "§8 (8.1–8.3), §9 (9.1–9.2)", 25, ["abrigo", "adocao", "eutanasia", "cata"]),
            ChapterDef(5, "CCZs, Políticas Públicas e Legislação", "§10 (10.1), §11 (11.1–11.3), §12, §13, §14, §15", 25, ["ccz", "politica-publica", "legislacao", "revisao"]),
        ],
    ),
    ModuleDef(
        order=6,
        title="Fauna e Legislação Ambiental",
        slug="fauna-legislacao-ambiental",
        master_file="06_FAUNA_AMBIENTAL_MASTER.md",
        subject_slug="fauna-legislacao-ambiental",
        category="specific",
        study_phase="1",
        estimated_hours=8.0,
        icon="🦜",
        description="CETAS, crimes contra a fauna, Lei 9.605/98, CONCEA e reabilitação de animais silvestres.",
        chapters=[
            ChapterDef(1, "Conceitos de Fauna Silvestre e Proteção Legal", "§2, §3 (3.1–3.4)", 30, ["fauna-silvestre", "protecao-fauna", "manejo", "contencao-fisica"]),
            ChapterDef(2, "CETAS — Funcionamento e Triagem", "§4 (4.1–4.2)", 25, ["cetas", "triagem", "fauna-silvestre", "recebimento"]),
            ChapterDef(3, "Destinação e Soltura de Animais Silvestres", "§5 (5.1–5.2), §6 (6.1)", 25, ["destinacao", "soltura", "reabilitacao", "reintroducao"]),
            ChapterDef(4, "SISBio, CONCEA e CEUA", "§7, §8 (8.1–8.2)", 20, ["sisbio", "concea", "ceua", "tres-rs"]),
            ChapterDef(5, "Criadouros, Pesquisa e Anestesia em Campo", "§9 (9.1), §10 (10.1–10.2)", 20, ["criadouros", "pesquisa-animal", "anestesia-campo"]),
            ChapterDef(6, "Lei 9.605/98 — Crimes Ambientais e Contra a Fauna", "§11 (11.1–11.4), §12 (12.1–12.2), §13", 35, ["lei-9605", "crimes-ambientais", "crimes-fauna", "art-29", "art-32", "art-37"]),
            ChapterDef(7, "Legislação, Tópicos Cobrados e Flashcards", "§14, §15, §16, §17", 20, ["legislacao", "fauna", "revisao"]),
        ],
    ),
    ModuleDef(
        order=7,
        title="Cirurgia, Anestesia e Contenção",
        slug="cirurgia-anestesia-contencao",
        master_file="07_CIRURGIA_ANESTESIA_CONTENCAO_MASTER.md",
        subject_slug="cirurgia-anestesia-contencao",
        category="specific",
        study_phase="1",
        estimated_hours=18.0,
        icon="💉",
        description="⚠️ LACUNA — Anestesiologia, cirurgia de castração (orquiectomia/OSH) e contenção química de fauna.",
        chapters=[
            ChapterDef(1, "Conceitos e Avaliação Pré-Anestésica", "§1, §2, §3 (ASA), §4 (jejum)", 35, ["anestesiologia", "pre-anestesico", "tripe-anestesico", "asa", "jejum"]),
            ChapterDef(2, "MPA — Fenotiazínicos e Benzodiazepínicos", "§5, §6 (acepromazina), §7 (benzodiazepinicos)", 30, ["mpa", "acepromazina", "diazepam", "midazolam"]),
            ChapterDef(3, "Alfa-2 Agonistas e Opioides", "§8 (xilazina, dexmedetomidina), §9 (opioides)", 35, ["alfa2-agonistas", "xilazina", "dexmedetomidina", "opioides", "morfina"]),
            ChapterDef(4, "Propofol, Cetamina e Anestesia Inalatória", "§10 (propofol), §11 (cetamina), §12 (inalatoria)", 35, ["propofol", "cetamina", "isoflurano", "anestesia-inalatoria"]),
            ChapterDef(5, "Anestesia Local, Analgesia e Monitorização", "§13, §14, §15, §16, §17", 40, ["anestesia-local", "analgesia-multimodal", "monitorizacao", "emergencias-anestesicas"]),
            ChapterDef(6, "Princípios Cirúrgicos, Assepsia e Instrumental", "§18 (Halsted), §19 (assepsia), §20 (instrumental)", 30, ["principios-halsted", "assepsia", "antissepsia", "esterilizacao", "instrumental-cirurgico", "fios"]),
            ChapterDef(7, "Orquiectomia em Cães e Gatos", "§21 (orquiectomia-caes), §22 (orquiectomia-gatos)", 30, ["orquiectomia", "castracao-caes", "castracao-gatos"]),
            ChapterDef(8, "OSH, Complicações e Pós-Operatório", "§23 (osh), §24 (complicacoes), §25 (pos-operatorio)", 30, ["osh", "ovariohisterectomia", "complicacoes-cirurgicas", "pos-operatorio"]),
            ChapterDef(9, "Contenção Química de Fauna Silvestre", "§26, §27 (dardos), §28 (dissociativos), §29 (megafauna), §30 (riscos)", 35, ["contencao-quimica", "fauna-silvestre", "miopatia-captura", "dardos", "tiletamina-zolazepam"]),
        ],
    ),
    ModuleDef(
        order=8,
        title="Fisiologia e Reprodução",
        slug="fisiologia-reproducao",
        master_file="08_FISIOLOGIA_REPRODUCAO_MASTER.md",
        subject_slug="fisiologia-reproducao",
        category="specific",
        study_phase="1",
        estimated_hours=10.0,
        icon="🔬",
        description="⚠️ LACUNA — Eixo HHG, ciclo estral comparativo (tabela mais cobrada), gestação e biotecnologias reprodutivas.",
        chapters=[
            ChapterDef(1, "Eixo Hipotálamo-Hipófise-Gônadas e Hormônios", "§1 (HHG), §2 (hormônios)", 35, ["eixo-hhg", "lh", "fsh", "progesterona", "estrogeno", "gnrh"]),
            ChapterDef(2, "Gametogênese, Fecundação e Implantação", "§3 (gametogenese), §4 (fecundacao)", 25, ["gametogenese", "espermatogenese", "ovogenese", "fecundacao", "implantacao"]),
            ChapterDef(3, "Ciclo Estral Comparativo — a tabela mais cobrada", "§5 (ciclo-estral), §6 (ovulacao-ciclicidade)", 40, ["ciclo-estral", "proestro", "estro", "diestro", "anestro", "ovulacao-espontanea", "ovulacao-induzida"]),
            ChapterDef(4, "Gestação e Parto", "§7 (gestacao), §8 (parto)", 35, ["gestacao", "duracao-gestacao", "parto", "parturicao", "estagio-parto"]),
            ChapterDef(5, "Puerpério, Lactação e Biotecnologias", "§9 (puerperio), §10 (lactacao), §11 (biotecnologias)", 25, ["puerperio", "lactacao", "inseminacao-artificial", "transferencia-embriao"]),
            ChapterDef(6, "Revisão, Pegadinhas e Quadros de Memorização", "§12, §13, §14", 20, ["reproducao", "flashcards", "revisao"]),
        ],
    ),
    ModuleDef(
        order=9,
        title="Lei Orgânica de Ponta Grossa",
        slug="lei-organica-ponta-grossa",
        master_file="09_LEI_ORGANICA_PONTA_GROSSA_MASTER.md",
        subject_slug="lei-organica-ponta-grossa",
        category="specific",
        study_phase="1",
        estimated_hours=8.0,
        icon="⚖️",
        description="📌 Micro-doses desde a S1. Competências municipais, Câmara, Prefeito, servidores e orçamento.",
        chapters=[
            ChapterDef(1, "Disposições Preliminares e Competências do Município", "§1, §2 (a–c)", 35, ["municipio-ponta-grossa", "competencias-municipais", "lei-organica", "competencias-proprias", "competencias-comuns"]),
            ChapterDef(2, "Organização dos Poderes e Câmara Municipal", "§3, §4", 35, ["poder-legislativo", "camara-municipal", "vereadores", "comissoes"]),
            ChapterDef(3, "Processo Legislativo e Poder Executivo", "§5, §6", 35, ["processo-legislativo", "prefeito", "vice-prefeito", "veto", "sancao"]),
            ChapterDef(4, "Administração Pública e Servidores", "§7, §8", 30, ["administracao-publica", "servidores-publicos", "direitos-servidores", "deveres"]),
            ChapterDef(5, "Orçamento, Fiscalização e Controle", "§9, §10", 30, ["orcamento", "fiscalizacao", "tribunal-contas", "controle-interno"]),
            ChapterDef(6, "Saúde, Meio Ambiente e Tabelas de Competências", "§11, §12, §13–§20", 30, ["saude-publica", "meio-ambiente", "tabelas-competencias", "pegadinhas-lei-organica"]),
        ],
    ),
    ModuleDef(
        order=10,
        title="Revisão Final de Véspera",
        slug="revisao-final-vespera",
        master_file="10_REVISAO_FINAL_VESPERA_MASTER.md",
        subject_slug=None,
        category="specific",
        study_phase="4",
        estimated_hours=4.0,
        icon="⚡",
        description="🔒 Reservado para Fase 4 (última semana). Condensado de todos os temas para a véspera da prova.",
        chapters=[
            ChapterDef(1, "Saúde Única e Zoonoses (véspera)", "Bloco 1", 25, ["saude-unica", "zoonoses", "revisao-final"]),
            ChapterDef(2, "Segurança Alimentar (véspera)", "Bloco 2", 20, ["seguranca-alimentar", "revisao-final"]),
            ChapterDef(3, "Bem-Estar Animal (véspera)", "Bloco 3", 15, ["bem-estar-animal", "revisao-final"]),
            ChapterDef(4, "Medicina Veterinária do Coletivo (véspera)", "Bloco 4", 15, ["medicina-coletiva", "revisao-final"]),
            ChapterDef(5, "Fauna e Meio Ambiente (véspera)", "Bloco 5", 20, ["fauna", "lei-9605", "revisao-final"]),
            ChapterDef(6, "Cirurgia e Anestesia (véspera)", "Bloco 6", 25, ["cirurgia", "anestesia", "revisao-final"]),
            ChapterDef(7, "Fisiologia e Reprodução (véspera)", "Bloco 7", 20, ["fisiologia", "reproducao", "revisao-final"]),
            ChapterDef(8, "Lei Orgânica de Ponta Grossa (véspera)", "Bloco 8", 15, ["lei-organica", "revisao-final"]),
            ChapterDef(9, "100 Fatos Essenciais — O que não posso errar", "Bloco 9", 25, ["revisao-final", "fatos-essenciais"]),
        ],
    ),
    ModuleDef(
        order=11,
        title="Língua Portuguesa",
        slug="lingua-portuguesa",
        master_file="11_PORTUGUES_CONCURSO_MASTER.md",
        subject_slug="portugues",
        category="basic",
        study_phase="1",
        estimated_hours=10.0,
        icon="📝",
        description="Interpretação de texto, gramática, concordância, crase, pontuação e sintaxe.",
        chapters=[
            ChapterDef(1, "Interpretação de Texto e Ideia Principal", "§1, §2", 35, ["interpretacao-texto", "leitura", "ideia-principal"]),
            ChapterDef(2, "Inferência e Coesão", "§3, §4", 30, ["inferencia", "coesao", "conectivos", "referencia"]),
            ChapterDef(3, "Coerência e Morfologia", "§5, §6", 25, ["coerencia", "morfologia", "substantivo", "adjetivo", "verbo"]),
            ChapterDef(4, "Classes Gramaticais e Concordância Verbal", "§7, §8", 35, ["classes-gramaticais", "concordancia-verbal", "sujeito-verbo"]),
            ChapterDef(5, "Concordância Nominal e Regência Verbal", "§9, §10", 30, ["concordancia-nominal", "regencia-verbal"]),
            ChapterDef(6, "Regência Nominal e Crase", "§11, §12", 35, ["regencia-nominal", "crase"]),
            ChapterDef(7, "Pontuação e Acentuação Gráfica", "§13, §14", 25, ["pontuacao", "acentuacao", "virgula"]),
            ChapterDef(8, "Sintaxe — Sujeito, Predicado e Frase", "§15, §16, §17", 30, ["sintaxe", "sujeito", "predicado", "frase-oracao-periodo"]),
            ChapterDef(9, "Período Composto, Revisão e Pegadinhas", "§18, §19, §20, §21", 25, ["periodo-composto", "subordinacao", "coordenacao", "revisao"]),
        ],
    ),
    ModuleDef(
        order=12,
        title="Informática",
        slug="informatica",
        master_file="12_INFORMATICA_CONCURSO_MASTER.md",
        subject_slug="informatica",
        category="basic",
        study_phase="1",
        estimated_hours=6.0,
        icon="💻",
        description="Windows, internet, e-mail, Word, Excel, PowerPoint e segurança da informação.",
        chapters=[
            ChapterDef(1, "Windows — Desktop, Arquivos e Atalhos", "Módulo 1", 30, ["windows", "atalhos-teclado", "explorador-arquivos", "desktop"]),
            ChapterDef(2, "Internet, Navegadores e E-mail", "Módulos 2, 3", 30, ["internet", "navegadores", "email", "http", "https", "cookies"]),
            ChapterDef(3, "Word e PowerPoint", "Módulos 4, 6", 25, ["word", "powerpoint", "atalhos-word", "formatacao"]),
            ChapterDef(4, "Excel — Funções, Referências e Fórmulas", "Módulo 5", 35, ["excel", "funcoes-excel", "referencias-relativas", "referencias-absolutas", "soma", "media"]),
            ChapterDef(5, "Segurança da Informação e Certificação Digital", "Módulos 7, 8", 30, ["seguranca-informacao", "malware", "backup", "certificacao-digital", "cid"]),
        ],
    ),
    ModuleDef(
        order=13,
        title="Matemática",
        slug="matematica",
        master_file="13_MATEMATICA_ESSENCIAL_REVISAO.md",
        subject_slug="matematica",
        category="basic",
        study_phase="1",
        estimated_hours=8.0,
        icon="🔢",
        description="Foco cirúrgico no núcleo de alta frequência: porcentagem, regra de três, médias e raciocínio lógico.",
        chapters=[
            ChapterDef(1, "Razão, Proporção e Regra de Três", "§1, §2, §3, §4", 40, ["razao", "proporcao", "regra-de-tres", "regra-de-tres-composta"]),
            ChapterDef(2, "Porcentagem e Médias", "§5, §6, §7", 35, ["porcentagem", "media-aritmetica", "media-ponderada"]),
            ChapterDef(3, "Raciocínio Lógico e Sistema de Medidas", "§8, §9", 30, ["raciocinio-logico", "sistema-medidas", "conversao-unidades"]),
            ChapterDef(4, "Problemas Clássicos e Tópicos Complementares", "§10, §11, §12, §13, §14, §15, §16, §17", 30, ["problemas-matematicos", "geometria", "probabilidade", "equacoes"]),
        ],
    ),
    ModuleDef(
        order=14,
        title="Conhecimentos Gerais",
        slug="conhecimentos-gerais",
        master_file="14_CONHECIMENTOS_GERAIS_REVISAO.md",
        subject_slug="conhecimentos-gerais",
        category="basic",
        study_phase="1",
        estimated_hours=6.0,
        icon="🌍",
        description="Ponta Grossa, Paraná, Brasil e atualidades recentes.",
        chapters=[
            ChapterDef(1, "Ponta Grossa — Identidade, História e Economia", "Módulo 1 (completo)", 35, ["ponta-grossa", "historia-ponta-grossa", "economia-ponta-grossa", "geografia-ponta-grossa"]),
            ChapterDef(2, "Paraná — Dados, História e Geografia", "Módulo 2 (completo)", 25, ["parana", "estado-parana", "economia-parana"]),
            ChapterDef(3, "Brasil — Estrutura Política e Dados Gerais", "Módulo 3 (completo)", 25, ["brasil", "tres-poderes", "estrutura-politica", "simbolos-nacionais"]),
            ChapterDef(4, "Atualidades — Política, Economia e Saúde", "Módulo 4 (partes 1–3)", 30, ["atualidades", "politica", "economia", "saude"]),
            ChapterDef(5, "Atualidades — Tecnologia, Meio Ambiente e Educação", "Módulo 4 (partes 4–6)", 25, ["atualidades", "tecnologia", "meio-ambiente", "educacao"]),
        ],
    ),
]


class Command(BaseCommand):
    help = "Popula StudyModule e StudyChapter a partir do mapeamento explícito (STUDY_PLAN_MAP)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simula sem gravar no banco.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        if dry_run:
            self.stdout.write(self.style.WARNING("Modo --dry-run: nenhum dado será gravado.\n"))

        expected_modules = len(STUDY_PLAN_MAP)
        expected_chapters = sum(len(m.chapters) for m in STUDY_PLAN_MAP)
        if (
            StudyModule.objects.count() >= expected_modules
            and StudyChapter.objects.count() >= expected_chapters
        ):
            self.stdout.write("Plano de estudos já populado — pulando.")
            return

        created_modules = 0
        updated_modules = 0
        created_chapters = 0
        updated_chapters = 0

        with transaction.atomic():
            for mod_def in STUDY_PLAN_MAP:
                subject = None
                if mod_def.subject_slug:
                    try:
                        subject = Subject.objects.get(slug=mod_def.subject_slug)
                    except Subject.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"  Subject '{mod_def.subject_slug}' não encontrado — módulo criado sem subject."
                            )
                        )

                module_data = {
                    "title": mod_def.title,
                    "master_file": mod_def.master_file,
                    "subject": subject,
                    "category": mod_def.category,
                    "study_phase": mod_def.study_phase,
                    "estimated_hours": mod_def.estimated_hours,
                    "icon": mod_def.icon,
                    "description": mod_def.description,
                    "is_active": True,
                }

                if not dry_run:
                    module, created = StudyModule.objects.update_or_create(
                        slug=mod_def.slug,
                        defaults={**module_data, "order": mod_def.order},
                    )
                    if created:
                        created_modules += 1
                    else:
                        updated_modules += 1
                else:
                    self.stdout.write(f"  [DRY] Módulo: {mod_def.title}")
                    continue

                for ch_def in mod_def.chapters:
                    from django.utils.text import slugify as dj_slugify
                    chapter_slug = dj_slugify(ch_def.title)

                    chapter_data = {
                        "title": ch_def.title,
                        "estimated_minutes": ch_def.estimated_minutes,
                        "tags": ch_def.tags,
                        "sections_source": ch_def.sections_source,
                        "is_active": True,
                    }

                    chapter, ch_created = StudyChapter.objects.update_or_create(
                        module=module,
                        order=ch_def.order,
                        defaults={**chapter_data, "slug": chapter_slug},
                    )
                    if ch_created:
                        created_chapters += 1
                    else:
                        updated_chapters += 1

                    # Subject do módulo como related_subject padrão
                    if subject:
                        chapter.related_subjects.add(subject)

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nImportação concluída:\n"
                f"  Módulos criados: {created_modules}\n"
                f"  Módulos atualizados: {updated_modules}\n"
                f"  Capítulos criados: {created_chapters}\n"
                f"  Capítulos atualizados: {updated_chapters}\n"
            )
        )
