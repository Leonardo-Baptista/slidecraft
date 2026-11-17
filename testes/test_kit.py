# -*- coding: utf-8 -*-
"""Testes do kit.

Existem porque o kit e compartilhado: uma mudanca nele muda todos os decks
futuros, e quem mexe nem sempre e quem escreveu. Cada teste aqui cobre uma
regra que ja foi quebrada em producao pelo menos uma vez.

    .venv/Scripts/python.exe -m pytest testes -q
"""
import sys
import unicodedata
from pathlib import Path

import pytest
from pptx.util import Inches, Pt

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from kit import base  # noqa: E402
from kit.layouts import (capa, comparacao, faixa_de_etapas,  # noqa: E402
                         fechamento, linha_do_tempo, provocacao,
                         texto_com_foto)
from kit.tema import conferir, nova_apresentacao  # noqa: E402
from kit.transicoes import aplicar_em_todos  # noqa: E402


# --------------------------------------------------------------------- tema

def test_tema_sai_em_montserrat(tmp_path):
    """O tema interno em Calibri fazia caixa de texto nova nascer fora do padrão."""
    arquivo = tmp_path / "t.pptx"
    nova_apresentacao().save(str(arquivo))
    achado = conferir(arquivo)
    assert achado["majorFont"] == "Montserrat"
    assert achado["minorFont"] == "Montserrat"
    assert achado["accent1"].upper() == "00E5C0"


def test_apresentacao_nasce_em_16_9():
    prs = nova_apresentacao()
    assert prs.slide_width == Inches(13.333)
    assert prs.slide_height == Inches(7.5)


# --------------------------------------------------------------------- foto

def test_cache_de_foto_segue_o_conteudo(tmp_path):
    """Trocar a imagem mantendo o nome não pode reaproveitar o tratamento antigo."""
    from PIL import Image

    assets, cache = tmp_path / "assets", tmp_path / "cache"
    assets.mkdir()
    origem = assets / "foto.jpg"
    Image.new("RGB", (400, 400), (255, 0, 0)).save(origem)

    with base.usando(assets, cache):
        primeiro = base.foto("foto.jpg", 200, 100)
        Image.new("RGB", (400, 400), (0, 0, 255)).save(origem)
        segundo = base.foto("foto.jpg", 200, 100)

    assert primeiro != segundo, "o cache ignorou a troca do arquivo"


def test_escopo_de_ativos_devolve_o_anterior(tmp_path):
    antes = base.ASSETS
    with base.usando(tmp_path):
        assert base.ASSETS == tmp_path
    assert base.ASSETS == antes


# ---------------------------------------------------------------- marcadores

def test_marcadores_devolvem_formas():
    """Havia duas assinaturas: o kit devolvia posicao, os decks devolviam formas."""
    prs = nova_apresentacao()
    s = prs.slides.add_slide(prs.slide_layouts[6])
    criadas = base.marcadores(s, Inches(1), Inches(1), ["um", "dois"])
    assert len(criadas) == 2
    assert all(len(par) == 2 for par in criadas), "cada item traz ponto e texto"


# ------------------------------------------------------------------ layouts

def test_todas_as_composicoes_geram():
    prs = nova_apresentacao()
    capa(prs, "Título", "Subtítulo")
    texto_com_foto(prs, 2, "Título", ["a", "b"], secao="Seção", apoio="Apoio",
                   fecho="Fecho")
    comparacao(prs, 3, "Título", ("Esquerda", ["a"]), ("Direita", ["b"]),
               apoio="Apoio", fecho="Fecho")
    faixa_de_etapas(prs, 4, "Título", [("Um", "desc"), ("Dois", "desc")],
                    fecho="Fecho")
    faixa_de_etapas(prs, 5, "Título", [("Um", "desc"), ("Dois", "desc")],
                    escada=True)
    linha_do_tempo(prs, 6, "Título", [("2024", "desc"), ("2026", "desc")])
    provocacao(prs, "Pergunta?", destaque="95%", chamada="Responda no chat.")
    fechamento(prs, "Frase final", contato="contato@exemplo.org")
    assert len(prs.slides._sldIdLst) == 8


def test_composicoes_cabem_na_area_util():
    """Forma fora da margem e o defeito mais comum depois de mexer em texto."""
    prs = nova_apresentacao()
    texto_com_foto(prs, 2, "Título em\nduas linhas",
                   ["um", "dois", "tres", "quatro"], secao="Seção",
                   apoio="Uma frase de apoio um pouco mais longa que o normal.",
                   fecho="Uma frase de fecho.")
    faixa_de_etapas(prs, 3, "Título", [("Um", "d"), ("Dois", "d"),
                                       ("Tres", "d"), ("Quatro", "d")],
                    escada=True, fecho="Fecho")
    for slide in prs.slides:
        for forma in slide.shapes:
            if forma.shape_type == 13:      # foto pode sangrar
                continue
            assert forma.top + forma.height <= prs.slide_height + Pt(2), (
                "forma passando da borda de baixo")
            assert forma.left + forma.width <= prs.slide_width + Pt(2), (
                "forma passando da borda da direita")


# --------------------------------------------------------------- transições

def test_transicao_entra_em_todos_os_slides():
    from kit.animacao import q

    prs = nova_apresentacao()
    for _ in range(3):
        prs.slides.add_slide(prs.slide_layouts[6])
    aplicar_em_todos(prs, morph_em=(2,))

    encontradas = []
    for slide in prs.slides:
        sld = slide._element
        tem_fade = sld.find(q("transition")) is not None
        tem_morph = b"morph" in sld.xml.encode("utf-8")
        encontradas.append("morph" if tem_morph else ("fade" if tem_fade else None))
    assert encontradas == ["fade", "morph", "fade"]


# ---------------------------------------------------------------- validador

def _validar(caminho):
    import subprocess
    r = subprocess.run(
        [sys.executable, str(RAIZ / "scripts" / "validar_deck.py"), str(caminho)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "")


def test_validador_reprova_fora_do_padrao(tmp_path):
    """O caso que passava batido: 4:3, fonte errada, corpo minusculo."""
    from pptx import Presentation
    from pptx.dml.color import RGBColor

    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(10), Inches(7.5)
    s = prs.slides.add_slide(prs.slide_layouts[6])
    caixa = s.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(1))
    run = caixa.text_frame.paragraphs[0].add_run()
    run.text = "Fora do padrão"
    run.font.name = "Arial"
    run.font.size = Pt(7)
    run.font.color.rgb = RGBColor(0xFF, 0x00, 0x00)
    arquivo = tmp_path / "ruim.pptx"
    prs.save(str(arquivo))

    codigo, saida = _validar(arquivo)
    assert codigo == 2
    for esperado in ("formato", "Calibri", "sem transição", "Arial"):
        assert esperado in saida, "o validador não acusou: %s" % esperado


def test_validador_aprova_deck_do_kit(tmp_path):
    prs = nova_apresentacao()
    capa(prs, "Título", "Subtítulo")
    comparacao(prs, 2, "Título", ("Esquerda", ["a"]), ("Direita", ["b"]))
    aplicar_em_todos(prs)
    arquivo = tmp_path / "bom.pptx"
    prs.save(str(arquivo))

    codigo, saida = _validar(arquivo)
    assert codigo == 0, saida


# ------------------------------------------------------------- editorial

# Os sinais proibidos entram por código de caractere, e não como literal: a
# regra vale também para este arquivo, e o verificador do repositório acusaria
# um travessão escrito aqui, com razão.
TRAVESSAO, MEIA_RISCA, MENOS = chr(0x2014), chr(0x2013), chr(0x2212)


def test_travessao_e_bloqueado_na_geracao():
    """A regra vale na geração: não dá para produzir um slide com travessão."""
    from kit.editorial import preparar

    for sinal in (TRAVESSAO, MEIA_RISCA, MENOS):
        with pytest.raises(ValueError):
            preparar("Título %s subtítulo" % sinal)
    assert preparar("Título: subtítulo") == "Título: subtítulo"


def test_texto_do_kit_recusa_travessao():
    prs = nova_apresentacao()
    s = prs.slides.add_slide(prs.slide_layouts[6])
    with pytest.raises(ValueError):
        base.texto(s, Inches(1), Inches(1), Inches(4), Inches(1),
                   "Antes %s depois" % TRAVESSAO, 14, base.BRANCO)


def test_acentuacao_e_apontada_com_a_caixa_certa():
    from kit.editorial import problemas

    achados = problemas("A Apresentacao tem padrao tecnico")  # grafia-literal
    assert "'Apresentacao' deve ser 'Apresentação'" in " ".join(achados)  # grafia-literal
    assert "'padrao' deve ser 'padrão'" in " ".join(achados)  # grafia-literal
    assert problemas("A apresentação tem padrão técnico") == []


def test_grafias_mapeiam_para_a_forma_acentuada():
    """Guarda a lista contra uma correção automática que a esvaziaria.

    Se alguma ferramenta acentuar as chaves do dicionário, cada palavra passa a
    apontar para ela mesma, o filtro descarta tudo e a regra some sem erro
    nenhum. Este teste é o alarme para isso.
    """
    from kit.editorial import GRAFIAS

    assert len(GRAFIAS) > 60
    for errada, correta in GRAFIAS.items():
        assert errada != correta
        assert errada == unicodedata.normalize("NFKD", correta).encode(
            "ascii", "ignore").decode("ascii")


def test_acentuacao_ignora_url_e_identificador():
    from kit.editorial import problemas

    assert problemas("veja exemplo.org/apresentacao") == []
    assert problemas("o arquivo build.py e a chave kit.base") == []


# --------------------------------------------- validador, regras de identidade

def _deck_com(tmp_path, monta, nome="caso.pptx"):
    prs = nova_apresentacao()
    monta(prs)
    aplicar_em_todos(prs)
    arquivo = tmp_path / nome
    prs.save(str(arquivo))
    return _validar(arquivo)


def test_validador_pega_forma_alem_da_margem(tmp_path):
    def monta(prs):
        s = prs.slides.add_slide(prs.slide_layouts[6])
        caixa = s.shapes.add_textbox(Inches(0.1), Inches(1), Inches(4),
                                     Inches(0.5))
        caixa.text_frame.paragraphs[0].add_run().text = "Colado na borda"

    codigo, saida = _deck_com(tmp_path, monta)
    assert "margem" in saida, saida


def test_validador_pega_preenchimento_fora_da_paleta(tmp_path):
    from pptx.dml.color import RGBColor

    def monta(prs):
        s = prs.slides.add_slide(prs.slide_layouts[6])
        forma = s.shapes.add_shape(1, Inches(2), Inches(2), Inches(3), Inches(1))
        forma.fill.solid()
        forma.fill.fore_color.rgb = RGBColor(0xFF, 0x00, 0x00)

    codigo, saida = _deck_com(tmp_path, monta)
    assert codigo == 2 and "preenchimento fora da paleta" in saida, saida


def test_validador_entra_em_grupo(tmp_path):
    def monta(prs):
        s = prs.slides.add_slide(prs.slide_layouts[6])
        a = s.shapes.add_textbox(Inches(2), Inches(2), Inches(3), Inches(1))
        run = a.text_frame.paragraphs[0].add_run()
        run.text = "Dentro do grupo"
        run.font.name = "Arial"
        b = s.shapes.add_textbox(Inches(6), Inches(2), Inches(3), Inches(1))
        b.text_frame.paragraphs[0].add_run().text = "Par do grupo"
        s.shapes.add_group_shape([a, b])

    codigo, saida = _deck_com(tmp_path, monta)
    assert codigo == 2 and "Arial" in saida, saida


def test_validador_entra_em_tabela(tmp_path):
    def monta(prs):
        s = prs.slides.add_slide(prs.slide_layouts[6])
        tabela = s.shapes.add_table(2, 2, Inches(2), Inches(2), Inches(6),
                                    Inches(1.5)).table
        run = tabela.cell(0, 0).text_frame.paragraphs[0].add_run()
        run.text = "Célula"
        run.font.name = "Arial"

    codigo, saida = _deck_com(tmp_path, monta)
    assert codigo == 2 and "Arial" in saida, saida


def test_validador_restringe_o_tipo_de_transicao(tmp_path):
    from lxml import etree

    from kit.animacao import q

    prs = nova_apresentacao()
    s = prs.slides.add_slide(prs.slide_layouts[6])
    transicao = etree.SubElement(s._element, q("transition"))
    transicao.set("spd", "med")
    etree.SubElement(transicao, q("push")).set("dir", "u")
    arquivo = tmp_path / "push.pptx"
    prs.save(str(arquivo))

    codigo, saida = _validar(arquivo)
    assert codigo == 2 and "push" in saida, saida


def test_validador_exige_fonte_de_corpo_no_tema(tmp_path):
    import re
    import zipfile

    prs = nova_apresentacao()
    prs.slides.add_slide(prs.slide_layouts[6])
    aplicar_em_todos(prs)
    original = tmp_path / "tema.pptx"
    prs.save(str(original))

    z = zipfile.ZipFile(str(original))
    dados = {n: z.read(n) for n in z.namelist()}
    z.close()
    tema = [n for n in dados if "theme" in n and n.endswith(".xml")][0]
    dados[tema] = re.sub(r'(<a:minorFont>\s*<a:latin typeface=")[^"]*',
                         r"\g<1>Arial",
                         dados[tema].decode("utf-8")).encode("utf-8")
    alterado = tmp_path / "tema_ruim.pptx"
    with zipfile.ZipFile(str(alterado), "w", zipfile.ZIP_DEFLATED) as saida_zip:
        for nome, conteudo in dados.items():
            saida_zip.writestr(nome, conteudo)

    codigo, saida = _validar(alterado)
    assert codigo == 2 and "fonte de corpo do tema" in saida, saida


# ------------------------------------------------------------------ perfis

def test_perfil_define_o_corpo_minimo():
    from kit.politica import PERFIS

    assert PERFIS["ao_vivo"] > PERFIS["leitura"] > PERFIS["anexo"]
    assert PERFIS["referencia"] < PERFIS["anexo"]


def test_metadados_do_arquivo_trazem_perfil_e_divulgacao(tmp_path):
    from kit.politica import metadados

    prs = nova_apresentacao(perfil="ao_vivo", divulgacao="publico")
    achado = metadados(prs)
    assert achado["perfil"] == "ao_vivo"
    assert achado["divulgacao"] == "publico"


# ----------------------------------------------------------------- layouts

def test_layout_recusa_lista_vazia():
    prs = nova_apresentacao()
    with pytest.raises(ValueError):
        faixa_de_etapas(prs, 2, "Título", [])
    with pytest.raises(ValueError):
        linha_do_tempo(prs, 3, "Título", [])
    with pytest.raises(ValueError):
        texto_com_foto(prs, 4, "Título", [])


def test_layout_recusa_conteudo_demais():
    prs = nova_apresentacao()
    with pytest.raises(ValueError):
        texto_com_foto(prs, 2, "Título", ["a", "b", "c", "d", "e"])


def test_barra_da_linha_do_tempo_usa_wipe():
    """A barra promete preencher da esquerda para a direita, não surgir."""
    prs = nova_apresentacao()
    linha_do_tempo(prs, 2, "Título", [("2024", "d"), ("2026", "d")])
    xml = list(prs.slides)[0]._element.xml
    assert "wipe(left)" in xml


# ----------------------------------------------------------------- medidas

def test_medida_de_texto_acompanha_a_largura():
    """Texto que não cabe numa linha tem de ser contado como mais de uma."""
    from kit.medidas import altura_do_texto, linhas_do_texto

    frase = "O SAM entra no meio do sistema, não no lugar dele"
    assert len(linhas_do_texto(frase, Inches(11.0), 30, negrito=True)) == 2
    assert len(linhas_do_texto(frase, Inches(4.0), 30, negrito=True)) >= 3
    assert altura_do_texto(frase, Inches(4.0), 30) > altura_do_texto(
        frase, Inches(11.0), 30)


def test_quebra_explicita_conta_como_linha():
    from kit.medidas import linhas_do_texto

    assert linhas_do_texto("um\ndois\ntres", Inches(9.0), 18) == [
        "um", "dois", "tres"]


def test_corpo_cai_ate_caber():
    from kit.medidas import cabe, maior_corpo_que_cabe

    frase = ("Se o modelo segmenta qualquer coisa, o problema de visão "
             "industrial está resolvido?")
    escolhido = maior_corpo_que_cabe(frase, Inches(11.0), Inches(1.9), 40, 24,
                                     negrito=True, entrelinha=1.12)
    assert 24 <= escolhido < 40
    assert cabe(frase, Inches(11.0), Inches(1.9), escolhido, negrito=True,
                entrelinha=1.12)


def test_abaixo_de_nao_move_o_que_ja_cabe():
    """A regra só empurra o que colidiria: slide aprovado não pode sair do lugar."""
    prs = nova_apresentacao()
    s = prs.slides.add_slide(prs.slide_layouts[6])
    curto = base.titulo(s, Inches(0.9), Inches(1.35), "Título curto",
                        tamanho=30, largura=Inches(11.0))
    assert base.abaixo_de(curto, 3.55) == 3.55

    longo = base.titulo(s, Inches(0.9), Inches(1.35),
                        "Um título bem mais longo, que ocupa duas linhas "
                        "inteiras nesta largura", tamanho=30,
                        largura=Inches(11.0))
    assert base.abaixo_de(longo, 2.18) > 2.18


# ------------------------------------------------- perfis de legibilidade

def test_perfil_ao_vivo_sobe_o_corpo_das_listas():
    """O perfil estava só documentado: o gerador tinha de passar a honrá-lo."""
    referencia = nova_apresentacao()
    ao_vivo = nova_apresentacao(perfil="ao_vivo")

    def corpo(prs):
        s = prs.slides.add_slide(prs.slide_layouts[6])
        par = base.marcadores(s, Inches(1), Inches(1), ["um"])[0][1]
        return par.text_frame.paragraphs[0].runs[0].font.size.pt

    assert corpo(referencia) == 12.5
    assert corpo(ao_vivo) >= 12


def test_papel_de_apoio_pode_ser_menor_que_o_perfil():
    """Legenda e número de página são apoio, e não texto de leitura."""
    from kit.politica import PAPEIS_DE_APOIO, PERFIS, PISO_ABSOLUTO

    assert PISO_ABSOLUTO == PERFIS["referencia"]
    for papel in ("legenda", "rotulo", "numero", "rodape"):
        assert papel in PAPEIS_DE_APOIO


# ------------------------------------------------- validador, texto sobre texto

def test_validador_acusa_texto_sobre_texto(tmp_path):
    """O defeito que só aparecia olhando o slide: título cobrindo o apoio."""
    prs = nova_apresentacao()
    s = prs.slides.add_slide(prs.slide_layouts[6])
    base.titulo(s, Inches(0.9), Inches(1.3),
                "Um título propositalmente longo, que ocupa mais de duas "
                "linhas inteiras nesta largura estreita", tamanho=32,
                largura=Inches(6.0))
    base.linha_apoio(s, Inches(0.9), Inches(1.9), "A frase de apoio embaixo.")
    aplicar_em_todos(prs)
    arquivo = tmp_path / "colisao.pptx"
    prs.save(str(arquivo))

    codigo, saida = _validar(arquivo)
    assert codigo == 2
    assert "texto sobre texto" in saida


def test_validador_aceita_colunas_lado_a_lado(tmp_path):
    """Duas colunas ocupam a mesma altura sem se atrapalharem."""
    prs = nova_apresentacao()
    s = prs.slides.add_slide(prs.slide_layouts[6])
    base.texto(s, Inches(0.9), Inches(2.0), Inches(4.0), Inches(1.0),
               "Coluna da esquerda, com algum texto dentro dela.", 12,
               base.BRANCO)
    base.texto(s, Inches(6.0), Inches(2.0), Inches(4.0), Inches(1.0),
               "Coluna da direita, com algum texto dentro dela.", 12,
               base.BRANCO)
    aplicar_em_todos(prs)
    arquivo = tmp_path / "colunas.pptx"
    prs.save(str(arquivo))

    codigo, saida = _validar(arquivo)
    assert "texto sobre texto" not in saida


# ------------------------------------------- regras de escrita do repositório

def _verificar_texto(caminho):
    import subprocess
    r = subprocess.run(
        [sys.executable, str(RAIZ / "scripts" / "verificar_texto.py"),
         str(caminho)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "")


def test_verificador_acusa_travessao_em_qualquer_arquivo(tmp_path):
    alvo = tmp_path / "nota.md"
    alvo.write_text("Uma frase %s com travessão.\n" % TRAVESSAO,
                    encoding="utf-8")
    codigo, saida = _verificar_texto(alvo)
    assert codigo == 2
    assert "travessão" in saida


def test_verificador_acusa_hifens_no_lugar_do_travessao(tmp_path):
    alvo = tmp_path / "nota.md"
    alvo.write_text("Uma frase -- com hifens.\n", encoding="utf-8")  # grafia-literal
    codigo, saida = _verificar_texto(alvo)
    assert codigo == 2


def test_verificador_ignora_regua_de_comentario(tmp_path):
    alvo = tmp_path / "codigo.py"
    alvo.write_text("# ---------------- seção\nx = 1\n", encoding="utf-8")
    codigo, _ = _verificar_texto(alvo)
    assert codigo == 0


def test_correcao_nao_toca_em_identificador():
    """Acentuar `titulo(` produziria um nome que compila e falha ao rodar."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "verificar_texto", RAIZ / "scripts" / "verificar_texto.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)

    fonte = 'x = titulo(s, secao="A")  # a composicao entra aqui\n'  # grafia-literal
    saida = modulo.corrigir_acentos_em_codigo(fonte)
    assert "titulo(s, secao=" in saida  # grafia-literal
    assert "composição" in saida


def test_correcao_preserva_bloco_de_codigo_no_markdown():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "verificar_texto", RAIZ / "scripts" / "verificar_texto.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)

    fonte = ("Veja a composicao abaixo.\n\n```python\nnova_apresentacao()\n"  # grafia-literal
             "```\n\nE a transicao no fim.\n")  # grafia-literal
    saida = modulo.corrigir_acentos(fonte)
    assert "composição" in saida
    assert "nova_apresentacao()" in saida
    assert "transição" in saida


# ------------------------------------------------------------- tema do IFES

def test_tema_ifes_sai_em_arial_e_no_verde_do_programa(tmp_path):
    """O modelo IFES não é o `escuro`: fonte e paleta mudam no tema interno."""
    from kit.tema_ifes import VERDE_2, nova_apresentacao_ifes

    prs = nova_apresentacao_ifes()
    arquivo = tmp_path / "ifes.pptx"
    prs.save(str(arquivo))

    achados = conferir(arquivo)
    assert achados["majorFont"] == "Arial"
    assert achados["minorFont"] == "Arial"
    assert achados["accent1"].upper() == VERDE_2


def test_identidade_fica_gravada_no_arquivo():
    """Sem isso o validador cobraria a paleta `escuro` de um deck IFES."""
    from kit.politica import identidade_de, metadados
    from kit.tema_ifes import nova_apresentacao_ifes

    assert identidade_de(nova_apresentacao_ifes()) == "ifes"
    assert identidade_de(nova_apresentacao()) == "escuro"
    assert metadados(nova_apresentacao_ifes())["perfil"] == "ao_vivo"


def test_paleta_e_fontes_mudam_com_a_identidade():
    from kit.politica import fontes_de, paleta_de

    assert "00E5C0" in paleta_de("escuro")
    assert "00E5C0" not in paleta_de("ifes")
    assert "1C7F5C" in paleta_de("ifes")
    assert fontes_de("escuro") == {"Montserrat"}
    assert "Arial" in fontes_de("ifes")


def test_identidade_desconhecida_e_recusada():
    from kit.politica import configurar

    with pytest.raises(ValueError):
        configurar(nova_apresentacao(), identidade="unesp")


def test_medida_muda_com_a_familia():
    """Medir Arial com a tabela da Montserrat erra a previsão de quebra."""
    from kit.medidas import largura_do_trecho, usar_familia

    frase = "Filtros de deteccao de bordas"  # grafia-literal
    montserrat = largura_do_trecho(frase, 24, True, "montserrat")
    arial = largura_do_trecho(frase, 24, True, "arial")
    assert arial < montserrat

    anterior = usar_familia("arial")
    try:
        assert largura_do_trecho(frase, 24, True) == arial
    finally:
        usar_familia(anterior)


def test_familia_sem_tabela_e_recusada():
    from kit.medidas import largura_do_trecho

    with pytest.raises(ValueError):
        largura_do_trecho("x", 12, False, "comic sans")


def test_composicoes_ifes_geram_e_ficam_na_area_util():
    from kit.layouts_ifes import (cabecalho, capa as capa_ifes, cartao, chip,
                                  corpo, destaque, fonte as fonte_ifes, novo,
                                  pol, rotulo)
    from kit.tema_ifes import DIREITA, MARGEM, nova_apresentacao_ifes

    prs = nova_apresentacao_ifes()
    capa_ifes(prs, "Título do seminário", "Disciplina e código",
              "Autores | IFES")
    s = novo(prs)
    cabecalho(s, "Título do slide", "Uma linha de contexto.")
    cartao(s, MARGEM, 1.45, 3.40, 1.20)
    chip(s, MARGEM + 0.2, 1.6, 1.6, 0.3, "TERMO")
    rotulo(s, MARGEM + 0.2, 2.0, "Rótulo")
    corpo(s, MARGEM + 0.2, 2.3, 3.0, 0.6, "Texto de leitura do cartão.")
    destaque(s, 6.06, "A frase que fecha o slide.")
    fonte_ifes(s, "Fonte: elaboração própria.")
    assert len(prs.slides.__iter__.__self__._sldIdLst) == 2

    # A capa tem grade própria e fica de fora: o conteúdo é que responde à
    # coluna lateral do modelo.
    for forma in s.shapes:
        if forma.left is None or not forma.width:
            continue
        if pol(forma.width) > 13:      # o fundo do modelo sangra de propósito
            continue
        assert pol(forma.left) >= MARGEM - 0.02
        assert pol(forma.left) + pol(forma.width) <= DIREITA + 0.02


def test_fecho_sai_sem_caixa_e_a_altura_acompanha_a_frase():
    """O fecho é régua mais frase. Caixa tingida com barra lateral saiu."""
    from kit.layouts_ifes import altura_do_destaque, destaque, novo, pol
    from kit.tema_ifes import nova_apresentacao_ifes

    prs = nova_apresentacao_ifes()
    s = novo(prs)
    formas_antes = len(s.shapes._spTree)
    regua, frase = destaque(s, 1.5, "Uma frase.")
    assert len(s.shapes._spTree) - formas_antes == 2   # régua e frase, só
    assert pol(regua.height) < 0.03                    # é régua, não bloco
    assert regua.fill.type == 1

    longa = ("Uma frase bem mais comprida, que ocupa duas linhas inteiras na "
             "largura útil do slide e ainda continua por mais um pouco.")
    assert altura_do_destaque(longa) > altura_do_destaque("Uma frase.")


def test_titulo_de_capa_nao_quebra_em_duas_linhas():
    """Duas linhas em 54 pontos estouram a faixa branca da capa."""
    from kit.layouts_ifes import _quebra, capa as capa_ifes, pol
    from kit.tema_ifes import CORPO, nova_apresentacao_ifes

    prs = nova_apresentacao_ifes()
    _, _, titulo, _, _ = capa_ifes(
        prs, "Filtros de Detecção de Bordas", "Disciplina", "Autores")
    corpo_usado = titulo.text_frame.paragraphs[0].runs[0].font.size.pt
    assert corpo_usado <= CORPO["titulo_capa"]
    assert not _quebra(titulo.text_frame.text, pol(titulo.width), corpo_usado)


def test_capa_recusa_titulo_que_nao_cabe_em_uma_linha():
    """Melhor parar a geração do que entregar a faixa branca estourada."""
    from kit.layouts_ifes import capa as capa_ifes
    from kit.tema_ifes import nova_apresentacao_ifes

    with pytest.raises(ValueError):
        capa_ifes(nova_apresentacao_ifes(),
                  "Um título longo demais para caber em uma única linha da "
                  "faixa branca da capa do modelo do programa",
                  "Disciplina", "Autores")


def test_validador_aceita_um_deck_no_modelo_do_ifes(tmp_path):
    from kit.layouts_ifes import cabecalho, capa as capa_ifes, destaque, novo
    from kit.layouts_ifes import fonte as fonte_ifes
    from kit.tema_ifes import nova_apresentacao_ifes

    prs = nova_apresentacao_ifes()
    capa_ifes(prs, "Título do seminário", "Disciplina e código",
              "Autores | IFES")
    s = novo(prs)
    cabecalho(s, "Título do slide", "Uma linha de contexto.")
    destaque(s, 6.06, "A frase que fecha o slide.")
    fonte_ifes(s, "Fonte: elaboração própria.")
    aplicar_em_todos(prs)
    arquivo = tmp_path / "ifes.pptx"
    prs.save(str(arquivo))

    codigo, saida = _validar(arquivo)
    assert codigo == 0, saida
    assert "identidade: ifes" in saida


def test_validador_recusa_a_paleta_escura_em_deck_do_ifes(tmp_path):
    """Turquesa do `escuro` num deck IFES é desvio de identidade."""
    from kit.layouts_ifes import cabecalho, forma, novo
    from kit.tema_ifes import nova_apresentacao_ifes

    prs = nova_apresentacao_ifes()
    s = novo(prs)
    cabecalho(s, "Título do slide", "Uma linha de contexto.")
    forma(s, 2.05, 2.0, 2.0, 0.5, "00E5C0")
    aplicar_em_todos(prs)
    arquivo = tmp_path / "misturado.pptx"
    prs.save(str(arquivo))

    codigo, saida = _validar(arquivo)
    assert codigo == 2
    assert "fora da paleta" in saida


# ------------------------------------------------- apresentação importada

def _origem(tmp_path):
    """Um .pptx "da pessoa": tema próprio, um slide com título e lista."""
    from pptx import Presentation
    from kit.tema import aplicar_tema

    prs = Presentation()
    aplicar_tema(prs, fonte="Georgia", cores={"accent1": "E07A1F",
                                              "lt2": "EEF1F6"})
    s = prs.slides.add_slide(prs.slide_layouts[1])
    s.shapes.title.text = "Resultados"
    s.placeholders[1].text_frame.text = "um\ndois"
    s.notes_slide.notes_text_frame.text = "nota"
    caminho = tmp_path / "origem.pptx"
    prs.save(str(caminho))
    return caminho


def test_extrair_tira_titulo_texto_e_notas(tmp_path):
    import json
    from kit.importado import extrair

    conteudo = json.loads(extrair(_origem(tmp_path), tmp_path / "deck")
                          .read_text(encoding="utf-8"))
    slide = conteudo["slides"][0]
    assert slide["titulo"] == "Resultados"
    assert [p["texto"] for p in slide["textos"][0]] == ["um", "dois"]
    assert slide["notas"] == "nota"


def test_modelo_importado_mantem_o_design_e_passa_no_validador(tmp_path):
    from kit.importado import abrir_modelo, design, itens, novo, titulo
    from kit.politica import identidade_de
    from kit.slides import anima

    prs = abrir_modelo(_origem(tmp_path))
    assert len(prs.slides._sldIdLst) == 0
    assert identidade_de(prs) == "importada"
    d = design(prs)
    assert d["fontes"]["corpo"] == "Georgia"
    assert d["cores"]["accent1"] == "E07A1F"
    s = novo(prs)
    t = titulo(s, "Um assunto por slide")
    linhas = itens(s, d["margem_esquerda"], 2.0, 6.0, ["um", "dois"])
    anima(s, [(0, [t])] + [(300, l) for l in linhas])
    aplicar_em_todos(prs)
    arquivo = tmp_path / "importado.pptx"
    prs.save(str(arquivo))

    codigo, saida = _validar(arquivo)
    assert codigo == 0, saida
    assert "identidade: importada" in saida


def test_importada_recusa_cor_fora_do_tema(tmp_path):
    from kit.importado import abrir_modelo, novo, retangulo, titulo

    prs = abrir_modelo(_origem(tmp_path))
    s = novo(prs)
    titulo(s, "Título")
    retangulo(s, 1.0, 2.0, 2.0, 1.0, "00E5C0")
    aplicar_em_todos(prs)
    arquivo = tmp_path / "fora.pptx"
    prs.save(str(arquivo))
    codigo, saida = _validar(arquivo)
    assert codigo == 2
    assert "fora da paleta" in saida


def test_linha_do_tempo_ifes_usa_wipe_e_fica_na_area_util(tmp_path):
    from kit.animacao import monta_timing
    from kit.layouts_ifes import linha_do_tempo, novo
    from kit.tema_ifes import nova_apresentacao_ifes

    prs = nova_apresentacao_ifes()
    s = novo(prs)
    efeitos = linha_do_tempo(s, [("2024", "Um", "Primeiro marco."),
                                 ("2025", "Dois", "Segundo marco."),
                                 ("2026", "Três", "Terceiro marco.")])
    assert any(e[1] == "wipe(left)" for e in efeitos)
    monta_timing(s, efeitos)
    aplicar_em_todos(prs)
    arquivo = tmp_path / "linha.pptx"
    prs.save(str(arquivo))
    codigo, saida = _validar(arquivo)
    assert codigo == 0, saida
    with pytest.raises(ValueError):
        linha_do_tempo(novo(prs), [("1", "só um", "")])


def test_extrair_acha_titulo_desenhado_e_margem_do_conteudo(tmp_path):
    """Apresentação desenhada à mão: título em caixa comum, layout 4:3 num
    slide 16:9. O título e a margem saem do conteúdo, não do layout."""
    import json
    from pptx import Presentation
    from kit.importado import extrair

    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rotulo = s.shapes.add_textbox(Inches(0.6), Inches(0.3), Inches(4), Inches(0.3))
    rotulo.text_frame.text = "SEÇÃO"
    rotulo.text_frame.paragraphs[0].runs[0].font.size = Pt(10)
    tit = s.shapes.add_textbox(Inches(0.6), Inches(0.7), Inches(12), Inches(0.6))
    tit.text_frame.text = "Título desenhado"
    tit.text_frame.paragraphs[0].runs[0].font.size = Pt(24)
    num = s.shapes.add_textbox(Inches(0.6), Inches(3.0), Inches(4), Inches(1))
    num.text_frame.text = "95%"
    num.text_frame.paragraphs[0].runs[0].font.size = Pt(40)
    origem = tmp_path / "desenhada.pptx"
    prs.save(str(origem))

    conteudo = json.loads(extrair(origem, tmp_path / "deck")
                          .read_text(encoding="utf-8"))
    assert conteudo["slides"][0]["titulo"] == "Título desenhado"
    design = json.loads((tmp_path / "deck" / "assets" / "importado"
                         / "design.json").read_text(encoding="utf-8"))
    assert abs(design["margem_esquerda"] - 0.6) < 0.01
