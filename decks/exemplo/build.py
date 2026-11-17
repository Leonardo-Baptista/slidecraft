# -*- coding: utf-8 -*-
"""Deck de exemplo: tudo o que o kit entrega, num tema inventado.

O tema é uma horta comunitária fictícia, e todos os números são inventados.
O assunto não importa: o deck existe para mostrar, funcionando, cada recurso
do kit na identidade padrão (modelo IFES). Abra o .pptx gerado no PowerPoint
e apresente (F5) para ver as animações.

    slide 1   capa com as três linhas entrando em cascata
    slide 2   linha do tempo: a barra preenche e os marcos entram na passagem
    slide 3   três números estratégicos que sobem de zero até o valor
    slide 4   fluxo de etapas em cartões numerados, da esquerda para a direita
    slide 5   imagem estática em moldura, com texto ao lado
    slide 6   GIF animado gerado em Python
    slide 7   vídeo curto, sem áudio, tocando sozinho em loop
    slides 8 e 9   transição Morph: a mesma estrutura, com outro destaque
    slide 10  encerramento

Todo slide tem transição (fade por preto, ou Morph onde a estrutura se
repete) e notas do apresentador.

    .venv/Scripts/python.exe decks/exemplo/gera_ativos.py
    .venv/Scripts/python.exe decks/exemplo/build.py
"""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(RAIZ))

from pptx.enum.text import PP_ALIGN  # noqa: E402
from pptx.util import Inches  # noqa: E402

from kit import base  # noqa: E402

base.ASSETS = AQUI / "assets"
base.CACHE = AQUI / "cache"
base.CACHE.mkdir(exist_ok=True)

from kit import tema_ifes as T  # noqa: E402
from kit.animacao import monta_timing  # noqa: E402
from kit.coreografia import FADE, efeitos_de_formas  # noqa: E402
from kit.clipes import ultimo_quadro  # noqa: E402
from kit.editorial import notas  # noqa: E402
from kit.layouts_ifes import (cabecalho, capa, cartao,  # noqa: E402
                              cartoes_de_numeros, chevron, chip, corpo,
                              destaque, fonte, imagem, linha_do_tempo, novo,
                              numero, texto)
from kit.numeros import inteiro, porcentagem, tocar_junto  # noqa: E402
from kit.slides import anima, inserir_video  # noqa: E402
from kit.tema_ifes import nova_apresentacao_ifes  # noqa: E402
from kit.transicoes import aplicar_em_todos  # noqa: E402

ASSETS = AQUI / "assets"
VIDEO = AQUI / "video"
SAIDA = RAIZ / "saida" / "exemplo.pptx"
FICTICIO = "Fonte: dados fictícios, criados para demonstrar o kit."


def efeitos(grupos, tipo=FADE, duracao=450):
    return efeitos_de_formas(grupos, tipo=tipo, duracao=duracao)


# ---------------------------------------------------------------- os slides

def s01_capa(prs):
    s, faixa, titulo, linha2, assinatura = capa(
        prs, "Horta Comunitária",
        "Um ano de colheita no bairro",
        "Nome de quem apresenta  |  Instituição  ·  2026")
    monta_timing(s, efeitos([(0, [titulo]), (320, [linha2]),
                             (560, [assinatura])], duracao=520))
    notas(s, "Capa. As três linhas entram em cascata curta. Troque título, "
             "subtítulo e assinatura; o kit ajusta a largura para cada linha "
             "caber em uma só.")


def s02_linha_do_tempo(prs):
    s = novo(prs)
    t, sub = cabecalho(s, "Como a horta começou",
                       "Quatro marcos, do terreno vazio à primeira feira.")
    marcos = (("Jan", "Terreno cedido", "A prefeitura libera a área."),
              ("Mar", "Primeiros canteiros", "Seis canteiros e um mutirão."),
              ("Jun", "Irrigação", "Cisterna e gotejamento."),
              ("Out", "Primeira feira", "Excedente vendido na praça."))
    faixa = destaque(s, 5.9, "Em dez meses, um terreno vazio virou feira.")
    fonte(s, FICTICIO)
    monta_timing(s, efeitos([(0, [t]), (240, [sub])])
                 + linha_do_tempo(s, marcos)
                 + efeitos([(3000, list(faixa))]))
    notas(s, "Linha do tempo: a barra preenche e cada marco entra quando ela "
             "passa por ele. Deixe a animação correr, são uns três segundos.")


def s03_numeros(prs):
    """Os números estratégicos sobem de zero até o valor quando o slide entra."""
    s = novo(prs)
    t, sub = cabecalho(s, "Um ano em três números",
                       "O que a horta entregou de janeiro a dezembro.")
    grupos, filmes = cartoes_de_numeros(
        s, [("Colhido", 1250, inteiro, "quilos de alimento"),
            ("Famílias", 86, inteiro, "atendidas toda semana"),
            ("Aproveitamento", 94, porcentagem(), "da colheita consumida")],
        VIDEO)
    faixa = destaque(s, 5.0, "Mais de uma tonelada de comida, a duas quadras "
                             "de casa.")
    fonte(s, FICTICIO)
    anima(s, [(0, [t]), (240, [sub])] + grupos + [(2200, list(faixa))])
    tocar_junto(s, filmes)      # sempre depois do anima
    notas(s, "Números estratégicos: cada um é um clipe curto que conta de "
             "zero até o valor. Parado ou em PDF, mostra o valor final.")


def s04_fluxo(prs):
    s = novo(prs)
    t, sub = cabecalho(s, "Do canteiro à mesa",
                       "Quatro etapas, toda semana, sempre na mesma ordem.")
    etapas = (("Plantar", "Mudas do viveiro\nentram na terça."),
              ("Regar", "Gotejamento de\nmanhã e à tarde."),
              ("Colher", "Mutirão no\nsábado cedo."),
              ("Distribuir", "Cestas prontas\nao meio-dia."))
    folga = 0.30
    largura = (T.UTIL - folga * 3) / 4
    grupos = []
    for i, (nome, descricao) in enumerate(etapas):
        x = T.MARGEM + i * (largura + folga)
        formas = [cartao(s, x, 1.95, largura, 2.3, (i % 4) + 1),
                  numero(s, x + 0.2, 2.15, str(i + 1)),
                  texto(s, x + 0.2, 2.75, largura - 0.4, 0.35, nome,
                        T.CORPO["cartao_titulo"], T.VERDE_1, negrito=True),
                  corpo(s, x + 0.2, 3.2, largura - 0.4, 0.9, descricao)]
        if i < 3:
            formas.append(chevron(s, x + largura + 0.07, 2.98))
        grupos.append((500 + i * 300, formas))
    faixa = destaque(s, 5.0, "A ordem não muda: é o que mantém a colheita "
                             "previsível.")
    fonte(s, FICTICIO)
    anima(s, [(0, [t]), (240, [sub])] + grupos + [(1900, list(faixa))])
    notas(s, "Fluxo de processo: cascata da esquerda para a direita, um "
             "cartão por vez.")


def _imagem_com_texto(prs, arquivo, titulo, subtitulo, itens, frase, nota):
    """Figura à esquerda, três linhas de texto à direita. Serve aos slides 5 e 6."""
    s = novo(prs)
    t, sub = cabecalho(s, titulo, subtitulo)
    moldura, figura = imagem(s, ASSETS / arquivo, T.MARGEM, 1.6, 6.0, 3.4)
    x = T.MARGEM + 6.3
    linhas = [corpo(s, x, 1.8 + i * 0.75, T.DIREITA - x, 0.6, item)
              for i, item in enumerate(itens)]
    faixa = destaque(s, 5.35, frase)
    fonte(s, FICTICIO)
    anima(s, [(0, [t]), (240, [sub]), (500, [moldura, figura])]
          + [(900 + i * 300, [l]) for i, l in enumerate(linhas)]
          + [(1900, list(faixa))])
    notas(s, nota)
    return s


def s05_imagem(prs):
    _imagem_com_texto(
        prs, "canteiros.png", "Seis canteiros, três culturas",
        "Vista de cima da área, como ficou em março.",
        ["Folhosas nos canteiros da frente.", "Raízes no meio.",
         "Ervas no fundo, perto da cisterna."],
        "Cada cultura no lugar onde a água chega melhor.",
        "Imagem estática: ponha o arquivo em assets/ e passe o nome. A "
        "moldura encaixa a imagem sem deformar.")


def s06_gif(prs):
    _imagem_com_texto(
        prs, "colheita.gif", "A colheita, mês a mês",
        "O GIF é gerado em Python e repete sozinho na apresentação.",
        ["Pico em novembro, com 165 kg.", "Queda no inverno, como esperado.",
         "Dezembro já planta o próximo ano."],
        "A curva acompanha a estação, não o esforço.",
        "GIF animado: gerado em gera_ativos.py com Pillow. O PowerPoint toca "
        "o GIF em loop durante a apresentação.")


def s07_video(prs):
    s = novo(prs)
    t, sub = cabecalho(s, "Seis semanas em seis segundos",
                       "Clipe curto, sem áudio, tocando sozinho em loop.")
    lista = [corpo(s, T.MARGEM + 6.3, 1.8 + i * 0.75, 4.2, 0.6, item)
             for i, item in enumerate(("Broto na primeira semana.",
                                       "Folhas abertas na terceira.",
                                       "Pronto para colher na sexta."))]
    faixa = destaque(s, 5.35, "Vídeo entra depois da animação, sempre.")
    fonte(s, FICTICIO + " Clipe gerado em código.")
    anima(s, [(0, [t]), (240, [sub])]
          + [(700 + i * 300, [l]) for i, l in enumerate(lista)]
          + [(1700, list(faixa))])
    # O vídeo vem depois do anima: monta_timing reescreve a árvore de tempo
    # inteira, e o nó de mídia se perderia.
    # Capa do vídeo é o último quadro: parado ou em PDF, mostra a planta pronta.
    capa_video = ultimo_quadro(ASSETS / "broto.mp4", base.CACHE / "broto_fim.jpg")
    inserir_video(s, ASSETS / "broto.mp4", Inches(T.MARGEM), Inches(1.6),
                  Inches(6.0), Inches(3.375), capa=str(capa_video))
    notas(s, "Vídeo: 15 a 25 segundos no máximo, sem áudio, início "
             "automático e loop. Coloque o .mp4 em assets/.")


def _ciclo(prs, foco):
    """Os mesmos três chips nos slides 8 e 9; muda só o destaque. É o Morph."""
    s = novo(prs)
    t, sub = cabecalho(s, "O ciclo se repete",
                       "Mesma estrutura em dois slides: o Morph anima a troca.")
    nomes = ("Plantar", "Cuidar", "Colher")
    chips = []
    for i, nome in enumerate(nomes):
        grande = i == foco
        largura, altura = (3.2, 1.2) if grande else (2.4, 0.7)
        x = T.MARGEM + i * 3.5 + (3.5 - largura) / 2
        y = 2.6 if grande else 2.85
        chips.append(chip(s, x, y, largura, altura, nome,
                          T.VERDE_2 if grande else T.VERDE_NEUTRO,
                          tamanho=24 if grande else 14))
    faixa = destaque(s, 5.0, ("Plantar é o começo de tudo." if foco == 0 else
                              "Colher é a recompensa, e o próximo plantio."))
    fonte(s, FICTICIO)
    anima(s, [(0, [t]), (240, [sub]), (600, [list(faixa)])])
    notas(s, "Morph: dois slides seguidos com as mesmas formas. Em "
             "aplicar_em_todos, morph_em recebe o número do segundo slide.")


def s10_encerramento(prs):
    s = novo(prs)
    t = texto(s, T.MARGEM, 2.3, T.UTIL, 1.0, "Obrigado!", 44, T.VERDE_2,
              negrito=True)
    c = texto(s, T.MARGEM, 3.5, T.UTIL, 0.5, "contato@exemplo.org", 18,
              T.TEXTO, alinhamento=PP_ALIGN.LEFT)
    anima(s, [(0, [t]), (400, [c])])
    notas(s, "Encerramento: fica na tela durante as perguntas.")


def main():
    if not (ASSETS / "broto.mp4").exists():
        print("ativos ausentes. rode antes: decks/exemplo/gera_ativos.py")
        return 1
    prs = nova_apresentacao_ifes(perfil="ao_vivo", divulgacao="publico")
    prs.core_properties.title = "Horta Comunitária"
    for construir in (s01_capa, s02_linha_do_tempo, s03_numeros, s04_fluxo,
                      s05_imagem, s06_gif, s07_video):
        construir(prs)
    _ciclo(prs, 0)
    _ciclo(prs, 2)
    s10_encerramento(prs)
    # Fade por preto em todos; Morph no 9, que repete a estrutura do 8.
    aplicar_em_todos(prs, morph_em=(9,))
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(SAIDA))
    print("gerado:", SAIDA, "|", len(prs.slides._sldIdLst), "slides")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
