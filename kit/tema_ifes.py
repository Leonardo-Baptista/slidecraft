# -*- coding: utf-8 -*-
"""Tema IFES: a identidade visual do modelo público de apresentação do IFES.

É a identidade padrão dos decks novos. Paleta, tipografia e grade foram
medidas no modelo oficial: cores em hexadecimal, corpos de fonte, coordenadas
da grade e os dois fundos em PNG, em `kit/assets/ifes`. A maquinaria continua
sendo a mesma do kit: `kit.animacao`, `kit.coreografia` e `kit.transicoes` não
sabem de cor nenhuma e servem aos dois temas sem alteração.

    from kit.tema_ifes import nova_apresentacao_ifes
    prs = nova_apresentacao_ifes()
"""
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.util import Inches

from kit import medidas
from kit.politica import configurar

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "kit" / "assets" / "ifes"
FUNDO_CAPA = ASSETS / "fundo_capa.png"
FUNDO_CONTEUDO = ASSETS / "fundo_conteudo.png"

# --------------------------------------------------------------------- paleta
# Três níveis de verde. Eles não são decoração: o modelo usa o nível para
# ordenar cartões e etapas, do primeiro ao terceiro, sempre nessa sequência.
VERDE_1 = "0B3D2C"   # o mais escuro, primeiro nível
VERDE_2 = "1C7F5C"   # cor do título e do destaque, segundo nível
VERDE_3 = "31775C"   # terceiro nível
VERDE_4 = "3A8A6F"   # quarto nível, quando a composição precisa de mais um
VERDE_NEUTRO = "6B8479"   # etapa sem ênfase, por exemplo um período antigo

BRANCO = "FFFFFF"
TEXTO = "2B3A34"     # corpo de leitura
APOIO = "6B7A73"     # subtítulo, legenda e linha de fonte
SETA = "85918B"      # chevron entre blocos

# Fundos de cartão, do mais saturado ao mais neutro, e a borda de cada um.
# O modelo emparelha fundo e borda; separar os dois produz cartão sujo.
CARTOES = (
    ("DFEDE6", "B9D2C6"),
    ("E6F3EC", "C4DACF"),
    ("EDF5F1", "CEE0D7"),
    ("F2F5F3", "DCE3DF"),
)
LINHA_FINA = "D3DCD7"    # régua de cabeçalho de tabela

PALETA = frozenset(
    {VERDE_1, VERDE_2, VERDE_3, VERDE_4, VERDE_NEUTRO, BRANCO, TEXTO, APOIO,
     SETA, LINHA_FINA, "007826", "F1F8F4"}
    | {c for par in CARTOES for c in par})

# ----------------------------------------------------------------- tipografia
FONTE = "Arial"
# A capa do modelo do programa vem em Tahoma nas duas linhas abaixo do título.
# É herança do modelo institucional, não escolha deste kit, e fica porque a
# instrução é seguir o modelo do programa.
FONTE_CAPA = "Tahoma"
FONTE_MONO = "Consolas"

CORPO = {
    "titulo_capa": 54,
    "capa": 21.77,
    "titulo": 24,
    "subtitulo": 13.5,
    "cartao_titulo": 16,
    "destaque": 14.5,
    "etiqueta": 14,
    "texto": 12.5,
    "texto_menor": 12,
    "rotulo": 10.5,
    "chip": 10,
    "mono": 11,
    # O modelo do programa escreve a linha de fonte em 9 pontos. O kit não
    # desce de 9,5, que é o piso absoluto de legibilidade em `kit.politica`.
    # Meio ponto não muda a diagramação e mantém a regra do repositório.
    "fonte": 9.5,
}

# ---------------------------------------------------------------------- grade
# A faixa verde do fundo ocupa a esquerda do slide, e o conteúdo começa depois
# dela. Daí a margem assimétrica: 2,05 à esquerda, 0,78 à direita.
L, A = Inches(13.333), Inches(7.5)
MARGEM = 2.05
UTIL = 10.50
DIREITA = MARGEM + UTIL          # 12,55 polegadas
Y_TITULO = 0.52
Y_SUBTITULO = 0.98
Y_CONTEUDO = 1.45                # primeiro elemento abaixo do subtítulo
Y_FONTE = 7.03
ALTURA_TITULO = 0.48
ALTURA_SUBTITULO = 0.40
ALTURA_FONTE = 0.30

# Colunas do modelo: três blocos de 3,40 com folga de 0,15, ou dois de 5,10.
COLUNA_3 = 3.40
COLUNA_2 = 5.10
FOLGA = 0.15

CORES_DO_TEMA = {
    "dk1": TEXTO,
    "lt1": BRANCO,
    "dk2": VERDE_1,
    "lt2": CARTOES[1][0],
    "accent1": VERDE_2,
    "accent2": VERDE_1,
    "accent3": VERDE_3,
    "accent4": VERDE_4,
    "accent5": APOIO,
    "accent6": CARTOES[0][0],
    "hlink": VERDE_2,
    "folHlink": VERDE_1,
}


def _parte_do_tema(prs):
    for parte in prs.part.package.iter_parts():
        nome = str(parte.partname)
        if "theme" in nome and nome.endswith(".xml"):
            return parte
    return None


def aplicar_tema(prs, fonte=FONTE, cores=None):
    """Troca fonte e paleta do tema interno, como `kit.tema` faz para a marca.

    Sem isso, qualquer caixa criada à mão depois no PowerPoint nasce em Calibri
    e a paleta oferecida ao editor continua sendo a padrão do Office.
    """
    cores = cores or CORES_DO_TEMA
    parte = _parte_do_tema(prs)
    if parte is None:
        return prs

    ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
    raiz = etree.fromstring(parte.blob)
    for no in raiz.xpath(".//a:majorFont/a:latin | .//a:minorFont/a:latin",
                         namespaces=ns):
        no.set("typeface", fonte)
    for nome, valor in cores.items():
        no = raiz.find(".//a:clrScheme/a:" + nome, ns)
        if no is not None:
            for filho in list(no):
                no.remove(filho)
            etree.SubElement(no, "{%s}srgbClr" % ns["a"]).set("val", valor)
    parte._blob = etree.tostring(raiz, xml_declaration=True, encoding="UTF-8",
                                 standalone=True)
    for no in prs._element.xpath(".//a:defRPr"):
        no.set("lang", "pt-BR")
    for mestre in prs.slide_masters:
        for no in mestre._element.xpath(".//a:defRPr"):
            no.set("lang", "pt-BR")
    return prs


def nova_apresentacao_ifes(perfil="ao_vivo", divulgacao="publico"):
    """Apresentação 16:9 vazia, com o tema do programa e a medição em Arial.

    O perfil padrão é `ao_vivo` porque é para isso que estes decks existem:
    projeção em sala, com o corpo mínimo que se lê do fundo da turma.
    """
    prs = Presentation()
    prs.slide_width, prs.slide_height = L, A
    medidas.usar_familia("arial")
    return configurar(aplicar_tema(prs), perfil, divulgacao, identidade="ifes")
