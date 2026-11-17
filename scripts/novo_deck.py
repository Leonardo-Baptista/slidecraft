# -*- coding: utf-8 -*-
"""Cria uma apresentação nova a partir do modelo.

    .venv/Scripts/python.exe scripts/novo_deck.py energia_solar

Copia decks/_modelo para decks/<nome>, ajusta o nome do arquivo de saída e
deixa a pasta de ativos pronta. Depois é só editar decks/<nome>/build.py.
"""
import re
import shutil
import sys
from pathlib import Path

# Saída em UTF-8 também no console do Windows, para acento não virar lixo.
sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
MODELO = RAIZ / "decks" / "_modelo"


def valida(nome):
    if not re.fullmatch(r"[a-z0-9_]+", nome):
        raise SystemExit(
            "nome invalido: use apenas minusculas, numeros e sublinhado.\n"
            "exemplo: energia_solar")
    return nome


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    nome = valida(sys.argv[1])
    destino = RAIZ / "decks" / nome
    if destino.exists():
        print("ja existe:", destino)
        return 1

    shutil.copytree(MODELO, destino)
    build = destino / "build.py"
    texto = build.read_text(encoding="utf-8")
    titulo = nome.replace("_", " ").title()
    texto = texto.replace('NOME = "Modelo"', 'NOME = "%s"' % titulo)
    texto = texto.replace('SAIDA = RAIZ / "saida" / "modelo.pptx"',
                          'SAIDA = RAIZ / "saida" / "%s.pptx"' % nome)
    texto = texto.replace(
        '"""Modelo de deck. Copie esta pasta para comecar uma apresentação nova.',
        '"""Deck: %s.' % titulo)
    build.write_text(texto, encoding="utf-8")

    (destino / "assets").mkdir(exist_ok=True)
    marcador = destino / "assets" / ".gitkeep"
    if not marcador.exists():
        marcador.touch()

    print("criado: decks/%s" % nome)
    print()
    print("proximos passos:")
    print("  1. ponha as fotos e imagens em decks/%s/assets" % nome)
    print("  2. edite decks/%s/build.py" % nome)
    print("  3. .venv/Scripts/python.exe decks/%s/build.py" % nome)
    print("  4. .venv/Scripts/python.exe scripts/exportar_slides.py "
          "saida/%s.pptx --contato" % nome)
    print("  5. .venv/Scripts/python.exe scripts/validar_deck.py "
          "saida/%s.pptx" % nome)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
