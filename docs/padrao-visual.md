# Padrão visual

Tudo descrito aqui já vem pronto no kit (`kit/tema_ifes.py`, `kit/layouts_ifes.py`, `kit/base.py`). Este documento existe para
que o padrão possa ser revisto e mantido com critério, e para que ninguém
precise adivinhar por que uma escolha foi feita.

---

## 0. Três níveis de regra

Nem tudo aqui tem o mesmo peso. Uma apresentação de resultados não precisa ter
a mesma composição de uma palestra, mas as duas precisam ser reconhecíveis como
o mesmo material. Por isso o padrão é lido em três níveis.

| Nível | O que é | Quem pode mudar |
|---|---|---|
| **Obrigatório** | identidade: paleta, tipografia, proporção 16:9, uso do logotipo, corpo mínimo legível, ausência de travessão | ninguém, sem mudar o kit e este documento |
| **Configurável** | composição, quantidade de slides claros, densidade, ritmo de animação, quantidade de marcadores | quem monta o deck, conforme público e ocasião |
| **Excepcional** | desvio deliberado de algo obrigatório | quem monta, registrando a justificativa no cabeçalho do `build.py` |

O validador em `scripts/validar_deck.py` trata o obrigatório como erro e o
configurável como aviso. Aviso não impede a entrega, pede uma olhada.

---

## 0b. Duas identidades

Todo deck novo nasce na identidade `ifes`, o modelo público de apresentação
do IFES, com paleta, tipografia e grade medidas no modelo oficial. A segunda,
`escuro`, é fundo preto com acento turquesa e Montserrat, pensada para
palestra com foto em tela cheia.

| | `escuro` | `ifes` (padrão) |
|---|---|---|
| Onde mora | `kit/tema.py`, `kit/base.py`, `kit/layouts.py` | `kit/tema_ifes.py`, `kit/layouts_ifes.py` |
| Fundo | preto ou branco, preenchimento sólido | imagem do modelo, com a faixa verde e o logotipo do IFES |
| Acento | turquesa `#00E5C0` | três verdes, `#0B3D2C`, `#1C7F5C` e `#31775C` |
| Fonte | Montserrat | Arial, com Tahoma nas duas linhas da capa |
| Margem | 0,9 dos dois lados | 2,05 à esquerda, 0,78 à direita |
| Como abrir | `nova_apresentacao()` | `nova_apresentacao_ifes()` |

Há uma terceira, `importada`, para reformular uma apresentação que a pessoa
já tem mantendo o design dela (`kit/importado.py`). Nela, o modelo é o
próprio arquivo de origem: mestre, layouts, fundos e logotipo continuam, e o
validador cobra a paleta e as fontes do tema dele e as margens dos layouts
dele, e não as do kit. O formato também pode continuar o original.

O que **não** muda entre as identidades: formato 16:9, as regras de escrita, o
vocabulário de animação, a transição em fade, a medição de texto antes de
desenhar e a exigência de procedência. `kit/animacao.py`, `kit/coreografia.py`
e `kit/transicoes.py` não sabem de cor nenhuma e servem às duas sem alteração.

A identidade fica gravada nos metadados do arquivo, por `kit.politica`, e é o
validador que a lê para saber qual paleta e qual fonte cobrar. Misturar as
duas é erro, e não aviso: turquesa num deck `ifes` reprova, assim como verde
do modelo IFES num deck `escuro`.

Na dúvida, use `ifes`. As seções 1 a 6 abaixo descrevem a identidade
`escuro`; os valores do modelo IFES estão em `kit/tema_ifes.py`, e o deck
`decks/exemplo` mostra cada um deles em uso.

---

## 1. Paleta

| Papel | Cor | Onde aparece |
|---|---|---|
| Fundo dominante | `#000000` | slides de foto, case, provocação e encerramento |
| Acento principal | `#00E5C0` turquesa | kicker, ponto de marcador, frase de fecho |
| Verde escuro | `#00846F` | blocos cheios, mapas, coluna de destaque |
| Verde claro | `#54C1AF` e `#B8E8DF` | texto dentro de bloco verde escuro |
| Texto secundário | `#575756` e `#9D9D9C` | apoio, legenda, número de página |
| Fundo claro | `#FFFFFF` e `#F7F7F6` | diagrama, tabela, comparação |

O acento da identidade `escuro` é turquesa, não verde. Isso muda o equilíbrio com o preto: o
turquesa aguenta menos área que um verde escuro aguentaria.

O turquesa marca hierarquia e destaque. Ele não decora. Se aparecer em tudo,
não destaca nada.

---

## 2. Tipografia

Montserrat em títulos e corpo, sempre.

| Elemento | Corpo | Peso |
|---|---|---|
| Título de capa | 44 a 52, 44 é o padrão da composição | negrito |
| Título de slide | 28 a 36 | negrito |
| Kicker | 11, caixa alta, espaçamento 1,6 | negrito |
| Linha de apoio | 12,5 a 13,5 | normal |
| Marcador | 11,5 a 12,5 | normal |
| Frase de fecho | 12 a 13,5 | negrito, turquesa |
| Número de página | 10 | normal, cinza |

Fonte decorativa não entra nos decks, por portabilidade: se a fonte não
estiver instalada na máquina que apresenta, o PowerPoint substitui e a
diagramação quebra. Por isso o modelo IFES usa Arial.

---

## 3. Grade

Slide 16:9, 13,333 por 7,5 polegadas. Margem lateral de 0,9 polegada, dos dois
lados. Nada encosta na borda, exceto foto em tela cheia.

Faixa de seis colunas para fluxos: primeira coluna em 0,9, largura 1,88, folga
0,09. Faixa de quatro blocos: largura 2,72, folga 0,16.

---

## 4. Ritmo

Configurável.

Os slides pretos carregam foto, case, provocação e encerramento. Os claros
carregam diagrama, tabela e comparação, e funcionam como respiro.

A regra não é alternar a cada slide, é não deixar o público sem respiro. O que
cansa é densidade seguida, não fundo preto seguido. Três slides pretos seguidos
funcionam quando o segundo é texto com foto e o terceiro é vídeo, nenhum deles
denso.

O limite prático: no máximo três slides densos em sequência. Em apresentação
online, dois.

---

## 4b. Composições aprovadas

Sete composições em `kit/layouts.py`, cada uma recebendo o conteúdo por
parâmetro. O autor escolhe a composição e entrega o texto: não decide
coordenada, corpo de fonte nem tempo de animação. É isso que faz duas pessoas
diferentes produzirem slides reconhecíveis como o mesmo material.

| Composição | Quando usar | Fundo |
|---|---|---|
| `capa` | abertura | preto, foto em tela cheia |
| `texto_com_foto` | problema, produto, conceito com imagem ao lado. Aceita vídeo no lugar da foto | preto |
| `comparacao` | dois lados, antes e depois, nós e eles | claro |
| `faixa_de_etapas` | fluxo de processo, pipeline. Com `escada=True`, progressão de maturidade | claro ou preto |
| `linha_do_tempo` | trajetória, evolução, marcos | preto |
| `provocacao` | virada entre blocos, com pergunta e número grande | preto |
| `fechamento` | último slide, com contato e QR code | preto |

O catálogo vivo é `decks/demonstracao`, que gera um slide por composição e roda
numa cópia limpa do repositório.

Quando a composição não couber, monte o slide na mão com os helpers de
`kit.base` e `kit.slides`. O kit não impede o caso especial, ele evita que o
caso comum vire decisão. Caso especial que se repetir três vezes vira
composição nova.

---

## 4c. Sem cara de slide feito por IA

O kit existe para estruturar e modernizar apresentações sem deixar a marca
evidente de material gerado por IA. Alguns vícios se repetem tanto nesse tipo
de material que denunciam a origem antes de qualquer leitura. Aqui eles são
evitados por regra, e vários são cobrados por código.

| Vício | O que o kit faz no lugar | Quem cobra |
|---|---|---|
| Travessão e meia-risca no texto, muitas vezes vários por slide | dois pontos, vírgula, parênteses ou ponto final | erro na geração, no validador e no `verificar_texto.py` |
| Barra ou filete colorido sobre cada título | título sozinho, com rótulo em caixa alta quando precisa situar | nenhuma composição desenha barra sobre título |
| Caixa tingida com faixa colorida na lateral, repetida em todo slide | régua fina e a frase de fecho, sem caixa | a composição `destaque` |
| Lista longa de marcadores | no máximo quatro por bloco; o resto vira outro slide | erro nas composições |
| Título de efeito ("Revolucionando o futuro") | título que diz o fato do slide | revisão |
| Emoji e ícone genérico como decoração | ícone só quando informa, número quando ordena | revisão |
| Animação em tudo, voando e girando | só `fade` e `wipe`, de entrada, onde há ordem | só esses dois efeitos existem no kit |
| Número sem fonte | linha de fonte no rodapé de todo slide com dado | revisão |
| Texto sem acento ou em português de Portugal | português do Brasil, acentuação conferida | aviso no `verificar_texto.py` |

O teste prático: se o slide pudesse estar em qualquer apresentação sobre
qualquer assunto, ele é genérico demais. Cada slide precisa dizer uma coisa
que só aquela apresentação diz.

---

## 5. Elementos recorrentes

```
┌──────────────────────────────────────────────────────┐
│  KICKER EM CAIXA ALTA                                │
│                                                       │
│  Título direto,                                       │
│  em duas linhas                                       │
│                                                       │
│  Uma linha de apoio explicando o contexto.            │
│                                                       │
│  •  marcador                                          │
│  •  marcador                                          │
│  •  marcador                                          │
│  ─────────────                                        │
│  Frase de fecho em turquesa                     01   │
└──────────────────────────────────────────────────────┘
```

- **Kicker** em caixa alta antes do título, dizendo de que bloco o slide faz
  parte. Ajuda quem chegou atrasado a se localizar.
- **Linha de apoio** abaixo do título, uma frase, nunca duas.
- **Marcadores** com ponto turquesa, no máximo quatro por bloco. Um slide de
  comparação tem dois blocos, então pode ter quatro de cada lado.
- **Frase de fecho** em turquesa no rodapé, com a ideia que o slide quer
  deixar. É a frase que a pessoa leva, mesmo que esqueça o resto.
- **Número de página** discreto no canto inferior direito. Ausente em capa,
  provocação e encerramento.

---

## 6. Tratamento de foto

Foto entra por `base.foto()`, que recorta no formato pedido, escurece e aplica
sombra.

```python
base.foto("capa.jpg", 2400, 1350, escurecer=0.55, gradiente=0.7)
```

- `escurecer` entre 0,3 e 0,9. Abaixo de 0,5 a foto vira textura de fundo,
  acima de 0,8 ela compete com o texto.
- `gradiente` cria sombra crescendo para a esquerda, onde costuma ficar o
  texto. Valor entre 0,5 e 0,9.
- `ancora` define o lado preservado no recorte: `centro`, `topo` ou `esquerda`.

Regra prática: se o texto branco ficar difícil de ler em tela compartilhada,
escureça mais. O compartilhamento de tela come contraste.

---

## 7. Animação

Dois efeitos no repositório inteiro: `fade` e `wipe`. Só entrada, nunca saída.
Sem giro, salto, trajetória ou efeito de entrada diferente por slide.

A disciplina é o que faz parecer caro. Variedade de efeitos faz parecer
apresentação de 2005.

Tudo dispara sozinho na abertura do slide, com gatilho `withEffect`. Quem
apresenta não pode depender de clique extra, ainda mais em evento online, com o
chat aberto ao lado.

**Animar estrutura, não decoração.** A animação precisa carregar significado:

| Conteúdo | Animação |
|---|---|
| Fluxo de processo | cascata da esquerda para a direita |
| Tabela comparativa | linha por linha, nunca célula por célula |
| Progressão ou maturidade | degrau por degrau, com wipe de baixo para cima |
| Linha do tempo | barra preenchendo, marcos entrando na passagem |
| Lista de argumentos | um por vez, com intervalo maior |
| Capa | nada. Capa que anima passa insegurança |
| Slide final | nada. O último slide fica parado durante as perguntas |
| Slide com vídeo | não animar o vídeo. O texto ao redor pode entrar enquanto ele roda, e costuma ficar melhor assim |

Tempos: 500 ms por elemento, 150 a 400 ms de intervalo. Um slide inteiro
raramente passa de 3 segundos de coreografia.

---

## 8. Transição

Fade por preto em todos os slides. O crossfade direto produz estouro de branco
quando o deck alterna fundo preto e fundo claro.

Morph apenas quando dois slides seguidos compartilham a mesma estrutura, por
exemplo um diagrama reapresentado com outro destaque. Nesse caso as formas se
movem em vez de trocar de slide, e a plateia entende que é o mesmo diagrama
sendo relido.

O kit grava o fade como reserva dentro do arquivo, então um PowerPoint sem
suporte a Morph cai no fade em vez de quebrar.

```python
from kit.transicoes import aplicar_em_todos
aplicar_em_todos(prs, morph_em=(6,))   # Morph ao entrar no slide 6
```

---

## 9. Vídeo

- 15 a 25 segundos, nunca mais.
- Sem áudio.
- 1280 de largura, 15 quadros por segundo, crf 26.
- Início automático, repetição até o slide mudar.
- O primeiro quadro serve de capa e de reserva se a reprodução falhar.

Se o clipe precisa terminar em um estado específico, como um contador que para
em um número, use o último quadro como capa. Assim o estado parado é o final, e
o número não volta a zero quando o vídeo encerra.

```python
from kit.clipes import cortar, primeiro_quadro, ultimo_quadro
cortar("bruto.mp4", "video/clipe.mp4", inicio=135, duracao=23)
```

---

## 9b. Perfis de legibilidade

O mesmo padrão serve a três situações diferentes, e o que muda é a densidade,
não a identidade. Escolha o perfil antes de começar a escrever o conteúdo.

| Perfil | Situação | Corpo mínimo | Densidade |
|---|---|---:|---|
| Ao vivo | apresentado por alguém, presencial ou online | 12 pontos | poucas palavras por slide, o detalhe vai para a fala |
| Leitura | enviado para a pessoa ler sozinha | 11 pontos | mais explicação, porque não há quem explique |
| Anexo técnico | tabela e diagrama de consulta, no fim do deck | 10 pontos | pode ser denso, porque é consultado, não apresentado |

Em apresentação online, suba um ponto em tudo: o compartilhamento de tela come
detalhe e contraste.

O validador avisa a partir de 9,5 pontos, que é o piso absoluto. Ficar no piso
é sinal de que o slide tem conteúdo demais, e a saída certa é dividir o slide,
não reduzir a fonte.

---

## 10. Escrita

Obrigatório, verificado na geração e na validação.

### 10.1 Nenhum travessão

Proibido travessão, meia-risca, barra horizontal e sinal de menos tipográfico,
em qualquer texto do material: título, rótulo, legenda, tabela, nota do
apresentador e nome de arquivo. Também é proibida a sequência de dois hifens
cercada por espaços, que é o mesmo recurso disfarçado.

A regra vale nos dois momentos. Na geração, `kit.base.texto` recusa o texto e
levanta erro: não existe caminho que produza um slide com travessão. Na
validação, `scripts/validar_deck.py` acusa como erro, o que cobre arquivos
editados na mão fora do kit.

No lugar: dois pontos, vírgula, parênteses ou ponto final. Para intervalo de
tempo, `a` ou `até`, como em `2013 a 2015`. Para número negativo, o hífen
comum.

### 10.2 Acentuação e português do Brasil

Todo texto sai em português do Brasil, com acentuação completa. Slide não é
código: `padrao`, `tecnico` e `apresentacao` são erro, não simplificação.

`kit/editorial.py` mantém uma lista de grafias inequívocas e aponta cada
ocorrência com a correção já na caixa certa, `Apresentacao` vira
`Apresentação` e `PADRAO` vira `PADRÃO`. A lista é propositalmente curta e só
contém palavras sem ambiguidade. Palavra ambígua não é apontada nem trocada:
isso continua sendo revisão humana.

O verificador ignora o que não é prosa, ou seja, URL, endereço de e-mail,
caminho de arquivo, identificador com sublinhado ou ponto, e trecho entre
crases. Escrever `build.py` ou `kit.base` num slide não vira alerta.

Todo texto gerado também recebe o idioma `pt-BR` no XML, incluindo as notas do
apresentador. Sem isso, o corretor do PowerPoint sublinha o material inteiro
como se fosse inglês na máquina de quem abrir.

### 10.3 Demais convenções

- Título de slide é frase direta, não frase de efeito comercial.
- Número por extenso quando for medida, algarismo quando for dado.
- Nome próprio sempre na mesma grafia, do primeiro ao último slide.

O validador em `scripts/validar_deck.py` acusa travessão no texto dos slides.

---

## 11. Números estratégicos que sobem

O número que carrega o argumento do slide pode entrar contando, de zero até o
valor. O PowerPoint não anima o valor de um texto; o kit gera um clipe curto
com o fundo, a fonte, o corpo e a cor do texto, e põe no lugar exato dele.

```python
from kit.numeros import inteiro, porcentagem, numero_que_sobe, tocar_junto

n = numero_que_sobe(s, AQUI / "video" / "familias.mp4", x, y, 3.0, 0.95,
                    ate=86, formatar=inteiro, corpo=48,
                    cor=T.VERDE_2, fundo=T.CARTOES[0][0])
anima(s, [(0, [titulo]), (500, [n])])
tocar_junto(s, [(n, 500)])      # sempre depois do anima
```

Regras:

- só quando quem pede quer destacar números estratégicos; não é padrão de
  todo número;
- no máximo três por slide, senão vira enfeite;
- `fundo` é a cor exata do que está atrás do número, cartão ou slide;
- parado ou em PDF, o slide mostra o valor final, nunca zero.

Número que vem de uma fonte entra com a linha de fonte do slide (`fonte(s,
...)`). Número digitado sem procedência não entra.
