# -*- coding: utf-8 -*-
"""Exporta os slides de um .pptx em PNG, para conferência visual.

Gerar não é suficiente. Colisão de texto, foto mal enquadrada e bloco fora da
margem só aparecem quando alguém olha os slides.

    .venv/Scripts/python.exe scripts/exportar_slides.py saida/meu_deck.pptx
    .venv/Scripts/python.exe scripts/exportar_slides.py saida/meu_deck.pptx --contato

Usa a automação do PowerPoint, então só roda em Windows com PowerPoint
instalado. O arquivo precisa estar fechado.
"""
import subprocess
import sys
from pathlib import Path

# Saída em UTF-8 também no console do Windows, para acento não virar lixo.
sys.stdout.reconfigure(encoding="utf-8")

LARGURA, ALTURA = 1280, 720

POWERSHELL = r"""
$ErrorActionPreference = "Stop"
$pp = New-Object -ComObject PowerPoint.Application
$pres = $pp.Presentations.Open("{arquivo}", $true, $false, $false)
foreach ($s in $pres.Slides) {{
  $nome = "{destino}\s" + ("{{0:d2}}" -f $s.SlideIndex) + ".png"
  $s.Export($nome, "PNG", {largura}, {altura})
}}
"exportados: " + $pres.Slides.Count
$pres.Close()
$pp.Quit()
"""


def contato(pasta, colunas=2):
    """Junta os PNG numa folha de contato, para olhar tudo de uma vez."""
    from PIL import Image, ImageDraw

    arquivos = sorted(pasta.glob("s*.png"))
    if not arquivos:
        return None
    largura, altura = 930, 523
    linhas = (len(arquivos) + colunas - 1) // colunas
    folha = Image.new("RGB", (colunas * largura, linhas * altura), "#2a2a2a")
    desenho = ImageDraw.Draw(folha)
    for i, arquivo in enumerate(arquivos):
        im = Image.open(arquivo).convert("RGB").resize(
            (largura - 8, altura - 8), Image.LANCZOS)
        x, y = (i % colunas) * largura + 4, (i // colunas) * altura + 4
        folha.paste(im, (x, y))
        desenho.rectangle([x, y, x + 40, y + 18], fill="#000000")
        desenho.text((x + 5, y + 4), arquivo.stem, fill="#00E5C0")
    destino = pasta / "contato.png"
    folha.save(destino)
    return destino


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    arquivo = Path(sys.argv[1]).resolve()
    if not arquivo.exists():
        print("arquivo não encontrado:", arquivo)
        return 1

    destino = arquivo.parent / ("_slides_" + arquivo.stem)
    destino.mkdir(exist_ok=True)
    for antigo in destino.glob("*.png"):
        antigo.unlink()

    comando = POWERSHELL.format(arquivo=arquivo, destino=destino,
                                largura=LARGURA, altura=ALTURA)
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                        "-Command", comando], capture_output=True, text=True)
    if r.returncode != 0:
        print("falhou:", (r.stderr or r.stdout).strip()[:400])
        print("confira se o arquivo esta fechado no PowerPoint.")
        return 1
    print(r.stdout.strip())
    print("pasta:", destino)

    if "--contato" in sys.argv:
        folha = contato(destino)
        if folha:
            print("folha de contato:", folha)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
