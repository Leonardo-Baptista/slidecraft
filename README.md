# slidecraft

Apresentações PowerPoint bem padronizadas, geradas por um agente de IA dentro
do seu editor.

Você abre este repositório no VS Code, Cursor, Antigravity ou outro editor com
agente (Claude Code, Codex, Gemini, Copilot), descreve a apresentação e o
agente faz o resto: cria o ambiente Python, pergunta o que falta, monta os
slides em código e entrega um `.pptx` editável, com o mesmo acabamento em
todos os slides.

O padrão não fica na cabeça de quem diagrama: fica em código. Paleta,
tipografia, posição de cada bloco, animação de entrada e transição já estão
resolvidas no kit.

---

## O que o kit entrega

| Recurso | Como aparece |
|---|---|
| Transição | fade por preto em todos os slides; Morph entre slides de mesma estrutura |
| Animação de entrada | automática, sem clique, só `fade` e `wipe`, na ordem do conteúdo |
| Números que sobem | o número estratégico entra contando de zero até o valor |
| Linha do tempo | a barra preenche e cada marco aparece quando ela passa |
| Imagens | encaixadas em moldura, sem deformar |
| GIFs gerados em Python | gráficos e processos animados, desenhados com Pillow |
| Vídeo | clipe curto, sem áudio, tocando sozinho em loop |
| Notas do apresentador | o roteiro de fala dentro de cada slide |
| Validação | um script confere paleta, fonte, margem, colisão de texto e transição |
| Escrita | português do Brasil, acentuação conferida, nenhum travessão |

O modelo padrão é o **modelo de apresentação do IFES**, público. Há também a
identidade `escuro` (fundo preto, acento turquesa, foto em tela cheia).

---

## Como usar com um agente de IA

1. Clone o repositório e abra a pasta no seu editor:
   ```
   git clone https://github.com/Leonardo-Baptista/slidecraft.git
   ```
2. No chat do agente, peça a apresentação. Por exemplo:
   > Crie uma apresentação sobre reciclagem de plástico para alunos do ensino
   > médio, 15 minutos. Siga o AGENTS.md.
3. O agente cria o ambiente virtual `.venv`, instala as dependências e faz as
   perguntas que faltam: quantos slides, texto da capa, quais imagens e vídeos
   usar e onde estão, quais números devem subir, se quer GIFs gerados em
   Python, se quer notas do apresentador.
4. Ele mostra o roteiro, slide por slide. Você aprova ou ajusta.
5. O arquivo sai em `saida/nome_do_deck.pptx`. Abra no PowerPoint e apresente
   (F5) para ver as animações.

Os agentes encontram o roteiro sozinhos: [AGENTS.md](AGENTS.md) é lido pelo
Codex, Cursor e Antigravity; [CLAUDE.md](CLAUDE.md), [GEMINI.md](GEMINI.md) e
[.github/copilot-instructions.md](.github/copilot-instructions.md) apontam para
ele.

---

## Veja funcionando antes

O deck de exemplo usa um tema inventado (uma horta comunitária, com números
fictícios) para mostrar cada recurso: capa, linha do tempo, números que sobem,
fluxo em cartões, imagem, GIF, vídeo, Morph e encerramento.

Windows:
```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe decks\exemplo\gera_ativos.py
.venv\Scripts\python.exe decks\exemplo\build.py
```

macOS e Linux:
```
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python decks/exemplo/gera_ativos.py
.venv/bin/python decks/exemplo/build.py
```

Abra `saida/exemplo.pptx`.

---

## Onde fica cada coisa

```
slidecraft/
├── AGENTS.md            roteiro do agente: ambiente, perguntas, geração, regras
├── kit/                 o sistema visual (não muda de deck para deck)
│   ├── tema_ifes.py         paleta, fontes e grade do modelo IFES
│   ├── layouts_ifes.py      cabeçalho, cartão, chip, destaque, fonte, imagem
│   ├── layouts.py           sete composições prontas da identidade escuro
│   ├── numeros.py           número que sobe de zero até o valor
│   ├── animacao.py          animação de entrada, escrita no XML
│   ├── transicoes.py        fade por preto e Morph
│   ├── slides.py            vídeo com início automático e loop
│   └── clipes.py            corte de vídeo e clipes gerados em código
├── decks/
│   ├── _modelo/             ponto de partida de todo deck novo (IFES)
│   ├── exemplo/             um slide de cada recurso, tema fictício
│   └── demonstracao/        catálogo da identidade escuro
├── scripts/
│   ├── novo_deck.py         cria decks/<nome> a partir do modelo
│   ├── produzir.py          gera, valida e exporta a folha de contato
│   ├── validar_deck.py      confere se o .pptx está no padrão
│   └── exportar_slides.py   slides em PNG (Windows com PowerPoint)
├── docs/                padrão visual, armadilhas conhecidas, validação
└── saida/               os .pptx gerados (fora do Git)
```

Cada apresentação é uma pasta em `decks/`:

```
decks/minha_palestra/
├── assets/          suas imagens, GIFs e vídeos (fora do Git)
├── gera_ativos.py   opcional: GIFs e clipes gerados em Python
└── build.py         os slides, um por função
```

---

## Sem agente, na mão

```
python scripts/novo_deck.py minha_palestra      (use o Python do .venv)
```

Ponha as imagens em `decks/minha_palestra/assets/`, edite
`decks/minha_palestra/build.py` copiando os slides de `decks/exemplo/build.py`
e rode:

```
python scripts/produzir.py minha_palestra
```

---

## Requisitos

- Python 3.10 ou mais novo. O ffmpeg vem dentro do ambiente virtual, pelo
  pacote `imageio-ffmpeg`; não precisa instalar.
- PowerPoint (Windows ou macOS) para apresentar. Morph pede PowerPoint 2019 ou
  365; nas versões antigas, vira fade.
- A exportação dos slides em imagem para conferência usa a automação do
  PowerPoint e só roda no Windows. Nos outros sistemas, o resto funciona e a
  conferência visual é abrindo o arquivo.

Para mexer no kit:

```
python -m pip install -r requirements-dev.txt
python -m pytest testes -q
```

---

## Autor

Leonardo Baptista.

## Licença

Código sob a licença MIT, em [LICENSE](LICENSE). Os fundos em
`kit/assets/ifes/` reproduzem o modelo institucional de apresentação do
Instituto Federal do Espírito Santo, de uso público; a marca do IFES pertence
à instituição.
