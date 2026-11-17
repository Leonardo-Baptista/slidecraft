# -*- coding: utf-8 -*-
"""Composições aprovadas, com conteúdo recebido por parâmetro.

Cada função monta um slide inteiro, já animado, e devolve o slide. O autor
escolhe a composição e entrega o conteúdo: não precisa decidir coordenada,
corpo de fonte nem tempo de animação. É isso que faz duas pessoas diferentes
produzirem slides reconhecíveis como o mesmo material.

As sete composições aqui são as que os dois primeiros decks provaram em uso.
Layout novo entra quando um deck precisar, não antes.

    from kit.layouts import capa, texto_com_foto, comparação
    capa(prs, "Energia solar", "Do telhado à rede", foto="capa.jpg")

Quando a composição não couber, monte o slide na mão com os helpers de
`kit.base` e `kit.slides`. O kit não impede o caso especial, só evita que o
caso comum vire decisão.
"""
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from kit import base
from kit.base import (A, BRANCO, CINZA, CINZA_CLARO, CINZA_ESCURO, CINZA_MEDIO,
                      FUNDO_CLARO, L, MARGEM, PRETO,
                      QUASE_PRETO, TURQUESA, TURQUESA_CLARO, VERDE_ESCURO,
                      abaixo_de, kicker, linha_apoio, marcadores,
                      retangulo, texto, titulo)
from kit.coreografia import FADE, WIPE_CIMA, WIPE_ESQUERDA, barra_de_progresso, efeitos_de_formas
from kit.animacao import monta_timing
from kit.medidas import maior_corpo_que_cabe
from kit.politica import papel
from kit.slides import anima, inserir_video, novo

PASSO_PADRAO = 300   # intervalo entre elementos, em milissegundos
DURACAO_PADRAO = 500


def _quantidade(itens, minimo, maximo, nome):
    if not minimo <= len(itens) <= maximo:
        raise ValueError("%s: use de %d a %d itens; divida o conteúdo em mais slides."
                         % (nome, minimo, maximo))


def _fecho(slide, y, frase, cor_regua=VERDE_ESCURO, cor_texto=TURQUESA,
           largura_regua=Inches(4.6), largura=Inches(6.4), tamanho=12):
    """Régua fina e a frase que o slide quer deixar."""
    regua = retangulo(slide, MARGEM, Inches(y), largura_regua, Pt(2), cor_regua)
    frase = texto(slide, MARGEM, Inches(y + 0.2), largura, Inches(0.5), frase,
                  tamanho, cor_texto, negrito=True, entrelinha=1.3)
    return [regua, frase]


# ------------------------------------------------------------------- 1. capa

def capa(prs, titulo_principal, subtitulo=None, foto=None, rodape=None,
         logo=None, tamanho=44):
    """Abertura. Foto em tela cheia, título à esquerda, sem animação.

    Capa que anima passa insegurança, então esta composição não anima nada.
    `logo` é o caminho de um PNG claro, de fundo transparente; sem ele, a capa
    sai sem logotipo. Posição fixa: canto inferior esquerdo, na margem.
    """
    s = novo(prs, PRETO)
    if foto:
        s.shapes.add_picture(base.foto(foto, 2400, 1350, 0.55, 0.72),
                             0, 0, L, A)
    tit = titulo(s, MARGEM, Inches(3.08), titulo_principal, tamanho=tamanho,
                 largura=Inches(9.4))
    if subtitulo:
        texto(s, MARGEM, Inches(abaixo_de(tit, 4.5, folga=0.14)), Inches(9.0),
              Inches(0.9), subtitulo, 19,
              BRANCO, entrelinha=1.3)
    if logo:
        s.shapes.add_picture(str(logo), MARGEM, Inches(6.3), Inches(1.45))
    if rodape:
        papel(texto(s, Inches(8.4), Inches(6.55), Inches(4.05), Inches(0.35),
                    rodape, 11, TURQUESA, alinhamento=PP_ALIGN.RIGHT,
                    espacamento=0.6), "rodape")
    return s


# -------------------------------------------------------- 2. texto com foto

def texto_com_foto(prs, indice, titulo_slide, itens, secao=None, apoio=None,
                   foto=None, video=None, fecho=None, largura_lateral=5.4,
                   tamanho_titulo=34, y_itens=None):
    """A composição mais usada: painel de texto à esquerda, imagem à direita.

    O título cabe em duas linhas. Passando disso, ele encosta na linha de
    apoio: quebre manualmente com `
` e encurte, em vez de deixar quebrar
    sozinho.

    `video` recebe o caminho de um clipe e substitui a foto. Nesse caso o vídeo
    entra depois da coreografia, que é a ordem que o PowerPoint exige.
    """
    s = novo(prs, PRETO, indice)
    _quantidade(itens, 1, 4, "Texto com foto")
    if not 3 <= largura_lateral <= 7.5:
        raise ValueError("A largura lateral deve estar entre 3 e 7,5 polegadas.")
    lateral = Inches(largura_lateral)
    # A coluna de texto acompanha o painel: painel mais largo, texto mais
    # estreito. Sem isso, dar mais espaco ao video faz o título invadir a
    # imagem.
    texto_util = Inches(13.333 - largura_lateral - 0.9 - 0.45)

    if video:
        retangulo(s, L - lateral, 0, lateral, A, QUASE_PRETO)
    elif foto:
        s.shapes.add_picture(base.foto(foto, int(lateral / 914400 * 300), 2250,
                                       0.85), L - lateral, 0, lateral, A)

    grupos, atraso = [], 0
    cabeca = []
    if secao:
        cabeca.append(kicker(s, MARGEM, Inches(1.1), secao))
    cabeca.append(titulo(s, MARGEM, Inches(1.62), titulo_slide,
                         tamanho=tamanho_titulo, largura=texto_util))
    grupos.append((atraso, cabeca))
    atraso += 350

    if apoio:
        grupos.append((atraso, [linha_apoio(s, MARGEM,
                                            Inches(abaixo_de(cabeca[-1], 3.55)),
                                            apoio,
                                            cor=CINZA_CLARO,
                                            largura=texto_util)]))
        atraso += 350

    inicio_itens = 4.62 if y_itens is None else float(y_itens)
    if inicio_itens < 3.3 or inicio_itens + (len(itens) - 1) * 0.44 + 0.32 > 6.45:
        raise ValueError("Os marcadores não cabem na área disponível antes do fecho.")
    linhas = marcadores(s, MARGEM, Inches(inicio_itens), itens, largura=texto_util)
    for linha in linhas:
        grupos.append((atraso, linha))
        atraso += PASSO_PADRAO

    if fecho:
        grupos.append((atraso + 200, _fecho(s, 6.5, fecho,
                                            largura=texto_util)))

    anima(s, grupos)
    if video:
        largura_video = lateral - Inches(0.5)
        altura = int(largura_video * 0.69)      # proporcao dos clipes do kit
        inserir_video(s, video, L - lateral + Inches(0.25),
                      (A - altura) / 2, largura_video, altura)
    return s


# ------------------------------------------------------------ 3. comparação

def comparacao(prs, indice, titulo_slide, esquerda, direita, apoio=None,
               fecho=None):
    """Duas colunas lado a lado, em fundo claro. Serve de respiro.

    esquerda e direita: (título, [itens]).
    """
    _quantidade(esquerda[1], 1, 4, "Coluna esquerda")
    _quantidade(direita[1], 1, 4, "Coluna direita")
    s = novo(prs, BRANCO, indice)
    tit = titulo(s, MARGEM, Inches(1.12), titulo_slide, cor=PRETO, tamanho=32,
                 largura=Inches(9.0))
    grupos = [(0, [tit])]
    if apoio:
        grupos.append((300, [linha_apoio(s, MARGEM,
                                         Inches(abaixo_de(tit, 1.95)), apoio,
                                         cor=CINZA_ESCURO,
                                         largura=Inches(9.5))]))

    blocos = [
        (esquerda, 0.9, FUNDO_CLARO, PRETO, CINZA_ESCURO, TURQUESA),
        (direita, 7.0, VERDE_ESCURO, BRANCO, TURQUESA_CLARO, BRANCO),
    ]
    atraso = 700
    for (cabeca, itens), x, cor_fundo, cor_tit, cor_item, cor_ponto in blocos:
        caixa = retangulo(s, Inches(x), Inches(2.75), Inches(5.45),
                          Inches(2.75), cor_fundo,
                          linha=CINZA_CLARO if cor_fundo == FUNDO_CLARO else None,
                          espessura=0.75)
        rotulo = texto(s, Inches(x + 0.35), Inches(3.02), Inches(4.8),
                       Inches(0.35), cabeca, 15, cor_tit, negrito=True)
        lista = marcadores(s, Inches(x + 0.35), Inches(3.6), itens,
                           cor=cor_item, tamanho=11.5, passo=Inches(0.44),
                           largura=Inches(4.6), cor_ponto=cor_ponto)
        grupos.append((atraso, [caixa, rotulo] + [f for par in lista for f in par]))
        atraso += 500
    retangulo(s, Inches(6.35), Inches(2.75), Inches(0.65), Inches(2.75), BRANCO)

    if fecho:
        grupos.append((atraso, _fecho(s, 5.85, fecho, cor_regua=CINZA_CLARO,
                                      cor_texto=PRETO, largura_regua=Inches(11.55),
                                      largura=Inches(11.5), tamanho=13.5)))
    anima(s, grupos)
    return s


# ------------------------------------------------------- 4. faixa de etapas

def faixa_de_etapas(prs, indice, titulo_slide, etapas, apoio=None, fecho=None,
                    destaques=(), escada=False, claro=True, y=2.9):
    """Sequência horizontal: fluxo de processo, pipeline ou escada de maturidade.

    etapas: lista de (nome, descricao). Com `escada=True` os blocos crescem da
    esquerda para a direita e entram com wipe de baixo para cima, o que constrói
    a progressão na frente de quem assiste.
    """
    _quantidade(etapas, 2, 4 if escada else 6, "Faixa de etapas")
    s = novo(prs, BRANCO if claro else PRETO, indice)
    tit = titulo(s, MARGEM, Inches(1.12), titulo_slide,
                 cor=PRETO if claro else BRANCO, tamanho=32, largura=Inches(10.0))
    grupos = [(0, [tit])]
    if apoio:
        grupos.append((300, [linha_apoio(s, MARGEM,
                                         Inches(abaixo_de(tit, 1.95)), apoio,
                                         cor=CINZA_ESCURO if claro else CINZA_MEDIO,
                                         largura=Inches(9.5))]))

    quantidade = len(etapas)
    folga = 0.12
    largura = (11.55 - folga * (quantidade - 1)) / quantidade
    base_y = y + 3.5
    atraso = 700
    rotulados = []
    for j, (nome, descricao) in enumerate(etapas):
        x = 0.9 + j * (largura + folga)
        forte = (not destaques) or (j in destaques)
        altura = (1.6 + j * 0.55) if escada else 1.75
        topo = base_y - altura if escada else y
        if escada:
            cor_fundo = [CINZA_CLARO, TURQUESA_CLARO, VERDE_ESCURO, PRETO][
                min(j, 3)]
            cor_nome = BRANCO if j >= 2 else PRETO
            cor_desc = TURQUESA_CLARO if j >= 2 else CINZA_ESCURO
            borda = None
        else:
            cor_fundo = (BRANCO if claro else QUASE_PRETO) if forte else (
                FUNDO_CLARO if claro else QUASE_PRETO)
            cor_nome = (PRETO if claro else BRANCO) if forte else CINZA
            cor_desc = (CINZA_ESCURO if claro else CINZA_MEDIO) if forte else CINZA
            borda = TURQUESA if (forte and destaques) else (
                CINZA_CLARO if claro else CINZA_ESCURO)
        caixa = retangulo(s, Inches(x), Inches(topo), Inches(largura),
                          Inches(altura), cor_fundo, linha=borda,
                          espessura=1.25 if forte else 0.75)
        num = papel(texto(s, Inches(x + 0.18), Inches(topo + 0.16),
                          Inches(0.6), Inches(0.25), "%02d" % (j + 1), 10,
                          TURQUESA if forte else CINZA, negrito=True,
                          espacamento=1.0), "legenda")
        rotulo = texto(s, Inches(x + 0.18), Inches(topo + 0.44),
                       Inches(largura - 0.3), Inches(0.6), nome, 14, cor_nome,
                       negrito=True, entrelinha=1.1)
        detalhe = papel(texto(s, Inches(x + 0.18), Inches(topo + 1.06),
                              Inches(largura - 0.32), Inches(0.6), descricao,
                              9.5, cor_desc, entrelinha=1.2), "legenda")
        rotulados.append((rotulo, detalhe, topo))
        formas = [caixa, num, rotulo, detalhe]
        if j < quantidade - 1 and not escada:
            formas.append(retangulo(s, Inches(x + largura), Inches(y + 0.85),
                                    Inches(folga), Pt(1.5),
                                    TURQUESA if forte else CINZA_CLARO))
        grupos.append((atraso, formas))
        atraso += 250

    # Rotulo de duas linhas cobriria a descricao. Na faixa reta as descricoes
    # desceriam desalinhadas se cada uma seguisse o seu rotulo, entao todas
    # acompanham o rotulo mais alto. Na escada cada degrau tem topo proprio e
    # o ajuste e por bloco.
    if escada:
        for rotulo, detalhe, topo in rotulados:
            detalhe.top = Inches(abaixo_de(rotulo, topo + 1.06, folga=0.04))
    elif rotulados:
        alvo = max(abaixo_de(r, t + 1.06, folga=0.04) for r, _, t in rotulados)
        for _, detalhe, _ in rotulados:
            detalhe.top = Inches(alvo)

    if fecho:
        grupos.append((atraso, _fecho(s, base_y + 0.15 if escada else y + 2.1,
                                      fecho,
                                      cor_regua=CINZA_CLARO if claro else VERDE_ESCURO,
                                      cor_texto=PRETO if claro else TURQUESA,
                                      largura_regua=Inches(11.55),
                                      largura=Inches(11.5), tamanho=13)))
    # A escada constroi os degraus de baixo para cima; o fluxo entra em fade.
    anima(s, grupos, tipo=WIPE_CIMA if escada else FADE)
    return s


# -------------------------------------------------------- 5. linha do tempo

def linha_do_tempo(prs, indice, titulo_slide, marcos, secao=None, apoio=None,
                   duracao_barra=2000, y=3.45):
    """Régua com marcos, preenchida por uma barra turquesa.

    marcos: lista de (rotulo, descricao). Cada marco aparece no instante em que
    a barra passa por ele, o que faz a linha se desenhar sozinha.
    """
    _quantidade(marcos, 2, 6, "Linha do tempo")
    if duracao_barra <= 0:
        raise ValueError("A duração da barra deve ser positiva.")
    s = novo(prs, PRETO, indice)
    grupos = []
    cabeca = []
    if secao:
        cabeca.append(kicker(s, MARGEM, Inches(0.95), secao))
    cabeca.append(titulo(s, MARGEM, Inches(1.35), titulo_slide, tamanho=30,
                         largura=Inches(7.0)))
    grupos.append((0, cabeca))
    if apoio:
        linha = linha_apoio(s, MARGEM, Inches(abaixo_de(cabeca[-1], 2.58)),
                            apoio, largura=Inches(9.5))
        grupos.append((300, [linha]))
        # A regua precisa de espaco para a data, que fica acima dela.
        y = abaixo_de(linha, y, folga=0.52)

    retangulo(s, MARGEM, Inches(y), Inches(11.55), Pt(1.5), CINZA_ESCURO)
    quantidade = len(marcos)
    passo = 11.55 / max(1, quantidade)
    posicoes = [0.9 + j * passo for j in range(quantidade)]
    barra = barra_de_progresso(s, y - 0.015, 0.9, posicoes[-1] + 0.06)

    for j, ((rotulo, descricao), x) in enumerate(zip(marcos, posicoes)):
        atual = j == quantidade - 1
        tam = Pt(13) if atual else Pt(9)
        fracao = (x + 0.06 - 0.9) / max(0.01, (posicoes[-1] + 0.06 - 0.9))
        atraso = 500 + int(duracao_barra * fracao)
        ponto = retangulo(s, Inches(x) - tam / 2 + Pt(1),
                          Inches(y) - tam / 2 + Pt(0.75), tam, tam,
                          TURQUESA if atual else BRANCO, forma=MSO_SHAPE.OVAL)
        data = texto(s, Inches(x - 0.05), Inches(y - 0.45), Inches(2.0),
                     Inches(0.3), rotulo, 15,
                     TURQUESA if atual else BRANCO, negrito=True)
        detalhe = papel(texto(s, Inches(x - 0.05), Inches(y + 0.22),
                              Inches(passo - 0.15), Inches(0.8), descricao,
                              10.5, CINZA_MEDIO, entrelinha=1.25), "legenda")
        grupos.append((atraso, [ponto, data, detalhe]))

    efeitos = efeitos_de_formas(grupos)
    filtro, preset, subtipo = WIPE_ESQUERDA
    efeitos.append((barra.shape_id, filtro, duracao_barra, 500, preset, subtipo))
    monta_timing(s, efeitos)
    return s


# ---------------------------------------------------------- 6. provocacao

def provocacao(prs, pergunta, destaque=None, chamada=None, tamanho=40):
    """Uma pergunta em fundo preto. Serve de virada entre blocos.

    `destaque` entra grande acima da pergunta, para o número ou a palavra que
    carrega o argumento.
    """
    s = novo(prs, PRETO)
    y = 2.35
    if destaque:
        texto(s, MARGEM, Inches(1.5), Inches(11.5), Inches(1.8), destaque, 110,
              TURQUESA, negrito=True)
        y = 4.05
    # A chamada fica no pe do slide, entao a pergunta e que tem de caber no
    # espaco acima dela. Reduzir o corpo preserva a composição; empurrar para
    # baixo a destruiria.
    if chamada:
        disponivel = 6.28 - y
        tamanho = maior_corpo_que_cabe(pergunta, Inches(11.0),
                                       Inches(disponivel), tamanho, 24,
                                       negrito=True, entrelinha=1.12)
    titulo(s, MARGEM, Inches(y), pergunta, tamanho=tamanho, largura=Inches(11.0))
    if chamada:
        # Sem barra lateral: a cor e o negrito já separam a chamada.
        texto(s, MARGEM, Inches(6.4), Inches(9.5), Inches(0.3),
              chamada, 12, TURQUESA, negrito=True)
    return s


# ---------------------------------------------------------- 7. fechamento

def fechamento(prs, frase, contato=None, complemento=None, foto=None,
               qr=None, logo=None):
    """Último slide. Fica parado na tela durante as perguntas, sem animação.

    `logo`, quando passado, vai para o canto inferior direito.
    """
    s = novo(prs, PRETO)
    if foto:
        s.shapes.add_picture(base.foto(foto, 2400, 1350, 0.38, 0.7), 0, 0, L, A)
    tit = titulo(s, MARGEM, Inches(2.93), frase, tamanho=32, largura=Inches(9.6))
    y_contato = abaixo_de(tit, 5.3, folga=0.22)
    if contato:
        texto(s, MARGEM, Inches(y_contato), Inches(5.6), Inches(0.3), contato,
              12.5, TURQUESA, negrito=True)
    if complemento:
        papel(texto(s, MARGEM, Inches(y_contato + 0.33), Inches(5.6),
                    Inches(0.3), complemento, 11, CINZA_MEDIO), "legenda")
    if qr:
        papel(retangulo(s, Inches(10.75), Inches(4.35), Inches(1.85),
                        Inches(1.85), BRANCO), "rodape")
        s.shapes.add_picture(str(qr), Inches(10.87), Inches(4.47),
                             Inches(1.61), Inches(1.61))
    if logo:
        s.shapes.add_picture(str(logo), Inches(10.95), Inches(6.35),
                             Inches(1.45))
    return s
