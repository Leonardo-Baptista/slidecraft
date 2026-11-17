# -*- coding: utf-8 -*-
"""Agrupamento de formas para animar, e a barra de progresso de linha do tempo.

O vocabulario do kit e proposital: dois efeitos apenas, fade e wipe. Repetir os
mesmos dois em todo o deck e o que faz a apresentação parecer um sistema. Cada
efeito entra sozinho, sem depender de clique.

Uso tipico, quando as formas ja existem no slide:

    from kit.animacao import monta_timing
    from kit.coreografia import FADE, efeitos_por_coluna

    ef = efeitos_por_coluna(slide, (2.10, 5.20), 0.9, 1.97, [0, 150, 300])
    monta_timing(slide, ef)

Quando o slide esta sendo gerado, e mais simples guardar as formas conforme
elas sao criadas e montar a lista de efeitos direto. Veja `anima()` nos decks.
"""
from pptx.util import Inches, Pt

from kit.base import TURQUESA, retangulo

# (filtro, presetID, presetSubtype)
FADE = ("fade", 10, 0)
WIPE_ESQUERDA = ("wipe(left)", 22, 8)
WIPE_CIMA = ("wipe(up)", 22, 4)
WIPE_DIREITA = ("wipe(right)", 22, 2)


def pol(valor):
    """Converte EMU em polegadas."""
    return valor / 914400.0


def coluna(forma, origem, passo, conector=False):
    bruto = (pol(forma.left) - origem) / passo
    return int(bruto) if conector else int(round(bruto))


def efeitos_por_coluna(slide, faixa, origem, passo, atrasos, tipo=FADE,
                       duracao=500):
    """Agrupa as formas de uma faixa horizontal em colunas.

    faixa: (topo, base) em polegadas, delimitando a area a animar.
    origem, passo: posicao da primeira coluna e distancia entre colunas.
    atrasos: um atraso em milissegundos por coluna.
    """
    topo, base = faixa
    saida = []
    for sh in slide.shapes:
        t = pol(sh.top)
        if not (topo <= t < base):
            continue
        conector = pol(sh.width) < 0.15 and pol(sh.height) < 0.05
        c = max(0, min(len(atrasos) - 1, coluna(sh, origem, passo, conector)))
        filtro, preset, sub = tipo
        saida.append((sh.shape_id, filtro, duracao, atrasos[c], preset, sub))
    return saida


def efeitos_por_faixa(slide, faixas, tipo=FADE, duracao=500):
    """Agrupa por faixas horizontais. faixas: lista de (topo, base, atraso)."""
    saida = []
    for topo, base, atraso in faixas:
        for sh in slide.shapes:
            if topo <= pol(sh.top) < base:
                filtro, preset, sub = tipo
                saida.append((sh.shape_id, filtro, duracao, atraso, preset, sub))
    return saida


def efeitos_de_formas(grupos, tipo=FADE, duracao=500):
    """Monta a lista de efeitos a partir de formas guardadas na geração.

    grupos: lista de (atraso_ms, [formas ou listas de formas]).
    """
    filtro, preset, sub = tipo
    efeitos = []
    for atraso, formas in grupos:
        for f in formas:
            for g in (f if isinstance(f, (list, tuple)) else [f]):
                efeitos.append((g.shape_id, filtro, duracao, atraso, preset, sub))
    return efeitos


def barra_de_progresso(slide, y, x_inicio, x_fim, nome="barra_progresso",
                       cor=TURQUESA, espessura=Pt(4.5)):
    """Barra que preenche uma linha do tempo, para animar com wipe(left).

    Fica logo atras dos marcadores, para os pontos continuarem por cima.
    """
    barra = retangulo(slide, Inches(x_inicio), Inches(y),
                      Inches(x_fim - x_inicio), espessura, cor)
    barra.name = nome
    for sh in slide.shapes:
        if abs(pol(sh.top) - (y + 0.02)) < 0.06 and pol(sh.width) > 11:
            arvore = barra._element.getparent()
            arvore.remove(barra._element)
            sh._element.addnext(barra._element)
            break
    return barra


def marcos_na_passagem(barra, posicoes, duracao_barra):
    """Atraso de cada marco, calculado pelo instante em que a barra o alcanca.

    posicoes: lista de x, em polegadas, do centro de cada marco.
    Devolve a lista de atrasos em milissegundos.
    """
    inicio = pol(barra.left)
    extensao = pol(barra.width)
    atrasos = []
    for x in posicoes:
        fracao = min(1.0, max(0.0, (x - inicio) / extensao))
        atrasos.append(int(duracao_barra * fracao))
    return atrasos
