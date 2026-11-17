# -*- coding: utf-8 -*-
"""Transição entre slides: fade por preto em todo o deck, Morph onde couber.

O fade por preto e o padrão do kit. Ele evita o estouro de branco que o
crossfade direto produz quando o deck alterna slides pretos e claros.

O Morph vale quando dois slides seguidos compartilham a mesma estrutura, por
exemplo um diagrama que e reapresentado com outro destaque: em vez de trocar de
slide, as formas se movem. Precisa de PowerPoint 2019 ou 365, por isso o fade
fica gravado como reserva dentro do proprio arquivo.
"""
from lxml import etree

from kit.animacao import q

NS_MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"
NS_P14 = "http://schemas.microsoft.com/office/powerpoint/2010/main"
NS_P159 = "http://schemas.microsoft.com/office/powerpoint/2015/09/main"


def _limpa(sld):
    for antigo in sld.findall(q("transition")):
        sld.remove(antigo)
    for antigo in sld.findall("{%s}AlternateContent" % NS_MC):
        sld.remove(antigo)


def aplicar_fade(slide, atraves_do_preto=True, velocidade="med"):
    """Transição em fade. Respeita a ordem dos filhos de p:sld."""
    sld = slide._element
    _limpa(sld)
    trans = etree.SubElement(sld, q("transition"))
    trans.set("spd", velocidade)
    trans.set("advClick", "1")
    fade = etree.SubElement(trans, q("fade"))
    if atraves_do_preto:
        fade.set("thruBlk", "1")
    timing = sld.find(q("timing"))
    if timing is not None:
        sld.remove(trans)
        timing.addprevious(trans)
    return trans


def aplicar_morph(slide, duracao_ms=1000):
    """Morph com fade por preto como reserva, para versoes sem suporte."""
    sld = slide._element
    _limpa(sld)

    alt = etree.SubElement(sld, "{%s}AlternateContent" % NS_MC,
                           nsmap={"mc": NS_MC})
    escolha = etree.SubElement(alt, "{%s}Choice" % NS_MC,
                               nsmap={"p14": NS_P14, "p159": NS_P159})
    escolha.set("Requires", "p159")
    t1 = etree.SubElement(escolha, q("transition"))
    t1.set("spd", "slow")
    t1.set("{%s}dur" % NS_P14, str(duracao_ms))
    t1.set("advClick", "1")
    etree.SubElement(t1, "{%s}morph" % NS_P159).set("option", "byObject")

    reserva = etree.SubElement(alt, "{%s}Fallback" % NS_MC)
    t2 = etree.SubElement(reserva, q("transition"))
    t2.set("spd", "med")
    t2.set("advClick", "1")
    etree.SubElement(t2, q("fade")).set("thruBlk", "1")
    return alt


def aplicar_em_todos(prs, morph_em=()):
    """Fade em todos os slides, Morph nos indices listados, base 1."""
    for i, slide in enumerate(prs.slides, start=1):
        if i in morph_em:
            aplicar_morph(slide)
        else:
            aplicar_fade(slide)
    return len(prs.slides._sldIdLst)
