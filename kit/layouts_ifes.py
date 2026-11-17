# -*- coding: utf-8 -*-
"""Composições do modelo IFES: os blocos que o modelo oficial usa.

Cada função aqui é um pedaço reconhecível do modelo do programa: o cabeçalho
com título e subtítulo, o cartão arredondado com número em círculo, o chip de
termo, a régua de fecho com a frase que o slide quer deixar, o chevron e a
linha de fonte no rodapé. Quem monta um deck no modelo escolhe o bloco e
entrega o texto; coordenada, corpo de fonte e cor vêm daqui.

As funções devolvem sempre as formas criadas, porque é delas que sai a
coreografia. A animação em si continua sendo a do kit:

    from kit.slides import anima
    from kit.layouts_ifes import cabecalho, cartao, destaque

    t, sub = cabecalho(s, "Título do slide", "Uma linha de contexto.")
    anima(s, [(0, [t]), (200, [sub])])
"""
from pathlib import Path

from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

from kit import tema_ifes as T
from kit.editorial import IDIOMA, preparar
from kit.medidas import altura_do_texto, linhas_do_texto
from kit.politica import papel


def cor(hexadecimal):
    """Aceita a cor como está escrita no tema, em texto."""
    if isinstance(hexadecimal, RGBColor):
        return hexadecimal
    return RGBColor.from_string(str(hexadecimal).lstrip("#").upper())


def pol(valor):
    """Polegadas, seja qual for a unidade recebida."""
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        return Emu(int(valor)).inches if valor > 100 else float(valor)
    return Emu(int(valor)).inches


def _emu(valor):
    """Converte polegada em Emu, deixando passar o que já é Length."""
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        return Inches(valor) if valor < 100 else Emu(int(valor))
    return valor


# ------------------------------------------------------------------- o slide

def novo(prs, fundo=None):
    """Slide em branco com o fundo do modelo aplicado em tela cheia.

    O fundo é uma imagem, e não um preenchimento: a faixa verde em diagonal e o
    logotipo do IFES fazem parte dela. É o que garante que o slide gerado aqui
    seja indistinguível de um slide montado à mão sobre o modelo.
    """
    s = prs.slides.add_slide(prs.slide_layouts[6])
    imagem = fundo or T.FUNDO_CONTEUDO
    papel(s.shapes.add_picture(str(imagem), 0, 0, T.L, T.A), "marca")
    return s


def texto(slide, x, y, cx, cy, conteudo, tamanho, cor_do_texto,
          negrito=False, alinhamento=PP_ALIGN.LEFT, entrelinha=1.0,
          caixa_alta=False, fonte=None, espacamento=None, ancora=None):
    """Caixa de texto no tema do programa. Mesmo contrato de `kit.base.texto`."""
    tb = slide.shapes.add_textbox(_emu(x), _emu(y), _emu(cx), _emu(cy))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    if ancora is not None:
        tf.vertical_anchor = ancora
    conteudo = preparar(conteudo)
    linhas = (conteudo.upper() if caixa_alta else conteudo).split("\n")
    for indice, linha in enumerate(linhas):
        p = tf.paragraphs[0] if indice == 0 else tf.add_paragraph()
        p.alignment = alinhamento
        p.line_spacing = entrelinha
        r = p.add_run()
        r.text = linha
        f = r.font
        f.name = fonte or T.FONTE
        f.size = Pt(tamanho)
        f.bold = negrito
        f.color.rgb = cor(cor_do_texto)
        f._rPr.set("lang", IDIOMA)
        if espacamento is not None:
            f._rPr.set("spc", str(int(espacamento * 100)))
    return tb


def forma(slide, x, y, cx, cy, preenchimento, tipo=MSO_SHAPE.RECTANGLE,
          borda=None, espessura=0.75, ajuste=None):
    """Retângulo, retângulo arredondado, elipse ou chevron, sem sombra."""
    s = slide.shapes.add_shape(tipo, _emu(x), _emu(y), _emu(cx), _emu(cy))
    if preenchimento is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = cor(preenchimento)
    if borda is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = cor(borda)
        s.line.width = Pt(espessura)
    s.shadow.inherit = False
    s.text_frame.text = ""
    if ajuste is not None and s.adjustments:
        s.adjustments[0] = ajuste
    return s


# --------------------------------------------------------------- o cabeçalho

def cabecalho(slide, titulo, subtitulo=None):
    """Título e subtítulo na posição fixa do modelo. Devolve as duas formas.

    O subtítulo é opcional, mas o modelo o usa em quase todo slide: é a frase
    que diz o que olhar, e sem ela o título fica sozinho sustentando o slide.
    """
    t = papel(texto(slide, T.MARGEM, T.Y_TITULO, T.UTIL, T.ALTURA_TITULO,
                    titulo, T.CORPO["titulo"], T.VERDE_2, negrito=True),
              "titulo")
    if subtitulo is None:
        return t, None
    sub = texto(slide, T.MARGEM, T.Y_SUBTITULO, T.UTIL, T.ALTURA_SUBTITULO,
                subtitulo, T.CORPO["subtitulo"], T.APOIO, entrelinha=1.15)
    return t, sub


def fonte(slide, conteudo):
    """Linha de procedência no rodapé. Obrigatória em todo slide com dado.

    O modelo pede que cada número, imagem e afirmação diga de onde
    veio. É o que separa uma aula de um slide bonito.
    """
    # A linha fica a meia polegada do fim do slide, então uma procedência
    # comprida escorre para fora da área visível. Isso não aparece em nenhuma
    # verificação de posição, porque rodapé é mobiliário e pode passar da
    # margem de conteúdo. Medir aqui é o que impede o texto de sumir.
    alto = altura_medida(conteudo, T.UTIL, T.CORPO["fonte"], False, 1.1)
    if T.Y_FONTE + alto > 7.5:
        raise ValueError(
            "Linha de fonte comprida demais: ocupa %.2f polegada e passa do "
            "fim do slide. Encurte a procedência: %r" % (alto, conteudo))
    return papel(texto(slide, T.MARGEM, T.Y_FONTE, T.UTIL, T.ALTURA_FONTE,
                       conteudo, T.CORPO["fonte"], T.APOIO, entrelinha=1.1),
                 "rodape")


def _quebra(conteudo, largura, tamanho, negrito=True, fonte=None):
    """Diz se o texto passa de uma linha na largura dada."""
    # Tahoma é um pouco mais larga que a Arial e não tem tabela medida no
    # repositório. Medir em Arial com folga cobre a diferença sem exigir uma
    # terceira tabela só para as duas linhas da capa.
    folga = 1.06 if fonte == T.FONTE_CAPA else 1.0
    return len(linhas_do_texto(conteudo, Inches(largura / folga), tamanho,
                               negrito, familia="arial")) > 1


def _uma_linha(conteudo, direita, largura, tamanho, negrito=True,
               esquerda_minima=1.26, corpo_minimo=None, fonte=None):
    """Largura e corpo que fazem o texto caber em uma linha só.

    A caixa cresce para a esquerda, mantendo a borda direita onde o modelo a
    colocou: é ela que alinha as três linhas da capa. Só quando nem a largura
    máxima resolve é que o corpo cede, de meio em meio ponto.
    """
    limite = direita - esquerda_minima
    while _quebra(conteudo, largura, tamanho, negrito, fonte) and largura < limite:
        largura = min(limite, largura + 0.25)
    piso = corpo_minimo if corpo_minimo is not None else tamanho
    while _quebra(conteudo, largura, tamanho, negrito, fonte) and tamanho > piso:
        tamanho -= 0.5
    if _quebra(conteudo, largura, tamanho, negrito, fonte):
        # Nem na largura máxima, nem no menor corpo aceitável. Encurtar o texto
        # é decisão de quem escreve, não do kit: melhor parar a geração do que
        # entregar uma capa com a faixa branca estourada.
        raise ValueError(
            "Texto comprido demais para uma linha da capa, mesmo em %s pontos: "
            "%r. Encurte a frase." % (tamanho, conteudo))
    return largura, tamanho


# ------------------------------------------------------------------- a capa

def capa(prs, titulo, disciplina, assinatura):
    """Abertura: fundo em tela cheia, faixa branca e três linhas de texto.

    As duas linhas de baixo saem em Tahoma porque é assim no modelo oficial do
    programa. Ver a nota em `kit.tema_ifes.FONTE_CAPA`.
    """
    s = prs.slides.add_slide(prs.slide_layouts[6])
    papel(s.shapes.add_picture(str(T.FUNDO_CAPA), Inches(-0.03), Inches(-0.03),
                               Inches(13.45), Inches(7.56)), "marca")
    faixa = forma(s, -0.52, 2.86, 14.19, 1.71, T.BRANCO, borda=T.BRANCO,
                  espessura=0.74)
    # As três linhas da capa ficam em uma linha cada. Duas linhas em 54 pontos
    # estouram a faixa branca e caem sobre a linha da disciplina; duas linhas
    # na assinatura deixam a última palavra sozinha. As caixas do modelo foram
    # medidas para um título curto, então aqui elas crescem para a esquerda
    # quando o texto pede, sem tirar a borda direita do lugar.
    largura_t, corpo_t = _uma_linha(titulo, 12.39, 8.48,
                                    T.CORPO["titulo_capa"], corpo_minimo=36)
    largura_d, corpo_d = _uma_linha(disciplina, 12.38, 8.77, T.CORPO["capa"],
                                    negrito=False, corpo_minimo=16,
                                    fonte=T.FONTE_CAPA)
    largura_a, corpo_a = _uma_linha(assinatura, 12.38, 7.52, T.CORPO["capa"],
                                    negrito=False, corpo_minimo=16,
                                    fonte=T.FONTE_CAPA)
    # Os três textos vão marcados como `capa`: a abertura tem grade própria,
    # sem a faixa verde à esquerda, e por isso não responde à margem de
    # conteúdo dos demais slides.
    t = papel(texto(s, 12.39 - largura_t, 2.95, largura_t, 0.93, titulo,
                    corpo_t, T.VERDE_2, negrito=True,
                    alinhamento=PP_ALIGN.CENTER), "capa")
    d = papel(texto(s, 12.38 - largura_d, 3.91, largura_d, 0.52, disciplina,
                    corpo_d, "007826", alinhamento=PP_ALIGN.RIGHT,
                    fonte=T.FONTE_CAPA), "capa")
    a = papel(texto(s, 12.38 - largura_a, 4.90, largura_a, 0.49, assinatura,
                    corpo_a, "007826", alinhamento=PP_ALIGN.RIGHT,
                    fonte=T.FONTE_CAPA), "capa")
    return s, faixa, t, d, a


# ---------------------------------------------------------- blocos do modelo

def cartao(slide, x, y, cx, cy, nivel=1, raio=0.06):
    """Cartão arredondado. `nivel` de 1 a 4 escolhe o par fundo mais borda."""
    fundo, borda = T.CARTOES[(nivel - 1) % len(T.CARTOES)]
    return forma(slide, x, y, cx, cy, fundo, tipo=MSO_SHAPE.ROUNDED_RECTANGLE,
                 borda=borda, ajuste=raio)


def moldura(slide, x, y, cx, cy, nivel=1):
    """Moldura branca para receber imagem. A borda acompanha o nível do bloco."""
    _, borda = T.CARTOES[(nivel - 1) % len(T.CARTOES)]
    return forma(slide, x, y, cx, cy, T.BRANCO,
                 tipo=MSO_SHAPE.ROUNDED_RECTANGLE, borda=borda, ajuste=0.045)


def imagem(slide, caminho, x, y, cx, cy, com_moldura=True, nivel=1,
           respiro=0.07):
    """Imagem dentro da moldura do modelo, encaixada sem deformar.

    A imagem é ajustada para caber na área útil mantendo a proporção, e fica
    centralizada dentro da moldura. Devolve (moldura, imagem); sem moldura, a
    primeira posição vem vazia.
    """
    from PIL import Image

    quadro = moldura(slide, x, y, cx, cy, nivel) if com_moldura else None
    util_x, util_y = cx - 2 * respiro, cy - 2 * respiro
    largura_px, altura_px = Image.open(str(caminho)).size
    escala = min(util_x / largura_px, util_y / altura_px)
    larg, alt = largura_px * escala, altura_px * escala
    figura = slide.shapes.add_picture(
        str(caminho), _emu(x + (cx - larg) / 2), _emu(y + (cy - alt) / 2),
        _emu(larg), _emu(alt))
    return quadro, figura


def rotulo(slide, x, y, conteudo, cor_do_texto=None, largura=3.08):
    """Rótulo em caixa alta acima de um bloco. Apoio, não texto de leitura."""
    return papel(texto(slide, x, y, largura, 0.22, conteudo, T.CORPO["rotulo"],
                       cor_do_texto or T.VERDE_1, negrito=True,
                       caixa_alta=True), "rotulo")


def corpo(slide, x, y, cx, cy, conteudo, tamanho=None, cor_do_texto=None,
          entrelinha=1.2, alinhamento=PP_ALIGN.LEFT):
    """Texto de leitura dentro de um cartão."""
    return texto(slide, x, y, cx, cy, conteudo,
                 tamanho or T.CORPO["texto"], cor_do_texto or T.TEXTO,
                 entrelinha=entrelinha, alinhamento=alinhamento)


def chip(slide, x, y, cx, cy, conteudo, preenchimento=None,
         cor_do_texto=None, tamanho=None, raio=0.23,
         tipo=MSO_SHAPE.ROUNDED_RECTANGLE):
    """Pílula com texto centralizado. Cheia por padrão, ou branca com borda."""
    preenchimento = T.VERDE_2 if preenchimento is None else preenchimento
    branco = str(preenchimento).upper() == T.BRANCO
    borda = T.CARTOES[1][1] if branco else None
    caixa = forma(slide, x, y, cx, cy, preenchimento, tipo=tipo, borda=borda,
                  ajuste=raio)
    tf = caixa.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = preparar(conteudo)
    r.font.name = T.FONTE
    r.font.size = Pt(tamanho or T.CORPO["chip"])
    r.font.bold = True
    r.font.color.rgb = cor(cor_do_texto or (T.TEXTO if branco else T.BRANCO))
    r.font._rPr.set("lang", IDIOMA)
    # Um chip é etiqueta, não texto de leitura: vale para ele o piso absoluto.
    return papel(caixa, "rotulo")


def numero(slide, x, y, conteudo, preenchimento=None, diametro=0.44):
    """Número em círculo cheio, do jeito que o modelo numera cartões."""
    return chip(slide, x, y, diametro, diametro, conteudo,
                preenchimento or T.VERDE_1, tamanho=T.CORPO["cartao_titulo"],
                raio=None, tipo=MSO_SHAPE.OVAL)


def chevron(slide, x, y, largura=0.16, altura=0.24):
    """A seta fina entre dois blocos. Sempre cinza: ela liga, não destaca."""
    return forma(slide, x, y, largura, altura, T.SETA, tipo=MSO_SHAPE.CHEVRON,
                 ajuste=0.5)


def destaque(slide, y, conteudo):
    """Frase de fecho do slide, em negrito, sozinha: sem caixa e sem barra.

    É a frase que a pessoa leva, mesmo que esqueça o resto. Uma frase só: duas
    frases aqui significam que o slide tem dois assuntos.

    Regra de ouro do repositório: nenhuma barra colorida. O modelo original
    traz esse fecho num bloco tingido com barra na borda esquerda; aqui o
    negrito e o espaço em volta bastam. O validador reprova barra colorida.

    Devolve uma tupla com a frase, para entrar na coreografia com
    `list(destaque(...))`.
    """
    frase = texto(slide, T.MARGEM, y + 0.15, T.UTIL, 0.40, conteudo,
                  T.CORPO["destaque"], T.TEXTO, negrito=True, entrelinha=1.18)
    return (frase,)


def altura_do_destaque(conteudo):
    """Quanto o fecho ocupa, do y pedido ao fim da frase. Para quem empilha."""
    return 0.15 + altura_medida(conteudo, T.UTIL, T.CORPO["destaque"], True,
                                1.18)


def linha(slide, x, y, largura, cor_da_linha=None, espessura=1.0):
    """Fio neutro horizontal, como o que separa cabeçalho de tabela.

    Sempre em cinza claro: barra colorida não entra no padrão.
    """
    regua = forma(slide, x, y, largura, Pt(espessura),
                  cor_da_linha or T.LINHA_FINA)
    return regua


def altura_medida(conteudo, largura, tamanho, negrito=False, entrelinha=1.0):
    """Altura real do texto em Arial, para empilhar sem colidir."""
    return altura_do_texto(conteudo, Inches(largura), tamanho, negrito,
                           entrelinha, familia="arial")


def abaixo_de(forma_acima, conteudo, largura, tamanho, negrito=False,
              entrelinha=1.0, folga=0.06):
    """Y logo abaixo do fim medido de um texto, e não do fim declarado."""
    return (pol(forma_acima.top)
            + altura_medida(conteudo, largura, tamanho, negrito, entrelinha)
            + folga)


# ------------------------------------------------- composições com movimento

def linha_do_tempo(slide, marcos, inicio=520, y_barra=3.02):
    """Marcos sobre uma barra que preenche da esquerda para a direita.

    marcos: lista de (etiqueta, nome, descricao), de 2 a 5. Cada marco entra
    no instante em que a barra passa por ele. Devolve a lista de efeitos,
    para somar com os do cabeçalho e entregar a `monta_timing`:

        t, sub = cabecalho(s, "Título", "Subtítulo")
        ef = efeitos_de_formas([(0, [t]), (240, [sub])])
        monta_timing(s, ef + linha_do_tempo(s, marcos))
    """
    from pptx.dml.color import RGBColor
    from kit.animacao import DURACAO_BARRA
    from kit.coreografia import (FADE, WIPE_ESQUERDA, barra_de_progresso,
                                 efeitos_de_formas, marcos_na_passagem)

    if not 2 <= len(marcos) <= 5:
        raise ValueError("Linha do tempo: use de 2 a 5 marcos.")
    passo = T.UTIL / len(marcos)
    largura = passo - 0.3
    grupos, centros = [], []
    for i, (etiqueta, nome, descricao) in enumerate(marcos):
        x = T.MARGEM + i * passo
        centro = x + 0.10
        centros.append(centro)
        atual = i == len(marcos) - 1
        grupos.append([
            chip(slide, x, y_barra - 1.16, 0.95, 0.30, etiqueta,
                 T.VERDE_2 if atual else T.VERDE_1),
            texto(slide, x, y_barra - 0.76, largura, 0.30, nome, 13.5, T.VERDE_1,
                  negrito=True),
            forma(slide, centro - 0.10, y_barra - 0.08, 0.20, 0.20, T.VERDE_1,
                  tipo=MSO_SHAPE.OVAL),
            texto(slide, x, y_barra + 0.32, largura, 0.80, descricao,
                  T.CORPO["texto"], T.TEXTO, entrelinha=1.2)])
    barra = barra_de_progresso(slide, y_barra, T.MARGEM, T.DIREITA,
                               cor=RGBColor.from_string(T.VERDE_2))
    atrasos = marcos_na_passagem(barra, centros, DURACAO_BARRA)
    efeitos = efeitos_de_formas([(inicio, [barra])], tipo=WIPE_ESQUERDA,
                                duracao=DURACAO_BARRA)
    efeitos += efeitos_de_formas(
        [(inicio + a, g) for a, g in zip(atrasos, grupos)], tipo=FADE,
        duracao=380)
    return efeitos


def cartoes_de_numeros(slide, blocos, pasta, y=1.95, inicio=500, corpo_numero=48):
    """Até três cartões com o número estratégico entrando contando.

    blocos: lista de (rotulo, valor, formatar, legenda); `formatar` vem de
    `kit.numeros` (inteiro, porcentagem()). `pasta` recebe os clipes, em geral
    AQUI / "video". Devolve (grupos, filmes): os grupos vão para `anima`, e
    os filmes para `tocar_junto`, sempre depois do `anima`.
    """
    from kit.numeros import numero_que_sobe

    if not 1 <= len(blocos) <= 3:
        raise ValueError("Cartões de números: no máximo três por slide.")
    grupos, filmes = [], []
    for i, (nome, valor, formatar, legenda) in enumerate(blocos):
        x = T.MARGEM + i * (T.COLUNA_3 + T.FOLGA)
        nivel = i + 1
        c = cartao(slide, x, y, T.COLUNA_3, 2.45, nivel)
        r = rotulo(slide, x + 0.25, y + 0.23, nome)
        n = numero_que_sobe(slide, Path(pasta) / ("numero_%d_%d.mp4" % (
            len(slide.part.package.presentation_part.presentation.slides), i)),
            x + 0.25, y + 0.60, T.COLUNA_3 - 0.5, 0.95, ate=valor,
            formatar=formatar, corpo=corpo_numero, cor=T.VERDE_2,
            fundo=T.CARTOES[nivel - 1][0])
        l = corpo(slide, x + 0.25, y + 1.67, T.COLUNA_3 - 0.5, 0.5, legenda)
        atraso = inicio + i * 350
        grupos.append((atraso, [c, r, n, l]))
        filmes.append((n, atraso))
    return grupos, filmes
