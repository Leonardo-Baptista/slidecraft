# -*- coding: utf-8 -*-
"""Vídeo para slide: corte, quadro de capa e clipes gerados em código.

O padrão do kit para clipe embutido: 15 a 25 segundos, sem áudio, 1280 de
largura, 15 quadros por segundo. Isso mantém o arquivo leve o bastante para o
PowerPoint abrir rápido e compartilhar tela sem engasgo.

O binário do ffmpeg vem do pacote imageio-ffmpeg, dentro do ambiente virtual.
Não é preciso instalar ffmpeg no sistema.
"""
import subprocess
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

LARGURA_PADRAO = 1280
QUADROS_POR_SEGUNDO = 15
QUALIDADE = 26  # crf do libx264: quanto menor, melhor e mais pesado


# Arial em negrito, procurada nos lugares de costume de cada sistema. Quem
# usa a identidade `escuro` passa o caminho da Montserrat em `fonte`.
CANDIDATAS = (
    "C:/Windows/Fonts/arialbd.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
)


def fonte_do_sistema(candidatas=CANDIDATAS):
    """Primeira fonte em negrito que existir nesta máquina."""
    for caminho in candidatas:
        if Path(caminho).exists():
            return Path(caminho)
    raise FileNotFoundError(
        "Nenhuma fonte em negrito encontrada. Passe o caminho de um .ttf em "
        "`fonte`.")


def _ffmpeg(*argumentos):
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
                    *argumentos], check=True)


def cortar(entrada, saida, inicio, duracao, largura=LARGURA_PADRAO,
           fps=QUADROS_POR_SEGUNDO, crf=QUALIDADE):
    """Corta um trecho, remove o áudio e recomprime no perfil do kit.

    inicio e duracao em segundos.
    """
    saida = Path(saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    _ffmpeg("-ss", str(inicio), "-t", str(duracao), "-i", str(entrada), "-an",
            "-vf", "scale=%d:-2,fps=%d" % (largura, fps),
            "-c:v", "libx264", "-crf", str(crf), "-preset", "medium",
            "-pix_fmt", "yuv420p", str(saida))
    return saida


def primeiro_quadro(clipe, destino):
    """Quadro de capa. É o que aparece antes de tocar e se a reprodução falhar."""
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    _ffmpeg("-i", str(clipe), "-frames:v", "1", "-q:v", "2", str(destino))
    return destino


def ultimo_quadro(clipe, destino):
    """Use como capa quando o clipe precisa terminar em um estado específico.

    Um contador que para em 95%, por exemplo: com o último quadro como capa, o
    estado parado é o final, e o número não volta a zero quando o vídeo encerra.
    """
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    _ffmpeg("-sseof", "-0.2", "-i", str(clipe), "-frames:v", "1", "-q:v", "2",
            str(destino))
    return destino


def duracao(clipe):
    """Duração em segundos, lida do cabeçalho do arquivo."""
    saida = subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-i", str(clipe)],
        capture_output=True, text=True, errors="ignore").stderr
    for linha in saida.splitlines():
        if "Duration:" in linha:
            bruto = linha.split("Duration:")[1].split(",")[0].strip()
            h, m, s = bruto.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    return None


def contador(destino, ate=95, sufixo="%", segundos=1.8, espera=1.0,
             largura=1200, altura=520, corpo=340,
             cor=(0x1C, 0x7F, 0x5C), fonte=None, fundo=(0, 0, 0),
             formatar=None, origem=(0, 40), ancora=None):
    """Clipe de um número subindo, desacelerando no fim.

    Serve para a provocação numérica que o PowerPoint não faz nativamente.
    Gerar um clipe é mais previsível que tentar reproduzir isso com animação.

    Para número dentro de cartão, e não em slide de provocação:
    - `fundo` é a cor do cartão, para o clipe não aparecer como um retângulo;
    - `formatar` recebe o valor do quadro e devolve o texto, o que permite
      vírgula decimal, ponto de milhar e marca de nota (94,4%*, 1.314). Com
      ele, o valor sobe sem arredondar para inteiro;
    - `ancora` é a âncora de texto do Pillow. "la" põe o topo das maiúsculas
      em `origem`, que é como a caixa de texto do PowerPoint alinha a primeira
      linha, e deixa o clipe no lugar exato do texto que ele substitui.
    """
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    pasta = destino.parent / ("_quadros_" + destino.stem)
    pasta.mkdir(exist_ok=True)

    tipo = ImageFont.truetype(str(fonte or fonte_do_sistema()), corpo)

    total = int(QUADROS_POR_SEGUNDO * 2 * segundos)
    curva = [ate * (1 - (1 - j / (total - 1)) ** 3) for j in range(total)]
    if formatar is None:
        rotulos = ["%d%s" % (round(v), sufixo) for v in curva]
    else:
        rotulos = [formatar(v) for v in curva[:-1]] + [formatar(ate)]
    rotulos += [rotulos[-1]] * int(QUADROS_POR_SEGUNDO * 2 * espera)

    for k, rotulo in enumerate(rotulos):
        im = Image.new("RGB", (largura, altura), fundo)
        ImageDraw.Draw(im).text(origem, rotulo, font=tipo, fill=cor,
                                anchor=ancora)
        im.save(pasta / ("q%03d.png" % k))

    _ffmpeg("-framerate", str(QUADROS_POR_SEGUNDO * 2),
            "-i", str(pasta / "q%03d.png"), "-c:v", "libx264", "-crf", "20",
            "-pix_fmt", "yuv420p", str(destino))
    for f in pasta.glob("*.png"):
        f.unlink()
    pasta.rmdir()
    return destino
