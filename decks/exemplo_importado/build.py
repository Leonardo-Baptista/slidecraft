# -*- coding: utf-8 -*-
"""Exemplo de reformulação mantendo o design da pessoa (identidade importada).

A origem, `assets/original.pptx`, tem três slides com listas longas e números
soltos no meio do texto. Aqui ela é reformulada sem perder o visual: mestre,
faixa, marca, cores e fonte (Georgia) continuam os dela, e o formato 4:3
também. O que muda é a estrutura e o movimento:

    original 1 -> slide 1   capa, nos espaços reservados do layout dela
    original 2 -> slide 2   três números estratégicos que sobem
    original 2 -> slide 3   linha do tempo com barra da esquerda para a direita
    original 3 -> slide 4   próximos passos, um item por vez
                  slide 5   encerramento

Transição em fade por preto em todos, como em qualquer deck do kit.

    .venv/Scripts/python.exe scripts/importar_pptx.py <arquivo.pptx> exemplo_importado
    .venv/Scripts/python.exe decks/exemplo_importado/build.py
"""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(RAIZ))

from pptx.enum.shapes import MSO_SHAPE  # noqa: E402
from pptx.util import Pt  # noqa: E402

from kit import base  # noqa: E402

base.ASSETS = AQUI / "assets"
base.CACHE = AQUI / "cache"
base.CACHE.mkdir(exist_ok=True)

from kit.animacao import DURACAO_BARRA, monta_timing  # noqa: E402
from kit.coreografia import (FADE, WIPE_ESQUERDA,  # noqa: E402
                             barra_de_progresso, efeitos_de_formas,
                             marcos_na_passagem)
from kit.editorial import notas  # noqa: E402
from kit.importado import (abrir_modelo, cor, design, itens,  # noqa: E402
                           limpar, novo, reservado, retangulo, texto, titulo)
from kit.numeros import inteiro, numero_que_sobe, porcentagem  # noqa: E402
from kit.numeros import tocar_junto  # noqa: E402
from kit.politica import papel  # noqa: E402
from kit.slides import anima  # noqa: E402
from kit.transicoes import aplicar_em_todos  # noqa: E402

ORIGEM = AQUI / "assets" / "original.pptx"
VIDEO = AQUI / "video"
SAIDA = RAIZ / "saida" / "exemplo_importado.pptx"


def s1_capa(prs):
    s = novo(prs, "title slide")
    t = titulo(s, "Coleta Seletiva na Escola")
    sub = reservado(s, 1, "Primeiro semestre, em números")
    anima(s, [(0, [t]), (350, [sub])])


def s2_numeros(prs, d):
    s = novo(prs)
    t = titulo(s, "Um semestre em três números")
    x0, util = d["margem_esquerda"], d["largura"] - d["margem_esquerda"] - d["margem_direita"]
    largura = (util - 0.4) / 3
    blocos = (("Recicláveis", 3400, inteiro, "quilos recolhidos"),
              ("Alunos", 620, inteiro, "participaram"),
              ("Separação", 87, porcentagem(), "feita do jeito certo"))
    grupos, filmes = [], []
    for i, (nome, valor, formatar, legenda) in enumerate(blocos):
        x = x0 + i * (largura + 0.2)
        cartao = retangulo(s, x, 2.0, largura, 2.6, "lt2")
        rotulo = texto(s, x + 0.2, 2.2, largura - 0.4, 0.3, nome.upper(), 12,
                       "accent2", negrito=True)
        # O número fica sobre o cartão: `fundo` é a cor exata do cartão.
        n = numero_que_sobe(s, VIDEO / ("numero_%d.mp4" % i), x + 0.2, 2.65,
                            largura - 0.4, 0.9, ate=valor, formatar=formatar,
                            corpo=36, cor=d["cores"]["accent1"],
                            fundo=d["cores"]["lt2"])
        leg = texto(s, x + 0.2, 3.7, largura - 0.4, 0.6, legenda, 14)
        atraso = 500 + i * 350
        grupos.append((atraso, [cartao, rotulo, n, leg]))
        filmes.append((n, atraso))
    fonte = papel(texto(s, x0, 6.55, util, 0.3, "Fonte: relatório da equipe, "
                        "primeiro semestre.", 10, "accent4"), "legenda")
    anima(s, [(0, [t])] + grupos + [(1800, [fonte])])
    tocar_junto(s, filmes)
    limpar(s)
    notas(s, "Agradecer a equipe da limpeza.")


def s3_linha_do_tempo(prs, d):
    s = novo(prs)
    t = titulo(s, "Como o semestre andou")
    x0 = d["margem_esquerda"]
    x1 = d["largura"] - d["margem_direita"]
    marcos = (("Fev", "Dois coletores\nno pátio"),
              ("Abr", "Coletores novos\nem cada andar"),
              ("Jun", "Feira de troca\ncom as famílias"))
    passo = (x1 - x0) / len(marcos)
    y = 3.4
    grupos, centros = [], []
    for i, (mes, descricao) in enumerate(marcos):
        x = x0 + i * passo
        centro = x + 0.12
        centros.append(centro)
        ponto = retangulo(s, x, y - 0.1, 0.24, 0.24, "accent1",
                          forma=MSO_SHAPE.OVAL)
        rot = texto(s, x, y - 0.75, passo - 0.2, 0.4, mes, 20, "dk1",
                    negrito=True, titulo_do_tema=True)
        det = texto(s, x, y + 0.35, passo - 0.2, 0.8, descricao, 14)
        grupos.append([ponto, rot, det])
    barra = barra_de_progresso(s, y, x0, x1, cor=cor(prs, "accent2"),
                               espessura=Pt(4))
    atrasos = marcos_na_passagem(barra, centros, DURACAO_BARRA)
    animacao = efeitos_de_formas([(0, [t])], tipo=FADE)
    animacao += efeitos_de_formas([(400, [barra])], tipo=WIPE_ESQUERDA,
                                  duracao=DURACAO_BARRA)
    animacao += efeitos_de_formas([(400 + a, g) for a, g in zip(atrasos, grupos)],
                                  duracao=380)
    monta_timing(s, animacao)
    limpar(s)


def s4_proximos(prs, d):
    s = novo(prs)
    t = titulo(s, "Próximos passos")
    util = d["largura"] - d["margem_esquerda"] - d["margem_direita"]
    linhas = itens(s, d["margem_esquerda"], 2.2, util,
                   ["Coletor de óleo na cantina",
                    "Oficina com as turmas do 6º ano",
                    "Meta de 5.000 kg no segundo semestre"], tamanho=20,
                   passo=0.8)
    anima(s, [(0, [t])] + [(500 + i * 350, l) for i, l in enumerate(linhas)])
    limpar(s)


def s5_encerramento(prs):
    s = novo(prs, "title slide")
    t = titulo(s, "Obrigado!")
    sub = reservado(s, 1, "Perguntas?")
    anima(s, [(0, [t]), (350, [sub])])


def main():
    if not ORIGEM.exists():
        print("origem ausente. rode antes: decks/exemplo_importado/gera_ativos.py")
        return 1
    prs = abrir_modelo(ORIGEM)
    d = design(prs)
    s1_capa(prs)
    s2_numeros(prs, d)
    s3_linha_do_tempo(prs, d)
    s4_proximos(prs, d)
    s5_encerramento(prs)
    aplicar_em_todos(prs)
    SAIDA.parent.mkdir(exist_ok=True)
    prs.save(str(SAIDA))
    print("gerado:", SAIDA, "|", len(prs.slides._sldIdLst), "slides")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
