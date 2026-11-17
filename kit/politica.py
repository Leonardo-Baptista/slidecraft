"""Configuração editorial e visual compartilhada, sem mudar a identidade.

Uma identidade é o conjunto fechado de cores e fontes que um material pode
usar. São duas: `ifes`, o modelo público de apresentação do IFES, que é o
ponto de partida de todo deck novo (`decks/_modelo`), e `escuro`, fundo preto
com acento turquesa e Montserrat, para palestra com foto em tela cheia. A
terceira, `importada`, é o design de uma apresentação que a pessoa já tinha
(`kit/importado.py`): paleta e fontes saem do tema do próprio arquivo. A
`ifes` mora em `kit/tema_ifes.py` e é lida daqui sob demanda, para não criar
importação circular.

O que muda com a identidade é apenas o que o validador aceita como paleta e
como família tipográfica. Grade, animação, transição e regras de escrita são as
mesmas para as duas.
"""
VERSAO = "1.3"
# Corpo mínimo do texto de leitura, por situacao de uso.
PERFIS = {"referencia": 9.5, "ao_vivo": 12, "leitura": 11, "anexo": 10}
# Rotulo, legenda e mobiliario podem ser menores que o texto de leitura: sao
# apoio, não leitura. Para eles vale o piso absoluto.
PAPEIS_DE_APOIO = ("rotulo", "legenda", "numero", "rodape", "marca")
PISO_ABSOLUTO = PERFIS["referencia"]
PALETA = frozenset({
    "000000", "0D0D0D", "FFFFFF", "00E5C0", "B8E8DF", "00846F", "54C1AF",
    "9D9D9C", "575756", "E6E6E6", "C8C8C8", "F7F7F6", "D0D0D0", "DDDDDD",
})
FONTES = frozenset({"Montserrat"})
IDENTIDADE_PADRAO = "escuro"
IDENTIDADES = ("escuro", "ifes", "importada")


def paleta_de(identidade=IDENTIDADE_PADRAO):
    """Cores aceitas pela identidade, em hexadecimal maiúsculo sem cerquilha."""
    if identidade == "ifes":
        from kit import tema_ifes
        return tema_ifes.PALETA
    return PALETA


def fontes_de(identidade=IDENTIDADE_PADRAO):
    """Famílias tipográficas aceitas pela identidade."""
    if identidade == "ifes":
        from kit import tema_ifes
        return frozenset({tema_ifes.FONTE, tema_ifes.FONTE_CAPA,
                          tema_ifes.FONTE_MONO})
    return FONTES


def configurar(prs, perfil="referencia", divulgacao="interno",
               identidade=IDENTIDADE_PADRAO):
    if perfil not in PERFIS:
        raise ValueError("Perfil desconhecido: %s" % perfil)
    if divulgacao not in ("interno", "publico"):
        raise ValueError("Divulgação deve ser interno ou publico.")
    if identidade not in IDENTIDADES:
        raise ValueError("Identidade desconhecida: %s" % identidade)
    prs.core_properties.language = "pt-BR"
    prs.core_properties.keywords = (
        "slidecraft;padrão=%s;perfil=%s;divulgacao=%s;identidade=%s"
        % (VERSAO, perfil, divulgacao, identidade))
    return prs


def piso_de_leitura(slide):
    """Corpo mínimo exigido pelo perfil do arquivo a que o slide pertence.

    As composições consultam este piso antes de escrever texto de leitura, de
    modo que declarar `perfil="ao_vivo"` no build já produza corpo de 12
    pontos, sem cada deck ter que repetir o tamanho slide a slide.
    """
    try:
        prs = slide.part.package.presentation_part.presentation
        return PERFIS[metadados(prs).get("perfil", "referencia")]
    except Exception:
        # Slide avulso, fora de uma apresentação configurada.
        return PISO_ABSOLUTO


def identidade_de(prs):
    """Identidade declarada no arquivo. Sem declaração, é a `escuro`."""
    return metadados(prs).get("identidade", IDENTIDADE_PADRAO)


def metadados(prs):
    return dict(p.split("=", 1) for p in prs.core_properties.keywords.split(";")
                if "=" in p)


def papel(forma, nome):
    """Papel semântico no painel de seleção, sem interferência visual."""
    forma.name = "gt:%s:%d" % (nome, forma.shape_id)
    return forma
