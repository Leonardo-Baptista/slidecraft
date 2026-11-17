# -*- coding: utf-8 -*-
"""Arvore de tempo do PowerPoint: animação de entrada escrita direto no XML.

A automacao do PowerPoint mapeia os identificadores de efeito de forma diferente
da numeracao do OOXML, e o resultado sai errado. Montar o XML aqui e previsivel:
quem manda na reprodução e o atributo filter de cada p:animEffect.
"""
from lxml import etree



NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
DURACAO_BARRA = 2200  # milissegundos


def q(tag):
    return "{%s}%s" % (NS_P, tag)


class Contador:
    """Os ids da arvore de tempo precisam ser unicos e crescentes."""

    def __init__(self, inicio=1):
        self.valor = inicio

    def proximo(self):
        self.valor += 1
        return self.valor


def efeito(pai, cont, spid, filtro, duracao, atraso, preset, subtipo=0):
    par = etree.SubElement(pai, q("par"))
    ctn = etree.SubElement(par, q("cTn"))
    ctn.set("id", str(cont.proximo()))
    ctn.set("presetID", str(preset))
    ctn.set("presetClass", "entr")
    ctn.set("presetSubtype", str(subtipo))
    ctn.set("fill", "hold")
    ctn.set("grpId", "0")
    ctn.set("nodeType", "withEffect")
    st = etree.SubElement(ctn, q("stCondLst"))
    etree.SubElement(st, q("cond")).set("delay", str(int(atraso)))
    filhos = etree.SubElement(ctn, q("childTnLst"))

    # torna a forma visivel no inicio do efeito
    conj = etree.SubElement(filhos, q("set"))
    cb = etree.SubElement(conj, q("cBhvr"))
    c1 = etree.SubElement(cb, q("cTn"))
    c1.set("id", str(cont.proximo()))
    c1.set("dur", "1")
    c1.set("fill", "hold")
    st1 = etree.SubElement(c1, q("stCondLst"))
    etree.SubElement(st1, q("cond")).set("delay", "0")
    tg = etree.SubElement(cb, q("tgtEl"))
    etree.SubElement(tg, q("spTgt")).set("spid", str(spid))
    an = etree.SubElement(cb, q("attrNameLst"))
    etree.SubElement(an, q("attrName")).text = "style.visibility"
    to = etree.SubElement(conj, q("to"))
    etree.SubElement(to, q("strVal")).set("val", "visible")

    # o efeito propriamente dito
    ae = etree.SubElement(filhos, q("animEffect"))
    ae.set("transition", "in")
    ae.set("filter", filtro)
    cb2 = etree.SubElement(ae, q("cBhvr"))
    c2 = etree.SubElement(cb2, q("cTn"))
    c2.set("id", str(cont.proximo()))
    c2.set("dur", str(int(duracao)))
    tg2 = etree.SubElement(cb2, q("tgtEl"))
    etree.SubElement(tg2, q("spTgt")).set("spid", str(spid))


def monta_timing(slide, efeitos):
    """efeitos: lista de (spid, filtro, duracao_ms, atraso_ms, preset, subtipo)."""
    sld = slide._element
    for antigo in sld.findall(q("timing")):
        sld.remove(antigo)

    cont = Contador()
    timing = etree.Element(q("timing"))
    tnlst = etree.SubElement(timing, q("tnLst"))
    par0 = etree.SubElement(tnlst, q("par"))
    raiz = etree.SubElement(par0, q("cTn"))
    raiz.set("id", "1")
    raiz.set("dur", "indefinite")
    raiz.set("restart", "never")
    raiz.set("nodeType", "tmRoot")
    filhos0 = etree.SubElement(raiz, q("childTnLst"))
    seq = etree.SubElement(filhos0, q("seq"))
    seq.set("concurrent", "1")
    seq.set("nextAc", "seek")
    ctn_seq = etree.SubElement(seq, q("cTn"))
    ctn_seq.set("id", str(cont.proximo()))
    ctn_seq.set("dur", "indefinite")
    ctn_seq.set("nodeType", "mainSeq")
    filhos_seq = etree.SubElement(ctn_seq, q("childTnLst"))

    par1 = etree.SubElement(filhos_seq, q("par"))
    ctn1 = etree.SubElement(par1, q("cTn"))
    ctn1.set("id", str(cont.proximo()))
    ctn1.set("fill", "hold")
    st1 = etree.SubElement(ctn1, q("stCondLst"))
    etree.SubElement(st1, q("cond")).set("delay", "indefinite")
    # dispara sozinho quando o slide entra
    cond_inicio = etree.SubElement(st1, q("cond"))
    cond_inicio.set("evt", "onBegin")
    cond_inicio.set("delay", "0")
    etree.SubElement(cond_inicio, q("tn")).set("val", "2")
    filhos1 = etree.SubElement(ctn1, q("childTnLst"))

    par2 = etree.SubElement(filhos1, q("par"))
    ctn2 = etree.SubElement(par2, q("cTn"))
    ctn2.set("id", str(cont.proximo()))
    ctn2.set("fill", "hold")
    st2 = etree.SubElement(ctn2, q("stCondLst"))
    etree.SubElement(st2, q("cond")).set("delay", "0")
    filhos2 = etree.SubElement(ctn2, q("childTnLst"))

    for spid, filtro, dur, atraso, preset, subtipo in efeitos:
        efeito(filhos2, cont, spid, filtro, dur, atraso, preset, subtipo)

    for nome, evento in (("prevCondLst", "onPrev"), ("nextCondLst", "onNext")):
        lst = etree.SubElement(seq, q(nome))
        cond = etree.SubElement(lst, q("cond"))
        cond.set("evt", evento)
        cond.set("delay", "0")
        tg = etree.SubElement(cond, q("tgtEl"))
        etree.SubElement(tg, q("sldTgt"))

    # ordem valida: cSld, clrMapOvr, transition, timing
    sld.append(timing)
    return len(efeitos)


def por_nome(slide):
    return {sh.name: sh for sh in slide.shapes}
