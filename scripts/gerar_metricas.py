# -*- coding: utf-8 -*-
"""Extrai a largura de cada caractere de uma família e grava o módulo medido.

Medir texto exige a fonte instalada, e o CI roda em uma máquina limpa. Em vez
de depender da fonte em tempo de validação, a largura de cada caractere fica
gravada no repositório, normalizada pelo tamanho da fonte. Rode este script de
novo apenas se uma família tipográfica usada pelo kit mudar.

    .venv/Scripts/python.exe scripts/gerar_metricas.py
    .venv/Scripts/python.exe scripts/gerar_metricas.py --familia arial

Montserrat é a família da identidade `escuro`. Arial é a família do modelo de
apresentação do IFES, seguida pelo tema em `kit/tema_ifes.py`. Cada uma
grava o seu próprio módulo, e `kit/medidas.py` escolhe a tabela na hora de
medir.
"""
import sys
from pathlib import Path

from PIL import ImageFont

RAIZ = Path(__file__).resolve().parent.parent
TAMANHO = 512  # medir grande reduz o erro de arredondamento para inteiro

PASTAS = (
    Path.home() / "AppData/Local/Microsoft/Windows/Fonts",
    Path("C:/Windows/Fonts"),
    Path("/usr/share/fonts"),
)

FAMILIAS = {
    "montserrat": {
        "nome": "Montserrat",
        "destino": "_metricas.py",
        "arquivos": {"regular": "Montserrat-Regular.ttf",
                     "negrito": "Montserrat-Bold.ttf"},
    },
    "arial": {
        "nome": "Arial",
        "destino": "_metricas_arial.py",
        "arquivos": {"regular": "arial.ttf", "negrito": "arialbd.ttf"},
    },
}

# Latim-1 útil mais os sinais que os decks usam. Sem travessões, por política.
CARACTERES = "".join(chr(c) for c in range(32, 127))
CARACTERES += "áàâãäéêëíïóôõöúüçñÁÀÂÃÄÉÊËÍÏÓÔÕÖÚÜÇÑºª°§µ€£¢¤¬±×÷…“”‘’"


def _acha(nome):
    for pasta in PASTAS:
        alvo = pasta / nome
        if alvo.exists():
            return alvo
        if pasta.exists():
            for achado in pasta.rglob(nome):
                return achado
    return None


def gerar(chave):
    familia = FAMILIAS[chave]
    tabelas = {}
    for estilo, nome in familia["arquivos"].items():
        caminho = _acha(nome)
        if caminho is None:
            print("fonte não encontrada:", nome)
            return 1
        fonte = ImageFont.truetype(str(caminho), TAMANHO)
        tabelas[estilo] = {c: round(fonte.getlength(c) / TAMANHO, 5)
                           for c in CARACTERES}
        print("medido:", caminho.name, len(tabelas[estilo]), "caracteres")

    linhas = [
        '# -*- coding: utf-8 -*-',
        '"""Larguras de caractere em %s, em múltiplos do corpo da fonte.'
        % familia["nome"],
        '',
        'Arquivo gerado por `scripts/gerar_metricas.py`. Não edite na mão.',
        '"""',
    ]
    for estilo in ("regular", "negrito"):
        itens = ", ".join("%r: %s" % (c, v) for c, v in tabelas[estilo].items())
        linhas.append("%s = {%s}" % (estilo.upper(), itens))
    linhas.append("")
    linhas.append("# Usado para qualquer caractere fora da tabela.")
    media = sum(tabelas["regular"].values()) / len(tabelas["regular"])
    linhas.append("MEDIA_DAS_LARGURAS = %.5f" % media)
    linhas.append("")
    destino = RAIZ / "kit" / familia["destino"]
    destino.write_text("\n".join(linhas), encoding="utf-8")
    print("gravado:", destino)
    return 0


def main(argumentos=None):
    argumentos = list(sys.argv[1:] if argumentos is None else argumentos)
    chave = "montserrat"
    if "--familia" in argumentos:
        chave = argumentos[argumentos.index("--familia") + 1].lower()
    if chave not in FAMILIAS:
        print("família desconhecida: %s. Use uma de: %s"
              % (chave, ", ".join(sorted(FAMILIAS))))
        return 1
    return gerar(chave)


if __name__ == "__main__":
    raise SystemExit(main())
