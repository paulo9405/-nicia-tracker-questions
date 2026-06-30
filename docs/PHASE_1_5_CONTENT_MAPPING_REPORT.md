# Relatório de Mapeamento de Conteúdo — Fase 1.5

> Gerado em: 30/06/2026  
> Fonte da verdade: `docs/STUDY_CONTENT_MAPPING.md`  
> Estratégia: extração de seções delimitadas por cabeçalhos dos arquivos MASTER

---

## Resumo geral

| Métrica | Valor |
|---|---|
| Módulos | 14 |
| Capítulos | 98 |
| Capítulos com conteúdo | 98 (100%) |
| Capítulos vazios | 0 |
| Total de caracteres | 361.080 |
| Média por capítulo | 3.684 chars |
| Menor capítulo | 1.233 chars |
| Maior capítulo | 11.599 chars |

---

## Estratégias de extração por tipo de arquivo

| Tipo | Formato do cabeçalho | Módulos |
|---|---|---|
| **numbered** | `## N. TÍTULO` (N = inteiro) | 1-9, 11, 13 |
| **bloco** | `# BLOCO N — TÍTULO` | 10 |
| **modulo** | `# MÓDULO N — TÍTULO` | 12, 14 |
| **modulo_head** | módulo N até subsection X | 14 (capítulo 4) |
| **modulo_tail** | subsection X até fim do módulo | 14 (capítulo 5) |

---

## Módulo 1 — Saúde Única
**Arquivo:** `01_SAUDE_UNICA_MASTER.md` | **Tipo:** `numbered`

| Cap | Título | Seções extraídas | Chars |
|---|---|---|---|
| 1 | Conceitos Fundamentais de Saúde Pública | §1, §2 | 3.550 |
| 2 | One Health — Conceito, Histórico e Princípios | §3 | 5.366 |
| 3 | Relação Saúde Humana, Animal e Ambiental | §4 | 2.484 |
| 4 | Zoonoses e Doenças Emergentes | §5 | 2.590 |
| 5 | Resistência Antimicrobiana e PAN-BR | §6 | 2.821 |
| 6 | Papel do Médico Veterinário na Saúde Única | §7 | 1.522 |
| 7 | Legislação, Tópicos Cobrados e Flashcards | §8, §9, §10, §11 | 7.149 |

> §1 = intro "Visão Geral" incluído no capítulo 1 (não descartado).

---

## Módulo 2 — Zoonoses e Vigilância
**Arquivo:** `02_ZOONOSES_VIGILANCIA_MASTER.md` | **Tipo:** `numbered`

| Cap | Título | Seções extraídas | Chars |
|---|---|---|---|
| 1 | Vigilância Epidemiológica e Notificação Compulsória | §2, §3 | 4.421 |
| 2 | Centros de Controle de Zoonoses (CCZ/UVZ) | §4 | 1.421 |
| 3 | Raiva — Epidemiologia e Profilaxia | §5 | 3.083 |
| 4 | Leishmaniose — Tegumentar e Visceral | §6 | 2.048 |
| 5 | Leptospirose | §7 | 1.233 |
| 6 | Toxoplasmose | §8 | 1.431 |
| 7 | Brucelose e Tuberculose | §9, §10 | 2.710 |
| 8 | Hantavirose e Febre Maculosa | §11, §12 | 2.470 |
| 9 | Animais Peçonhentos e Outras Zoonoses | §13, §14 | 3.595 |
| 10 | Legislação, Tópicos Cobrados e Flashcards | §15, §16, §17, §18 | 7.218 |

> §1 (Visão Geral/Intro do módulo) não mapeado — intencional conforme STUDY_CONTENT_MAPPING.

---

## Módulo 3 — Segurança Alimentar
**Arquivo:** `03_SEGURANCA_ALIMENTAR_MASTER.md` | **Tipo:** `numbered`

| Cap | Título | Seções extraídas | Chars |
|---|---|---|---|
| 1 | BPF — Fundamentos e Multiplicação Microbiana | §2 | 2.591 |
| 2 | RDC 216/2004 — Serviços de Alimentação | §3 | 2.811 |
| 3 | RDC 275/2002 — POPs e Lista de Verificação | §4, §5 | 4.544 |
| 4 | APPCC — Análise de Perigos e PCCs | §6 | 1.788 |
| 5 | Padrões Microbiológicos — Conceitos e RDC 724/2022 | §7, §8 | 5.385 |
| 6 | IN 161/2022 e IN 313/2024 | §9 | 6.069 |
| 7 | Interpretação de Resultados Microbiológicos | §10 | 2.929 |
| 8 | Resíduos de Serviços de Saúde e RDC 222/2018 | §11, §12 | 8.380 |
| 9 | Fiscalização, Legislação e Flashcards | §13, §14, §15, §16, §17 | 10.738 |

> §1 (intro) não mapeado — intencional.

---

## Módulo 4 — Bem-Estar Animal
**Arquivo:** `04_BEM_ESTAR_ANIMAL_MASTER.md` | **Tipo:** `numbered`

| Cap | Título | Seções extraídas | Chars |
|---|---|---|---|
| 1 | Conceitos de BEA, Senciência e Cinco Liberdades | §1, §2, §3, §4 | 6.917 |
| 2 | Indicadores de BEA e Welfare Quality | §5 | 2.431 |
| 3 | Dor, Estresse e Cortisol | §6, §7 | 3.633 |
| 4 | Enriquecimento Ambiental e Transporte Animal | §8, §9 | 4.510 |
| 5 | Abate Humanitário | §10 | 2.069 |
| 6 | Maus-Tratos — Art. 32 da Lei 9.605/98 | §11 | 4.115 |
| 7 | Lei Sansão, Legislação e Flashcards | §12, §13, §14, §15, §16 | 10.930 |

---

## Módulo 5 — Medicina Veterinária do Coletivo
**Arquivo:** `05_MED_VET_COLETIVO_MASTER.md` | **Tipo:** `numbered`

| Cap | Título | Seções extraídas | Chars |
|---|---|---|---|
| 1 | Medicina Veterinária do Coletivo e Guarda Responsável | §2, §3 | 3.040 |
| 2 | Controle Populacional e Manejo Ético | §4, §5 | 5.870 |
| 3 | Castração e Programas de Esterilização | §6, §7 | 4.728 |
| 4 | Abrigos, Adoção e Eutanásia | §8, §9 | 2.843 |
| 5 | CCZs, Políticas Públicas e Legislação | §10, §11, §12, §13, §14, §15 | 11.599 |

> §1 (intro) não mapeado — intencional.

---

## Módulo 6 — Fauna e Legislação Ambiental
**Arquivo:** `06_FAUNA_AMBIENTAL_MASTER.md` | **Tipo:** `numbered`

| Cap | Título | Seções extraídas | Chars |
|---|---|---|---|
| 1 | Conceitos de Fauna Silvestre e Proteção Legal | §2, §3 | 4.519 |
| 2 | CETAS — Funcionamento e Triagem | §4 | 1.927 |
| 3 | Destinação e Soltura de Animais Silvestres | §5, §6 | 3.149 |
| 4 | SISBio, CONCEA e CEUA | §7, §8 | 2.781 |
| 5 | Criadouros, Pesquisa e Anestesia em Campo | §9, §10 | 3.857 |
| 6 | Lei 9.605/98 — Crimes Ambientais e Contra a Fauna | §11, §12, §13 | 4.741 |
| 7 | Legislação, Tópicos Cobrados e Flashcards | §14, §15, §16, §17 | 8.976 |

> §1 (intro) não mapeado — intencional.

---

## Módulo 7 — Cirurgia, Anestesia e Contenção
**Arquivo:** `07_CIRURGIA_ANESTESIA_CONTENCAO_MASTER.md` | **Tipo:** `numbered`

> Arquivo tem 33 seções. Seções §31-§33 (Fechamento) não mapeadas para nenhum capítulo.

| Cap | Título | Seções extraídas | Chars |
|---|---|---|---|
| 1 | Conceitos e Avaliação Pré-Anestésica | §1, §2, §3, §4 | 4.099 |
| 2 | MPA — Fenotiazínicos e Benzodiazepínicos | §5, §6, §7 | 2.283 |
| 3 | Alfa-2 Agonistas e Opioides | §8, §9 | 2.303 |
| 4 | Propofol, Cetamina e Anestesia Inalatória | §10, §11, §12 | 2.897 |
| 5 | Anestesia Local, Analgesia e Monitorização | §13, §14, §15, §16, §17 | 4.823 |
| 6 | Princípios Cirúrgicos, Assepsia e Instrumental | §18, §19, §20 | 3.026 |
| 7 | Orquiectomia em Cães e Gatos | §21, §22 | 1.478 |
| 8 | OSH, Complicações e Pós-Operatório | §23, §24, §25 | 3.037 |
| 9 | Contenção Química de Fauna Silvestre | §26, §27, §28, §29, §30 | 4.867 |

---

## Módulo 8 — Fisiologia e Reprodução
**Arquivo:** `08_FISIOLOGIA_REPRODUCAO_MASTER.md` | **Tipo:** `numbered`

| Cap | Título | Seções extraídas | Chars |
|---|---|---|---|
| 1 | Eixo Hipotálamo-Hipófise-Gônadas e Hormônios | §1, §2 | 3.086 |
| 2 | Gametogênese, Fecundação e Implantação | §3, §4 | 2.241 |
| 3 | Ciclo Estral Comparativo (a tabela mais cobrada) | §5, §6 | 2.775 |
| 4 | Gestação e Parto | §7, §8 | 2.757 |
| 5 | Puerpério, Lactação e Biotecnologias | §9, §10, §11 | 3.159 |
| 6 | Revisão, Pegadinhas e Quadros de Memorização | §12, §13, §14 | 2.406 |

---

## Módulo 9 — Lei Orgânica de Ponta Grossa
**Arquivo:** `09_LEI_ORGANICA_PONTA_GROSSA_MASTER.md` | **Tipo:** `numbered`

| Cap | Título | Seções extraídas | Chars |
|---|---|---|---|
| 1 | Disposições Preliminares e Competências do Município | §1, §2 | 3.979 |
| 2 | Organização dos Poderes e Câmara Municipal | §3, §4 | 3.070 |
| 3 | Processo Legislativo e Poder Executivo | §5, §6 | 3.473 |
| 4 | Administração Pública e Servidores | §7, §8 | 3.037 |
| 5 | Orçamento, Fiscalização e Controle | §9, §10 | 2.549 |
| 6 | Saúde, Meio Ambiente e Tabelas de Competências | §11-§20 | 9.407 |

---

## Módulo 10 — Revisão Final de Véspera
**Arquivo:** `10_REVISAO_FINAL_VESPERA_MASTER.md` | **Tipo:** `bloco` (`# BLOCO N —`)

| Cap | Título | Bloco extraído | Chars |
|---|---|---|---|
| 1 | Saúde Única e Zoonoses (véspera) | Bloco 1 | 2.719 |
| 2 | Segurança Alimentar (véspera) | Bloco 2 | 2.238 |
| 3 | Bem-Estar Animal (véspera) | Bloco 3 | 1.420 |
| 4 | Medicina Veterinária do Coletivo (véspera) | Bloco 4 | 1.333 |
| 5 | Fauna e Meio Ambiente (véspera) | Bloco 5 | 1.698 |
| 6 | Cirurgia e Anestesia (véspera) | Bloco 6 | 2.314 |
| 7 | Fisiologia e Reprodução (véspera) | Bloco 7 | 1.708 |
| 8 | Lei Orgânica de Ponta Grossa (véspera) | Bloco 8 | 1.271 |
| 9 | 100 Fatos Essenciais — O que não posso errar | Bloco 9 | 7.361 |

---

## Módulo 11 — Língua Portuguesa
**Arquivo:** `11_PORTUGUES_CONCURSO_MASTER.md` | **Tipo:** `numbered`

| Cap | Título | Seções extraídas | Chars |
|---|---|---|---|
| 1 | Interpretação de Texto e Ideia Principal | §1, §2 | 2.695 |
| 2 | Inferência e Coesão | §3, §4 | 2.761 |
| 3 | Coerência e Morfologia | §5, §6 | 2.488 |
| 4 | Classes Gramaticais e Concordância Verbal | §7, §8 | 3.802 |
| 5 | Concordância Nominal e Regência Verbal | §9, §10 | 3.172 |
| 6 | Regência Nominal e Crase | §11, §12 | 3.206 |
| 7 | Pontuação e Acentuação Gráfica | §13, §14 | 3.559 |
| 8 | Sintaxe — Sujeito, Predicado e Frase | §15, §16, §17 | 3.247 |
| 9 | Período Composto, Revisão e Pegadinhas | §18, §19, §20, §21 | 5.483 |

> §21 é a última seção; inclui a tabela "TOP PEGADINHAS" e o rodapé do arquivo.

---

## Módulo 12 — Informática
**Arquivo:** `12_INFORMATICA_CONCURSO_MASTER.md` | **Tipo:** `modulo` (`# MÓDULO N —`)

| Cap | Título | Módulos extraídos | Chars |
|---|---|---|---|
| 1 | Windows — Desktop, Arquivos e Atalhos | Módulo 1 | 3.148 |
| 2 | Internet, Navegadores e E-mail | Módulos 2, 3 | 4.898 |
| 3 | Word e PowerPoint | Módulos 4, 6 | 2.919 |
| 4 | Excel — Funções, Referências e Fórmulas | Módulo 5 | 2.913 |
| 5 | Segurança da Informação e Certificação Digital | Módulos 7, 8 | 7.686 |

> Módulo 8 é o último do arquivo; inclui "Revisão Relâmpago" e "Top Pegadinhas" da informática.  
> Capítulo 3 usa Módulos 4 e 6 (Word e PowerPoint), ignorando Módulo 5 (Excel, tratado no cap 4).

---

## Módulo 13 — Matemática
**Arquivo:** `13_MATEMATICA_ESSENCIAL_REVISAO.md` | **Tipo:** `numbered`

| Cap | Título | Seções extraídas | Chars |
|---|---|---|---|
| 1 | Razão, Proporção e Regra de Três | §1, §2, §3, §4 | 3.419 |
| 2 | Porcentagem e Médias | §5, §6, §7 | 1.803 |
| 3 | Raciocínio Lógico e Sistema de Medidas | §8, §9 | 1.839 |
| 4 | Problemas Clássicos e Tópicos Complementares | §10-§17 | 3.999 |

> §17 é a última seção; inclui a "Revisão Relâmpago" e "Top Erros" ao final do arquivo.

---

## Módulo 14 — Conhecimentos Gerais
**Arquivo:** `14_CONHECIMENTOS_GERAIS_REVISAO.md` | **Tipo:** `modulo` (`# MÓDULO N —`)

| Cap | Título | Extração | Chars |
|---|---|---|---|
| 1 | Ponta Grossa — Identidade, História e Economia | Módulo 1 completo | 2.826 |
| 2 | Paraná — Dados, História e Geografia | Módulo 2 completo | 1.935 |
| 3 | Brasil — Estrutura Política e Dados Gerais | Módulo 3 completo | 1.723 |
| 4 | Atualidades — Política, Economia e Saúde | Módulo 4 até `## Tecnologia` | 1.739 |
| 5 | Atualidades — Tecnologia, Meio Ambiente e Educação | Módulo 4 a partir de `## Tecnologia` | 4.024 |

> Capítulos 4 e 5 dividem o Módulo 4 no subsection `## Tecnologia`.  
> Capítulo 5 inclui a "Revisão Relâmpago" e "Top Pegadinhas" de Conhecimentos Gerais.

---

## Notas sobre seções não mapeadas

Alguns arquivos possuem seções introdutórias (§1 de visão geral/índice) não atribuídas a nenhum capítulo. Esta é uma decisão intencional do `STUDY_CONTENT_MAPPING.md`:

| Arquivo | §1 não mapeado | Justificativa |
|---|---|---|
| 02_ZOONOSES | §1 | Seção de visão geral — conteúdo absorvido no capítulo 1 via §2/§3 |
| 03_SEGURANCA_ALIMENTAR | §1 | Idem |
| 05_MED_VET_COLETIVO | §1 | Idem |
| 06_FAUNA_AMBIENTAL | §1 | Idem |
| 07_CIRURGIA | §31-§33 | Fechamento/Integração — não mapeados explicitamente |

Nenhum conteúdo foi inventado, resumido ou reescrito. Todo o texto nos capítulos é extraído diretamente dos arquivos MASTER correspondentes.
