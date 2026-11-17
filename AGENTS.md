# Instruções para o agente de IA

Você está num repositório que gera apresentações PowerPoint (`.pptx`) em
Python, com padrão visual fixo: transição em todos os slides, animação de
entrada automática, números que sobem, GIF e vídeo gerados em código e
validação automática. Siga este roteiro do começo ao fim. Responda e escreva
em português do Brasil.

---

## 1. Prepare o ambiente você mesmo

Não peça para a pessoa rodar comandos. Faça você, no terminal integrado.

1. Confira se há Python 3.10 ou mais novo: `python --version` (no macOS e
   Linux, `python3 --version`). Se não houver, explique à pessoa como instalar
   (python.org) e pare até ela confirmar.
2. Se a pasta `.venv` não existir, crie o ambiente virtual e instale:

   Windows:
   ```
   python -m venv .venv
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
   macOS e Linux:
   ```
   python3 -m venv .venv
   .venv/bin/python -m pip install -r requirements.txt
   ```
3. Teste gerando o deck de exemplo:
   ```
   <python do .venv> decks/exemplo/gera_ativos.py
   <python do .venv> decks/exemplo/build.py
   ```
   Deve imprimir `gerado: .../saida/exemplo.pptx`.

Daqui em diante, `PY` é o Python do `.venv` (`.venv\Scripts\python.exe` no
Windows, `.venv/bin/python` no macOS e Linux). Nunca instale pacotes fora do
`.venv`.

---

## 2. Entreviste antes de criar

Antes de escrever qualquer slide, faça as perguntas abaixo **em uma única
mensagem**, numeradas, e espere a resposta. Se a pessoa já respondeu alguma
no pedido, não pergunte de novo. Sugira um padrão para cada uma, para ela
poder responder só "ok".

1. **Tema e objetivo**: do que trata, e o que o público deve pensar ou decidir
   ao final?
2. **Público e duração**: para quem, e quantos minutos de fala?
3. **Quantidade de slides**: quantos? (padrão: um slide por minuto e meio,
   contando capa e encerramento)
4. **Capa**: título, subtítulo e assinatura (nome, instituição, data).
5. **Identidade visual**: `ifes` (padrão, modelo IFES em verde) ou `escuro`
   (fundo preto, acento turquesa, foto em tela cheia)? Na `escuro`, quer
   logotipo? Se sim, o caminho do PNG.
6. **Imagens**: há fotos ou figuras para inserir? Em que pasta estão? Em qual
   slide vai cada uma?
7. **Vídeos**: há clipes? Onde estão? (o kit corta para 15 a 25 segundos, sem
   áudio, em loop)
8. **Números estratégicos**: há números que devem entrar contando, de zero até
   o valor? Quais, e de onde vêm (fonte)?
9. **GIFs gerados em Python**: quer alguma figura animada (gráfico que cresce,
   processo passo a passo, simulação)? O que ela deve mostrar?
10. **Material de apoio**: textos, PDFs ou dados para usar como conteúdo?
11. **Notas do apresentador**: quer o roteiro de fala nas notas de cada slide?

Depois das respostas, mostre o **roteiro**: uma linha por slide (número,
título, o que entra e qual recurso: cartões, linha do tempo, número que sobe,
imagem, GIF, vídeo, Morph). Só gere depois que a pessoa aprovar.

---

## 3. Gere o deck

1. Crie a pasta do deck a partir do modelo:
   ```
   PY scripts/novo_deck.py nome_do_deck
   ```
   Nome em minúsculas com sublinhado, descrevendo o assunto.
2. Copie as imagens, GIFs e vídeos da pessoa para `decks/nome_do_deck/assets/`.
   Vídeo longo: corte com `kit.clipes.cortar(entrada, saida, inicio, duracao)`.
3. GIFs e clipes gerados em código vão num `decks/nome_do_deck/gera_ativos.py`,
   no molde de `decks/exemplo/gera_ativos.py` (Pillow para quadros, GIF com
   `save_all=True`; vídeo pelo ffmpeg que já vem no `.venv`). O primeiro quadro
   do GIF deve ser o estado final: é o que aparece parado e no PDF.
4. Escreva `decks/nome_do_deck/build.py`. **Copie os slides de
   `decks/exemplo/build.py`**, que tem um exemplo funcionando de cada recurso:

   | Recurso | Função no exemplo |
   |---|---|
   | capa com cascata | `s01_capa` |
   | linha do tempo com barra | `s02_linha_do_tempo` |
   | números que sobem | `s03_numeros` |
   | fluxo de etapas em cartões | `s04_fluxo` |
   | imagem em moldura com texto | `s05_imagem` |
   | GIF animado | `s06_gif` |
   | vídeo em loop | `s07_video` |
   | Morph entre dois slides | `_ciclo` e `morph_em` no `main` |
   | encerramento | `s10_encerramento` |

   Para a identidade `escuro`, use `decks/demonstracao/build.py` e
   `kit/layouts.py` (sete composições prontas).
5. Rode tudo de uma vez:
   ```
   PY scripts/produzir.py nome_do_deck
   ```
   Isso gera os ativos, o `.pptx` em `saida/`, valida e, no Windows com
   PowerPoint instalado, exporta a folha de contato
   `saida/_slides_nome_do_deck/contato.png`.
6. **Olhe a folha de contato** (abra a imagem). Procure texto colidindo,
   bloco fora do lugar, slide vazio, imagem deformada. Corrija no `build.py` e
   rode de novo até sair limpo. Sem PowerPoint (macOS, Linux), avise a pessoa
   que a conferência visual fica com ela, abrindo o `.pptx`.
7. Entregue: caminho do `.pptx`, o roteiro final e o que precisa de revisão
   humana (dados, nomes, imagens).

---

## 4. Regras que não mudam

- **Transição em todos os slides**: termine o `main` com
  `aplicar_em_todos(prs)` (fade por preto). Morph só entre dois slides
  seguidos com as mesmas formas: `aplicar_em_todos(prs, morph_em=(n,))`, com
  `n` sendo o segundo slide.
- **Animação de entrada automática** em todo slide de conteúdo, só `fade` e
  `wipe`, por `anima(...)` ou `monta_timing(...)`. Animar estrutura (ordem,
  fluxo, hierarquia), nunca decoração.
- **Número que sobe** (`kit.numeros.numero_que_sobe`) só quando a pessoa pedir
  números estratégicos, no máximo três por slide. Ligue com `tocar_junto`
  depois do `anima`.
- **Vídeo depois da animação**: `inserir_video` sempre depois do
  `anima`/`monta_timing` do slide, senão o vídeo não toca.
- **Não invente dados.** Número, nome, data e citação vêm da pessoa ou do
  material dela. Se faltar, pergunte. Slide com dado leva a linha de fonte,
  `fonte(s, "Fonte: ...")`. Dado ilustrativo é marcado como fictício.
- **No máximo quatro itens** por lista ou bloco. Mais que isso, divida em dois
  slides.
- **Escrita**: português do Brasil com acentuação correta, e nenhum travessão
  nem meia-risca (use dois pontos, vírgula ou parênteses). O kit recusa
  travessão no texto do slide.
- **Imagens e vídeos no lugar certo**: tudo em `decks/nome_do_deck/assets/`;
  o resultado sai em `saida/`. Nada disso vai para o Git.
- **Não altere o `kit/` para resolver um deck.** O que for específico fica no
  `build.py` do deck. Mudança no kit só se a pessoa pedir, e com
  `PY -m pip install -r requirements-dev.txt` e `PY -m pytest testes -q`
  passando depois.

Referências: [docs/padrao-visual.md](docs/padrao-visual.md) (o padrão e o
porquê de cada regra), [docs/armadilhas.md](docs/armadilhas.md) (problemas
conhecidos e solução), [docs/validacao.md](docs/validacao.md) (o que o
validador cobra).
