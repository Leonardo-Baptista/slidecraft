# -*- coding: utf-8 -*-
"""Imagens, GIF e vídeo do deck que apresenta o padrão do repositório.

Tudo desenhado com Pillow, para rodar em qualquer máquina:

    vicio_antes.png    um slide com os vícios típicos de material feito por
                       IA: barra ao lado do texto, filete sobre o título,
                       travessões, lista longa, ícones decorativos
    vicio_depois.png   o mesmo conteúdo dentro do padrão
    validador.gif      a lista de conferência do validador, item a item
    fade.mp4           dois slides trocando com fade por preto

Os vícios só aparecem como imagem: no slide de verdade o validador os
reprovaria, que é justamente o ponto.

    .venv/Scripts/python.exe decks/padrao/gera_ativos.py
"""
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(RAIZ))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from kit import tema_ifes as T  # noqa: E402
from kit.clipes import _ffmpeg, fonte_do_sistema  # noqa: E402

# Saída em UTF-8 também no console do Windows, para acento não virar lixo.
sys.stdout.reconfigure(encoding="utf-8")

ASSETS = AQUI / "assets"
# Montado em tempo de execução: o caractere não pode aparecer escrito no
# código do repositório, e aqui ele é o próprio exemplo do vício.
TRAVESSAO = chr(0x2014)
REGULARES = ("C:/Windows/Fonts/arial.ttf",
             "/System/Library/Fonts/Supplemental/Arial.ttf",
             "/Library/Fonts/Arial.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def negrito(tamanho):
    return ImageFont.truetype(str(fonte_do_sistema("Arial")), tamanho)


def regular(tamanho):
    for caminho in REGULARES:
        if Path(caminho).exists():
            return ImageFont.truetype(caminho, tamanho)
    return negrito(tamanho)


def _moldura(d, w, h):
    d.rectangle((0, 0, w - 1, h - 1), outline=rgb("C4DACF"), width=3)


def vicio_antes(destino, w=1200, h=675):
    im = Image.new("RGB", (w, h), rgb("FFFFFF"))
    d = ImageDraw.Draw(im)
    _moldura(d, w, h)
    d.rectangle((70, 60, 190, 72), fill=rgb("00B894"))           # filete
    d.rectangle((70, 100, 82, 175), fill=rgb("6C5CE7"))          # barra lateral
    d.text((100, 95), "Revolucionando o Futuro", fill=rgb("2D3436"),
           font=negrito(46))
    d.text((100, 150), "Inovação %s eficiência %s resultados" % (
        TRAVESSAO, TRAVESSAO), fill=rgb("636E72"), font=regular(26))
    itens = ("Sinergia entre times %s alinhamento" % TRAVESSAO,
             "Transformação digital de ponta a ponta",
             "Eficiência operacional otimizada",
             "Experiência do usuário aprimorada",
             "Escalabilidade %s robustez %s segurança" % (TRAVESSAO, TRAVESSAO),
             "Inteligência orientada a dados",
             "Cultura de inovação contínua")
    cores = ("FF7675", "FDCB6E", "00B894", "0984E3", "6C5CE7", "E84393",
             "00CEC9")
    for i, (item, c) in enumerate(zip(itens, cores)):
        y = 225 + i * 52
        d.ellipse((100, y + 4, 128, y + 32), fill=rgb(c))        # "ícone"
        d.text((145, y + 2), item, fill=rgb("2D3436"), font=regular(25))
    d.rounded_rectangle((760, 250, 1130, 560), 24, fill=rgb("F1F2F6"))
    d.rectangle((760, 250, 772, 560), fill=rgb("00B894"))        # faixa lateral
    d.text((800, 300), "Insight", fill=rgb("2D3436"), font=negrito(30))
    d.text((800, 350), "Dados são o\nnovo petróleo.", fill=rgb("636E72"),
           font=regular(26), spacing=10)
    im.save(destino)


def vicio_depois(destino, w=1200, h=675):
    im = Image.new("RGB", (w, h), rgb("FFFFFF"))
    d = ImageDraw.Draw(im)
    _moldura(d, w, h)
    d.text((80, 70), "Três ganhos medidos em 2026", fill=rgb(T.VERDE_2),
           font=negrito(44))
    d.text((80, 130), "O que mudou depois da integração dos times.",
           fill=rgb(T.APOIO), font=regular(26))
    for i, item in enumerate(("Entrega em 9 dias, antes 21",
                              "Retrabalho caiu pela metade",
                              "Um único painel de indicadores")):
        y = 230 + i * 70
        d.ellipse((84, y + 10, 98, y + 24), fill=rgb(T.VERDE_2))
        d.text((120, y), item, fill=rgb(T.TEXTO), font=regular(30))
    d.text((80, 500), "Menos espera, menos retrabalho, um só número.",
           fill=rgb(T.TEXTO), font=negrito(30))
    d.text((80, 610), "Fonte: dados fictícios.", fill=rgb(T.APOIO),
           font=regular(20))
    im.save(destino)


def validador_gif(destino, w=900, h=560):
    itens = ("Transição em todos os slides", "Entrada automática, sem clique",
             "Cores e fontes da identidade", "Nenhuma barra decorativa",
             "Nenhum travessão", "Texto sem colisão", "Corpo mínimo do perfil")
    quadros, duracoes = [], []
    for k in range(len(itens) + 1):
        im = Image.new("RGB", (w, h), rgb("FFFFFF"))
        d = ImageDraw.Draw(im)
        d.text((50, 30), "validar_deck.py", fill=rgb(T.VERDE_1),
               font=negrito(34))
        for i, item in enumerate(itens):
            y = 100 + i * 62
            feito = i < k
            d.ellipse((50, y, 90, y + 40),
                      fill=rgb(T.VERDE_2 if feito else "E6EBE8"))
            if feito:
                d.line((60, y + 21, 68, y + 30, 82, y + 11), fill=rgb("FFFFFF"),
                       width=5)
            d.text((110, y + 4), item,
                   fill=rgb(T.TEXTO if feito else "A8B3AD"), font=regular(28))
        quadros.append(im.convert("P", palette=Image.ADAPTIVE, colors=16))
        duracoes.append(450)
    # Primeiro quadro é o estado final: é o que aparece parado e no PDF.
    quadros.insert(0, quadros[-1])
    duracoes = [1500] + duracoes[:-1] + [2500]
    quadros[0].save(destino, save_all=True, append_images=quadros[1:],
                    duration=duracoes, loop=0, optimize=True)


def _slide_falso(w, h, fundo, titulo, cor):
    im = Image.new("RGB", (w, h), rgb(fundo))
    d = ImageDraw.Draw(im)
    d.text((90, 90), titulo, fill=rgb(cor), font=negrito(64))
    for i in range(3):
        d.rounded_rectangle((90 + i * 370, 260, 420 + i * 370, 520), 20,
                            fill=rgb(T.CARTOES[i][0]))
    return im


def fade_mp4(destino, w=1280, h=720, fps=15):
    """Slide A, fade para o preto, slide B: a transição padrão do kit."""
    a = _slide_falso(w, h, "FFFFFF", "Slide anterior", T.VERDE_1)
    b = _slide_falso(w, h, "F2F5F3", "Slide seguinte", T.VERDE_2)
    preto = Image.new("RGB", (w, h), (0, 0, 0))
    sequencia = [a] * fps
    sequencia += [Image.blend(a, preto, i / 10) for i in range(1, 11)]
    sequencia += [Image.blend(preto, b, i / 10) for i in range(1, 11)]
    sequencia += [b] * (fps * 2)
    pasta = AQUI / "cache" / "_quadros_fade"
    pasta.mkdir(parents=True, exist_ok=True)
    for k, quadro in enumerate(sequencia):
        quadro.save(pasta / ("q%03d.png" % k))
    _ffmpeg("-framerate", str(fps), "-i", str(pasta / "q%03d.png"),
            "-c:v", "libx264", "-crf", "24", "-pix_fmt", "yuv420p", "-an",
            str(destino))
    shutil.rmtree(pasta)


def main():
    ASSETS.mkdir(exist_ok=True)
    vicio_antes(ASSETS / "vicio_antes.png")
    vicio_depois(ASSETS / "vicio_depois.png")
    validador_gif(ASSETS / "validador.gif")
    fade_mp4(ASSETS / "fade.mp4")
    print("ativos gerados em", ASSETS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
