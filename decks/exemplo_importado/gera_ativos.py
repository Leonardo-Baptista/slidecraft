# -*- coding: utf-8 -*-
"""Fabrica a "apresentação que a pessoa já tinha", para o exemplo de importação.

Na vida real este arquivo vem da pessoa. Aqui ele é gerado para o exemplo
rodar em qualquer máquina: tema próprio (azul-marinho, laranja e Georgia),
uma faixa e uma marca no slide mestre, e três slides densos, do jeito que
costumam chegar: listas longas, números soltos no meio do texto.

    .venv/Scripts/python.exe decks/exemplo_importado/gera_ativos.py
"""
import copy
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(RAIZ))

from pptx import Presentation  # noqa: E402
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402
from pptx.util import Inches, Pt  # noqa: E402

from kit.tema import aplicar_tema  # noqa: E402

# Saída em UTF-8 também no console do Windows, para acento não virar lixo.
sys.stdout.reconfigure(encoding="utf-8")

ASSETS = AQUI / "assets"
CORES = {"dk1": "1F2A44", "lt1": "FFFFFF", "dk2": "1F2A44", "lt2": "EEF1F6",
         "accent1": "E07A1F", "accent2": "2E86AB", "accent3": "5B8C5A",
         "accent4": "8C8C8C", "accent5": "C9D3E0", "accent6": "F4D6B8",
         "hlink": "2E86AB", "folHlink": "1F2A44"}


def _no_mestre(prs, forma):
    """Move uma forma criada num slide para o mestre: vira parte do design."""
    arvore = prs.slide_masters[0].shapes._spTree
    arvore.append(copy.deepcopy(forma._element))
    forma._element.getparent().remove(forma._element)


def main():
    ASSETS.mkdir(exist_ok=True)
    prs = Presentation()          # 4:3, como muito arquivo antigo
    aplicar_tema(prs, fonte="Georgia", cores=CORES)

    rascunho = prs.slides.add_slide(prs.slide_layouts[6])
    faixa = rascunho.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(7.1),
                                      prs.slide_width, Inches(0.4))
    faixa.fill.solid()
    faixa.fill.fore_color.rgb = RGBColor.from_string(CORES["dk1"])
    faixa.line.fill.background()
    marca = rascunho.shapes.add_textbox(Inches(7.2), Inches(7.14), Inches(2.6),
                                        Inches(0.3))
    marca.text_frame.text = "ESCOLA MODELO"
    run = marca.text_frame.paragraphs[0].runs[0]
    run.font.size, run.font.bold = Pt(11), True
    run.font.color.rgb = RGBColor.from_string(CORES["accent1"])
    _no_mestre(prs, faixa)
    _no_mestre(prs, marca)
    prs.part.drop_rel(prs.slides._sldIdLst[0].rId)
    prs.slides._sldIdLst.remove(prs.slides._sldIdLst[0])

    s = prs.slides.add_slide(prs.slide_layouts[0])
    s.shapes.title.text = "Coleta Seletiva na Escola"
    s.placeholders[1].text = "Relatório do primeiro semestre"

    s = prs.slides.add_slide(prs.slide_layouts[1])
    s.shapes.title.text = "Resultados do semestre"
    s.placeholders[1].text_frame.text = (
        "Começamos em fevereiro com dois coletores\n"
        "Em abril chegaram os coletores novos\n"
        "Em junho fizemos a feira de troca\n"
        "Recolhemos 3.400 kg de recicláveis\n"
        "Participaram 620 alunos\n"
        "A separação correta chegou a 87%\n"
        "A cooperativa do bairro buscou o material toda semana")
    s.notes_slide.notes_text_frame.text = "Agradecer a equipe da limpeza."

    s = prs.slides.add_slide(prs.slide_layouts[1])
    s.shapes.title.text = "Próximos passos"
    s.placeholders[1].text_frame.text = (
        "Coletor de óleo na cantina\nOficina com as turmas do 6º ano\n"
        "Meta de 5.000 kg no segundo semestre")

    prs.save(str(ASSETS / "original.pptx"))
    print("apresentação de origem:", ASSETS / "original.pptx")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
