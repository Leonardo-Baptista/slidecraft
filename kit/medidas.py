# -*- coding: utf-8 -*-
"""Mede texto antes de renderizar, para prever quebra de linha e colisão.

O python-pptx grava o XML, e quem quebra a linha é o PowerPoint na hora de
abrir. Sem medir, um título que ganha uma palavra passa a ocupar três linhas e
cobre a linha de apoio logo abaixo, e nada no processo acusa.

Aqui a largura de cada caractere vem de `kit/_metricas.py` e de
`kit/_metricas_arial.py`, gerados a partir das fontes reais. A conta reproduz a
quebra do PowerPoint: quebra por palavra, palavra longa demais quebra no meio,
entrelinha multiplica a altura da linha.

    from kit.medidas import altura_do_texto, linhas_do_texto
    altura_do_texto("Título longo", largura=Inches(5), tamanho=30)

Montserrat é a família da identidade `escuro` e o padrão de toda função. Os
decks montados sobre o modelo IFES usam Arial, e passam `familia="arial"`
ou chamam `usar_familia("arial")` uma vez no início do build. Sem isso, um
título em Arial seria medido com a tabela da Montserrat e a previsão de quebra
sairia errada, que é exatamente o erro que este módulo existe para evitar.
"""
from pptx.util import Emu, Inches, Pt

from kit import _metricas, _metricas_arial

# Recuo interno padrão de uma caixa de texto do PowerPoint, nos dois lados.
RECUO_LATERAL = Inches(0.1)
RECUO_VERTICAL = Inches(0.05)

# Altura da caixa de linha de cada família, em múltiplos do corpo da fonte.
FAMILIAS = {
    "montserrat": (_metricas, 1.21),
    "arial": (_metricas_arial, 1.15),
}
PADRAO_DE_FAMILIA = "montserrat"
# A caixa de linha da Montserrat mede cerca de 1,21 vez o corpo da fonte.
ALTURA_DE_LINHA = FAMILIAS[PADRAO_DE_FAMILIA][1]


def usar_familia(nome):
    """Troca a família assumida por quem não passa `familia` explicitamente.

    Existe para o build de um deck inteiro declarar a fonte uma vez, em vez de
    repetir o argumento em cada medida. Devolve o nome anterior, para quem
    precisar restaurar.
    """
    global PADRAO_DE_FAMILIA, ALTURA_DE_LINHA
    nome = _conferida(nome)
    anterior = PADRAO_DE_FAMILIA
    PADRAO_DE_FAMILIA = nome
    ALTURA_DE_LINHA = FAMILIAS[nome][1]
    return anterior


def _conferida(nome):
    chave = str(nome or PADRAO_DE_FAMILIA).lower()
    if chave not in FAMILIAS:
        raise ValueError("Família sem tabela de medidas: %s" % nome)
    return chave


def altura_de_linha(familia=None):
    """Altura da caixa de linha da família, em múltiplos do corpo."""
    return FAMILIAS[_conferida(familia)][1]


def largura_do_trecho(trecho, tamanho, negrito=False, familia=None):
    """Largura de um trecho sem quebras, em polegadas."""
    modulo = FAMILIAS[_conferida(familia)][0]
    tabela = modulo.NEGRITO if negrito else modulo.REGULAR
    soma = sum(tabela.get(c, modulo.MEDIA_DAS_LARGURAS)
               for c in trecho)
    return soma * float(tamanho) / 72.0


def linhas_do_texto(conteudo, largura, tamanho, negrito=False, familia=None):
    """Linhas que o texto ocupa dentro da largura dada.

    `largura` aceita Emu, Length ou polegadas em float. Devolve a lista de
    linhas, já considerando as quebras explícitas com barra n.
    """
    util = _em_polegadas(largura) - Emu(RECUO_LATERAL).inches
    if util <= 0:
        return list(str(conteudo).split("\n"))
    saida = []
    for paragrafo in str(conteudo).split("\n"):
        palavras = paragrafo.split(" ")
        atual = ""
        for palavra in palavras:
            tentativa = palavra if not atual else atual + " " + palavra
            if (largura_do_trecho(tentativa, tamanho, negrito, familia) <= util
                    or not atual):
                atual = tentativa
            else:
                saida.append(atual)
                atual = palavra
            # Palavra sozinha maior que a caixa: o PowerPoint parte no meio.
            while (largura_do_trecho(atual, tamanho, negrito, familia) > util
                   and len(atual) > 1):
                corte = len(atual)
                while corte > 1 and largura_do_trecho(atual[:corte], tamanho,
                                                      negrito, familia) > util:
                    corte -= 1
                saida.append(atual[:corte])
                atual = atual[corte:]
        saida.append(atual)
    return saida


def altura_do_texto(conteudo, largura, tamanho, negrito=False, entrelinha=1.0,
                    espaco_antes=0.0, familia=None):
    """Altura ocupada pelo texto, em polegadas, incluindo o recuo da caixa."""
    quantidade = len(linhas_do_texto(conteudo, largura, tamanho, negrito,
                                     familia))
    corpo = (float(tamanho) / 72.0 * altura_de_linha(familia)
             * max(entrelinha, 1.0))
    return (quantidade * corpo + Emu(RECUO_VERTICAL).inches * 2
            + float(espaco_antes) / 72.0 * max(quantidade - 1, 0))


def _em_polegadas(valor):
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        # Valor grande demais para ser polegada: veio em Emu.
        return Emu(int(valor)).inches if valor > 100 else float(valor)
    return Emu(int(valor)).inches


def cabe(conteudo, largura, altura, tamanho, negrito=False, entrelinha=1.0,
         familia=None):
    """Diz se o texto cabe na caixa declarada."""
    return altura_do_texto(conteudo, largura, tamanho, negrito, entrelinha,
                           familia=familia) <= _em_polegadas(altura) + 0.02


def maior_corpo_que_cabe(conteudo, largura, altura, tamanho, minimo,
                         negrito=False, entrelinha=1.0, passo=0.5,
                         familia=None):
    """Reduz o corpo até o texto caber, sem passar do mínimo de legibilidade.

    Devolve o tamanho escolhido. Quando nem o mínimo cabe, devolve o mínimo: a
    decisão de cortar texto é de quem escreve, não do kit.
    """
    atual = float(tamanho)
    while atual > minimo and not cabe(conteudo, largura, altura, atual,
                                      negrito, entrelinha, familia):
        atual -= passo
    return max(atual, float(minimo))
