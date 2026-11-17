# -*- coding: utf-8 -*-
"""Elementos comuns do deck: paleta, tipografia e helpers de layout.

Regra de escrita: nenhum travessao, meia-risca ou traco horizontal em texto de slide.
"""
import hashlib
from contextlib import contextmanager
from pathlib import Path

from PIL import Image, ImageEnhance
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt
from kit.editorial import IDIOMA, preparar
from kit.medidas import altura_do_texto
from kit.politica import papel, piso_de_leitura

RAIZ = Path(__file__).resolve().parent.parent
# Padrão do kit. Cada deck sobrescreve base.ASSETS e base.CACHE apontando para
# a sua propria pasta, antes de chamar foto().
ASSETS = RAIZ / "kit" / "assets"
CACHE = RAIZ / "kit" / "cache"
CACHE.mkdir(parents=True, exist_ok=True)

PRETO = RGBColor(0x00, 0x00, 0x00)
QUASE_PRETO = RGBColor(0x0D, 0x0D, 0x0D)
BRANCO = RGBColor(0xFF, 0xFF, 0xFF)
TURQUESA = RGBColor(0x00, 0xE5, 0xC0)
TURQUESA_CLARO = RGBColor(0xB8, 0xE8, 0xDF)
VERDE_ESCURO = RGBColor(0x00, 0x84, 0x6F)
CINZA = RGBColor(0x9D, 0x9D, 0x9C)
CINZA_ESCURO = RGBColor(0x57, 0x57, 0x56)
CINZA_CLARO = RGBColor(0xE6, 0xE6, 0xE6)
CINZA_MEDIO = RGBColor(0xC8, 0xC8, 0xC8)
FUNDO_CLARO = RGBColor(0xF7, 0xF7, 0xF6)

FONTE = "Montserrat"
L, A = Inches(13.333), Inches(7.5)
MARGEM = Inches(0.9)


@contextmanager
def usando(assets, cache=None):
    """Aponta ASSETS e CACHE para um deck, e devolve ao sair.

    Cada deck normalmente define base.ASSETS no topo do build e pronto, porque
    e um deck por processo. Quando for preciso gerar mais de um no mesmo
    processo, use isto: sem o escopo, o segundo deck herdaria os ativos do
    primeiro.

        with base.usando(AQUI / "assets"):
            ...
    """
    global ASSETS, CACHE
    antigos = ASSETS, CACHE
    ASSETS = Path(assets)
    CACHE = Path(cache) if cache else Path(assets).parent / "cache"
    CACHE.mkdir(parents=True, exist_ok=True)
    try:
        yield
    finally:
        ASSETS, CACHE = antigos


def foto(nome, largura, altura, escurecer=1.0, gradiente=None, saturar=None,
         ancora="centro"):
    """Corta e trata uma foto, devolvendo o caminho do arquivo em cache.

    A chave do cache inclui um resumo do conteúdo do arquivo, e não so o nome.
    Trocar a imagem mantendo o mesmo nome gera um tratamento novo, em vez de
    reaproveitar o antigo sem ninguem perceber.
    """
    origem = ASSETS / nome
    resumo = hashlib.md5(origem.read_bytes()).hexdigest()[:10]
    chave = "%s_%s_%dx%d_%s_%s_%s_%s.jpg" % (
        Path(nome).stem, resumo, largura, altura, escurecer, gradiente,
        saturar, ancora)
    destino = CACHE / chave
    if destino.exists():
        return str(destino)
    im = Image.open(origem).convert("RGB")
    alvo, prop = largura / altura, im.width / im.height
    if prop > alvo:
        nova = int(im.height * alvo)
        x = 0 if ancora == "esquerda" else (im.width - nova) // 2
        im = im.crop((x, 0, x + nova, im.height))
    else:
        nova = int(im.width / alvo)
        y = 0 if ancora == "topo" else (im.height - nova) // 2
        im = im.crop((0, y, im.width, y + nova))
    im = im.resize((largura, altura), Image.LANCZOS)
    if saturar is not None:
        im = ImageEnhance.Color(im).enhance(saturar)
    if escurecer != 1.0:
        im = ImageEnhance.Brightness(im).enhance(escurecer)
    if gradiente:
        sombra = Image.new("L", (im.width, 1))
        for x in range(im.width):
            t = min(1.0, x / (im.width * gradiente))
            sombra.putpixel((x, 0), int(255 * (1 - t) * 0.92))
        im = Image.composite(Image.new("RGB", im.size, (0, 0, 0)), im,
                             sombra.resize((im.width, im.height)))
    im.save(destino, quality=92)
    return str(destino)


def fundo(slide, cor):
    f = slide.background.fill
    f.solid()
    f.fore_color.rgb = cor


def texto(slide, x, y, cx, cy, conteudo, tamanho, cor, negrito=False,
          espacamento=None, alinhamento=PP_ALIGN.LEFT, entrelinha=1.0,
          caixa_alta=False):
    tb = slide.shapes.add_textbox(x, y, cx, cy)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = alinhamento
    p.line_spacing = entrelinha
    r = p.add_run()
    r.text = preparar(conteudo.upper() if caixa_alta else conteudo)
    fo = r.font
    fo.name = FONTE
    fo.size = Pt(tamanho)
    fo.bold = negrito
    fo.color.rgb = cor
    fo._rPr.set("lang", IDIOMA)
    if espacamento is not None:
        fo._rPr.set("spc", str(int(espacamento * 100)))
    return tb


def retangulo(slide, x, y, cx, cy, cor, forma=MSO_SHAPE.RECTANGLE,
              linha=None, espessura=1.0):
    s = slide.shapes.add_shape(forma, x, y, cx, cy)
    if cor is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = cor
    if linha is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = linha
        s.line.width = Pt(espessura)
    s.shadow.inherit = False
    s.text_frame.text = ""
    return s


def kicker(slide, x, y, conteudo, cor=TURQUESA):
    return papel(texto(slide, x, y, Inches(6.0), Inches(0.3), conteudo, 11, cor,
                       negrito=True, espacamento=1.6, caixa_alta=True), "rotulo")


def titulo(slide, x, y, conteudo, cor=BRANCO, tamanho=34, largura=Inches(7.4)):
    return papel(texto(slide, x, y, largura, Inches(1.6), conteudo, tamanho, cor,
                       negrito=True, entrelinha=1.12), "titulo")


def fim_do_texto(forma):
    """Polegada em que o texto da forma realmente termina.

    A caixa e criada com altura nominal, e o texto cresce para baixo. Quem
    posiciona o elemento seguinte precisa da altura medida, não da declarada.
    """
    conteudo = forma.text_frame.text
    paragrafo = forma.text_frame.paragraphs[0]
    corpo = 18.0
    negrito = False
    if paragrafo.runs:
        fonte = paragrafo.runs[0].font
        corpo = fonte.size.pt if fonte.size is not None else corpo
        negrito = bool(fonte.bold)
    entrelinha = paragrafo.line_spacing
    entrelinha = entrelinha if isinstance(entrelinha, float) else 1.0
    return (Emu(int(forma.top)).inches
            + altura_do_texto(conteudo, forma.width, corpo, negrito, entrelinha))


def abaixo_de(forma, y, folga=0.06):
    """Y proposto, empurrado apenas quando o texto acima invadiria o espaco.

    Devolve o proprio `y` sempre que o título couber onde a composição previu,
    de modo que nenhum slide ja aprovado mude de lugar. So o caso que colidiria
    desce, e desce o mínimo.
    """
    return max(float(y), fim_do_texto(forma) + folga)


def linha_apoio(slide, x, y, conteudo, cor=CINZA_MEDIO, tamanho=13.5,
                largura=Inches(6.4)):
    return texto(slide, x, y, largura, Inches(0.9), conteudo, tamanho, cor,
                 entrelinha=1.35)


def marcadores(slide, x, y, itens, cor=BRANCO, tamanho=12.5, passo=Inches(0.44),
               cor_ponto=TURQUESA, largura=Inches(5.2)):
    """Lista com ponto turquesa.

    Devolve uma lista de pares [ponto, texto], um por item, para animar cada
    linha separadamente. Assinatura unica: antes o kit devolvia a posicao final
    e os decks devolviam as formas, o que gerava duas interfaces para a mesma
    responsabilidade.
    """
    # O perfil do arquivo manda no texto de leitura: uma lista nunca sai
    # menor que o corpo mínimo declarado no build.
    tamanho = max(tamanho, piso_de_leitura(slide))
    criadas = []
    for item in itens:
        ponto = retangulo(slide, x, y + Inches(0.09), Pt(7), Pt(7), cor_ponto,
                          forma=MSO_SHAPE.OVAL)
        linha = texto(slide, x + Inches(0.35), y, largura - Inches(0.35), Inches(0.32), item,
                      tamanho, cor, entrelinha=1.25)
        criadas.append([ponto, linha])
        y += passo
    return criadas


def numero(slide, indice, escuro=True):
    """Numero de pagina. Mobiliario, não conteúdo: fica fora da margem."""
    return papel(
        texto(slide, L - Inches(1.1), A - Inches(0.62), Inches(0.5),
              Inches(0.3), "%02d" % indice, 10,
              CINZA if escuro else CINZA_ESCURO, alinhamento=PP_ALIGN.RIGHT),
        "numero")


def novo_slide(prs, cor=PRETO, indice=None):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    fundo(s, cor)
    if indice is not None:
        numero(s, indice, escuro=(cor in (PRETO, QUASE_PRETO)))
    return s
