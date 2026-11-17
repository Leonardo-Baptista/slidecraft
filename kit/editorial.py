"""Regras verificáveis de escrita para materiais em português do Brasil.

Não é um corretor gramatical completo. A lista abaixo só contém grafias
inequívocas; palavras ambíguas exigem revisão humana e nunca são substituídas.
"""
import re
import unicodedata

IDIOMA = "pt-BR"
PROIBIDOS = frozenset(chr(n) for n in (0x2012, 0x2013, 0x2014, 0x2015,
                                      0x2212, 0x2E3A, 0x2E3B, 0xFE58))
# A chave é escrita sem acento de propósito: é a grafia errada que se procura.
# Nenhuma ferramenta de correção automática pode reescrever este bloco, sob
# pena de a lista passar a mapear cada palavra para ela mesma e a regra deixar
# de existir em silêncio. O teste `test_grafias_mapeiam_para_acentuada` guarda
# exatamente isso.
GRAFIAS = dict(zip(
    ("apresentacao apresentacoes acentuacao acentuacoes portugues nao "
     "informacao informacoes operacao operacoes validacao validacoes "
     "comparacao comparacoes segmentacao segmentacoes geracao geracoes "
     "solucao solucoes conclusao conclusoes configuracao configuracoes "
     "deteccao predicao predicoes traducao transicao transicoes "
     "animacao animacoes composicao composicoes reproducao revisao "
     "sequencia frequencia referencia referencias tecnica tecnicas "
     "tecnico tecnicos titulo titulos subtitulo subtitulos secao secoes "
     "padrao padroes criterio criterios dominio dominios conteudo conteudos "
     "protecao manutencao medicao medicoes integracao implementacao "
     "implantacao implantacoes tambem apos atraves possivel possiveis "
     "minimo minima maximo maxima hipotese hipoteses arquitetura").split(),
    ("apresentação apresentações acentuação acentuações português não "
     "informação informações operação operações validação validações "
     "comparação comparações segmentação segmentações geração gerações "
     "solução soluções conclusão conclusões configuração configurações "
     "detecção predição predições tradução transição transições "
     "animação animações composição composições reprodução revisão "
     "sequência frequência referência referências técnica técnicas "
     "técnico técnicos título títulos subtítulo subtítulos seção seções "
     "padrão padrões critério critérios domínio domínios conteúdo conteúdos "
     "proteção manutenção medição medições integração implementação "
     "implantação implantações também após através possível possíveis "
     "mínimo mínima máximo máxima hipótese hipóteses arquitetura").split()))
GRAFIAS = {a: b for a, b in GRAFIAS.items() if a != b}


def normalizar(texto):
    return unicodedata.normalize("NFC", str(texto))


def problemas(texto):
    """Retorna problemas sem alterar grafias, nomes próprios, URLs ou código."""
    texto = normalizar(texto)
    achados = []
    if any(c in PROIBIDOS for c in texto) or re.search(r"\s--+\s", texto):
        achados.append("travessão ou sinal equivalente proibido; use pontuação comum")
    # Identificadores, caminhos, e-mails e URLs não são prosa.
    prosa = re.sub(r"https?://\S+|\S+@\S+|`[^`]*`|\b\w+[/\\_]\S*", "", texto)
    for palavra in sorted(set(re.findall(r"\b[^\W\d_]+\b", prosa, re.UNICODE))):
        correta = GRAFIAS.get(palavra.casefold())
        if not correta:
            continue
        # A sugestão acompanha a caixa da palavra original, para poder ser
        # aplicada sem uma segunda decisão de quem corrige.
        if palavra.isupper():
            correta = correta.upper()
        elif palavra[:1].isupper():
            correta = correta[:1].upper() + correta[1:]
        achados.append("acentuação: '%s' deve ser '%s'" % (palavra, correta))
    return achados


def preparar(texto):
    """Impede travessões na geração; a revisão lexical ocorre no validador."""
    texto = normalizar(texto)
    if any(c in PROIBIDOS for c in texto) or re.search(r"\s--+\s", texto):
        raise ValueError("Travessões não são permitidos em nenhum texto do material.")
    return texto


def notas(slide, conteudo):
    """Notas em pt-BR, incluindo referências e ressalvas para quem apresenta."""
    tf = slide.notes_slide.notes_text_frame
    tf.text = preparar(conteudo)
    for p in tf.paragraphs:
        p._p.get_or_add_pPr().get_or_add_defRPr().set("lang", IDIOMA)
        for r in p.runs:
            r.font._rPr.set("lang", IDIOMA)

