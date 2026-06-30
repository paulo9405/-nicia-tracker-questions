# STUDY_CONTENT_MAPPING.md
# Mapeamento Manual de Conteúdo — Plano de Estudos Nícia Track

> **Fonte da verdade para o `import_study_plan.py`.**
> Cada entrada define um módulo e seus capítulos. O parser NÃO infere automaticamente capítulos a partir de cabeçalhos markdown. Toda alteração de estrutura é feita aqui, não no código.
>
> **Formato:** `subject_slug` deve corresponder exatamente ao slug existente na tabela `questions_subject`.
> **Seções de origem:** referência aos cabeçalhos `##` do arquivo MASTER correspondente.

---

## MÓDULO 1 — Saúde Única

```
master_file: 01_SAUDE_UNICA_MASTER.md
subject_slug: saude-unica
category: specific
study_phase: "1"
order: 1
estimated_hours: 8.0
icon: 🌿
```

### Capítulos

| order | title | sections_source | estimated_minutes | tags |
|---|---|---|---|---|
| 1 | Conceitos Fundamentais de Saúde Pública | §1, §2 (2.1–2.3) | 25 | saude-publica, saude-coletiva, glossario |
| 2 | One Health — Conceito, Histórico e Princípios | §3 (3.1–3.5) | 40 | one-health, ohhlep, manhattan, saude-unica |
| 3 | Relação Saúde Humana, Animal e Ambiental | §4 (4.1–4.4) | 25 | saude-ambiental, cisticercose, mudancas-climaticas |
| 4 | Zoonoses e Doenças Emergentes | §5 (5.1–5.5) | 20 | zoonoses, doencas-emergentes, guia-tripartite |
| 5 | Resistência Antimicrobiana e PAN-BR | §6 (6.1–6.4) | 35 | resistencia-antimicrobiana, pan-br, amr, objetivos-estrategicos |
| 6 | Papel do Médico Veterinário na Saúde Única | §7 (7.1–7.3) | 20 | medico-veterinario, saude-unica, alimentos-seguros |
| 7 | Legislação, Tópicos Cobrados e Flashcards | §8, §9, §10, §11 | 20 | legislacao, saude-unica, revisao |

---

## MÓDULO 2 — Zoonoses e Vigilância

```
master_file: 02_ZOONOSES_VIGILANCIA_MASTER.md
subject_slug: zoonoses-vigilancia
category: specific
study_phase: "1"
order: 2
estimated_hours: 12.0
icon: 🦟
```

### Capítulos

| order | title | sections_source | estimated_minutes | tags |
|---|---|---|---|---|
| 1 | Vigilância Epidemiológica e Notificação Compulsória | §2 (2.1–2.4), §3 (3.1–3.6) | 40 | vigilancia-epidemiologica, notificacao-compulsoria, sinan, portaria-mpa-19 |
| 2 | Centros de Controle de Zoonoses (CCZ/UVZ) | §4 (4.1–4.2) | 20 | ccz, uvz, controle-zoonoses, vetores |
| 3 | Raiva — Epidemiologia e Profilaxia | §5 (5.1–5.4) | 40 | raiva, profilaxia-raiva, ciclos-raiva, pos-exposicao |
| 4 | Leishmaniose — Tegumentar e Visceral | §6 (6.1–6.2) | 30 | leishmaniose, leishmaniose-tegumentar, leishmaniose-visceral, calazar |
| 5 | Leptospirose | §7 | 25 | leptospirose |
| 6 | Toxoplasmose | §8 | 20 | toxoplasmose |
| 7 | Brucelose e Tuberculose | §9, §10 | 30 | brucelose, tuberculose |
| 8 | Hantavirose e Febre Maculosa | §11, §12 | 25 | hantavirose, febre-maculosa |
| 9 | Animais Peçonhentos e Outras Zoonoses | §13, §14 (14.1–14.7) | 30 | animais-peconhentos, teniase-cisticercose, febre-amarela, influenza-aviaria, larva-migrans |
| 10 | Legislação, Tópicos Cobrados e Flashcards | §15, §16, §17, §18 | 20 | legislacao, zoonoses, revisao |

---

## MÓDULO 3 — Segurança Alimentar

```
master_file: 03_SEGURANCA_ALIMENTAR_MASTER.md
subject_slug: seguranca-alimentar
category: specific
study_phase: "1"
order: 3
estimated_hours: 10.0
icon: 🍽️
```

### Capítulos

| order | title | sections_source | estimated_minutes | tags |
|---|---|---|---|---|
| 1 | BPF — Fundamentos e Multiplicação Microbiana | §2 (2.1–2.3) | 30 | boas-praticas, bpf, multiplicacao-microbiana, contaminacao-cruzada |
| 2 | RDC 216/2004 — Serviços de Alimentação | §3 (3.1–3.4) | 35 | rdc-216, temperatura, higienizacao, manipuladores |
| 3 | RDC 275/2002 — POPs e Lista de Verificação | §4 (4.1–4.4), §5 (5.1–5.4) | 35 | rdc-275, pop, lista-verificacao, procedimentos-operacionais |
| 4 | APPCC — Análise de Perigos e PCCs | §6 (6.1–6.3) | 25 | appcc, haccp, ponto-critico, sete-principios |
| 5 | Padrões Microbiológicos — Conceitos e RDC 724/2022 | §7 (7.1–7.4), §8 (8.1–8.3) | 35 | padroes-microbiologicos, rdc-724, microrganismos |
| 6 | IN 161/2022 e IN 313/2024 | §9 (9.1–9.8) | 30 | in-161, in-313, listeria, criterios-microbiologicos |
| 7 | Interpretação de Resultados Microbiológicos | §10 (10.1–10.5) | 30 | plano-duas-classes, plano-tres-classes, amostra-representativa |
| 8 | Resíduos de Serviços de Saúde e RDC 222/2018 | §11 (11.1–11.6), §12 (12.1–12.4) | 35 | rss, rdc-222, pgrss, grupos-rss |
| 9 | Fiscalização, Legislação e Flashcards | §13, §14, §15, §16, §17 | 20 | fiscalizacao, legislacao, seguranca-alimentar, revisao |

---

## MÓDULO 4 — Bem-Estar Animal

```
master_file: 04_BEM_ESTAR_ANIMAL_MASTER.md
subject_slug: bem-estar-animal
category: specific
study_phase: "1"
order: 4
estimated_hours: 8.0
icon: 🐾
```

### Capítulos

| order | title | sections_source | estimated_minutes | tags |
|---|---|---|---|---|
| 1 | Conceitos de BEA, Senciência e Cinco Liberdades | §1 (1.1–1.2), §2, §3, §4 | 35 | bem-estar-animal, senciencia, cinco-liberdades, etologia |
| 2 | Indicadores de BEA e Welfare Quality | §5 (5.1–5.4) | 25 | indicadores-bea, welfare-quality, indicadores-comportamentais |
| 3 | Dor, Estresse e Cortisol | §6 (6.1–6.2), §7 (7.1–7.2) | 25 | dor, estresse, cortisol, cascata-fisiologica |
| 4 | Enriquecimento Ambiental e Transporte Animal | §8 (8.1–8.3), §9 (9.1–9.3) | 25 | enriquecimento-ambiental, transporte-animal, boas-praticas |
| 5 | Abate Humanitário | §10 (10.1–10.2) | 20 | abate-humanitario, insensibilizacao |
| 6 | Maus-Tratos — Art. 32 da Lei 9.605/98 | §11 (11.1–11.6) | 30 | maus-tratos, art-32, lei-9605, dolo-culpa |
| 7 | Lei Sansão, Legislação e Flashcards | §12, §13 (13.1), §14, §15, §16 | 25 | lei-sansao, tres-rs, legislacao, bem-estar-animal, revisao |

---

## MÓDULO 5 — Medicina Veterinária do Coletivo

```
master_file: 05_MED_VET_COLETIVO_MASTER.md
subject_slug: medicina-veterinaria-coletivo
category: specific
study_phase: "1"
order: 5
estimated_hours: 8.0
icon: 🏥
```

### Capítulos

| order | title | sections_source | estimated_minutes | tags |
|---|---|---|---|---|
| 1 | Medicina Veterinária do Coletivo e Guarda Responsável | §2 (2.1–2.2), §3 | 30 | medicina-coletiva, guarda-responsavel, nasf, mudanca-paradigma |
| 2 | Controle Populacional e Manejo Ético | §4 (4.1–4.6), §5 (5.1–5.3) | 35 | controle-populacional, manejo-etico, oms-informe, exterminio-ineficaz |
| 3 | Castração e Programas de Esterilização | §6 (6.1–6.3), §7 (7.1–7.5) | 30 | castracao, esterilizacao, res-cfmv-1596, castracao-quimica-vedada |
| 4 | Abrigos, Adoção e Eutanásia | §8 (8.1–8.3), §9 (9.1–9.2) | 25 | abrigo, adocao, eutanasia, cata |
| 5 | CCZs, Políticas Públicas e Legislação | §10 (10.1), §11 (11.1–11.3), §12, §13, §14, §15 | 25 | ccz, politica-publica, legislacao, revisao |

---

## MÓDULO 6 — Fauna e Legislação Ambiental

```
master_file: 06_FAUNA_AMBIENTAL_MASTER.md
subject_slug: fauna-legislacao-ambiental
category: specific
study_phase: "1"
order: 6
estimated_hours: 8.0
icon: 🦜
```

### Capítulos

| order | title | sections_source | estimated_minutes | tags |
|---|---|---|---|---|
| 1 | Conceitos de Fauna Silvestre e Proteção Legal | §2, §3 (3.1–3.4) | 30 | fauna-silvestre, protecao-fauna, manejo, contencao-fisica |
| 2 | CETAS — Funcionamento e Triagem | §4 (4.1–4.2) | 25 | cetas, triagem, fauna-silvestre, recebimento |
| 3 | Destinação e Soltura de Animais Silvestres | §5 (5.1–5.2), §6 (6.1) | 25 | destinacao, soltura, reabilitacao, reintroducao |
| 4 | SISBio, CONCEA e CEUA | §7, §8 (8.1–8.2) | 20 | sisbio, concea, ceua, tres-rs |
| 5 | Criadouros, Pesquisa e Anestesia em Campo | §9 (9.1), §10 (10.1–10.2) | 20 | criadouros, pesquisa-animal, anestesia-campo |
| 6 | Lei 9.605/98 — Crimes Ambientais e Contra a Fauna | §11 (11.1–11.4), §12 (12.1–12.2), §13 | 35 | lei-9605, crimes-ambientais, crimes-fauna, art-29, art-32, art-37 |
| 7 | Legislação, Tópicos Cobrados e Flashcards | §14, §15, §16, §17 | 20 | legislacao, fauna, revisao |

---

## MÓDULO 7 — Cirurgia, Anestesia e Contenção

```
master_file: 07_CIRURGIA_ANESTESIA_CONTENCAO_MASTER.md
subject_slug: cirurgia-anestesia-contencao
category: specific
study_phase: "1"
order: 7
estimated_hours: 18.0
icon: 💉
```

> ⚠️ **LACUNA — prioridade máxima.** Este módulo está fora da zona de conforto da candidata.
> Leitura lenta, com pausa após cada capítulo para anotações.

### Capítulos

| order | title | sections_source | estimated_minutes | tags |
|---|---|---|---|---|
| 1 | Conceitos e Avaliação Pré-Anestésica | §1, §2, §3 (ASA), §4 (jejum) | 35 | anestesiologia, pre-anestesico, tripé-anestesico, asa, jejum |
| 2 | MPA — Fenotiazínicos e Benzodiazepínicos | §5, §6 (acepromazina), §7 (benzodiazepinicos) | 30 | mpa, acepromazina, diazepam, midazolam |
| 3 | Alfa-2 Agonistas e Opioides | §8 (xilazina, dexmedetomidina), §9 (opioides) | 35 | alfa2-agonistas, xilazina, dexmedetomidina, opioides, morfina |
| 4 | Propofol, Cetamina e Anestesia Inalatória | §10 (propofol), §11 (cetamina), §12 (inalatoria) | 35 | propofol, cetamina, isoflurano, anestesia-inalatoria |
| 5 | Anestesia Local, Analgesia e Monitorização | §13 (anestesia-local), §14 (analgesia-multimodal), §15 (monitorizacao), §16 (recuperacao), §17 (emergencias) | 40 | anestesia-local, analgesia-multimodal, monitorizacao, emergencias-anestesicas |
| 6 | Princípios Cirúrgicos, Assepsia e Instrumental | §18 (Halsted), §19 (assepsia), §20 (instrumental) | 30 | principios-halsted, assepsia, antissepsia, esterilizacao, instrumental-cirurgico, fios |
| 7 | Orquiectomia em Cães e Gatos | §21 (orquiectomia-caes), §22 (orquiectomia-gatos) | 30 | orquiectomia, castracao-caes, castracao-gatos |
| 8 | OSH, Complicações e Pós-Operatório | §23 (osh), §24 (complicacoes), §25 (pos-operatorio) | 30 | osh, ovariohisterectomia, complicacoes-cirurgicas, pos-operatorio |
| 9 | Contenção Química de Fauna Silvestre | §26 (captura), §27 (dardos), §28 (dissociativos), §29 (megafauna), §30 (riscos) | 35 | contencao-quimica, fauna-silvestre, miopatia-captura, dardos, tiletamina-zolazepam |

---

## MÓDULO 8 — Fisiologia e Reprodução

```
master_file: 08_FISIOLOGIA_REPRODUCAO_MASTER.md
subject_slug: fisiologia-reproducao
category: specific
study_phase: "1"
order: 8
estimated_hours: 10.0
icon: 🔬
```

> ⚠️ **LACUNA** — estudar com tabelas comparativas (ciclo estral, gestação).

### Capítulos

| order | title | sections_source | estimated_minutes | tags |
|---|---|---|---|---|
| 1 | Eixo Hipotálamo-Hipófise-Gônadas e Hormônios | §1 (HHG), §2 (hormônios) | 35 | eixo-hhg, lh, fsh, progesterona, estrogeno, gnrh |
| 2 | Gametogênese, Fecundação e Implantação | §3 (gametogenese), §4 (fecundacao) | 25 | gametogenese, espermatogenese, ovogenese, fecundacao, implantacao |
| 3 | Ciclo Estral Comparativo (a tabela mais cobrada) | §5 (ciclo-estral), §6 (ovulacao-ciclicidade) | 40 | ciclo-estral, proestro, estro, diestro, anestro, ovulacao-espontanea, ovulacao-induzida |
| 4 | Gestação e Parto | §7 (gestacao), §8 (parto) | 35 | gestacao, duracao-gestacao, parto, parturicao, estagio-parto |
| 5 | Puerpério, Lactação e Biotecnologias | §9 (puerperio), §10 (lactacao), §11 (biotecnologias) | 25 | puerperio, lactacao, inseminacao-artificial, transferencia-embriao |
| 6 | Revisão, Pegadinhas e Quadros de Memorização | §12, §13, §14 | 20 | reproducao, flashcards, revisao |

---

## MÓDULO 9 — Lei Orgânica de Ponta Grossa

```
master_file: 09_LEI_ORGANICA_PONTA_GROSSA_MASTER.md
subject_slug: lei-organica-ponta-grossa
category: specific
study_phase: "1"
order: 9
estimated_hours: 8.0
icon: ⚖️
```

> 📌 **Micro-doses desde a Semana 1** — não concentrar tudo na Fase 1. Ler em frações a partir de S1.

### Capítulos

| order | title | sections_source | estimated_minutes | tags |
|---|---|---|---|---|
| 1 | Disposições Preliminares e Competências do Município | §1, §2 (a–c) | 35 | municipio-ponta-grossa, competencias-municipais, lei-organica, competencias-proprias, competencias-comuns |
| 2 | Organização dos Poderes e Câmara Municipal | §3, §4 | 35 | poder-legislativo, camara-municipal, vereadores, comissoes |
| 3 | Processo Legislativo e Poder Executivo | §5, §6 | 35 | processo-legislativo, prefeito, vice-prefeito, veto, sancao |
| 4 | Administração Pública e Servidores | §7, §8 | 30 | administracao-publica, servidores-publicos, direitos-servidores, deveres |
| 5 | Orçamento, Fiscalização e Controle | §9, §10 | 30 | orcamento, fiscalizacao, tribunal-contas, controle-interno |
| 6 | Saúde, Meio Ambiente e Tabelas de Competências | §11, §12, §13–§20 | 30 | saude-publica, meio-ambiente, tabelas-competencias, pegadinhas-lei-organica |

---

## MÓDULO 10 — Revisão Final de Véspera

```
master_file: 10_REVISAO_FINAL_VESPERA_MASTER.md
subject_slug: (transversal — sem subject único)
category: specific
study_phase: "4"
order: 10
estimated_hours: 4.0
icon: ⚡
```

> 🔒 **Reservado para Fase 4 (última semana).** Não exibir como disponível antes da Semana 11.

### Capítulos

| order | title | sections_source | estimated_minutes | tags |
|---|---|---|---|---|
| 1 | Saúde Única e Zoonoses (véspera) | Bloco 1 | 25 | saude-unica, zoonoses, revisao-final |
| 2 | Segurança Alimentar (véspera) | Bloco 2 | 20 | seguranca-alimentar, revisao-final |
| 3 | Bem-Estar Animal (véspera) | Bloco 3 | 15 | bem-estar-animal, revisao-final |
| 4 | Medicina Veterinária do Coletivo (véspera) | Bloco 4 | 15 | medicina-coletiva, revisao-final |
| 5 | Fauna e Meio Ambiente (véspera) | Bloco 5 | 20 | fauna, lei-9605, revisao-final |
| 6 | Cirurgia e Anestesia (véspera) | Bloco 6 | 25 | cirurgia, anestesia, revisao-final |
| 7 | Fisiologia e Reprodução (véspera) | Bloco 7 | 20 | fisiologia, reproducao, revisao-final |
| 8 | Lei Orgânica de Ponta Grossa (véspera) | Bloco 8 | 15 | lei-organica, revisao-final |
| 9 | 100 Fatos Essenciais — O que não posso errar | Bloco 9 | 25 | revisao-final, fatos-essenciais |

---

## MÓDULO 11 — Língua Portuguesa

```
master_file: 11_PORTUGUES_CONCURSO_MASTER.md
subject_slug: portugues
category: basic
study_phase: "1"
order: 11
estimated_hours: 10.0
icon: 📝
```

### Capítulos

| order | title | sections_source | estimated_minutes | tags |
|---|---|---|---|---|
| 1 | Interpretação de Texto e Ideia Principal | §1, §2 | 35 | interpretacao-texto, leitura, ideia-principal |
| 2 | Inferência e Coesão | §3, §4 | 30 | inferencia, coesao, conectivos, referencia |
| 3 | Coerência e Morfologia | §5, §6 | 25 | coerencia, morfologia, substantivo, adjetivo, verbo |
| 4 | Classes Gramaticais e Concordância Verbal | §7, §8 | 35 | classes-gramaticais, concordancia-verbal, sujeito-verbo |
| 5 | Concordância Nominal e Regência Verbal | §9, §10 | 30 | concordancia-nominal, regencia-verbal |
| 6 | Regência Nominal e Crase | §11, §12 | 35 | regencia-nominal, crase |
| 7 | Pontuação e Acentuação Gráfica | §13, §14 | 25 | pontuacao, acentuacao, virgula |
| 8 | Sintaxe — Sujeito, Predicado e Frase | §15, §16, §17 | 30 | sintaxe, sujeito, predicado, frase-oracao-periodo |
| 9 | Período Composto, Revisão e Pegadinhas | §18, §19, §20, §21 | 25 | periodo-composto, subordinacao, coordenacao, revisao |

---

## MÓDULO 12 — Informática

```
master_file: 12_INFORMATICA_CONCURSO_MASTER.md
subject_slug: informatica
category: basic
study_phase: "1"
order: 12
estimated_hours: 6.0
icon: 💻
```

### Capítulos

| order | title | sections_source | estimated_minutes | tags |
|---|---|---|---|---|
| 1 | Windows — Desktop, Arquivos e Atalhos | Módulo 1 | 30 | windows, atalhos-teclado, explorador-arquivos, desktop |
| 2 | Internet, Navegadores e E-mail | Módulos 2, 3 | 30 | internet, navegadores, email, http, https, cookies |
| 3 | Word e PowerPoint | Módulos 4, 6 | 25 | word, powerpoint, atalhos-word, formatacao |
| 4 | Excel — Funções, Referências e Fórmulas | Módulo 5 | 35 | excel, funcoes-excel, referencias-relativas, referencias-absolutas, soma, media |
| 5 | Segurança da Informação e Certificação Digital | Módulos 7, 8 | 30 | seguranca-informacao, malware, backup, certificacao-digital, cid |

---

## MÓDULO 13 — Matemática

```
master_file: 13_MATEMATICA_ESSENCIAL_REVISAO.md
subject_slug: matematica
category: basic
study_phase: "1"
order: 13
estimated_hours: 8.0
icon: 🔢
```

### Capítulos

| order | title | sections_source | estimated_minutes | tags |
|---|---|---|---|---|
| 1 | Razão, Proporção e Regra de Três | §1, §2, §3, §4 | 40 | razao, proporcao, regra-de-tres, regra-de-tres-composta |
| 2 | Porcentagem e Médias | §5, §6, §7 | 35 | porcentagem, media-aritmetica, media-ponderada |
| 3 | Raciocínio Lógico e Sistema de Medidas | §8, §9 | 30 | raciocinio-logico, sistema-medidas, conversao-unidades |
| 4 | Problemas Clássicos e Tópicos Complementares | §10, §11, §12, §13, §14, §15, §16, §17 | 30 | problemas-matematicos, geometria, probabilidade, equacoes |

---

## MÓDULO 14 — Conhecimentos Gerais

```
master_file: 14_CONHECIMENTOS_GERAIS_REVISAO.md
subject_slug: conhecimentos-gerais
category: basic
study_phase: "1"
order: 14
estimated_hours: 6.0
icon: 🌍
```

### Capítulos

| order | title | sections_source | estimated_minutes | tags |
|---|---|---|---|---|
| 1 | Ponta Grossa — Identidade, História e Economia | Módulo 1 (completo) | 35 | ponta-grossa, historia-ponta-grossa, economia-ponta-grossa, geografia-ponta-grossa |
| 2 | Paraná — Dados, História e Geografia | Módulo 2 (completo) | 25 | parana, estado-parana, economia-parana |
| 3 | Brasil — Estrutura Política e Dados Gerais | Módulo 3 (completo) | 25 | brasil, tres-poderes, estrutura-politica, simbolos-nacionais |
| 4 | Atualidades — Política, Economia e Saúde | Módulo 4 (partes 1–3) | 30 | atualidades, politica, economia, saude |
| 5 | Atualidades — Tecnologia, Meio Ambiente e Educação | Módulo 4 (partes 4–6) | 25 | atualidades, tecnologia, meio-ambiente, educacao |

---

## Resumo de todos os módulos

| # | Módulo | Fase | Capítulos | Horas est. | Category |
|---|---|---|---|---|---|
| 1 | Saúde Única | 1 | 7 | 8.0 | specific |
| 2 | Zoonoses e Vigilância | 1 | 10 | 12.0 | specific |
| 3 | Segurança Alimentar | 1 | 9 | 10.0 | specific |
| 4 | Bem-Estar Animal | 1 | 7 | 8.0 | specific |
| 5 | Medicina Veterinária do Coletivo | 1 | 5 | 8.0 | specific |
| 6 | Fauna e Legislação Ambiental | 1 | 7 | 8.0 | specific |
| 7 | Cirurgia, Anestesia e Contenção | 1 | 9 | 18.0 | specific |
| 8 | Fisiologia e Reprodução | 1 | 6 | 10.0 | specific |
| 9 | Lei Orgânica de Ponta Grossa | 1 | 6 | 8.0 | specific |
| 10 | Revisão Final de Véspera | 4 | 9 | 4.0 | specific |
| 11 | Língua Portuguesa | 1 | 9 | 10.0 | basic |
| 12 | Informática | 1 | 5 | 6.0 | basic |
| 13 | Matemática | 1 | 4 | 8.0 | basic |
| 14 | Conhecimentos Gerais | 1 | 5 | 6.0 | basic |
| **TOTAL** | | | **98 capítulos** | **~124 h** | |
