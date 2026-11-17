# -*- coding: utf-8 -*-
"""Helpers de slide: criacao, animação e video.

Antes cada deck redefinia `novo`, `anima`, `poster` e `liga_video`. Interfaces
parecidas, implementacoes levemente diferentes, e nenhuma garantia de que um
ajuste em um deck chegasse ao outro. Agora moram aqui.

    from kit.slides import novo, anima, inserir_video
"""
from pathlib import Path

from pptx.enum.text import PP_ALIGN
from pptx.util import Inches

from kit import base
from kit.animacao import monta_timing, q
from kit.base import (A, CINZA, CINZA_ESCURO, L, PRETO, QUASE_PRETO, fundo,
                      texto)
from kit.politica import papel
from kit.coreografia import FADE, efeitos_de_formas


def novo(prs, cor=PRETO, indice=None):
    """Slide em branco, com o numero de pagina discreto.

    Capa, provocacao e encerramento não levam numero: passe indice=None.
    """
    s = prs.slides.add_slide(prs.slide_layouts[6])
    fundo(s, cor)
    if indice is not None:
        # Mobiliario, não conteúdo: marcado para ficar fora da margem.
        papel(texto(s, L - Inches(1.1), A - Inches(0.62), Inches(0.5),
                    Inches(0.3), "%02d" % indice, 10,
                    CINZA if cor in (PRETO, QUASE_PRETO) else CINZA_ESCURO,
                    alinhamento=PP_ALIGN.RIGHT), "numero")
    return s


def anima(slide, grupos, duracao=500, tipo=FADE):
    """Escreve a coreografia do slide.

    grupos: lista de (atraso em milissegundos, [formas ou listas de formas]).
    """
    monta_timing(slide, efeitos_de_formas(grupos, tipo=tipo, duracao=duracao))


def poster(clipe, nome=None, pasta=None):
    """Primeiro quadro do clipe, para servir de capa e de reserva."""
    from kit.clipes import primeiro_quadro

    clipe = Path(clipe)
    destino = Path(pasta or base.CACHE) / ((nome or clipe.stem) + "_poster.jpg")
    if destino.exists():
        return str(destino)
    return str(primeiro_quadro(clipe, destino))


def inserir_video(slide, clipe, x, y, largura, altura, atraso=0, loop=True,
                  capa=None):
    """Insere o clipe e liga o inicio automatico e a repeticao.

    Chame depois de `anima`. `monta_timing` reescreve a arvore de tempo inteira
    e o no de midia criado pelo add_movie se perde se vier antes.
    """
    clipe = Path(clipe)
    filme = slide.shapes.add_movie(
        str(clipe), x, y, largura, altura,
        poster_frame_image=capa or poster(clipe), mime_type="video/mp4")
    _liga_video(slide, filme.shape_id, atraso=atraso, loop=loop)
    return filme


def _liga_video(slide, spid, atraso=0, loop=True):
    """Recoloca o comando de reprodução e a repeticao na arvore de tempo."""
    from lxml import etree

    sld = slide._element
    caminho = (".//p:seq//p:cTn[@nodeType='mainSeq']"
               "/p:childTnLst/p:par/p:cTn/p:childTnLst/p:par"
               "/p:cTn/p:childTnLst")

    timing = sld.find(q("timing"))
    # Slide sem animação nenhuma não tem sequência principal, e e ali que mora
    # o comando de tocar. Nesse caso, monta a estrutura vazia primeiro.
    if timing is None or not timing.xpath(caminho):
        monta_timing(slide, [])
        timing = sld.find(q("timing"))

    ids = [int(v) for v in timing.xpath(".//@id") if str(v).isdigit()]
    proximo = max(ids) + 1 if ids else 2
    alvos = timing.xpath(caminho)
    if alvos:
        par = etree.SubElement(alvos[0], q("par"))
        ctn = etree.SubElement(par, q("cTn"))
        ctn.set("id", str(proximo)); proximo += 1
        ctn.set("presetID", "1")
        ctn.set("presetClass", "mediacall")
        ctn.set("presetSubtype", "0")
        ctn.set("fill", "hold")
        ctn.set("nodeType", "withEffect")
        st = etree.SubElement(ctn, q("stCondLst"))
        etree.SubElement(st, q("cond")).set("delay", str(int(atraso)))
        filhos = etree.SubElement(ctn, q("childTnLst"))
        cmd = etree.SubElement(filhos, q("cmd"))
        cmd.set("type", "call")
        cmd.set("cmd", "playFrom(0.0)")
        cb = etree.SubElement(cmd, q("cBhvr"))
        c = etree.SubElement(cb, q("cTn"))
        c.set("id", str(proximo)); proximo += 1
        c.set("dur", "1")
        c.set("fill", "hold")
        tg = etree.SubElement(cb, q("tgtEl"))
        etree.SubElement(tg, q("spTgt")).set("spid", str(spid))

    raizes = timing.xpath("./p:tnLst/p:par/p:cTn/p:childTnLst")
    if raizes:
        video = etree.SubElement(raizes[0], q("video"))
        media = etree.SubElement(video, q("cMediaNode"))
        media.set("vol", "80000")
        c = etree.SubElement(media, q("cTn"))
        c.set("id", str(proximo))
        if loop:
            c.set("repeatCount", "indefinite")
        c.set("fill", "hold")
        c.set("display", "0")
        st = etree.SubElement(c, q("stCondLst"))
        etree.SubElement(st, q("cond")).set("delay", "indefinite")
        tg = etree.SubElement(media, q("tgtEl"))
        etree.SubElement(tg, q("spTgt")).set("spid", str(spid))
