# -*- coding: utf-8 -*-
"""Deck: o padrão do slidecraft, apresentado dentro do próprio padrão.

Cada slide explica uma regra do repositório e, ao mesmo tempo, a cumpre.
Serve para apresentar o repositório a quem vai usar, e como exemplo de deck
completo no modelo IFES.

    slide 1    capa em cascata
    slide 2    os dois caminhos, em cartões com seta
    slide 3    regra de ouro e vícios de IA: antes e depois
    slide 4    regras de escrita, em quatro cartões
    slide 5    três números que sobem
    slide 6    linha do tempo: a ordem de montagem de um slide
    slide 7    GIF gerado em Python: a conferência do validador
    slide 8    vídeo gerado em código: o fade por preto
    slides 9 e 10   Morph entre as identidades
    slide 11   que movimento usar
    slide 12   encerramento

    .venv/Scripts/python.exe decks/padrao/gera_ativos.py
    .venv/Scripts/python.exe decks/padrao/build.py
"""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(RAIZ))

from pptx.util import Inches  # noqa: E402

from kit import base  # noqa: E402

base.ASSETS = AQUI / "assets"
base.CACHE = AQUI / "cache"
base.CACHE.mkdir(exist_ok=True)

from kit import tema_ifes as T  # noqa: E402
from kit.animacao import monta_timing  # noqa: E402
from kit.clipes import ultimo_quadro  # noqa: E402
from kit.coreografia import efeitos_de_formas  # noqa: E402
from kit.editorial import notas  # noqa: E402
from kit.layouts_ifes import (cabecalho, capa, cartao,  # noqa: E402
                              cartoes_de_numeros, chevron, chip, corpo,
                              destaque, fonte, imagem, linha_do_tempo, novo,
                              numero, rotulo, texto)
from kit.numeros import inteiro, tocar_junto  # noqa: E402
from kit.slides import anima, inserir_video  # noqa: E402
from kit.tema_ifes import nova_apresentacao_ifes  # noqa: E402
from kit.transicoes import aplicar_em_todos  # noqa: E402

ASSETS = AQUI / "assets"
VIDEO = AQUI / "video"
SAIDA = RAIZ / "saida" / "padrao.pptx"
REPOSITORIO = "Fonte: repositório slidecraft, novembro de 2026."


def efeitos(grupos, duracao=450):
    return efeitos_de_formas(grupos, duracao=duracao)


def _cartoes(s, blocos, y=1.95, altura=2.3, com_seta=False, inicio=500):
    """Cartões numerados lado a lado. blocos: lista de (título, texto)."""
    folga = 0.30
    largura = (T.UTIL - folga * (len(blocos) - 1)) / len(blocos)
    grupos = []
    for i, (nome, descricao) in enumerate(blocos):
        x = T.MARGEM + i * (largura + folga)
        formas = [cartao(s, x, y, largura, altura, (i % 4) + 1),
                  numero(s, x + 0.2, y + 0.2, str(i + 1)),
                  texto(s, x + 0.2, y + 0.8, largura - 0.4, 0.35, nome,
                        T.CORPO["cartao_titulo"], T.VERDE_1, negrito=True),
                  corpo(s, x + 0.2, y + 1.25, largura - 0.4, 0.9, descricao)]
        if com_seta and i < len(blocos) - 1:
            formas.append(chevron(s, x + largura + 0.07, y + altura / 2 - 0.12))
        grupos.append((inicio + i * 300, formas))
    return grupos


# ---------------------------------------------------------------- os slides

def s01_capa(prs):
    s, _, titulo, linha2, assinatura = capa(
        prs, "O padrão slidecraft",
        "Apresentações com estrutura, movimento e sem cara de IA",
        "Leonardo Baptista  ·  2026")
    monta_timing(s, efeitos([(0, [titulo]), (320, [linha2]),
                             (560, [assinatura])], duracao=520))
    notas(s, "Este deck apresenta o padrão do repositório e, ao mesmo tempo, "
             "segue cada regra que apresenta.")


def s02_caminhos(prs):
    s = novo(prs)
    t, sub = cabecalho(s, "Dois caminhos até o arquivo final",
                       "Do zero ou a partir de uma apresentação que já existe.")
    grupos = _cartoes(s, [
        ("Pedido", "Tema, público e\nduração, ou um .pptx."),
        ("Perguntas", "Uma mensagem só,\ncom padrão sugerido."),
        ("Roteiro", "Uma linha por slide,\naprovada antes."),
        ("Arquivo", "Gerado, validado\ne conferido.")], com_seta=True)
    faixa = destaque(s, 4.8, "Nada é gerado sem roteiro aprovado.")
    fonte(s, REPOSITORIO)
    anima(s, [(0, [t]), (240, [sub])] + grupos + [(1800, list(faixa))])
    notas(s, "Com um .pptx, a primeira pergunta é se o design do original "
             "fica ou se passa para o padrão do repositório.")


def s03_regra_de_ouro(prs):
    s = novo(prs)
    t, sub = cabecalho(s, "Regra de ouro: nenhuma barra",
                       "O mesmo conteúdo com os vícios típicos de IA e dentro "
                       "do padrão.")
    r1 = rotulo(s, T.MARGEM, 1.55, "Com os vícios")
    m1, f1 = imagem(s, ASSETS / "vicio_antes.png", T.MARGEM, 1.85, 5.1, 2.95)
    x = T.MARGEM + 5.4
    r2 = rotulo(s, x, 1.55, "Dentro do padrão")
    m2, f2 = imagem(s, ASSETS / "vicio_depois.png", x, 1.85, 5.1, 2.95)
    l1 = corpo(s, T.MARGEM, 4.95, 5.1, 0.6, "Barra ao lado do texto, filete "
               "sobre o título, travessões, sete itens e ícones decorativos.")
    l2 = corpo(s, x, 4.95, 5.1, 0.6, "Título que diz o fato, três itens, "
               "frase de fecho em negrito e fonte do dado.")
    faixa = destaque(s, 5.65, "Hierarquia se faz com negrito, corpo e espaço, "
                              "nunca com barra.")
    fonte(s, "Fonte: imagens geradas em código para este deck; o validador "
             "reprova barra num slide de verdade.")
    anima(s, [(0, [t]), (240, [sub]), (600, [r1, m1, f1, l1]),
              (1300, [r2, m2, f2, l2]), (2100, list(faixa))])
    notas(s, "À esquerda, só como imagem: num slide de verdade o validador "
             "reprovaria a barra. A única barra permitida é a da linha do "
             "tempo, porque ela é o próprio conteúdo.")


def s04_escrita(prs):
    s = novo(prs)
    t, sub = cabecalho(s, "Escrita que não denuncia a origem",
                       "Quatro regras, duas delas cobradas por código.")
    grupos = _cartoes(s, [
        ("Sem travessão", "Dois pontos, vírgula,\nparênteses ou ponto."),
        ("Título com fato", "Diz o que o slide\nmostra, sem efeito."),
        ("Até quatro itens", "O resto vira\noutro slide."),
        ("Dado com fonte", "Linha de fonte em\ntodo slide com número.")])
    faixa = destaque(s, 4.8, "Se o slide servisse para qualquer apresentação, "
                             "ele é genérico demais.")
    fonte(s, REPOSITORIO)
    anima(s, [(0, [t]), (240, [sub])] + grupos + [(1800, list(faixa))])
    notas(s, "O travessão é recusado na geração e a lista longa, nas "
             "composições. Título e fonte do dado dependem de quem escreve.")


def s05_numeros(prs):
    s = novo(prs)
    t, sub = cabecalho(s, "O padrão em três números",
                       "O que garante que todo deck sai igual.")
    grupos, filmes = cartoes_de_numeros(
        s, [("Testes automáticos", 58, inteiro, "a cada mudança no kit"),
            ("Identidades", 3, inteiro, "IFES, escuro e importada"),
            ("Efeitos de entrada", 2, inteiro, "fade e wipe, nada mais")],
        VIDEO)
    faixa = destaque(s, 5.0, "Pouco vocabulário, repetido sempre igual, é o "
                             "que parece sistema.")
    fonte(s, REPOSITORIO)
    anima(s, [(0, [t]), (240, [sub])] + grupos + [(2200, list(faixa))])
    tocar_junto(s, filmes)
    notas(s, "Números estratégicos entram contando. Parado ou em PDF, o slide "
             "mostra o valor final.")


def s06_ordem(prs):
    s = novo(prs)
    t, sub = cabecalho(s, "A ordem de montagem de um slide",
                       "Trocar a ordem faz o vídeo parar de tocar.")
    marcos = (("1º", "Formas", "Título, cartões e texto."),
              ("2º", "Animação", "Entrada de cada grupo."),
              ("3º", "Mídia", "Vídeo e números que sobem."),
              ("4º", "Transição", "Fade em todos, Morph onde cabe."))
    faixa = destaque(s, 5.9, "A animação reescreve a árvore de tempo; a mídia "
                             "vem depois dela.")
    fonte(s, REPOSITORIO)
    monta_timing(s, efeitos([(0, [t]), (240, [sub])])
                 + linha_do_tempo(s, marcos)
                 + efeitos([(3000, list(faixa))]))
    notas(s, "Linha do tempo: a barra preenche e cada marco aparece quando "
             "ela passa. Os pontos ficam sempre na frente da barra.")


def _midia_com_texto(prs, titulo, subtitulo, itens, frase, nota, arquivo,
                     video=False):
    s = novo(prs)
    t, sub = cabecalho(s, titulo, subtitulo)
    x = T.MARGEM + 6.3
    linhas = [corpo(s, x, 1.8 + i * 0.75, T.DIREITA - x, 0.6, item)
              for i, item in enumerate(itens)]
    faixa = destaque(s, 5.35, frase)
    fonte(s, "Fonte: gerado em código para este deck.")
    grupos = [(0, [t]), (240, [sub])]
    if not video:
        moldura, figura = imagem(s, ASSETS / arquivo, T.MARGEM, 1.6, 6.0, 3.4)
        grupos.append((500, [moldura, figura]))
    grupos += [(900 + i * 300, [l]) for i, l in enumerate(linhas)]
    anima(s, grupos + [(1900, list(faixa))])
    if video:
        capa_video = ultimo_quadro(ASSETS / arquivo,
                                   base.CACHE / (Path(arquivo).stem + ".jpg"))
        inserir_video(s, ASSETS / arquivo, Inches(T.MARGEM), Inches(1.6),
                      Inches(6.0), Inches(3.375), capa=str(capa_video))
    notas(s, nota)


def s07_gif(prs):
    _midia_com_texto(
        prs, "Conferido antes de entregar",
        "GIF gerado em Python, repetindo sozinho na apresentação.",
        ["O validador lê o arquivo, sem abrir o PowerPoint.",
         "Erro reprova; aviso pede uma olhada.",
         "A folha de contato fecha a conferência."],
        "Gerar não basta: alguém olha os slides.",
        "O primeiro quadro do GIF é o estado final, para o PDF e a miniatura.",
        "validador.gif")


def s08_video(prs):
    _midia_com_texto(
        prs, "Fade por preto entre todos os slides",
        "Vídeo curto, sem áudio, em loop, inserido depois da animação.",
        ["Evita o estouro de branco entre fundos diferentes.",
         "O Morph entra só onde a estrutura se repete.",
         "Sem clique: tudo entra sozinho."],
        "Transição discreta é a que ninguém percebe.",
        "Vídeo de 15 a 25 segundos no máximo, sem áudio. O quadro de capa é "
        "o último, para não aparecer vazio.",
        "fade.mp4", video=True)


def _identidades(prs, foco):
    s = novo(prs)
    t, sub = cabecalho(s, "Três identidades, as mesmas regras",
                       "Mesma estrutura em dois slides: o Morph anima a troca.")
    for i, nome in enumerate(("IFES", "Escuro", "Importada")):
        grande = i == foco
        largura, altura = (3.2, 1.2) if grande else (2.4, 0.7)
        x = T.MARGEM + i * 3.5 + (3.5 - largura) / 2
        chip(s, x, 2.6 if grande else 2.85, largura, altura, nome,
             T.VERDE_2 if grande else T.VERDE_NEUTRO,
             tamanho=24 if grande else 14)
    frase = ("IFES é o padrão de todo deck novo." if foco == 0 else
             "Importada mantém o visual de quem trouxe o arquivo.")
    faixa = destaque(s, 5.0, frase)
    fonte(s, REPOSITORIO)
    anima(s, [(0, [t]), (240, [sub]), (600, list(faixa))])
    notas(s, "Morph: dois slides seguidos com as mesmas formas, só o "
             "destaque muda.")


def s11_movimento(prs):
    s = novo(prs)
    t, sub = cabecalho(s, "Que movimento usar",
                       "Animar estrutura, nunca decoração.")
    pares = (("Número estratégico", "sobe de zero até o valor"),
             ("Datas em sequência", "linha do tempo que se desenha"),
             ("Etapas de processo", "cartões em cascata"),
             ("Lista de argumentos", "um item por vez"))
    grupos = []
    for i, (caso, movimento) in enumerate(pares):
        y = 1.75 + i * 0.75
        grupos.append((500 + i * 300, [
            chip(s, T.MARGEM, y, 3.2, 0.48, caso, T.VERDE_1),
            corpo(s, T.MARGEM + 3.5, y + 0.1, 6.5, 0.4, movimento)]))
    faixa = destaque(s, 5.0, "Capa e encerramento ficam quase parados.")
    fonte(s, REPOSITORIO)
    anima(s, [(0, [t]), (240, [sub])] + grupos + [(1800, list(faixa))])
    notas(s, "Onde a animação não significa nada, ela só atrasa a leitura.")


def s12_encerramento(prs):
    s = novo(prs)
    t = texto(s, T.MARGEM, 2.3, T.UTIL, 1.0, "Use, adapte, contribua.", 40,
              T.VERDE_2, negrito=True)
    c = texto(s, T.MARGEM, 3.5, T.UTIL, 0.5,
              "github.com/Leonardo-Baptista/slidecraft", 18, T.TEXTO)
    anima(s, [(0, [t]), (400, [c])])
    notas(s, "Contribuição por pull request, com aprovação do mantenedor.")


def main():
    if not (ASSETS / "fade.mp4").exists():
        print("ativos ausentes. rode antes: decks/padrao/gera_ativos.py")
        return 1
    prs = nova_apresentacao_ifes(perfil="ao_vivo", divulgacao="publico")
    prs.core_properties.title = "O padrão slidecraft"
    for construir in (s01_capa, s02_caminhos, s03_regra_de_ouro, s04_escrita,
                      s05_numeros, s06_ordem, s07_gif, s08_video):
        construir(prs)
    _identidades(prs, 0)
    _identidades(prs, 2)
    s11_movimento(prs)
    s12_encerramento(prs)
    aplicar_em_todos(prs, morph_em=(10,))
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(SAIDA))
    print("gerado:", SAIDA, "|", len(prs.slides._sldIdLst), "slides")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
