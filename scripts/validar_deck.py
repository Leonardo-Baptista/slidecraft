# -*- coding: utf-8 -*-
"""Confere se um .pptx esta no padrão, e não so se abre.

Percorre as formas pelo python-pptx, entrando em grupos e em celulas de tabela,
e le a arvore de tempo pelo XML associando cada efeito ao objeto certo pelo
spid. Separa erro de aviso: erro e desvio de identidade ou coisa que quebra na
apresentação, aviso e algo para olhar antes de entregar.

    .venv/Scripts/python.exe scripts/validar_deck.py saida/meu_deck.pptx
    .venv/Scripts/python.exe scripts/validar_deck.py saida/meu_deck.pptx --detalhe
    .venv/Scripts/python.exe scripts/validar_deck.py saida/meu.pptx --perfil ao_vivo

O perfil define o corpo mínimo aceito. Quando o arquivo carrega o perfil nos
metadados, gravado por kit.politica, ele e usado automaticamente.

Codigo de saida: 0 sem nada, 1 so com aviso, 2 com erro.
"""
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

# Saída em UTF-8 também no console do Windows, para acento não virar lixo.
sys.stdout.reconfigure(encoding="utf-8")

from pptx import Presentation
from pptx.util import Emu, Inches

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from kit import editorial  # noqa: E402
from kit.medidas import altura_do_texto  # noqa: E402
from kit.politica import (IDENTIDADES, PAPEIS_DE_APOIO,  # noqa: E402
                          PERFIS, PISO_ABSOLUTO, VERSAO, fontes_de, metadados,
                          paleta_de)
from kit.tema import conferir as conferir_tema  # noqa: E402

# ------------------------------------------------------------- o que e padrão
LARGURA, ALTURA = Inches(13.333), Inches(7.5)
TOLERANCIA_FORMATO = Emu(20000)
FOLGA_MARGEM = Inches(0.08)      # arredondamento de layout, não desvio

# Grade e tipografia de cada identidade. A margem do modelo IFES e
# assimetrica de proposito: a faixa verde do fundo ocupa a esquerda do slide,
# e a area util comeca depois dela.
GRADES = {
    "escuro": {"esquerda": Inches(0.9), "direita": Inches(0.9),
                 "fonte_do_tema": "Montserrat", "familia": "montserrat"},
    "ifes": {"esquerda": Inches(2.05), "direita": Inches(0.783),
             "fonte_do_tema": "Arial", "familia": "arial"},
}
MARGEM = GRADES["escuro"]["esquerda"]
TRANSICOES_PERMITIDAS = {"fade", "morph"}
TEXTO_DE_EXEMPLO = (
    "Título direto", "Subtítulo em uma linha", "Primeiro ponto",
    "Segundo ponto", "Terceiro ponto", "Coluna da esquerda",
    "Coluna da direita", "mês de ano", "A frase que o slide quer deixar",
    "A conclusão da comparação", "Uma frase de apoio", "Lorem ipsum",
)

# Elementos de mobiliario podem encostar fora da margem de conteúdo. A capa
# entra na lista porque tem grade propria: ela não tem a coluna lateral que
# define a margem dos slides de conteúdo.
PAPEIS_FORA_DA_MARGEM = ("numero", "rodape", "marca", "capa")

MSO_GRUPO, MSO_MEDIA, MSO_PICTURE = 6, 16, 13

# Sobreposicao entre duas caixas de texto. A medida util e a invasao vertical
# em polegadas, e não a fracao de area: uma caixa de rotulo tem menos de tres
# decimos de polegada de altura, e ali qualquer arredondamento vira uma fracao
# alta sem que nada apareca na tela. Meia linha de corpo e o limite: abaixo
# disso o olho não ve, acima e texto legivel por cima de texto legivel.
INVASAO_TOLERADA = 0.09          # polegadas de sobreposicao vertical
COBERTURA_HORIZONTAL = 0.35      # fracao da largura da caixa mais estreita


def _resumo(forma):
    conteudo = " ".join(forma.text_frame.text.split())
    return conteudo[:34] + ("..." if len(conteudo) > 34 else "")


class Relatorio:
    def __init__(self):
        self.erros = []
        self.avisos = []

    def erro(self, slide, texto):
        if (slide, texto) not in self.erros:
            self.erros.append((slide, texto))

    def aviso(self, slide, texto):
        if (slide, texto) not in self.avisos:
            self.avisos.append((slide, texto))


# ------------------------------------------------------------------- formas

def percorrer(formas, dentro_de_grupo=False):
    """Todas as formas, entrando em grupos. Devolve (forma, em_grupo)."""
    for forma in formas:
        if forma.shape_type == MSO_GRUPO:
            yield forma, dentro_de_grupo
            for interna in percorrer(forma.shapes, True):
                yield interna
        else:
            yield forma, dentro_de_grupo


def quadros_de_texto(forma):
    """Quadros de texto da forma, incluindo os de dentro de tabela."""
    if getattr(forma, "has_table", False):
        for linha in forma.table.rows:
            for celula in linha.cells:
                yield celula.text_frame
    elif forma.has_text_frame:
        yield forma.text_frame


def fontes_corpos_cores(quadro):
    fontes, corpos, cores = set(), [], set()
    for paragrafo in quadro.paragraphs:
        for run in paragrafo.runs:
            fontes.add(run.font.name)
            if run.font.size is not None:
                corpos.append(round(run.font.size.pt, 1))
            try:
                if run.font.color and run.font.color.rgb is not None:
                    cores.add(str(run.font.color.rgb).upper())
            except (AttributeError, TypeError):
                pass
    return fontes, corpos, cores


def cor_de_preenchimento(forma):
    """Cor solida de preenchimento, quando houver."""
    try:
        preenchimento = forma.fill
        if preenchimento.type is not None and preenchimento.type == 1:
            return str(preenchimento.fore_color.rgb).upper()
    except (AttributeError, TypeError, ValueError):
        pass
    return None


def papel_de(forma):
    nome = forma.name or ""
    return nome.split(":")[1] if nome.startswith("gt:") and ":" in nome[3:] else ""


def caixa_ocupada(forma, familia=None):
    """Retangulo que o texto realmente ocupa, e não o declarado na forma.

    A altura declarada raramente corresponde ao que aparece: o kit cria caixas
    baixas e deixa o texto crescer para baixo. Medindo linha a linha, a colisao
    entre um título de tres linhas e a linha de apoio abaixo dele aparece aqui,
    antes de alguem abrir o arquivo.
    """
    if not forma.has_text_frame or not forma.text_frame.text.strip():
        return None
    if forma.left is None or not forma.width:
        return None
    largura = Emu(int(forma.width)).inches
    alto = 0.0
    for paragrafo in forma.text_frame.paragraphs:
        conteudo = "".join(r.text for r in paragrafo.runs)
        if not conteudo:
            alto += 0.12
            continue
        primeiro = paragrafo.runs[0].font
        tamanho = primeiro.size.pt if primeiro.size is not None else 18.0
        entrelinha = paragrafo.line_spacing or 1.0
        if not isinstance(entrelinha, float):
            entrelinha = 1.0
        alto += altura_do_texto(conteudo, forma.width, tamanho,
                                bool(primeiro.bold), entrelinha,
                                familia=familia)
    esquerda = Emu(int(forma.left)).inches
    topo = Emu(int(forma.top)).inches
    ancora = str(getattr(forma.text_frame, "vertical_anchor", "") or "")
    if "MIDDLE" in ancora:
        topo += (Emu(int(forma.height)).inches - alto) / 2.0
    return (esquerda, topo, esquerda + largura, topo + alto)


def _invasao(a, b):
    """Invasao vertical em polegadas, contada so quando as caixas se cruzam.

    Devolve zero quando as caixas mal se tocam na horizontal, porque duas
    colunas lado a lado ocupam a mesma faixa de altura sem se atrapalharem.
    """
    largura = min(a[2], b[2]) - max(a[0], b[0])
    altura = min(a[3], b[3]) - max(a[1], b[1])
    if largura <= 0 or altura <= 0:
        return 0.0
    estreita = min(a[2] - a[0], b[2] - b[0])
    if estreita <= 0 or largura / estreita < COBERTURA_HORIZONTAL:
        return 0.0
    return altura


def colisoes_de_texto(slide, familia=None):
    """Pares de caixas de texto que se cobrem alem do tolerado."""
    caixas = []
    for forma, em_grupo in percorrer(slide.shapes):
        if em_grupo or forma.shape_type == MSO_GRUPO:
            continue
        caixa = caixa_ocupada(forma, familia)
        if caixa is not None:
            caixas.append((forma, caixa))
    achados = []
    for i in range(len(caixas)):
        for j in range(i + 1, len(caixas)):
            invasao = _invasao(caixas[i][1], caixas[j][1])
            if invasao > INVASAO_TOLERADA:
                achados.append((caixas[i][0], caixas[j][0], invasao))
    return achados


# ------------------------------------------------------------------- timing

def timing_do_slide(xml):
    toca, loop = set(), set()
    for bloco in re.finditer(r"<p:cmd[^>]*playFrom.*?</p:cmd>", xml, re.S):
        toca.update(int(v) for v in re.findall(r'spTgt spid="(\d+)"', bloco.group(0)))
    for bloco in re.finditer(r"<p:video>.*?</p:video>", xml, re.S):
        if 'repeatCount="indefinite"' in bloco.group(0):
            loop.update(int(v) for v in
                        re.findall(r'spTgt spid="(\d+)"', bloco.group(0)))
    return (toca, loop, len(re.findall(r"<p:animEffect", xml)),
            len(re.findall(r'nodeType="clickEffect"', xml)))


def transicao_do_slide(xml):
    if "morph" in xml:
        return "morph"
    achado = re.search(r"<p:transition[^>]*>\s*<p:(\w+)", xml)
    return achado.group(1) if achado else None


# ----------------------------------------------------------------- analise

def analisa(caminho, detalhe=False, perfil_pedido=None):
    rel = Relatorio()
    prs = Presentation(str(caminho))
    z = zipfile.ZipFile(str(caminho))

    try:
        meta = metadados(prs)
    except (AttributeError, ValueError):
        meta = {}
    perfil = perfil_pedido or meta.get("perfil", "referencia")
    if perfil not in PERFIS:
        rel.erro(0, "perfil desconhecido: %s" % perfil)
        perfil = "referencia"
    corpo_minimo = PERFIS[perfil]

    identidade = meta.get("identidade", "escuro")
    if identidade not in IDENTIDADES:
        rel.erro(0, "identidade desconhecida: %s" % identidade)
        identidade = "escuro"
    grade = GRADES[identidade]
    paleta = paleta_de(identidade)
    fontes_permitidas = set(fontes_de(identidade)) | {None}
    familia = grade["familia"]

    if (abs(prs.slide_width - LARGURA) > TOLERANCIA_FORMATO
            or abs(prs.slide_height - ALTURA) > TOLERANCIA_FORMATO):
        rel.erro(0, "formato %s x %s, o padrão e 16:9 de 13,333 por 7,5 polegadas"
                 % (round(prs.slide_width / 914400, 2),
                    round(prs.slide_height / 914400, 2)))

    tema = conferir_tema(caminho)
    for papel_fonte, rotulo in (("majorFont", "títulos"), ("minorFont", "corpo")):
        if tema.get(papel_fonte) != grade["fonte_do_tema"]:
            rel.erro(0, "fonte de %s do tema em %s, deveria ser %s"
                     % (rotulo, tema.get(papel_fonte), grade["fonte_do_tema"]))

    linhas = []
    nomes = sorted((n for n in z.namelist()
                    if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                   key=lambda n: int(re.findall(r"\d+", n)[-1]))

    for indice, (slide, nome) in enumerate(zip(prs.slides, nomes), start=1):
        xml = z.read(nome).decode("utf-8")
        toca, loop, efeitos, clique = timing_do_slide(xml)
        transicao = transicao_do_slide(xml)

        midias, fora, pequenos = [], 0, []
        fontes_ruins, cores_ruins, fundos_ruins = set(), set(), set()
        exemplo = False

        for forma, em_grupo in percorrer(slide.shapes):
            if forma.shape_type == MSO_MEDIA:
                midias.append(forma)

            # Margem de conteúdo, e não so a borda do slide. Forma que
            # alcanca a borda esta sangrando de proposito, como painel lateral
            # ou faixa: nesse lado ela não e cobrada. Foto, video e mobiliario
            # ficam fora da verificacao.
            if (forma.shape_type not in (MSO_PICTURE, MSO_GRUPO, MSO_MEDIA)
                    and not em_grupo
                    and papel_de(forma) not in PAPEIS_FORA_DA_MARGEM
                    and forma.left is not None and forma.width):
                direita = forma.left + forma.width
                baixo = forma.top + forma.height
                invade_esquerda = (forma.left < grade["esquerda"] - FOLGA_MARGEM
                                   and forma.left > FOLGA_MARGEM)
                invade_direita = (
                    direita > LARGURA - grade["direita"] + FOLGA_MARGEM
                    and direita < LARGURA - FOLGA_MARGEM)
                sai_do_slide = (forma.top < -FOLGA_MARGEM
                                or baixo > ALTURA + FOLGA_MARGEM)
                if invade_esquerda or invade_direita or sai_do_slide:
                    fora += 1

            preenchimento = cor_de_preenchimento(forma)
            if preenchimento and preenchimento not in paleta:
                fundos_ruins.add(preenchimento)

            # Rotulo e legenda sao apoio, não leitura: para eles vale o piso
            # absoluto, e não o mínimo do perfil.
            minimo = (PISO_ABSOLUTO if papel_de(forma) in PAPEIS_DE_APOIO
                      else corpo_minimo)
            for quadro in quadros_de_texto(forma):
                fontes, corpos, cores = fontes_corpos_cores(quadro)
                fontes_ruins |= {f for f in fontes
                                 if f not in fontes_permitidas}
                pequenos += [c for c in corpos if c < minimo]
                cores_ruins |= {c for c in cores if c not in paleta}
                conteudo = quadro.text
                for achado in editorial.problemas(conteudo):
                    if achado.startswith("travessao") or achado.startswith("travessão"):
                        rel.erro(indice, achado)
                    else:
                        rel.erro(indice, achado)
                if any(t in conteudo for t in TEXTO_DE_EXEMPLO):
                    exemplo = True

        if transicao is None:
            rel.erro(indice, "sem transição")
        elif transicao not in TRANSICOES_PERMITIDAS:
            rel.erro(indice, "transição %s fora do padrão, use fade ou morph"
                     % transicao)
        if clique:
            rel.erro(indice, "%d efeito(s) dependendo de clique" % clique)
        for midia in midias:
            if midia.shape_id not in toca:
                rel.erro(indice, "video %s não inicia sozinho" % midia.name)
        if fontes_ruins:
            rel.erro(indice, "fonte fora do padrão: %s"
                     % ", ".join(sorted(fontes_ruins)))
        if exemplo:
            rel.erro(indice, "texto de exemplo do modelo ainda no slide")
        if fundos_ruins:
            rel.erro(indice, "preenchimento fora da paleta: %s"
                     % ", ".join("#" + c for c in sorted(fundos_ruins)))
        if pequenos:
            rel.aviso(indice, "corpo abaixo de %s pontos, perfil %s: %s"
                      % (corpo_minimo, perfil,
                         ", ".join(str(c) for c in sorted(set(pequenos)))))
        if cores_ruins:
            rel.aviso(indice, "cor de texto fora da paleta: %s"
                      % ", ".join("#" + c for c in sorted(cores_ruins)))
        if fora:
            rel.aviso(indice,
                      "%d forma(s) passando da margem de %.2f polegada"
                      % (fora, Emu(int(grade["esquerda"])).inches))
        for a, b, invasao in colisoes_de_texto(slide, familia):
            rel.erro(indice,
                     "texto sobre texto, %.2f polegada de invasao: '%s' e '%s'"
                     % (invasao, _resumo(a), _resumo(b)))

        ids_midia = {m.shape_id for m in midias}
        linhas.append((indice, transicao or "NENHUMA", efeitos, len(midias),
                       len(toca & ids_midia), len(loop & ids_midia),
                       len(slide.shapes)))

    # ------------------------------------------------------------- relatorio
    print("arquivo: %s" % caminho)
    print("tamanho: %.1f MB   slides: %d   tema: %s   identidade: %s"
          "   perfil: %s   padrão: %s"
          % (Path(caminho).stat().st_size / 1e6, len(linhas),
             tema.get("majorFont"), identidade, perfil,
             meta.get("padrao", VERSAO)))
    print()
    print("  #   transição  efeitos  video  auto  loop  formas")
    print("  " + "-" * 52)
    for linha in linhas:
        print("  %-3d %-10s %-8d %-6d %-5d %-5d %d" % linha)

    midia = [i for i in z.infolist() if i.filename.startswith("ppt/media/")]
    peso_video = sum(i.file_size for i in midia
                     if i.filename.lower().endswith((".mp4", ".avi", ".mov")))
    print()
    print("midia embutida: %d arquivos, %.1f MB, sendo %.1f MB de video"
          % (len(midia), sum(i.file_size for i in midia) / 1e6, peso_video / 1e6))
    if peso_video > 25e6:
        rel.aviso(0, "video embutido acima de 25 MB, recomprima os clipes")

    if detalhe:
        contagem = Counter()
        for slide in prs.slides:
            for forma, _ in percorrer(slide.shapes):
                for quadro in quadros_de_texto(forma):
                    contagem.update(fontes_corpos_cores(quadro)[2])
        print()
        print("cores de texto usadas:")
        for cor, n in contagem.most_common():
            print("  #%s  %dx%s" % (cor, n, "" if cor in paleta
                                    else "   fora da paleta"))

    print()
    if rel.erros:
        print("ERROS")
        for slide, texto in rel.erros:
            print("  - %s%s" % ("slide %d: " % slide if slide else "", texto))
    if rel.avisos:
        print("AVISOS")
        for slide, texto in rel.avisos:
            print("  - %s%s" % ("slide %d: " % slide if slide else "", texto))
    if not rel.erros and not rel.avisos:
        print("nenhum erro, nenhum aviso")

    return 2 if rel.erros else (1 if rel.avisos else 0)


def main():
    argumentos = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not argumentos:
        print(__doc__)
        return 1
    perfil = None
    if "--perfil" in sys.argv:
        pos = sys.argv.index("--perfil")
        if pos + 1 < len(sys.argv):
            perfil = sys.argv[pos + 1]
            if perfil in argumentos:
                argumentos.remove(perfil)
    caminho = Path(argumentos[0])
    if not caminho.exists():
        print("arquivo não encontrado:", caminho)
        return 1
    return analisa(caminho, detalhe="--detalhe" in sys.argv, perfil_pedido=perfil)


if __name__ == "__main__":
    raise SystemExit(main())
