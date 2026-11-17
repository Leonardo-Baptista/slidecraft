# -*- coding: utf-8 -*-
"""Gera, valida e prepara a revisão de um deck, num comando só.

    .venv/Scripts/python.exe scripts/produzir.py exemplo
    .venv/Scripts/python.exe scripts/produzir.py exemplo --sem-imagens

Sem argumento, roda todos os decks. Serve para conferir o repositório inteiro
depois de mexer no kit. Pastas começando com sublinhado são modelo, não deck, e
ficam fora da varredura: peça pelo nome se quiser rodar o `_modelo`.

    .venv/Scripts/python.exe scripts/produzir.py

O resultado considera todas as etapas pedidas: gerar os ativos, gerar o
arquivo, validar e produzir as imagens de revisão. Uma etapa que falhou nunca
termina como sucesso.

Gerar as imagens prepara a revisão visual. Olhar os slides continua sendo
trabalho de gente, e o comando diz isso no fim.

Codigo de saida: 0 tudo limpo, 1 algum aviso, 2 erro ou etapa que falhou.
"""
import subprocess
import sys
from pathlib import Path

# Saída em UTF-8 também no console do Windows, para acento não virar lixo.
sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
PYTHON = RAIZ / ".venv" / "Scripts" / "python.exe"
DECKS = RAIZ / "decks"
SAIDA = RAIZ / "saida"


def executar(argumentos, titulo):
    r = subprocess.run([str(PYTHON if PYTHON.exists() else sys.executable)]
                       + [str(a) for a in argumentos],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=str(RAIZ))
    saida = (r.stdout or "") + (r.stderr or "")
    if r.returncode not in (0, 1, 2):
        print("  %s: falhou" % titulo)
        print("    " + saida.strip().splitlines()[-1][:160])
    return r.returncode, saida


def nome_do_arquivo(deck, saida_build):
    """Descobre o .pptx pelo que o build imprimiu."""
    for linha in saida_build.splitlines():
        if "gerado:" in linha:
            caminho = linha.split("gerado:")[1].split("|")[0].strip()
            return Path(caminho)
    candidato = SAIDA / (deck + ".pptx")
    return candidato if candidato.exists() else None


def produzir(deck, com_imagens=True):
    build = DECKS / deck / "build.py"
    if not build.exists():
        print("deck sem build.py:", deck)
        return 2

    print("=" * 62)
    print(deck)
    print("=" * 62)

    etapas = {}
    ativos = DECKS / deck / "gera_ativos.py"
    if ativos.exists():
        codigo_ativos, saida_ativos = executar([ativos], "ativos")
        etapas["ativos"] = codigo_ativos == 0
        if codigo_ativos == 0:
            print("  ativos gerados")
        else:
            print("  ativos: FALHOU")
            print("    " + (saida_ativos.strip().splitlines()
                            or ["sem saida"])[-1][:200])
            return 2

    codigo, saida = executar([build], "build")
    if codigo != 0:
        print("  geração falhou")
        print("    " + (saida.strip().splitlines() or ["sem saida"])[-1][:200])
        return 2
    arquivo = nome_do_arquivo(deck, saida)
    if arquivo is None or not arquivo.exists():
        print("  não encontrei o arquivo gerado")
        return 2
    print("  gerado: %s, %.1f MB" % (arquivo.name, arquivo.stat().st_size / 1e6))

    codigo_validacao, relatorio = executar(
        [RAIZ / "scripts" / "validar_deck.py", arquivo], "validação")
    for linha in relatorio.splitlines():
        limpa = linha.strip()
        if set(limpa) <= {"-"}:      # a regua da tabela não interessa aqui
            continue
        if limpa.startswith("- ") or limpa in ("ERROS", "AVISOS"):
            print("  " + limpa)
    if codigo_validacao == 0:
        print("  validação: limpa")

    if com_imagens:
        codigo_export, _ = executar(
            [RAIZ / "scripts" / "exportar_slides.py", arquivo, "--contato"],
            "exportacao")
        pasta = arquivo.parent / ("_slides_" + arquivo.stem)
        gerou = codigo_export == 0 and (pasta / "contato.png").exists()
        etapas["imagens"] = gerou
        if gerou:
            print("  imagens de revisão: %s" % (pasta / "contato.png"))
        else:
            print("  imagens de revisão: FALHOU, confira se o arquivo esta "
                  "fechado no PowerPoint")

    # Uma etapa pedida que falhou não pode terminar como sucesso. Gerar as
    # imagens prepara a revisão; olhar os slides continua sendo com voce.
    if not all(etapas.values()):
        return 2
    return codigo_validacao


def main():
    argumentos = [a for a in sys.argv[1:] if not a.startswith("--")]
    com_imagens = "--sem-imagens" not in sys.argv

    if argumentos:
        decks = argumentos
    else:
        # Pasta comecando com sublinhado e modelo, não deck. O _modelo acusa
        # texto de exemplo por construcao, e poluiria a varredura.
        decks = sorted(p.name for p in DECKS.iterdir()
                       if (p / "build.py").exists()
                       and not p.name.startswith("_"))

    # As regras de escrita valem para o repositório todo, e não só para os
    # slides: um travessão num comentário passa despercebido e reaparece no
    # próximo texto copiado dali.
    codigo_texto, relatorio_texto = executar(
        [RAIZ / "scripts" / "verificar_texto.py"], "escrita")
    if codigo_texto != 0:
        print("=" * 62)
        print("escrita do repositório")
        print("=" * 62)
        for linha in relatorio_texto.strip().splitlines()[:12]:
            print("  " + linha.strip())
        print()

    pior = codigo_texto
    for deck in decks:
        pior = max(pior, produzir(deck, com_imagens))
        print()

    print("=" * 62)
    print({0: "tudo limpo", 1: "com avisos", 2: "com erros ou etapa que falhou"}[pior])
    if pior == 0 and com_imagens:
        print("as imagens de revisão estao prontas. falta olhar os slides.")
    return pior


if __name__ == "__main__":
    raise SystemExit(main())
