# Armadilhas conhecidas

Problemas que já custaram tempo, com a causa e a solução. Leia antes de gastar
uma hora com algo que já foi resolvido.

---

## 1. A automação do PowerPoint erra o efeito de animação

**Sintoma:** você pede um wipe e o PowerPoint gera um esticar. Pede um fade e
ele gera um aparecer, sem transição de opacidade.

**Causa:** a numeração de efeitos da API de automação não bate com a do formato
do arquivo. `msoAnimEffectWipe` vale 23 na API, mas o `presetID` 23 no OOXML é
outro efeito.

**Solução:** o kit escreve a animação direto no XML, onde o comportamento é
definido pelo atributo `filter` do `p:animEffect`, que é inequívoco:
`filter="wipe(left)"`, `filter="fade"`. É o que `kit/animacao.py` faz.

---

## 2. Reescrever a árvore de tempo apaga o vídeo

**Sintoma:** o vídeo fica no slide mas não toca, nem no clique.

**Causa:** `monta_timing` substitui o `p:timing` inteiro. O nó de mídia criado
pelo `add_movie` mora ali dentro e se perde.

**Solução:** no slide com vídeo, crie as formas, escreva a animação e só então
insira o vídeo. `kit.slides.inserir_video` recoloca o comando de reprodução e a
repetição, e monta a sequência principal quando o slide não tem outra animação.

```python
anima(s, [...])                                  # primeiro a coreografia
inserir_video(s, clipe, x, y, largura, altura)   # depois o video
```

---

## 3. O número volta a zero quando o vídeo para

**Sintoma:** um clipe que conta até 95% mostra 0% de novo quando você clica
para avançar.

**Causa:** todo vídeo tem um quadro de capa, que aparece antes de tocar e
quando ele encerra. A capa padrão é o primeiro quadro.

**Solução:** use o último quadro como capa, com `kit.clipes.ultimo_quadro`.
Assim o estado parado é o final.

---

## 4. Arquivo aberto no PowerPoint não pode ser sobrescrito

**Sintoma:** `PermissionError: [Errno 13]` ao salvar.

**Solução:** feche o arquivo antes de rodar o gerador. Se precisar comparar
versões, gere com outro nome.

---

## 5. Peso do arquivo

**Sintoma:** PowerPoint demora para abrir e para entrar em modo de
apresentação. O compartilhamento de tela engasga.

**Causa:** vídeo inserido sem recompressão. Um deck com quatro vídeos brutos
passou de 100 MB, sendo 98 MB só de vídeo.

**Solução:** sempre cortar com `kit.clipes.cortar`, que aplica o perfil do kit.
Um clipe de 23 segundos no perfil padrão dá cerca de 600 KB.

---

## 6. Fonte ausente quebra a diagramação

**Sintoma:** o deck abre com texto de tamanho diferente, títulos quebrando em
mais linhas e blocos estourando.

**Causa:** Montserrat não instalada na máquina que apresenta.

**Solução:** instalar a família completa antes. Se não for possível, gerar um
PDF, que congela a diagramação, aceitando perder animação e vídeo.

---

## 7. Ajuste manual não volta para o código

**Sintoma:** alguém edita o `.pptx` na mão, roda o `build.py` de novo e perde a
edição.

**Causa:** o gerador reescreve o arquivo inteiro.

**Solução:** decidir de que lado está a verdade. Se o deck ainda vai evoluir,
mude no código. Se já foi entregue e recebeu ajuste manual, marque isso no
cabeçalho do `build.py` que o script reproduz a estrutura, não o arquivo
final.

---

## 8. Tela preta no lugar do vídeo

**Sintoma:** o vídeo aparece como retângulo preto na primeira abertura.

**Causa:** falha transitória de decodificação do PowerPoint, geralmente ligada
à aceleração de hardware. Não é o arquivo.

**Solução:** fechar e reabrir o PowerPoint resolve. Para confirmar que o
problema não está no clipe, meça o brilho médio ao longo dele: se for
constante, o arquivo está bom.

---

## 9. Texto colidindo depois de uma edição

**Sintoma:** o título encosta na linha de apoio, ou o último marcador invade o
rodapé.

**Causa:** título que passou de uma para duas linhas, ou item de lista que
cresceu.

**Solução:** o validador acusa isso sozinho desde que passou a medir o texto,
comparando o que cada caixa realmente ocupa em vez da altura declarada. Ainda
assim, quebrar o título manualmente com `\n` dá o melhor resultado, porque a
quebra fica onde faz sentido na frase, e não onde a largura acabou.

As composições já empurram para baixo o que colidiria. Em slide montado fora
delas, use `base.abaixo_de(forma, y)` para posicionar o que vem depois de um
título: a função devolve o próprio `y` quando o texto cabe, e só empurra quando
haveria colisão, então nenhum slide já aprovado sai do lugar por causa dela.

---

## 10. Negação no .gitignore não funciona dentro de pasta ignorada

**Sintoma:** você escreve `!pasta/arquivo.pptx` e o arquivo continua fora.

**Causa:** o Git não entra em diretório ignorado, então a negação nunca é
avaliada.

**Solução:** ignorar o conteúdo, não o diretório. Use `pasta/*` e depois
`!pasta/arquivo.pptx`.
