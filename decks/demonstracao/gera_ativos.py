# -*- coding: utf-8 -*-
"""Cria as imagens do deck de demonstracao, em codigo.

O deck de demonstracao precisa rodar numa copia limpa do repositorio, entao
não pode depender de foto de terceiros nem de imagem de banco. As imagens aqui
sao geradas: não tem licenca, não tem dado de ninguém e saem iguais em qualquer
maquina.

    .venv/Scripts/python.exe decks/demonstracao/gera_ativos.py
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

AQUI = Path(__file__).resolve().parent
ASSETS = AQUI / "assets"
ASSETS.mkdir(exist_ok=True)

TURQUESA = (0x00, 0xE5, 0xC0)
VERDE = (0x00, 0x84, 0x6F)
BRASA = (0xFF, 0x8C, 0x1A)


def _mistura(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def textura_industrial(destino, largura=2400, altura=1350, semente=7):
    """Fundo abstrato com brilho quente, no lugar de uma foto real."""
    random.seed(semente)
    im = Image.new("RGB", (largura, altura), (0, 0, 0))
    d = ImageDraw.Draw(im)

    # brilho central, imitando metal incandescente
    cx, cy = largura * 0.62, altura * 0.58
    for raio in range(int(largura * 0.55), 0, -6):
        t = 1 - raio / (largura * 0.55)
        cor = _mistura((0, 0, 0), BRASA, t ** 3)
        d.ellipse([cx - raio, cy - raio * 0.6, cx + raio, cy + raio * 0.6],
                  fill=cor)

    # estrutura escura em primeiro plano
    for _ in range(18):
        x = random.randint(0, largura)
        largura_barra = random.randint(12, 60)
        d.rectangle([x, 0, x + largura_barra, altura], fill=(6, 6, 8))
    im = im.filter(ImageFilter.GaussianBlur(9))

    # particulas, para a imagem não ficar chapada
    d = ImageDraw.Draw(im)
    for _ in range(400):
        x, y = random.randint(0, largura), random.randint(0, altura)
        r = random.randint(1, 3)
        d.ellipse([x, y, x + r, y + r], fill=_mistura(BRASA, (255, 255, 255),
                                                      random.random()))
    im.save(destino, quality=92)
    return destino


def painel_tecnico(destino, largura=1600, altura=2200, semente=3):
    """Imagem vertical, para o painel lateral da composição texto com foto."""
    random.seed(semente)
    im = Image.new("RGB", (largura, altura), (8, 8, 10))
    d = ImageDraw.Draw(im)
    for j in range(34):
        y = int(altura * j / 34)
        t = abs(math.sin(j / 4.0))
        d.rectangle([0, y, largura, y + 14],
                    fill=_mistura((10, 10, 12), VERDE, t * 0.55))
    cx, cy = largura * 0.5, altura * 0.45
    for raio in range(int(largura * 0.45), 0, -5):
        t = 1 - raio / (largura * 0.45)
        d.ellipse([cx - raio, cy - raio, cx + raio, cy + raio],
                  fill=_mistura((8, 8, 10), TURQUESA, t ** 4))
    im = im.filter(ImageFilter.GaussianBlur(6))
    im.save(destino, quality=92)
    return destino


def main():
    textura_industrial(ASSETS / "capa_demo.jpg")
    painel_tecnico(ASSETS / "painel_demo.jpg")
    textura_industrial(ASSETS / "fechamento_demo.jpg", semente=21)
    print("ativos gerados em", ASSETS)
    for f in sorted(ASSETS.glob("*.jpg")):
        print("  ", f.name)


if __name__ == "__main__":
    main()
