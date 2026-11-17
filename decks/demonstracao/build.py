# -*- coding: utf-8 -*-
"""Catalogo das composições do kit, em forma de apresentação.

Cada slide usa uma composição diferente de `kit.layouts`, com conteúdo
inventado. Serve para tres coisas: ver o padrão funcionando, testar o kit
depois de qualquer mudanca, e treinar quem esta chegando.

Roda numa copia limpa do repositorio: as imagens sao geradas em codigo por
gera_ativos.py, sem foto de terceiros e sem arquivo de licenca.

    .venv/Scripts/python.exe decks/demonstracao/gera_ativos.py
    .venv/Scripts/python.exe decks/demonstracao/build.py
"""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(RAIZ))

from kit import base  # noqa: E402

base.ASSETS = AQUI / "assets"
base.CACHE = AQUI / "cache"
base.CACHE.mkdir(exist_ok=True)

from kit.layouts import (capa, comparacao, faixa_de_etapas,  # noqa: E402
                         fechamento, linha_do_tempo, provocacao,
                         texto_com_foto)
from kit.tema import nova_apresentacao  # noqa: E402
from kit.transicoes import aplicar_em_todos  # noqa: E402

SAIDA = RAIZ / "saida" / "demonstracao.pptx"


def main():
    if not (AQUI / "assets" / "capa_demo.jpg").exists():
        print("ativos ausentes. rode antes:")
        print("  .venv/Scripts/python.exe decks/demonstracao/gera_ativos.py")
        return 1

    prs = nova_apresentacao()

    capa(prs, "Catálogo de composições",
         "As sete composições do kit, em uma apresentação",
         foto="capa_demo.jpg",
         rodape="slidecraft  |  catálogo da identidade escuro")

    texto_com_foto(
        prs, 2, "Texto com foto,\na composição mais usada",
        ["Painel de texto à esquerda, imagem à direita",
         "Até quatro marcadores, entrando um a um",
         "A frase de fecho fica em turquesa, no rodapé",
         "Trocando foto por vídeo, o clipe entra no lugar"],
        secao="Composição 2: texto com foto",
        apoio="Serve para apresentar um problema, um produto ou um conceito "
              "que precisa de imagem ao lado.",
        foto="painel_demo.jpg",
        fecho="Uma ideia por slide, e a frase que resume no rodapé.")

    comparacao(
        prs, 3, "Comparação em duas colunas",
        ("Coluna neutra", ["Fundo claro, texto escuro",
                           "Para o lado conhecido",
                           "Ponto turquesa nos marcadores"]),
        ("Coluna em destaque", ["Fundo verde escuro",
                                "Para o lado que interessa",
                                "Ponto branco, por contraste"]),
        apoio="Fundo claro, servindo de respiro depois de dois slides pretos.",
        fecho="O fecho da comparação fica embaixo, em uma frase só.")

    faixa_de_etapas(
        prs, 4, "Faixa de etapas, para fluxo de processo",
        [("Entrada", "O que chega\nno processo"),
         ("Transformação", "O que acontece\ncom o material"),
         ("Medição", "O que o sistema\nobserva"),
         ("Decisão", "O que a operação\nrecebe"),
         ("Registro", "O que fica\npara depois")],
        apoio="As etapas entram da esquerda para a direita, acompanhando o "
              "sentido do processo.",
        destaques=(2, 3),
        fecho="A animação carrega o significado: o material atravessando.")

    faixa_de_etapas(
        prs, 5, "A mesma faixa, em escada",
        [("PoC", "É tecnicamente\npossível?"),
         ("Piloto", "Funciona no\nprocesso real?"),
         ("Industrialização", "Opera com\nconfiabilidade?"),
         ("Rollout", "Replica e\nse sustenta?")],
        apoio="Com escada, os blocos crescem e entram de baixo para cima.",
        escada=True,
        fecho="A pergunta muda a cada degrau. O custo de errar também.")

    linha_do_tempo(
        prs, 6, "Linha do tempo com barra\nque se preenche",
        [("2021", "O primeiro marco\nda sequência"),
         ("2023", "Um marco no meio\ndo caminho"),
         ("2025", "Outro marco,\nmais recente"),
         ("2026", "O marco atual,\nem destaque")],
        secao="Composição 6",
        apoio="Cada marco aparece no instante em que a barra passa por ele.")

    provocacao(prs, "Uma pergunta que vira\no bloco da apresentação.",
               destaque="95%",
               chamada="Responda no chat: sim ou não.")

    fechamento(prs, "A frase final, que resume\no argumento inteiro.",
               contato="contato@exemplo.org",
               complemento="exemplo.org",
               foto="fechamento_demo.jpg")

    aplicar_em_todos(prs)
    SAIDA.parent.mkdir(exist_ok=True)
    prs.save(str(SAIDA))
    print("gerado:", SAIDA, "|", len(prs.slides._sldIdLst),
          "slides, um por composição")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
