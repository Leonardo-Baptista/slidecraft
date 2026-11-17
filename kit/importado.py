# -*- coding: utf-8 -*-
"""Apresentação que a pessoa já tem: extrair o conteúdo e manter o design.

Dois usos, conforme a escolha da pessoa:

1. Passar para o padrão do kit (`ifes` ou `escuro`): `extrair` tira texto,
   imagens, vídeos, tabelas, gráficos e notas para a pasta do deck, e o deck
   novo é escrito com as composições do kit.
2. Manter o design dela (identidade `importada`): `abrir_modelo` abre o
   próprio arquivo, apaga os slides e deixa mestre, layouts, fundos,
   logotipo, cores e fontes. Os slides novos nascem dos layouts dela e
   recebem a animação, a transição, os números que sobem e a linha do tempo
   do kit.

    import kit.importado as imp

    prs = imp.abrir_modelo(ASSETS / "original.pptx")
    d = imp.design(prs)                   # cores, fontes, margens, tamanho
    s = imp.novo(prs, "título e conteúdo")   # layout por parte do nome
    t = imp.titulo(s, "Um assunto por slide")
    linhas = imp.itens(s, d["margem_esquerda"], 2.0, 8.0, ["um", "dois"])
    anima(s, [(0, [t])] + [(400 + i * 300, l) for i, l in enumerate(linhas)])
"""
import json
import unicodedata
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE, PP_PLACEHOLDER
from pptx.enum.text import PP_ALIGN
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.util import Emu, Inches, Pt

from kit import medidas
from kit.editorial import IDIOMA, preparar
from kit.politica import configurar, metadados, papel

NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
TITULOS = (PP_PLACEHOLDER.TITLE, PP_PLACEHOLDER.CENTER_TITLE)


# ------------------------------------------------------------ design system

def _tema(prs):
    """XML do tema do primeiro mestre."""
    mestre = prs.slide_masters[0].part
    return etree.fromstring(mestre.part_related_by(RT.THEME).blob)


def _pol(emu):
    return round(Emu(int(emu)).inches, 3)


def design(prs):
    """Cores e fontes do tema, tamanho do slide e margens dos layouts.

    As margens saem dos espaços reservados de título e corpo dos layouts: é
    onde a pessoa diagramou o texto, e é ali que o conteúdo novo deve ficar.
    """
    tema = _tema(prs)
    cores = {}
    for no in tema.find(".//{%s}clrScheme" % NS_A):
        nome = etree.QName(no).localname
        filho = no[0]
        valor = filho.get("val") if etree.QName(filho).localname == "srgbClr" \
            else filho.get("lastClr")
        if valor:
            cores[nome] = valor.upper()

    def familia(tag):
        no = tema.find(".//{%s}%s/{%s}latin" % (NS_A, tag, NS_A))
        return no.get("typeface") if no is not None else None

    largura, altura = _pol(prs.slide_width), _pol(prs.slide_height)
    # Medida no conteúdo dos slides quando houver: muita apresentação é
    # desenhada à mão sobre layouts que nunca foram ajustados ao formato.
    meta = metadados(prs)
    importado = "paleta" in meta
    # Num deck já montado por `abrir_modelo`, paleta e margens são as do
    # original, gravadas nos metadados, e não as dos slides novos.
    margens_slides = (
        (float(meta["margem_e"]), float(meta["margem_d"])) if importado
        else _margens_do_conteudo(prs, largura))
    esquerdas, direitas = [], []
    layouts = []
    for layout in prs.slide_layouts:
        reservados = []
        for ph in layout.placeholders:
            reservados.append(str(ph.placeholder_format.type).split(".")[-1]
                              .split(" ")[0].lower())
            if (ph.placeholder_format.type in TITULOS + (PP_PLACEHOLDER.BODY,
                                                          PP_PLACEHOLDER.OBJECT)
                    and ph.left is not None and ph.width):
                esquerdas.append(_pol(ph.left))
                direitas.append(largura - _pol(ph.left + ph.width))
        layouts.append({"nome": layout.name, "reservados": reservados})
    return {
        "largura": largura, "altura": altura,
        "cores": cores,
        "fontes": {"titulo": familia("majorFont"), "corpo": familia("minorFont")},
        "margem_esquerda": margens_slides[0] if margens_slides else (
            min(esquerdas) if esquerdas else 0.5),
        "margem_direita": margens_slides[1] if margens_slides else (
            min(direitas) if direitas else 0.5),
        "layouts": layouts,
        # O design de muita apresentação é desenhado slide a slide, e não no
        # tema: a paleta de verdade é a que os slides usam.
        "cores_usadas": ([c for c in meta["paleta"].split(",") if c]
                         if importado else _cores_usadas(prs)),
        "fundos": [_fundo(s) for s in prs.slides],
    }


def _margens_do_conteudo(prs, largura):
    """Menor recuo de texto à esquerda e à direita, nos slides existentes."""
    esquerdas, direitas = [], []
    for slide in prs.slides:
        for forma in slide.shapes:
            if (not forma.has_text_frame or not forma.text_frame.text.strip()
                    or forma.left is None or not forma.width):
                continue
            e = _pol(forma.left)
            d = largura - _pol(forma.left + forma.width)
            # Encostado na borda é faixa ou rodapé sangrado, não margem.
            if e > 0.1:
                esquerdas.append(e)
            if d > 0.1:
                direitas.append(d)
    if not esquerdas or not direitas:
        return None
    # Percentil baixo, e não o mínimo: um selo isolado perto da borda não
    # pode virar a margem do deck inteiro.
    esquerdas.sort()
    direitas.sort()
    return (round(esquerdas[len(esquerdas) // 10], 3),
            round(direitas[len(direitas) // 10], 3))


def _fundo(slide):
    """Cor sólida do fundo do slide, ou None quando herda do layout."""
    try:
        if slide.background.fill.type == 1:
            return str(slide.background.fill.fore_color.rgb).upper()
    except (AttributeError, TypeError, ValueError):
        pass
    return None


def _cores_usadas(prs, limite=16):
    """As cores mais usadas em preenchimento, texto e fundo dos slides."""
    from collections import Counter
    conta = Counter()
    for slide in prs.slides:
        if _fundo(slide):
            conta[_fundo(slide)] += 3
        for forma in _formas(slide.shapes):
            try:
                if forma.fill.type == 1:
                    conta[str(forma.fill.fore_color.rgb).upper()] += 1
            except (AttributeError, TypeError, ValueError, NotImplementedError):
                pass
            if not forma.has_text_frame:
                continue
            for p in forma.text_frame.paragraphs:
                for r in p.runs:
                    try:
                        if r.font.color.rgb is not None:
                            conta[str(r.font.color.rgb).upper()] += 1
                    except (AttributeError, TypeError, ValueError):
                        pass
    return [c for c, _ in conta.most_common(limite)]


def cor(prs, nome):
    """Cor do tema pelo papel ("accent1", "dk1", "lt1") ou em hexadecimal."""
    from pptx.dml.color import RGBColor
    cores = design(prs)["cores"]
    return RGBColor.from_string(cores.get(nome, str(nome).lstrip("#")).upper())


# -------------------------------------------------------------- extração

def _paragrafos(quadro):
    return [{"nivel": p.level, "texto": "".join(r.text for r in p.runs)}
            for p in quadro.paragraphs
            if "".join(r.text for r in p.runs).strip()]


def _formas(formas):
    for forma in formas:
        if forma.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from _formas(forma.shapes)
        else:
            yield forma


def _titulo_provavel(slide, altura, minimo=18):
    """Título desenhado como caixa de texto comum: a caixa mais alta do slide
    com fonte de título (18 pontos ou mais). Número grande de destaque costuma
    ficar abaixo do título, e rótulo pequeno acima dele fica de fora."""
    candidatos = []
    for forma in _formas(slide.shapes):
        if not forma.has_text_frame or forma.top is None:
            continue
        corpos = [r.font.size.pt for p in forma.text_frame.paragraphs
                  for r in p.runs if r.font.size]
        if corpos and max(corpos) >= minimo and forma.text_frame.text.strip():
            candidatos.append((forma.top, forma.text_frame.text.strip()))
    return min(candidatos)[1] if candidatos else None


def extrair(origem, pasta_deck):
    """Tira o conteúdo do .pptx para `assets/importado` e grava dois JSON.

    `conteudo.json`: um item por slide, com layout, título, textos, tabelas,
    gráficos (categorias e séries), imagens, vídeos e notas. `design.json`:
    o que `design` devolve. Devolve o caminho de `conteudo.json`.
    """
    origem, pasta = Path(origem), Path(pasta_deck) / "assets" / "importado"
    pasta.mkdir(parents=True, exist_ok=True)
    prs = Presentation(str(origem))
    slides = []
    for n, slide in enumerate(prs.slides, start=1):
        item = {"slide": n, "layout": slide.slide_layout.name, "titulo": None,
                "textos": [], "tabelas": [], "graficos": [], "imagens": [],
                "videos": [], "notas": ""}
        k = 0
        for forma in _formas(slide.shapes):
            if forma.is_placeholder and \
                    forma.placeholder_format.type in TITULOS and forma.has_text_frame:
                item["titulo"] = forma.text_frame.text.strip() or None
            elif forma.has_text_frame and forma.text_frame.text.strip():
                item["textos"].append(_paragrafos(forma.text_frame))
            if getattr(forma, "has_table", False) and forma.has_table:
                item["tabelas"].append([[c.text for c in linha.cells]
                                        for linha in forma.table.rows])
            if getattr(forma, "has_chart", False) and forma.has_chart:
                grafico = forma.chart
                item["graficos"].append({
                    "tipo": str(grafico.chart_type).split(".")[-1].split(" ")[0],
                    "categorias": [str(c) for c in grafico.plots[0].categories],
                    "series": [{"nome": s.name, "valores": list(s.values)}
                               for s in grafico.plots[0].series]})
            if forma.shape_type == MSO_SHAPE_TYPE.PICTURE:
                k += 1
                destino = pasta / ("s%02d_imagem%d.%s"
                                   % (n, k, forma.image.ext))
                destino.write_bytes(forma.image.blob)
                item["imagens"].append({
                    "arquivo": "importado/" + destino.name,
                    "largura": _pol(forma.width), "altura": _pol(forma.height)})
        for rel in slide.part.rels.values():
            if rel.is_external or rel.reltype not in (RT.MEDIA, RT.VIDEO):
                continue
            parte = rel.target_part
            destino = pasta / ("s%02d_%s" % (n, Path(str(parte.partname)).name))
            if not destino.exists():
                destino.write_bytes(parte.blob)
                item["videos"].append("importado/" + destino.name)
        if not item["titulo"]:
            item["titulo"] = _titulo_provavel(slide, prs.slide_height)
        item["fundo"] = _fundo(slide)
        if slide.has_notes_slide:
            item["notas"] = slide.notes_slide.notes_text_frame.text.strip()
        slides.append(item)

    saida = pasta / "conteudo.json"
    saida.write_text(json.dumps({"origem": origem.name, "slides": slides},
                                ensure_ascii=False, indent=1), encoding="utf-8")
    (pasta / "design.json").write_text(
        json.dumps(design(prs), ensure_ascii=False, indent=1), encoding="utf-8")
    return saida


# ------------------------------------------------- o arquivo como modelo

def abrir_modelo(origem, perfil="ao_vivo", divulgacao="publico"):
    """Abre o .pptx da pessoa, apaga os slides e guarda o design dela.

    Mestre, layouts, tema, fundos e logotipo continuam. As margens medidas e
    as cores que os slides dela usavam ficam nos metadados, para o validador
    cobrar a grade e a paleta dela, e não as do kit. Fundo desenhado slide a
    slide (capa escura, por exemplo) não está no mestre: veja `fundos` em
    `design.json` e repita com `kit.base.fundo(s, cor)`.
    """
    prs = Presentation(str(origem))
    d = design(prs)          # antes de apagar: margens e cores dos slides
    lista = prs.slides._sldIdLst
    for sld in list(lista):
        prs.part.drop_rel(sld.rId)
        lista.remove(sld)
    # shortcut: o texto é medido com a tabela da Arial, que fica perto da
    # maioria das fontes sem serifa; para fonte muito larga ou condensada, a
    # detecção de colisão perde precisão.
    medidas.usar_familia("arial")
    configurar(prs, perfil, divulgacao, identidade="importada")
    prs.core_properties.keywords += ";margem_e=%.3f;margem_d=%.3f;paleta=%s" % (
        d["margem_esquerda"], d["margem_direita"], ",".join(d["cores_usadas"]))
    return prs


def _sem_acento(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower())
                   if unicodedata.category(c) != "Mn")


def novo(prs, layout=None):
    """Slide num layout da pessoa, escolhido por parte do nome.

    Sem nome, usa o layout "somente título" (ou "em branco"), que deixa o
    fundo e o logotipo dela e dá espaço para as composições do kit.
    """
    nomes = [layout] if layout else [
        "somente título", "apenas título", "title only", "em branco", "blank"]
    for procurado in nomes:
        for candidato in prs.slide_layouts:  # a comparação ignora acento
            if _sem_acento(procurado) in _sem_acento(candidato.name):
                return prs.slides.add_slide(candidato)
    if layout:
        raise ValueError("Layout %r não existe. Há: %s" % (
            layout, ", ".join(l.name for l in prs.slide_layouts)))
    return prs.slides.add_slide(prs.slide_layouts[len(prs.slide_layouts) - 1])


def limpar(slide):
    """Remove espaços reservados vazios, que apareceriam na edição."""
    for forma in list(slide.placeholders):
        if forma.has_text_frame and not forma.text_frame.text.strip():
            forma._element.getparent().remove(forma._element)


def titulo(slide, conteudo):
    """Escreve no espaço reservado de título do layout, com a fonte e a cor
    do modelo da pessoa. Devolve a forma."""
    for forma in slide.placeholders:
        if forma.placeholder_format.type in TITULOS:
            forma.text_frame.text = preparar(conteudo)
            for p in forma.text_frame.paragraphs:
                for r in p.runs:
                    r.font._rPr.set("lang", IDIOMA)
            return papel(forma, "titulo")
    raise ValueError("Este layout não tem título. Escolha outro em novo().")


def reservado(slide, indice, conteudo):
    """Escreve num espaço reservado do layout pelo índice (1 = subtítulo ou
    corpo, na maioria dos modelos). Mantém fonte, corpo e cor do modelo."""
    forma = slide.placeholders[indice]
    forma.text_frame.text = preparar(conteudo)
    for p in forma.text_frame.paragraphs:
        for r in p.runs:
            r.font._rPr.set("lang", IDIOMA)
    return forma


def texto(slide, x, y, cx, cy, conteudo, tamanho, cor_do_texto="dk1",
          negrito=False, alinhamento=PP_ALIGN.LEFT, entrelinha=1.15,
          titulo_do_tema=False, funcao=None):
    """Caixa de texto na fonte do tema da pessoa. Posições em polegadas.

    `funcao="rotulo"` ou `"legenda"` marca texto de apoio, que pode ser menor
    que o corpo mínimo de leitura do perfil (vale o piso absoluto, 9,5).
    """
    prs = slide.part.package.presentation_part.presentation
    d = design(prs)
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(cx), Inches(cy))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, linha in enumerate(preparar(conteudo).split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = alinhamento
        p.line_spacing = entrelinha
        r = p.add_run()
        r.text = linha
        r.font.name = d["fontes"]["titulo" if titulo_do_tema else "corpo"]
        r.font.size = Pt(tamanho)
        r.font.bold = negrito
        r.font.color.rgb = cor(prs, cor_do_texto)
        r.font._rPr.set("lang", IDIOMA)
    return papel(tb, funcao) if funcao else tb


def itens(slide, x, y, largura, conteudos, tamanho=16, cor_do_texto="dk1",
          cor_do_ponto="accent1", passo=0.55):
    """Lista com ponto na cor de destaque do tema. Uma [ponto, texto] por item,
    para animar linha a linha. No máximo quatro."""
    if not 1 <= len(conteudos) <= 4:
        raise ValueError("Use de 1 a 4 itens; divida o conteúdo em mais slides.")
    prs = slide.part.package.presentation_part.presentation
    criadas = []
    for conteudo in conteudos:
        ponto = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x),
                                       Inches(y + 0.1), Pt(8), Pt(8))
        ponto.fill.solid()
        ponto.fill.fore_color.rgb = cor(prs, cor_do_ponto)
        ponto.line.fill.background()
        ponto.shadow.inherit = False
        linha = texto(slide, x + 0.3, y, largura - 0.3, 0.4, conteudo, tamanho,
                      cor_do_texto)
        criadas.append([ponto, linha])
        y += passo
    return criadas


def retangulo(slide, x, y, cx, cy, preenchimento, borda=None,
              forma=MSO_SHAPE.ROUNDED_RECTANGLE):
    """Cartão nas cores do tema ("accent1", "lt2") ou em hexadecimal."""
    prs = slide.part.package.presentation_part.presentation
    s = slide.shapes.add_shape(forma, Inches(x), Inches(y), Inches(cx),
                               Inches(cy))
    s.fill.solid()
    s.fill.fore_color.rgb = cor(prs, preenchimento)
    if borda:
        s.line.color.rgb = cor(prs, borda)
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    if forma == MSO_SHAPE.ROUNDED_RECTANGLE and s.adjustments:
        s.adjustments[0] = 0.06
    return s


def margens(prs):
    """Margens gravadas por `abrir_modelo`, em polegadas."""
    meta = metadados(prs)
    return float(meta.get("margem_e", 0.5)), float(meta.get("margem_d", 0.5))
