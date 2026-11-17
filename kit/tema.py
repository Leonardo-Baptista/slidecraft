# -*- coding: utf-8 -*-
"""Tema `escuro`: fonte e paleta dentro do proprio arquivo.

O gerador pinta cada objeto com a cor e a fonte certas, mas isso não alcanca o
tema interno do arquivo. Sem tratar o tema, qualquer caixa de texto criada na
mao depois nasce em Calibri, e a paleta oferecida pelo PowerPoint continua
sendo a padrão do Office.

Este modulo reescreve o tema para Montserrat e para as cores da identidade
`escuro`.

    from kit.tema import nova_apresentacao
    prs = nova_apresentacao()
"""
import re
from lxml import etree

from pptx import Presentation
from pptx.util import Inches

from kit.base import A, L
from kit.politica import configurar

FONTE = "Montserrat"

# A ordem importa: e a que o PowerPoint mostra na paleta do tema.
CORES = {
    "dk1": "000000",   # texto escuro
    "lt1": "FFFFFF",   # fundo claro
    "dk2": "0D0D0D",   # quase preto
    "lt2": "F7F7F6",   # fundo claro alternativo
    "accent1": "00E5C0",  # turquesa, o acento
    "accent2": "00846F",  # verde escuro
    "accent3": "54C1AF",  # verde claro
    "accent4": "9D9D9C",  # cinza
    "accent5": "575756",  # cinza escuro
    "accent6": "E6E6E6",  # cinza claro
    "hlink": "00E5C0",
    "folHlink": "00846F",
}


def _parte_do_tema(prs):
    for rel in prs.part.package.iter_parts():
        if "theme" in str(rel.partname) and str(rel.partname).endswith(".xml"):
            return rel
    return None


def aplicar_tema(prs, fonte=FONTE, cores=None):
    """Troca fonte e paleta do tema interno da apresentação."""
    cores = cores or CORES
    parte = _parte_do_tema(prs)
    if parte is None:
        return prs

    ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
    root = etree.fromstring(parte.blob)
    for node in root.xpath(".//a:majorFont/a:latin | .//a:minorFont/a:latin", namespaces=ns):
        node.set("typeface", fonte)
    for nome, valor in cores.items():
        node = root.find(".//a:clrScheme/a:" + nome, ns)
        if node is not None:
            for child in list(node):
                node.remove(child)
            etree.SubElement(node, "{%s}srgbClr" % ns["a"]).set("val", valor)
    parte._blob = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
    # Os padrões de texto também participam da edição manual no PowerPoint.
    for node in prs._element.xpath(".//a:defRPr"):
        node.set("lang", "pt-BR")
    for master in prs.slide_masters:
        for node in master._element.xpath(".//a:defRPr"):
            node.set("lang", "pt-BR")
    return prs


def nova_apresentacao(fonte=FONTE, perfil="referencia", divulgacao="interno"):
    """Apresentação em branco, 16:9, ja com o tema `escuro`."""
    prs = Presentation()
    prs.slide_width, prs.slide_height = L, A
    return configurar(aplicar_tema(prs, fonte=fonte), perfil, divulgacao)


def conferir(caminho):
    """Le um .pptx e devolve as fontes declaradas no tema. Util em teste."""
    import zipfile
    z = zipfile.ZipFile(str(caminho))
    tema = [n for n in z.namelist() if "theme" in n and n.endswith(".xml")][0]
    xml = z.read(tema).decode("utf-8")
    achados = {}
    for tag in ("majorFont", "minorFont"):
        m = re.search(tag + r">.*?typeface=\"([^\"]*)\"", xml, re.S)
        achados[tag] = m.group(1) if m else None
    m = re.search(r"<a:accent1>\s*<a:srgbClr val=\"([0-9A-Fa-f]{6})\"", xml)
    achados["accent1"] = m.group(1) if m else None
    return achados
