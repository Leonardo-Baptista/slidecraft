# -*- coding: utf-8 -*-
"""Prepara a reformulação de uma apresentação que a pessoa já tem.

    python scripts/importar_pptx.py caminho/da/apresentacao.pptx nome_do_deck

Cria decks/<nome> a partir do modelo (se ainda não existir), copia o arquivo
para assets/original.pptx e extrai para assets/importado/:

    conteudo.json   título, textos, tabelas, gráficos, imagens, vídeos e
                    notas de cada slide
    design.json     cores e fontes do tema, tamanho do slide, margens e
                    layouts do modelo da pessoa
    sNN_*           as imagens e os vídeos de cada slide

Depois disso, o agente lê os dois JSON, pergunta se a pessoa quer manter o
design dela ou passar para o padrão do kit, e escreve o build.py.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

# Saída em UTF-8 também no console do Windows, para acento não virar lixo.
sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from kit.importado import extrair  # noqa: E402


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    origem, nome = Path(sys.argv[1]), sys.argv[2]
    if not origem.exists() or origem.suffix.lower() != ".pptx":
        print("arquivo .pptx não encontrado:", origem)
        return 1
    pasta = RAIZ / "decks" / nome
    if not pasta.exists():
        r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "novo_deck.py"),
                            nome], capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout + r.stderr)
            return 1
    (pasta / "assets").mkdir(exist_ok=True)
    destino = pasta / "assets" / "original.pptx"
    # Reimportar o próprio original.pptx não pode tentar copiar sobre si mesmo.
    if not destino.exists() or not destino.samefile(origem):
        shutil.copyfile(origem, destino)
    conteudo = extrair(origem, pasta)
    dados = json.loads(conteudo.read_text(encoding="utf-8"))
    design = json.loads((conteudo.parent / "design.json")
                        .read_text(encoding="utf-8"))

    print("importado:", origem.name, "->", "decks/%s" % nome)
    print("slides: %d   tamanho: %s x %s pol   fontes: %s / %s"
          % (len(dados["slides"]), design["largura"], design["altura"],
             design["fontes"]["titulo"], design["fontes"]["corpo"]))
    print("cores do tema:", ", ".join("%s=%s" % kv
                                      for kv in design["cores"].items()))
    print("layouts:", "; ".join(l["nome"] for l in design["layouts"]))
    print()
    for s in dados["slides"]:
        partes = ["%d textos" % len(s["textos"])]
        for chave in ("tabelas", "graficos", "imagens", "videos"):
            if s[chave]:
                partes.append("%d %s" % (len(s[chave]), chave))
        if s["notas"]:
            partes.append("notas")
        print("  %2d  %-40s %s" % (s["slide"], (s["titulo"] or "(sem título)")[:40],
                                   ", ".join(partes)))
    print()
    print("conteúdo em", conteudo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
