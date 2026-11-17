# Como contribuir

Obrigado pelo interesse. Este repositório tem uma branch só, a `main`, e ela
é protegida: toda mudança entra por pull request e precisa da aprovação do
mantenedor, Leonardo Baptista, antes de ir para a `main`.

## Passo a passo

1. Faça um fork do repositório no GitHub.
2. Crie uma branch a partir da `main`, com nome que diga o assunto:
   ```
   git checkout -b linha-do-tempo-vertical
   ```
3. Faça a mudança. Se mexer no `kit/`, inclua ou ajuste um teste em
   `testes/test_kit.py`.
4. Rode as conferências antes de enviar:
   ```
   python -m pip install -r requirements-dev.txt
   python scripts/verificar_texto.py
   python -m pytest testes -q
   python scripts/produzir.py --sem-imagens
   ```
5. Abra o pull request para a `main` explicando o que mudou e por quê. Se a
   mudança for visual, anexe a folha de contato de antes e de depois.
6. Os testes rodam sozinhos no GitHub. Com eles passando, o mantenedor revisa
   e aprova, pede ajustes ou recusa.

## O que costuma ser aceito

- Correção de defeito, com o teste que teria pegado o defeito.
- Recurso novo que sirva a vários decks, não a um só.
- Melhoria no `AGENTS.md` que faça os agentes errarem menos.
- Documentação mais clara.

## O que não entra

- Mudança no kit para resolver um deck específico: isso fica no `build.py`
  do deck.
- Apresentações prontas, fotos, vídeos ou qualquer material de terceiros. O
  `.gitignore` bloqueia `saida/` e `decks/*/assets/`, mas a responsabilidade
  é de quem envia.
- Dados de empresa, cliente ou pessoa.

## Convenções

- Português do Brasil em código, comentários, documentação e mensagens de
  commit, com acentuação correta.
- Nenhum travessão nem meia-risca em lugar nenhum: use dois pontos, vírgula
  ou parênteses. `scripts/verificar_texto.py` cobra isso.
- Comentário explica o porquê, não o quê.
- Uma função por slide nos decks, nomeada `sNN_assunto`.
