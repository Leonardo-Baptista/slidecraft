# Validação antes de apresentar

Gerar não é suficiente. Três conferências evitam a maioria dos problemas que
só aparecem na frente da plateia.

---

## 0. O comando único

Na maioria das vezes, isto basta. Ele gera, valida e prepara a revisão visual:

```bash
.venv\Scripts\python.exe scripts\produzir.py meu_deck
```

Sem argumento, roda todos os decks. É o teste do repositório depois de mexer
no kit. Código de saída 0 quando tudo está limpo, 1 com aviso, 2 com erro.

As seções abaixo detalham cada etapa, para quando você precisar olhar de
perto.

---

## 1. Validador automático

Lê o XML do arquivo, sem abrir o PowerPoint, e relata o que cada slide tem.

```bash
.venv\Scripts\python.exe scripts\validar_deck.py saida\meu_deck.pptx
```

Saída típica:

```
arquivo: saida/demonstracao.pptx
tamanho: 0.4 MB   slides: 8   tema: Montserrat   identidade: ifes   perfil: ao_vivo   padrao: 1.3

  #   transicao  efeitos  video  auto  loop  formas
  ----------------------------------------------------
  1   fade       0        0      0     0     6
  2   fade       13       0      0     0     15
  3   fade       10       1      1     1     12
```

Ele percorre as formas entrando em grupos e em células de tabela, e associa
cada efeito ao objeto certo pelo identificador, em vez de procurar texto solto
no XML.

A linha de cabeçalho traz a identidade declarada no arquivo, e é ela que define
o que o validador cobra: paleta, família tipográfica e margem. Um deck no
modelo IFES sai como `identidade: ifes`, com a paleta verde e a Arial;
um deck escuro sai como `escuro`, com o turquesa e a Montserrat. Misturar
as duas reprova. Ver a seção 0b em docs/padrao-visual.md.

**Erros**, que reprovam o arquivo:

| Erro | O que significa |
|---|---|
| formato fora de 16:9 | não é o padrão da empresa |
| fonte de títulos ou de corpo do tema fora da família da identidade | caixa de texto criada na mão nasceria errada |
| fonte fora do padrão | a família da identidade é obrigatória, inclusive dentro de grupo e de tabela |
| preenchimento fora da paleta | cor de fundo que não pertence à identidade do arquivo |
| travessão no texto | quebra a regra de escrita |
| acentuação | palavra sem acento que deveria ter |
| sem transição, ou transição fora de fade e morph | passou batido ou saiu do vocabulário |
| efeito dependendo de clique | trava a apresentação esperando um clique |
| vídeo que não inicia sozinho | a árvore de tempo foi reescrita depois do vídeo |
| texto de exemplo do modelo | alguém esqueceu de trocar o conteúdo |
| texto sobre texto | duas caixas de texto se cobrindo na tela |

**Avisos**, que pedem uma olhada:

| Aviso | O que significa |
|---|---|
| corpo abaixo do mínimo do perfil | texto pequeno demais para a situação de uso |
| cor de texto fora da paleta | pode ser intencional, confira |
| forma passando da margem de 0,9 polegada | caixa mais larga que a área de conteúdo |
| vídeo acima de 25 MB | arquivo pesado, PowerPoint lento para abrir |

O corpo mínimo vem do perfil gravado no arquivo. Para conferir com outro
perfil, use `--perfil` seguido de `ao_vivo`, `leitura`, `anexo` ou
`referencia`.

O corpo mínimo do perfil vale para o texto de leitura. Rótulo, legenda, número
de página e rodapé são apoio, marcados no nome da forma como `gt:legenda:...`,
e para eles vale o piso absoluto de 9,5 pontos. Uma legenda de 10 pontos ao
lado de um corpo de 12 é hierarquia, e não desvio.

### 1.1 Texto sobre texto

Esta é a verificação que substitui o olho para o defeito mais comum depois de
uma edição. O validador não confia na altura declarada da caixa, que quase
nunca corresponde ao que aparece: o kit cria caixas baixas e deixa o texto
crescer para baixo. Ele mede quantas linhas cada trecho vai ocupar, usando as
larguras reais da Montserrat gravadas em `kit/_metricas.py`, e compara os
retângulos resultantes.

A denúncia sai quando duas caixas se invadem em mais de 0,09 polegada na
vertical e se cruzam em pelo menos 35% da largura da mais estreita. As duas
condições juntas evitam o alarme falso: duas colunas lado a lado ocupam a mesma
faixa de altura sem se atrapalharem, e um rótulo que encosta um décimo de
milímetro na descrição não aparece na tela.

Para gerar de novo as larguras, caso uma família tipográfica mude:

```bash
.venv\Scripts\python.exe scripts\gerar_metricas.py
```

Código de saída: 0 sem nada, 1 só com aviso, 2 com erro.

---

## 1.2 Regras de escrita do repositório

O validador cuida dos slides. As regras de escrita valem para tudo que está
escrito no projeto, incluindo código, comentário, documentação e mensagem de
commit, e quem cuida disso é um verificador próprio:

```bash
.venv\Scripts\python.exe scripts\verificar_texto.py
.venv\Scripts\python.exe scripts\verificar_texto.py --corrigir
```

Ele roda junto com `scripts\produzir.py` e no fluxo de integração contínua.

**Travessão** é erro em qualquer arquivo, seja o caractere tipográfico ou a
sequência de dois ou três hifens cercada por espaços. Uma régua de quatro ou
mais hifens continua valendo como separador de comentário.

**Acentuação** é erro em `.md` e `.txt`, e aviso em código. A correção
automática entra em prosa, e em código entra apenas dentro de string, docstring
e comentário, lendo o arquivo por token. O motivo é concreto: acentuar
`titulo(` ou `secao=` produz um identificador que ainda compila e só quebra na
hora de rodar.

Nunca são tocados: identificador, caminho, endereço, trecho entre crases, bloco
de código cercado no Markdown e string de uma palavra só, que em código quase
sempre é uma chave comparada com igualdade. Num diagrama Mermaid, o que está
entre aspas ou entre barras verticais é rótulo lido por gente, e recebe acento
como qualquer outra prosa.

Quando a grafia errada é o próprio assunto, como no teste da regra, a marcação
`grafia-literal` no fim da linha isenta aquela linha.

---

## 2. Conferência visual

Colisão de texto, foto mal enquadrada e bloco que estourou a margem só
aparecem olhando.

```bash
.venv\Scripts\python.exe scripts\exportar_slides.py saida\meu_deck.pptx --contato
```

Gera um PNG por slide e uma folha de contato com todos juntos, em
`saida\_slides_<nome>\`. Olhe a folha inteira antes de olhar slide a slide: os
problemas de ritmo, como três slides densos em sequência, só aparecem no
conjunto.

O arquivo precisa estar fechado no PowerPoint.

---

## 3. Perguntar ao PowerPoint o que ele entendeu

O validador lê o XML. Esta conferência é diferente: ela pergunta ao próprio
PowerPoint como ele interpretou o arquivo. Vale quando algo parece certo no XML
e errado na tela.

```powershell
$pp = New-Object -ComObject PowerPoint.Application
$pres = $pp.Presentations.Open("C:\caminho\deck.pptx", $true, $false, $false)
foreach ($s in $pres.Slides) {
  "slide {0}: {1} efeitos, transicao {2}" -f $s.SlideIndex,
    $s.TimeLine.MainSequence.Count, $s.SlideShowTransition.EntryEffect
}
$pres.Close(); $pp.Quit()
```

Códigos de transição: `1793` é fade, `3954` é Morph.

---

## 4. Checklist antes de enviar ou apresentar

- [ ] Validador sem alertas.
- [ ] Folha de contato conferida, sem texto colidindo.
- [ ] Nenhum bloco com mais de quatro marcadores.
- [ ] Alternância entre fundo preto e claro, sem três densos seguidos.
- [ ] Vídeos iniciam sozinhos e repetem.
- [ ] Nomes de produto na grafia do portfólio.
- [ ] Todo número com linha de fonte no slide.
- [ ] Nenhum dado confidencial que não tenha sido liberado.
- [ ] Montserrat instalada na máquina que vai apresentar.
- [ ] Arquivo abre e roda em modo de apresentação, do primeiro ao último slide.

---

## 5. Teste em condição real

Se a apresentação for online, abra uma reunião de teste sozinho, compartilhe a
tela e passe o deck inteiro. Duas coisas aparecem só assim: contraste que some
na compressão do compartilhamento, e vídeo que engasga porque o arquivo está
pesado demais.
