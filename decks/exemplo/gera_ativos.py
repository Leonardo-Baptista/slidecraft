# -*- coding: utf-8 -*-
"""Cria em código as imagens, o GIF e o vídeo do deck de exemplo.

Nada aqui vem de foto ou de banco de imagem: tudo é desenhado com Pillow, sai
igual em qualquer máquina e não tem licença de terceiros. É também o modelo de
como gerar figura animada para um deck seu.

    canteiros.png   ilustração estática, para o slide de imagem
    colheita.gif    gráfico de barras que cresce mês a mês (GIF animado)
    broto.mp4       clipe curto de um broto crescendo (vídeo em loop)

    .venv/Scripts/python.exe decks/exemplo/gera_ativos.py      (Windows)
    .venv/bin/python decks/exemplo/gera_ativos.py              (macOS e Linux)
"""
import math
import random
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(RAIZ))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from kit import tema_ifes as T  # noqa: E402
from kit.clipes import _ffmpeg, fonte_do_sistema  # noqa: E402

ASSETS = AQUI / "assets"
ASSETS.mkdir(exist_ok=True)
MESES = ("jan", "fev", "mar", "abr", "mai", "jun",
         "jul", "ago", "set", "out", "nov", "dez")
# Dados fictícios, só para a demonstração.
COLHEITA_KG = (40, 55, 70, 95, 120, 110, 90, 105, 130, 150, 165, 120)


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def fonte(tamanho):
    return ImageFont.truetype(str(fonte_do_sistema()), tamanho)


def canteiros(destino, largura=1600, altura=1000, semente=3):
    """Vista de cima de seis canteiros, com mudas em três tons de verde."""
    aleatorio = random.Random(semente)
    im = Image.new("RGB", (largura, altura), rgb("F2F5F3"))
    d = ImageDraw.Draw(im)
    tons = [rgb(T.VERDE_1), rgb(T.VERDE_2), rgb(T.VERDE_4)]
    for linha in range(2):
        for coluna in range(3):
            x0 = 90 + coluna * 490
            y0 = 90 + linha * 430
            d.rounded_rectangle((x0, y0, x0 + 440, y0 + 380), 28,
                                fill=rgb("DFEDE6"), outline=rgb("B9D2C6"),
                                width=6)
            tom = tons[(linha * 3 + coluna) % 3]
            for _ in range(38):
                cx = aleatorio.randint(x0 + 40, x0 + 400)
                cy = aleatorio.randint(y0 + 40, y0 + 340)
                r = aleatorio.randint(12, 26)
                d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=tom)
    im.save(destino)


def colheita_gif(destino, largura=960, altura=540, quadros=36):
    """Barras que crescem da esquerda para a direita, uma por mês.

    O quadro final fica parado mais tempo: é o que fica na tela enquanto
    quem apresenta fala. O GIF repete sozinho no PowerPoint.
    """
    maximo = max(COLHEITA_KG)
    base_y, topo_y, x0, passo = altura - 70, 60, 70, (largura - 110) / 12
    pequena, grande = fonte(22), fonte(28)
    imagens = []
    for k in range(quadros):
        im = Image.new("RGB", (largura, altura), rgb(T.BRANCO))
        d = ImageDraw.Draw(im)
        d.line((x0 - 10, base_y, largura - 30, base_y), fill=rgb(T.LINHA_FINA),
               width=3)
        total = 0
        for i, kg in enumerate(COLHEITA_KG):
            # Cada barra começa um pouco depois da anterior e sobe suave.
            t = max(0.0, min(1.0, (k - i * 2) / 10))
            t = 1 - (1 - t) ** 3
            h = (base_y - topo_y) * kg / maximo * t
            x = x0 + i * passo
            cor = T.VERDE_2 if i == COLHEITA_KG.index(maximo) else T.VERDE_4
            if h > 1:
                d.rectangle((x, base_y - h, x + passo * 0.7, base_y),
                            fill=rgb(cor))
            d.text((x + passo * 0.35, base_y + 12), MESES[i],
                   fill=rgb(T.APOIO), font=pequena, anchor="ma")
            total += kg * t
        d.text((largura - 30, 20), "{:,} kg no ano".format(round(total)).replace(",", "."),
               fill=rgb(T.VERDE_1), font=grande, anchor="ra")
        imagens.append(im.convert("P", palette=Image.ADAPTIVE, colors=32))
    # O primeiro quadro é o que aparece no PDF e na miniatura, então ele é o
    # gráfico completo; depois as barras crescem de novo.
    imagens.insert(0, imagens[-1])
    duracoes = [1500] + [70] * (quadros - 1) + [2500]
    imagens[0].save(destino, save_all=True, append_images=imagens[1:],
                    duration=duracoes, loop=0, optimize=True)


def broto_mp4(destino, largura=1280, altura=720, segundos=6, fps=15):
    """Um caule que sobe e abre folhas. Vídeo curto, sem áudio, para loop."""
    pasta = AQUI / "cache" / "_quadros_broto"
    pasta.mkdir(parents=True, exist_ok=True)
    total = segundos * fps
    for k in range(total):
        t = min(1.0, k / (total * 0.8))
        im = Image.new("RGB", (largura, altura), rgb("F2F5F3"))
        d = ImageDraw.Draw(im)
        d.rectangle((0, altura - 120, largura, altura), fill=rgb("8A6A4A"))
        topo = altura - 120 - 480 * t
        cx = largura // 2
        d.line((cx, altura - 120, cx, topo), fill=rgb(T.VERDE_1), width=14)
        for j, y_rel in enumerate((0.25, 0.5, 0.75)):
            abre = max(0.0, min(1.0, (t - y_rel * 0.8) / 0.25))
            if abre <= 0:
                continue
            y = altura - 120 - 480 * y_rel
            lado = -1 if j % 2 else 1
            comp = 150 * abre
            folha = [(cx, y), (cx + lado * comp, y - 60 * abre),
                     (cx + lado * comp * 0.6, y + 10)]
            d.polygon(folha, fill=rgb(T.VERDE_2 if j % 2 else T.VERDE_4))
        oscila = math.sin(k / fps * 2) * 4
        d.ellipse((cx - 30 + oscila, topo - 30, cx + 30 + oscila, topo + 30),
                  fill=rgb(T.VERDE_2))
        im.save(pasta / ("q%03d.png" % k))
    _ffmpeg("-framerate", str(fps), "-i", str(pasta / "q%03d.png"),
            "-c:v", "libx264", "-crf", "24", "-pix_fmt", "yuv420p", "-an",
            str(destino))
    shutil.rmtree(pasta)


def main():
    canteiros(ASSETS / "canteiros.png")
    colheita_gif(ASSETS / "colheita.gif")
    broto_mp4(ASSETS / "broto.mp4")
    print("ativos gerados em", ASSETS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
