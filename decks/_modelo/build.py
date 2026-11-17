# -*- coding: utf-8 -*-
"""Modelo de deck. Copie esta pasta para comecar uma apresentação nova.

    python scripts/novo_deck.py nome_do_deck

Identidade padrão: modelo IFES (`kit.tema_ifes` e `kit.layouts_ifes`). Para
ver cada recurso funcionando (linha do tempo, números que sobem, GIF, vídeo,
Morph), abra `decks/exemplo/build.py` e copie o slide que precisar.

Regras que valem para qualquer deck:

- um assunto por slide, e uma frase de fecho (`destaque`) que o resume;
- todo slide com dado leva a linha de fonte (`fonte`);
- animar estrutura, nunca decoração; capa e encerramento quase parados;
- nenhum travessão, meia-risca ou traço horizontal em texto de slide;
- imagens, GIFs e vídeos ficam em `assets/` desta pasta.
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

from kit import tema_ifes as T  # noqa: E402
from kit.animacao import monta_timing  # noqa: E402
from kit.coreografia import efeitos_de_formas  # noqa: E402
from kit.editorial import notas  # noqa: E402
from kit.layouts_ifes import (cabecalho, capa, cartao, corpo,  # noqa: E402
                              destaque, fonte, novo, numero, texto)
from kit.slides import anima  # noqa: E402
from kit.tema_ifes import nova_apresentacao_ifes  # noqa: E402
from kit.transicoes import aplicar_em_todos  # noqa: E402

NOME = "Modelo"
SAIDA = RAIZ / "saida" / "modelo.pptx"


def s01_capa(prs):
    s, _, titulo, linha2, assinatura = capa(
        prs, NOME, "Subtítulo em uma linha", "Nome  |  Instituição  ·  mês de ano")
    monta_timing(s, efeitos_de_formas([(0, [titulo]), (320, [linha2]),
                                       (560, [assinatura])], duracao=520))
    notas(s, "O que dizer na abertura.")


def s02_tres_cartoes(prs):
    s = novo(prs)
    t, sub = cabecalho(s, "Título direto", "Uma frase de apoio, dizendo o que olhar.")
    grupos = []
    for i, item in enumerate(("Primeiro ponto", "Segundo ponto",
                              "Terceiro ponto")):
        x = T.MARGEM + i * (T.COLUNA_3 + T.FOLGA)
        grupos.append((500 + i * 300, [
            cartao(s, x, 1.95, T.COLUNA_3, 2.2, i + 1),
            numero(s, x + 0.2, 2.15, str(i + 1)),
            corpo(s, x + 0.2, 2.8, T.COLUNA_3 - 0.4, 1.1, item)]))
    faixa = destaque(s, 4.8, "A frase que o slide quer deixar.")
    fonte(s, "Fonte: de onde vieram os dados deste slide.")
    anima(s, [(0, [t]), (240, [sub])] + grupos + [(1600, list(faixa))])
    notas(s, "O que dizer neste slide.")


def s03_encerramento(prs):
    s = novo(prs)
    t = texto(s, T.MARGEM, 2.3, T.UTIL, 1.0, "Obrigado!", 44, T.VERDE_2,
              negrito=True)
    c = texto(s, T.MARGEM, 3.5, T.UTIL, 0.5, "contato@exemplo.org", 18,
              T.TEXTO)
    anima(s, [(0, [t]), (400, [c])])


def main():
    prs = nova_apresentacao_ifes(perfil="ao_vivo", divulgacao="publico")
    prs.core_properties.title = NOME
    for construir in (s01_capa, s02_tres_cartoes, s03_encerramento):
        construir(prs)
    aplicar_em_todos(prs)
    SAIDA.parent.mkdir(exist_ok=True)
    prs.save(str(SAIDA))
    print("gerado:", SAIDA, "|", len(prs.slides._sldIdLst),
          "slides, com transição em fade")


if __name__ == "__main__":
    main()
