# -*- coding: utf-8 -*-
"""Número que entra contando: de zero até o valor, no lugar exato do texto.

O PowerPoint não anima o valor de um texto. O kit resolve com um clipe curto,
gerado em código por `kit.clipes.contador`, com o fundo, a fonte, o corpo e a
cor que o texto teria. O quadro de capa é o valor final, desenhado direto e
não tirado do vídeo: quem abre o arquivo sem apresentar, ou exporta para PDF,
vê o número certo, e não um zero.

Use só para o número que carrega o argumento do slide. Três por slide, no
máximo: contador em todo lugar vira enfeite.

    from kit.numeros import numero_que_sobe, tocar_junto

    n = numero_que_sobe(s, AQUI / "video" / "alunos.mp4", 2.4, 2.1, 3.0, 0.9,
                        ate=1250, formatar=inteiro, corpo=44,
                        cor="1C7F5C", fundo="DFEDE6")
    anima(s, [(0, [t]), (400, [n])])
    tocar_junto(s, [(n, 400)])          # sempre depois do anima
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pptx.util import Inches

from kit.clipes import contador, fonte_do_sistema, ultimo_quadro
from kit.slides import _liga_video

PIXELS_POR_POLEGADA = 300


def _rgb(valor):
    """Aceita "1C7F5C", "#1C7F5C", RGBColor ou tupla."""
    if isinstance(valor, tuple):
        return valor
    texto = str(valor).lstrip("#")
    return tuple(int(texto[i:i + 2], 16) for i in (0, 2, 4))


def _familia(slide):
    """Família do número: a mesma do texto ao redor, conforme a identidade."""
    from kit.politica import identidade_de
    try:
        prs = slide.part.package.presentation_part.presentation
        identidade = identidade_de(prs)
    except AttributeError:
        return None
    if identidade == "escuro":
        return "Montserrat"
    if identidade == "importada":
        from kit.importado import design
        return design(prs)["fontes"]["corpo"]
    return "Arial"


def inteiro(valor):
    """1250 vira 1.250."""
    return "{:,}".format(int(round(valor))).replace(",", ".")


def porcentagem(casas=0):
    """Formatador de porcentagem com vírgula decimal: 94,5%."""
    def formatar(valor):
        return ("%.*f%%" % (casas, valor)).replace(".", ",")
    return formatar


def numero_que_sobe(slide, clipe, x, y, largura, altura, ate, corpo, cor,
                    fundo="FFFFFF", formatar=inteiro, fonte=None,
                    segundos=1.4):
    """Insere o clipe do número subindo e devolve a forma do filme.

    x, y, largura e altura em polegadas. `fundo` precisa ser a cor exata do
    que está atrás (cartão ou slide), senão o clipe aparece como retângulo.
    O filme entra na coreografia como qualquer forma; o comando de tocar é
    ligado por `tocar_junto`, depois do `anima`. Sem `fonte`, usa a família
    da identidade do arquivo: Arial no `ifes`, Montserrat no `escuro` e a
    fonte do tema na `importada`.
    """
    clipe = Path(clipe)
    clipe.parent.mkdir(parents=True, exist_ok=True)
    fonte = Path(fonte) if fonte else fonte_do_sistema(_familia(slide))
    cor, alvo = _rgb(cor), _rgb(fundo)
    w = int(largura * PIXELS_POR_POLEGADA) // 2 * 2
    h = int(altura * PIXELS_POR_POLEGADA) // 2 * 2
    px = int(round(corpo / 72 * PIXELS_POR_POLEGADA))
    capa = clipe.with_suffix(".png")
    pedido = alvo
    # A compressão em yuv420p desloca a cor de fundo em alguns níveis. Mede o
    # que saiu e, se não bater, gera de novo com o fundo compensado.
    for _ in range(3):
        contador(clipe, ate=ate, segundos=segundos, espera=0.4, largura=w,
                 altura=h, corpo=px, cor=cor, fonte=str(fonte), fundo=pedido,
                 formatar=formatar, origem=(0, 0), ancora="la")
        ultimo_quadro(clipe, capa)
        with Image.open(capa) as quadro:
            saiu = quadro.convert("RGB").getpixel((w - 4, h - 4))
        erro = [a - s for a, s in zip(alvo, saiu)]
        if max(abs(e) for e in erro) <= 1:
            break
        pedido = tuple(max(0, min(255, p + e)) for p, e in zip(pedido, erro))
    imagem = Image.new("RGB", (w, h), alvo)
    ImageDraw.Draw(imagem).text((0, 0), formatar(ate), fill=cor, anchor="la",
                                font=ImageFont.truetype(str(fonte), px))
    imagem.save(capa)
    return slide.shapes.add_movie(
        str(clipe), Inches(x), Inches(y), Inches(largura), Inches(altura),
        poster_frame_image=str(capa), mime_type="video/mp4")


def tocar_junto(slide, filmes):
    """Liga cada clipe para tocar quando o seu grupo entra, sem repetir.

    filmes: lista de (filme, atraso em milissegundos).
    """
    for filme, atraso in filmes:
        _liga_video(slide, filme.shape_id, atraso=atraso, loop=False)
