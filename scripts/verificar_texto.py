# -*- coding: utf-8 -*-
"""Aplica as regras de escrita a todo o repositório, e não só aos slides.

Duas regras valem em qualquer texto do projeto, incluindo código, comentário,
documentação e mensagem de commit:

1. Nenhum travessão, meia risca, barra horizontal nem sinal de menos
   tipográfico. No lugar deles: dois pontos, vírgula, parênteses, ponto final,
   "a" para intervalo numérico e o hífen comum para negativo.
2. Português do Brasil acentuado. A lista de grafias em `kit.editorial` só
   contém casos inequívocos; palavra ambígua nunca entra ali.

O travessão é erro em qualquer arquivo. A acentuação é erro na documentação e
nos textos de interface, e aviso em comentário e docstring de código, onde o
custo de uma troca errada é maior que o ganho.

    .venv/Scripts/python.exe scripts/verificar_texto.py
    .venv/Scripts/python.exe scripts/verificar_texto.py --corrigir
    .venv/Scripts/python.exe scripts/verificar_texto.py docs/validacao.md

Código de saída: 0 limpo, 1 só com aviso, 2 com erro.
"""
import io
import re
import sys
import tokenize
from pathlib import Path

# Saída em UTF-8 também no console do Windows, para acento não virar lixo.
sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from kit import editorial  # noqa: E402

EXTENSOES = (".py", ".md", ".txt", ".yml", ".yaml", ".json", ".ps1", ".cfg",
             ".toml", ".ini")
# As regras de escrita valem para o que o repositório escreve. Material
# recebido de cliente e pasta de origem entram aqui: acusar travessão numa
# especificação técnica da AMT não corrige nada e ainda esconde os achados
# reais no meio do ruído.
IGNORAR = (".venv", ".git", "saida", "cache", "assets", "__pycache__",
           "node_modules", "referencias", "marca", "_historico",
           "Palestra", "Coqueria AMT")
# Gerado por script, ou dono da própria regra: a grafia ali não é prosa.
# `kit/editorial.py` guarda a lista das grafias erradas, então cada palavra dela
# apareceria aqui como problema, e acentuá-las esvaziaria a regra.
ARQUIVOS_IGNORADOS = ("kit/_metricas.py", "kit/_metricas_arial.py",
                      "kit/editorial.py")
# Em código, uma string de uma palavra só é quase sempre um nome, e não prosa:
# chave de dicionário, papel de forma, metadado, nome de pasta, valor comparado
# com igualdade. Acentuar uma dessas não quebra a compilação, quebra a
# comparação em silêncio na hora de rodar. Prosa tem mais de uma palavra, então
# essa é a linha divisória, e ela dispensa manter uma lista de exceções que
# envelheceria a cada chave nova.
UMA_PALAVRA = re.compile(r"^[\w.-]*$")
# Escape explícito, para o caso raro em que a escrita errada é o assunto: um
# teste da própria regra, ou um exemplo do que não fazer. Basta a marcação no
# fim da linha, e nem o relatório nem a correção mexem naquela linha, tanto
# para a acentuação quanto para o travessão.
MARCA_LITERAL = "grafia-literal"
# Onde a acentuação é cobrada como erro, e não como aviso.
PROSA = (".md", ".txt")

# Hífen duplo ou triplo entre espaços é travessão digitado à mão. Uma régua de
# quatro ou mais hífens é separador visual de comentário, e não pontuação.
COMO_TRAVESSAO = re.compile(r"(?<!-)\s-{2,3}\s(?!-)")

# Palavra de prosa: não encostada em underscore, barra nem ponto de atributo,
# que é como um identificador (nova_apresentacao, kit.animacao, slides/secao)
# se distingue de uma palavra escrita para ler. O ponto final de frase não
# conta, e por isso o lookahead só recusa o ponto seguido de letra.
PALAVRA_DE_PROSA = re.compile(
    r"(?<![\w/\\])(?<!\w\.)([^\W\d_]+)(?![\w/\\])(?!\.\w)", re.UNICODE)
CERCA = re.compile(r"^\s*(?:```|~~~)\s*(\w*)")
ENDERECO = re.compile(r"https?://|\S+@\S+")
# Num diagrama Mermaid o que está entre aspas é rótulo lido por gente, e não
# identificador: ali a acentuação vale como em qualquer outra prosa.
ROTULO_MERMAID = re.compile(r'"([^"]*)"')
# Fora do Python a mesma ideia vale: em JSON, YAML ou num exemplo de comando,
# uma string de uma palavra entre aspas é um nome, e não prosa.
NOME_ENTRE_ASPAS = re.compile(r'"[\w.-]*"')
# Rótulo de aresta sem aspas, como em A -->|sim| B.
ARESTA_MERMAID = re.compile(r"\|([^|\n]+)\|")


def arquivos(alvos=None):
    if alvos:
        for alvo in alvos:
            caminho = Path(alvo)
            if not caminho.is_absolute():
                caminho = (Path.cwd() / caminho).resolve()
            if caminho.is_file():
                yield caminho
        return
    for caminho in sorted(RAIZ.rglob("*")):
        if not caminho.is_file() or caminho.suffix.lower() not in EXTENSOES:
            continue
        relativo = caminho.relative_to(RAIZ)
        if any(parte in IGNORAR for parte in relativo.parts):
            continue
        if relativo.as_posix() in ARQUIVOS_IGNORADOS:
            continue
        yield caminho


def travessoes(texto):
    """Linhas com travessão, uma entrada por ocorrência."""
    achados = []
    for numero, linha in enumerate(texto.splitlines(), start=1):
        if MARCA_LITERAL in linha:
            continue
        for caractere in sorted(set(linha) & editorial.PROIBIDOS):
            achados.append((numero, "travessão U+%04X em: %s"
                            % (ord(caractere), linha.strip()[:70])))
        if COMO_TRAVESSAO.search(linha):
            achados.append((numero, "hífens usados como travessão: %s"
                            % linha.strip()[:70]))
    return achados


def corrigir_acentos(texto):
    """Troca apenas as grafias da lista, preservando a caixa.

    Não encosta em identificador, caminho, URL, trecho entre crases nem bloco
    de código cercado: ali a grafia sem acento é o nome real de alguma coisa, e
    trocar quebraria o exemplo que a documentação está dando.
    """
    def troca(achado):
        palavra = achado.group(1)
        correta = editorial.GRAFIAS.get(palavra.casefold())
        if not correta:
            return palavra
        if palavra.isupper():
            return correta.upper()
        if palavra[:1].isupper():
            return correta[:1].upper() + correta[1:]
        return correta

    def fora_das_crases(linha):
        # Trecho entre crases e string de uma palavra entre aspas ficam de fora.
        partes = re.split(r"(`[^`]*`|\"[\w.-]*\")", linha)
        return "".join(parte if (parte.startswith("`")
                                 or NOME_ENTRE_ASPAS.fullmatch(parte))
                       else PALAVRA_DE_PROSA.sub(troca, parte)
                       for parte in partes)

    saida = []
    linguagem = None
    for linha in texto.splitlines(keepends=True):
        cerca = CERCA.match(linha)
        if cerca:
            linguagem = None if linguagem is not None else (cerca.group(1) or "")
            saida.append(linha)
            continue
        if linguagem == "mermaid":
            ajustada = ROTULO_MERMAID.sub(
                lambda m: '"%s"' % PALAVRA_DE_PROSA.sub(troca, m.group(1)),
                linha)
            saida.append(ARESTA_MERMAID.sub(
                lambda m: "|%s|" % PALAVRA_DE_PROSA.sub(troca, m.group(1)),
                ajustada))
            continue
        if linguagem is not None or ENDERECO.search(linha):
            saida.append(linha)
            continue
        saida.append(fora_das_crases(linha))
    return "".join(saida)


def _e_nome(tok):
    """Diz se o token é um nome, e não um texto escrito para ler."""
    return (tok.type == tokenize.STRING
            and tok.start[0] == tok.end[0]
            and UMA_PALAVRA.match(tok.string.strip("\"'")) is not None)


def _prosa_do_codigo(texto):
    """Tokens de string, docstring e comentário que são texto para ler.

    Tudo que não passa por aqui é nome: `titulo(`, `secao=` e `kit.animacao`
    estão certos como estão, e apontá-los encheria o relatório de ruído até
    ninguém mais ler.
    """
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(texto).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return None
    linhas = texto.splitlines()
    return [tok for tok in tokens
            if tok.type in (tokenize.STRING, tokenize.COMMENT)
            and not _e_nome(tok)
            and MARCA_LITERAL not in linhas[tok.start[0] - 1]]


def _acentuar(trecho):
    """Aplica a lista de grafias a um trecho de prosa, preservando a caixa."""
    def troca(achado):
        palavra = achado.group(1)
        correta = editorial.GRAFIAS.get(palavra.casefold())
        if not correta:
            return palavra
        if palavra.isupper():
            return correta.upper()
        if palavra[:1].isupper():
            return correta[:1].upper() + correta[1:]
        return correta

    return PALAVRA_DE_PROSA.sub(troca, trecho)


def acentos_em_codigo(texto):
    """Grafia sem acento dentro de um arquivo Python, na linha certa.

    Uma docstring ocupa várias linhas e o token começa na primeira delas. O
    problema é apontado onde a palavra está, e não onde a docstring abre, senão
    quem for corrigir procura no lugar errado.
    """
    tokens = _prosa_do_codigo(texto)
    if tokens is None:
        return []
    achados = []
    for tok in tokens:
        for deslocamento, linha in enumerate(tok.string.splitlines()):
            if _acentuar(linha) == linha:
                continue
            for problema in editorial.problemas(linha):
                if problema.startswith("acentuação"):
                    achados.append((tok.start[0] + deslocamento, problema))
    return achados


def corrigir_acentos_em_codigo(texto):
    """Acentua string, docstring e comentário de um arquivo Python, e mais nada.

    Percorre por token e reescreve por posição absoluta, o que alcança também a
    docstring de várias linhas. Nenhum identificador é tocado, e uma string de
    uma palavra só é deixada como está, porque quase sempre é o nome de alguma
    coisa que o código compara com igualdade.
    """
    tokens = _prosa_do_codigo(texto)
    if tokens is None:
        return texto

    # Posição absoluta de cada início de linha, para converter (linha, coluna).
    inicios, posicao = [], 0
    for linha in texto.splitlines(keepends=True):
        inicios.append(posicao)
        posicao += len(linha)
    inicios.append(posicao)

    partes, anterior = [], 0
    for tok in tokens:
        try:
            comeco = inicios[tok.start[0] - 1] + tok.start[1]
            fim = inicios[tok.end[0] - 1] + tok.end[1]
        except IndexError:
            continue
        if comeco < anterior:
            continue
        partes.append(texto[anterior:comeco])
        partes.append(_acentuar(texto[comeco:fim]))
        anterior = fim
    partes.append(texto[anterior:])
    return "".join(partes)


def acentos(texto, codigo=False):
    """Linhas com grafia sem acento, restrito à lista inequívoca.

    Em prosa, aponta exatamente o que `corrigir_acentos` trocaria, comparando o
    texto com a versão corrigida: o relatório nunca cobra uma linha que a
    correção automática recusaria mexer. Em código, a leitura é por token.
    """
    if codigo:
        return acentos_em_codigo(texto)
    achados = []
    originais = texto.splitlines()
    corrigidas = corrigir_acentos(texto).splitlines()
    for numero, (antes, depois) in enumerate(zip(originais, corrigidas), start=1):
        if antes == depois:
            continue
        for problema in editorial.problemas(antes):
            if problema.startswith("acentuação"):
                achados.append((numero, problema))
    return achados


def main():
    corrigir = "--corrigir" in sys.argv
    alvos = [a for a in sys.argv[1:] if not a.startswith("--")]
    erros, avisos, corrigidos = [], [], 0

    for caminho in arquivos(alvos):
        try:
            relativo = caminho.relative_to(RAIZ).as_posix()
        except ValueError:
            relativo = caminho.as_posix()
        try:
            texto = caminho.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        for numero, problema in travessoes(texto):
            erros.append("%s:%d  %s" % (relativo, numero, problema))

        codigo = caminho.suffix.lower() == ".py"
        achados = acentos(texto, codigo=codigo)
        # A correção automática nunca reescreve uma linha inteira de código:
        # em arquivo Python ela entra só em string e comentário, por token.
        # Acentuar uma chamada ou um argumento nomeado produziria um
        # identificador que ainda compila e quebra só na hora de rodar.
        if corrigir and achados and (codigo or caminho.suffix.lower() in PROSA):
            novo = (corrigir_acentos_em_codigo(texto) if codigo
                    else corrigir_acentos(texto))
            if novo != texto:
                caminho.write_text(novo, encoding="utf-8")
                corrigidos += 1
                achados = acentos(novo, codigo=codigo)
        destino = erros if caminho.suffix.lower() in PROSA else avisos
        for numero, problema in achados:
            destino.append("%s:%d  %s" % (relativo, numero, problema))

    if corrigidos:
        print("acentuação corrigida em %d arquivo(s)" % corrigidos)
        print()
    if erros:
        print("ERROS")
        for linha in erros:
            print("  " + linha)
    if avisos:
        print("AVISOS")
        for linha in avisos:
            print("  " + linha)
    if not erros and not avisos:
        print("texto do repositório limpo: nenhum travessão, nenhuma grafia "
              "sem acento")
    return 2 if erros else (1 if avisos else 0)


if __name__ == "__main__":
    raise SystemExit(main())
