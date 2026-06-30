# INFORMÁTICA BÁSICA — MATERIAL MASTER PARA CONCURSO

> Material de **estudo para concurso** (não é manual técnico nem apostila acadêmica). Cobre o conteúdo de **Informática Básica** do edital CP 003/2026 — Prefeitura de Ponta Grossa, cargo Médico Veterinário (Nível Superior) — no formato dos MASTER 01–11: tabelas, resumos, comparativos, macetes e pegadinhas.
>
> **Peso na prova:** 5 questões × 2,50 = **12,50 pts** · **Nota mínima 2,50 (eliminatório por disciplina)**.
> **Prioridade: ALTA — maior ROI da prova** (pouco conteúdo, alto retorno; ideal para garantir os 12,50 pts quase inteiros). Ver [MAPEAMENTO_DISCIPLINAS_BASICAS.md].
>
> **Ementa do edital:** Microsoft Office (Word, Excel, PowerPoint); Windows; Internet e intranet; organização/gerenciamento de arquivos, pastas e programas; certificação e assinatura digital; Segurança da Informação.

> 🎯 **REGRA DE OURO:** banca de concurso municipal cobra **conceito decoreba + atalho + pegadinha de versão**. É a matéria mais "garantível" da prova: decore tabelas, atalhos e diferenças. Nunca zere.

---

## ÍNDICE
- **Módulo 1 — Windows** (área de trabalho, arquivos, pastas, atalhos, Explorador, gerenciamento)
- **Módulo 2 — Internet** (navegadores, URL, HTTP/HTTPS, cookies, download/upload, pesquisa)
- **Módulo 3 — E-mail** (CC, CCO, anexos, spam, phishing)
- **Módulo 4 — Word**
- **Módulo 5 — Excel** (fórmulas, SOMA, MÉDIA, MÁXIMO, MÍNIMO, CONT.SE, referências)
- **Módulo 6 — PowerPoint**
- **Módulo 7 — Segurança da Informação** (malware, vírus, worm, trojan, ransomware, backup, firewall, antivírus)
- **Módulo 8 — Certificação Digital** (assinatura, certificado, ICP-Brasil)
- **Revisão relâmpago · Top pegadinhas**

---

# MÓDULO 1 — WINDOWS ⭐⭐

**Explicação simples:** Windows é o **sistema operacional** (SO) — o programa que controla o computador e roda os outros programas. Em concurso cai a **interface** (área de trabalho, janelas) e o **gerenciamento de arquivos** (Explorador).

## Área de Trabalho (Desktop)

| Elemento | O que é |
|---|---|
| **Ícones** | Atalhos/representações de programas, arquivos e pastas |
| **Barra de Tarefas** | Faixa (geralmente inferior) com programas abertos e fixados |
| **Menu Iniciar** | Acesso a programas, configurações e desligar (tecla **⊞ Windows**) |
| **Área de Notificação** | Relógio, volume, rede, ícones em segundo plano (ao lado do relógio) |
| **Lixeira** | Guarda arquivos excluídos **do disco local** (recuperáveis até esvaziar) |

## Arquivos × Pastas

| Conceito | Definição |
|---|---|
| **Arquivo** | Conjunto de dados gravado (documento, foto, programa). Tem **nome + extensão** (ex.: `relatorio.docx`) |
| **Pasta (diretório)** | "Gaveta" que organiza/agrupa arquivos e outras pastas (subpastas) |
| **Extensão** | Indica o **tipo** do arquivo: `.docx` Word, `.xlsx` Excel, `.pptx` PowerPoint, `.pdf`, `.txt`, `.jpg`, `.exe` (programa), `.zip` (compactado) |

**Regras de nomes de arquivo (cai!):** **não** pode usar os caracteres `\ / : * ? " < > |`. Pode ter espaços e ponto.

## Explorador de Arquivos (Windows Explorer / "Este Computador")

- Abre com **⊞ Windows + E**.
- Mostra unidades (C:, D:), pastas e arquivos; permite copiar, mover, renomear, excluir.

## Atalhos de teclado do Windows (DECORE — caem direto)

| Atalho | Ação |
|---|---|
| **Ctrl + C / Ctrl + X / Ctrl + V** | Copiar / Recortar / Colar |
| **Ctrl + Z / Ctrl + Y** | Desfazer / Refazer |
| **Ctrl + A** | Selecionar tudo |
| **Ctrl + P** | Imprimir |
| **Ctrl + F** | Localizar |
| **F2** | Renomear (arquivo selecionado) |
| **Delete** | Enviar para a Lixeira |
| **Shift + Delete** | Excluir **definitivamente** (NÃO vai para a Lixeira) ⚠️ |
| **⊞ Win + E** | Abrir Explorador de Arquivos |
| **⊞ Win + D** | Mostrar área de trabalho |
| **⊞ Win + L** | Bloquear o computador |
| **Alt + Tab** | Alternar entre janelas abertas |
| **Alt + F4** | Fechar a janela/programa ativo |
| **PrtScn** | Capturar a tela (print) |
| **F5** | Atualizar |

## Gerenciamento de arquivos — operações

| Operação | Como/efeito |
|---|---|
| **Copiar** | Duplica (origem **permanece**) |
| **Recortar (mover)** | Move (origem **some**) |
| **Renomear** | F2 ou clicar no nome |
| **Excluir** | Delete → Lixeira / Shift+Delete → definitivo |
| **Compactar (ZIP)** | Reduz tamanho e junta vários arquivos em um |

**Pegadinhas ⚠️:**
- **Shift + Delete** apaga **sem** passar pela Lixeira → **não dá para recuperar** pela Lixeira.
- Arquivos excluídos de **pen drive / rede** geralmente **não vão** para a Lixeira (somem direto).
- Dois arquivos com **mesmo nome e mesma extensão** não podem coexistir na **mesma** pasta.
- **Mover** (recortar) ≠ **copiar**: ao mover, o arquivo **deixa** o local de origem.

**Macete:** **Ctrl = ação dentro do programa** (C/V/Z/P/F); **Win = ação do sistema** (E/D/L). **Shift+Delete = adeus pra sempre.**

---

# MÓDULO 2 — INTERNET ⭐⭐

**Explicação simples:** Internet é a **rede mundial** que conecta computadores. **Intranet** é uma rede **interna/privada** de uma organização (mesma tecnologia, acesso restrito). **Extranet** = parte da intranet liberada a parceiros externos com login.

## Internet × Intranet × Extranet (comparativo — cai!)

| | Internet | Intranet | Extranet |
|---|---|---|---|
| Alcance | Mundial, pública | Interna da empresa | Intranet estendida a externos |
| Acesso | Qualquer um | Restrito (funcionários) | Parceiros/clientes com senha |
| Tecnologia | TCP/IP, navegador | A **mesma** da Internet | A mesma |

## Navegadores (browsers)

Programa para acessar páginas web. Exemplos: **Google Chrome, Mozilla Firefox, Microsoft Edge, Safari, Opera**.

| Recurso do navegador | Função |
|---|---|
| **Favoritos/Marcadores** | Salvar sites para acesso rápido |
| **Histórico** | Lista de páginas visitadas |
| **Guia/Aba (tab)** | Abrir vários sites na mesma janela (**Ctrl+T** nova aba) |
| **Modo anônimo/privativo** | Não salva histórico/cookies **localmente** (⚠️ não deixa você "invisível" na rede) |
| **Cache** | Armazena temporariamente partes do site para carregar mais rápido |

## URL — endereço de um recurso na web

Estrutura: `https:// www. site .com.br /pagina`

| Parte | Significado |
|---|---|
| **https://** | Protocolo |
| **www** | Subdomínio (servidor web) |
| **site.com.br** | Domínio (.com = comercial, .gov = governo, .edu = ensino, .org = organização; .br = Brasil) |
| **/pagina** | Caminho do recurso |

## HTTP × HTTPS (comparativo — clássico de prova)

| | HTTP | HTTPS |
|---|---|---|
| Significado | HyperText Transfer Protocol | HTTP **Secure** |
| Segurança | **Sem** criptografia | **Com** criptografia (SSL/TLS) |
| Indicador | — | **Cadeado** 🔒 na barra |
| Uso | Sites comuns | Bancos, compras, login (dados sigilosos) |

## Cookies

Pequenos **arquivos de texto** que o site grava no navegador para **lembrar** do usuário (login, preferências, carrinho).
- ⚠️ Cookie **não é vírus** e **não** "rouba" o computador — apenas guarda informações de navegação. Podem ser apagados pelo navegador.

## Download × Upload

| | Download | Upload |
|---|---|---|
| Direção | **Baixar:** servidor → seu computador | **Enviar:** seu computador → servidor |
| Exemplo | Baixar um PDF | Anexar foto numa nuvem/site |

## Pesquisa (buscadores)

Ferramentas de busca (Google, Bing). Operadores que caem:

| Operador | Efeito |
|---|---|
| `"frase exata"` | Busca a frase **exatamente** como escrita |
| `-palavra` | **Exclui** resultados com essa palavra |
| `site:gov.br` | Busca **só** dentro daquele site/domínio |
| `filetype:pdf` | Busca só arquivos de um tipo |

**Pegadinhas ⚠️:**
- **HTTPS** = seguro/criptografado; **HTTP** = sem segurança. Banca troca os dois.
- **Modo anônimo NÃO te deixa invisível** para o provedor, site ou empregador — só não salva histórico **no aparelho**.
- **Download** = baixar (vem pra você); **Upload** = enviar (sai de você). Não inverter.
- Cookie ≠ malware.

**Macete:** **HTTP**S = o "**S**" é de **Segurança** (cadeado). **Down**load = vem pra **baixo** (pra você); **Up**load = sobe pra rede.

---

# MÓDULO 3 — E-MAIL ⭐⭐

**Explicação simples:** correio eletrônico. Caem os **campos de destinatário** e as **ameaças** (spam/phishing).

## Campos do destinatário (CC × CCO — campeão de pegadinha)

| Campo | Nome | Quem vê os endereços? |
|---|---|---|
| **Para (To)** | Destinatário principal | Todos veem |
| **Cc** | Com Cópia (*Carbon Copy*) | **Todos veem** quem está em Cc |
| **Cco** | Com Cópia **Oculta** (*Blind Carbon Copy* / Bcc) | **Ninguém vê** quem está em Cco — fica **invisível** aos demais |

> ⭐ **Diferença que SEMPRE cai:** quem está em **Cco fica oculto**; quem está em **Cc é visível** a todos. Para enviar a uma lista grande sem expor endereços, usa-se **Cco**.

## Anexos

Arquivos enviados junto com o e-mail.
- Provedores **limitam o tamanho** (tipicamente ~20–25 MB).
- ⚠️ **Anexo é o principal vetor de vírus/malware** — não abrir anexos de remetente desconhecido.

## Spam × Phishing (comparativo)

| | Spam | Phishing |
|---|---|---|
| O que é | Mensagem **não solicitada** em massa (propaganda) | **Golpe/fraude:** finge ser empresa/banco para **roubar dados** |
| Intenção | Geralmente incômoda/comercial | **Maliciosa** (senhas, cartão, CPF) |
| Como age | Volume, repetição | Link/site falso, urgência, isca |
| Defesa | Filtro **anti-spam** | Desconfiar, não clicar, conferir remetente |

**Pegadinhas ⚠️:**
- **Cc visível × Cco oculto** — não inverter.
- **Spam ≠ phishing:** spam é "lixo eletrônico" (chato); **phishing é golpe** (perigoso, rouba dados).
- Phishing usa **engenharia social** (engana o usuário), não necessariamente um vírus.

**Macete:** **Cc**o = o "**O**" é de **Oculto**. **Phishing** lembra "**fishing**" (pescaria) → joga isca pra pescar seus dados.

---

# MÓDULO 4 — WORD ⭐⭐

**Explicação simples:** editor de **textos** do pacote Office. Extensão padrão: **`.docx`**.

## Recursos principais

| Recurso | Função |
|---|---|
| **Fonte / Tamanho** | Tipo e tamanho da letra |
| **Negrito / Itálico / Sublinhado** | Estilo do texto |
| **Alinhamento** | Esquerda, centralizado, direita, justificado |
| **Marcadores / Numeração** | Listas |
| **Cabeçalho / Rodapé** | Texto que se repete no topo/base das páginas |
| **Localizar e Substituir** | Achar/trocar palavras (Ctrl+U substituir) |
| **Verificação ortográfica** | Sublinha erros em vermelho |
| **Controlar Alterações** | Registra edições (revisão) |

## Atalhos do Word (DECORE)

| Atalho | Ação |
|---|---|
| **Ctrl + N** | **Negrito** (em português!) |
| **Ctrl + I** | Itálico |
| **Ctrl + S** | **Sublinhado** (em português!) ⚠️ |
| **Ctrl + B** | **Salvar** (em português!) ⚠️ |
| **Ctrl + O** | Novo documento |
| **Ctrl + A** | Abrir |
| **Ctrl + P** | Imprimir |
| **Ctrl + E** | Centralizar |
| **Ctrl + J** | Justificar |
| **Ctrl + T** | Selecionar tudo |

> ⚠️ **PEGADINHA CLÁSSICA — Office em português troca as letras:** No Word **PT-BR**, **Ctrl+B = Salvar** (de "salvar Backup"? não — é a convenção PT), **Ctrl+S = Sublinhado**, **Ctrl+N = Negrito**, **Ctrl+T = selecionar Tudo**. No Office em inglês seria B=Bold, S=Save, U=Underline. A banca adora cobrar o **atalho em português**.

**Pegadinhas ⚠️:**
- **Ctrl+B salva** e **Ctrl+S sublinha** (no Word em português). Não confundir com o inglês.
- `.docx` é o **padrão moderno**; `.doc` é o antigo.
- **Justificado** alinha nas **duas** margens; **centralizado** é diferente.

**Macete (Office PT-BR):** **S**ublinhado = **S**; **N**egrito = **N**; sal**B**ar... pense "**B** de salvar" como exceção a decorar. **T** = **T**udo (selecionar).

---

# MÓDULO 5 — EXCEL ⭐⭐⭐ (a estrela da prova de informática)

**Explicação simples:** programa de **planilhas** (cálculos). Extensão **`.xlsx`**. É a parte que **mais cai** — domine as fórmulas.

## Conceitos básicos

| Termo | O que é |
|---|---|
| **Célula** | Cruzamento de coluna (letra) e linha (número): **A1, B2, C3** |
| **Coluna** | Vertical, identificada por **letras** (A, B, C...) |
| **Linha** | Horizontal, identificada por **números** (1, 2, 3...) |
| **Intervalo** | Faixa de células: **A1:A10** (dois-pontos = "até") |
| **Planilha / Pasta de trabalho** | Planilha = aba; Pasta de trabalho = o arquivo inteiro |

> ⭐ **REGRA Nº 1:** toda fórmula/função começa com **= (sinal de igual)**. Ex.: `=A1+B1`. Sem o "=", o Excel trata como texto.

## Operadores

`+` soma · `-` subtração · `*` multiplicação · `/` divisão · `^` potência · `%` porcentagem.
- **`:` (dois-pontos)** = intervalo contínuo → `A1:A5` (de A1 **até** A5).
- **`;` (ponto e vírgula)** = separa argumentos/células avulsas → `SOMA(A1;A5)` (só A1 **e** A5).

## Funções essenciais (DECORE — caem quase sempre)

| Função | O que faz | Exemplo | Resultado |
|---|---|---|---|
| **=SOMA(A1:A5)** | Soma o intervalo | soma de A1 até A5 | total |
| **=MÉDIA(A1:A5)** | Média aritmética | (A1+...+A5)/5 | média |
| **=MÁXIMO(A1:A5)** | Maior valor | — | o maior |
| **=MÍNIMO(A1:A5)** | Menor valor | — | o menor |
| **=CONT.NÚM(A1:A5)** | Conta células com **números** | — | quantidade |
| **=CONT.SE(A1:A5;">10")** | Conta células que **atendem a um critério** | conta quantas são >10 | quantidade |
| **=SE(A1>7;"Aprovado";"Reprovado")** | Teste lógico (condição) | se A1>7 → "Aprovado", senão "Reprovado" | texto |

> ⚠️ **Diferença que cai:** `:` soma o **intervalo inteiro** (`SOMA(A1:A3)` = A1+A2+A3); `;` soma **só as listadas** (`SOMA(A1;A3)` = A1+A3, **ignora A2**).

**Exemplos de CONT.SE:** `=CONT.SE(B2:B10;"Aprovado")` conta quantos "Aprovado"; `=CONT.SE(C2:C10;">=60")` conta quantos ≥ 60.

## Referências (relativa × absoluta — clássico!)

| Tipo | Símbolo | Comportamento ao **copiar/arrastar** |
|---|---|---|
| **Relativa** | `A1` | **Muda** conforme você arrasta (A1→A2→A3) |
| **Absoluta** | `$A$1` | **Trava** (sempre A1, não muda) |
| **Mista** | `$A1` ou `A$1` | Trava só a coluna **ou** só a linha |

> ⭐ O **cifrão `$` trava** a referência. `$A$1` = totalmente travada. Tecla de atalho para inserir o $: **F4**.

**Pegadinhas ⚠️:**
- Fórmula **sem `=`** não calcula (vira texto).
- **`:` (intervalo) ≠ `;` (lista)** — muda totalmente o resultado da soma.
- **Referência relativa muda ao arrastar; absoluta (`$`) não muda.**
- Em Excel **PT-BR** usa-se **`;`** para separar argumentos (em versões com vírgula decimal). MÉDIA, MÁXIMO, MÍNIMO têm **acento** no nome em português.

**Macete:** **`=` para começar**, **`:` = "até"** (intervalo), **`;` = "e"** (avulsos), **`$` = cadeado** (trava a referência, F4).

---

# MÓDULO 6 — POWERPOINT ⭐

**Explicação simples:** programa de **apresentações** de slides do Office. Extensão **`.pptx`**.

| Conceito | O que é |
|---|---|
| **Slide** | Cada "tela"/página da apresentação |
| **Layout** | Modelo de organização dos elementos no slide (título, conteúdo, imagem) |
| **Slide Mestre** | Modelo que define o padrão de **todos** os slides de uma vez |
| **Transição** | Efeito **entre um slide e outro** |
| **Animação** | Efeito **em um elemento dentro** do slide |
| **Tema / Design** | Conjunto de cores, fontes e fundo |

| Atalho/recurso | Ação |
|---|---|
| **F5** | Iniciar apresentação **do começo** |
| **Shift + F5** | Apresentar **a partir do slide atual** |
| **Esc** | Encerrar a apresentação |

**Pegadinhas ⚠️:**
- **Transição** = entre slides; **animação** = dentro do slide (em um objeto). Não confundir.
- **F5** apresenta do início; **Shift+F5** do slide atual.
- Extensões: Word `.docx` · Excel `.xlsx` · PowerPoint `.pptx`. Não trocar.

**Macete:** **slide** = página; **layout** = arrumação; **transição (slide→slide)** ≠ **animação (objeto)**.

---

# MÓDULO 7 — SEGURANÇA DA INFORMAÇÃO ⭐⭐⭐

**Explicação simples:** proteger informações contra ameaças. Caem **tipos de malware** e **ferramentas de defesa**.

## Pilares da segurança (a banca cita a sigla **CID/DIC**)

| Pilar | Significa |
|---|---|
| **Confidencialidade** | Só quem é autorizado acessa |
| **Integridade** | Dado não é alterado indevidamente |
| **Disponibilidade** | Informação acessível quando necessária |
> (+ Autenticidade e Não-repúdio em algumas bancas)

## Malware = "software malicioso" (termo guarda-chuva)

| Tipo | O que faz | Marca registrada |
|---|---|---|
| **Vírus** | Infecta arquivos; **precisa do usuário** executar para se espalhar | Anexa-se a um arquivo/programa hospedeiro |
| **Worm (verme)** | Se **autorreplica** e se espalha **sozinho** pela rede (sem hospedeiro) | Não precisa de ação do usuário ⚠️ |
| **Trojan (Cavalo de Troia)** | Finge ser um programa **útil/legítimo**, mas abre porta para invasão | Disfarce / engana o usuário |
| **Ransomware** | **Sequestra/criptografa** os dados e **exige resgate** ($, geralmente em cripto) | Pede resgate (ransom) ⚠️ |
| **Spyware** | **Espiona** o usuário (coleta dados) | Espionagem |
| **Keylogger** | Captura o que é **digitado** (senhas) | Grava teclas |

> ⭐ **Diferenças que mais caem:**
> - **Vírus precisa do usuário** (executar o arquivo); **Worm se espalha sozinho** pela rede.
> - **Trojan** = disfarce de programa bom; **Ransomware** = pede **resgate**.

## Ferramentas de defesa

| Ferramenta | Função |
|---|---|
| **Antivírus** | Detecta e remove **malware** (precisa estar **atualizado**) |
| **Firewall** | "Porteiro" da rede — **controla o tráfego** de entrada/saída (bloqueia acessos não autorizados) |
| **Backup** | **Cópia de segurança** dos dados (defesa nº 1 contra ransomware e perdas) |
| **Atualizações (patches)** | Corrigem falhas de segurança |
| **Senha forte / 2FA** | Autenticação |

> ⭐ **Backup × Firewall × Antivírus (não confundir):** **Backup** = cópia para **recuperar** dados; **Firewall** = controla **tráfego** de rede; **Antivírus** = combate **malware**. São coisas diferentes.

## Tipos de backup (cai em municipal)

| Tipo | O que copia |
|---|---|
| **Completo (full)** | **Todos** os dados |
| **Incremental** | Só o que mudou **desde o último backup (qualquer um)** |
| **Diferencial** | Só o que mudou **desde o último backup completo** |

**Pegadinhas ⚠️:**
- **Vírus ≠ worm:** vírus precisa de hospedeiro/ação do usuário; **worm se autorreplica sozinho**.
- **Firewall NÃO é antivírus:** firewall filtra **tráfego de rede**, não remove vírus já instalado.
- **Backup** é a melhor defesa contra **ransomware** (se há cópia, não se paga resgate).
- **Antivírus desatualizado** perde eficácia.
- **Malware** é o gênero; vírus, worm, trojan, ransomware são **espécies**.

**Macete:** **Worm = "anda sozinho" (Web/rede)**; **Trojan = Truque (disfarce)**; **Ransomware = Resgate**; **Firewall = parede de fogo (porteiro da rede)**; **Backup = cópia (salva vidas)**.

---

# MÓDULO 8 — CERTIFICAÇÃO DIGITAL ⭐⭐

**Explicação simples:** tecnologia que garante **identidade** e **autenticidade** no meio digital — quem assinou foi realmente quem diz ser, e o documento não foi alterado.

## Conceitos (não confundir!)

| Conceito | O que é |
|---|---|
| **Certificado Digital** | "Identidade/RG eletrônico" — arquivo que **identifica** uma pessoa/empresa, emitido por uma Autoridade Certificadora (AC) |
| **Assinatura Digital** | **Processo** que usa o certificado para **assinar** um documento, garantindo autoria e integridade |
| **Chave pública / privada** | Par de chaves (criptografia assimétrica): a **privada** assina (secreta); a **pública** verifica |
| **ICP-Brasil** | **Infraestrutura de Chaves Públicas Brasileira** — a "raiz" oficial que dá **validade jurídica** aos certificados no Brasil |

## O que a assinatura digital garante

| Garante | Significa |
|---|---|
| **Autenticidade** | Confirma **quem** assinou |
| **Integridade** | Garante que o documento **não foi alterado** após assinado |
| **Não-repúdio** | O signatário **não pode negar** que assinou |

> ⚠️ **Assinatura digital ≠ confidencialidade:** ela garante **autoria e integridade**, mas **não** necessariamente esconde o conteúdo (isso é a **criptografia** de sigilo).

## Assinatura digital × assinatura digitalizada (PEGADINHA clássica)

| | Assinatura **Digital** | Assinatura **Digitalizada (escaneada)** |
|---|---|---|
| O que é | Criptografia + certificado (ICP-Brasil) | **Imagem** da assinatura à caneta (foto/scan) |
| Validade | **Jurídica plena** | **Sem** garantia técnica/jurídica forte |
| Segurança | Alta (autoria + integridade) | Baixa (fácil de copiar) |

**Pegadinhas ⚠️:**
- **Certificado** (a identidade) ≠ **assinatura** (o ato de assinar com ela).
- **Digital ≠ digitalizada:** digitalizada é só a **imagem** da firma escaneada — não tem valor de assinatura digital.
- Quem dá validade no Brasil é a **ICP-Brasil**.
- **Chave privada** é **secreta** (assina); **chave pública** é compartilhada (verifica).

**Macete:** **Certificado = RG digital**; **Assinatura = o ato de assinar com esse RG**; **ICP-Brasil = o "cartório raiz"** que valida tudo. **Privada assina, pública confere.**

---

## REVISÃO RELÂMPAGO (VÉSPERA) ⚡

- **Shift+Delete** apaga **definitivo** (não vai pra Lixeira). **Win+E** abre Explorador.
- **HTTPS = seguro (cadeado)**; HTTP = sem segurança. **Download = baixar; Upload = enviar.**
- **Cookie não é vírus**; modo anônimo **não te deixa invisível**.
- **Cc = visível; Cco = oculto.** **Spam = chato; Phishing = golpe que rouba dados.**
- **Word PT-BR: Ctrl+B = Salvar, Ctrl+S = Sublinhado, Ctrl+N = Negrito, Ctrl+T = Tudo.**
- **Excel: fórmula começa com `=`. `:` = intervalo (até); `;` = avulsos (e). `$` trava (absoluta).**
- **SOMA, MÉDIA, MÁXIMO, MÍNIMO, CONT.SE** — domine a sintaxe.
- **PowerPoint: F5 apresenta; transição = entre slides; animação = no objeto.**
- **Vírus precisa do usuário; Worm anda sozinho; Trojan = disfarce; Ransomware = resgate.**
- **Firewall = tráfego de rede; Antivírus = malware; Backup = cópia (anti-ransomware).**
- **Certificado = RG digital; Assinatura digital ≠ digitalizada; ICP-Brasil dá validade jurídica.**

---

## TOP PEGADINHAS QUE A BANCA REPETE

| Afirmação da banca | Certo? | Por quê |
|---|---|---|
| "Shift+Delete envia para a Lixeira" | ❌ | Exclui **definitivamente** |
| "Modo anônimo deixa o usuário invisível na internet" | ❌ | Só não salva histórico **local** |
| "Cookie é um tipo de vírus" | ❌ | É arquivo de texto, não malware |
| "Quem está em Cc fica oculto" | ❌ | **Cco** é que fica oculto |
| "Spam e phishing são a mesma coisa" | ❌ | Spam = lixo; phishing = **golpe** |
| "No Word em português, Ctrl+S salva" | ❌ | Ctrl+S = **Sublinhar**; salvar = **Ctrl+B** |
| "Fórmula no Excel pode começar sem o sinal de =" | ❌ | Tem de começar com **=** |
| "=SOMA(A1;A3) soma A1, A2 e A3" | ❌ | `;` soma **só A1 e A3** (`:` somaria o intervalo) |
| "Referência $A$1 muda ao arrastar" | ❌ | Absoluta **trava** (não muda) |
| "Worm precisa do usuário para se espalhar" | ❌ | Worm se **autorreplica sozinho** |
| "Firewall remove vírus do computador" | ❌ | Firewall controla **tráfego**; quem remove é o **antivírus** |
| "Assinatura digitalizada (escaneada) tem o mesmo valor da digital" | ❌ | Digitalizada é só **imagem**, sem validade técnica |

---

*MASTER de Informática Básica para concurso — cobre Windows, Internet, E-mail, Word, Excel, PowerPoint, Segurança da Informação e Certificação Digital (edital CP 003/2026 · 5 questões / 12,50 pts). Material de revisão objetiva; não substitui resolução de questões da banca. Padrão da biblioteca MASTER 01–11.*
