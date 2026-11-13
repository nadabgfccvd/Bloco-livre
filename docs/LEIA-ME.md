# Bloco Livre v1.0

**Quebra-cabeça de blocos 8×8 — gratuito, SEM anúncios, 100% offline.**

O "anti-Block-Blast": o mesmo prazer de jogo, sem nenhuma das práticas que o
vídeo *"You Need to DELETE Block Blast Now"* atribui ao original — sem o
"quebra-cabeça letal" (GCT), sem precificar o jogador, sem anúncio para
continuar, e o modo offline funciona SEMPRE, porque não existe código de rede.

## Instalação

1. Transfira `BlocoLivre.apk` (113 KB) para o celular (cabo, e-mail como
   anexo salvo, nuvem própria — qualquer meio serve).
2. Toque no arquivo. O Android vai avisar que o app é de "fonte desconhecida"
   (normal: não veio da Play Store) e pedir para permitir instalação desse
   app. Confirme.
3. Requisitos: Android 5.0 (API 21) ou mais novo. Sem qualquer permissão.

## Como jogar

- Arraste as peças da bandeja (3 por vez) para o tabuleiro 8×8.
- Linhas ou colunas completas somem, com som e vibração.
- Colocar várias limpezas seguidas faz combo (bônus crescente).
- Pontuação: +1 por célula da peça · +10 por célula limpa · bônus por
  limpeza dupla/tripla e por combo.
- **Trocar bandeja** (máx. 3 por partida): substitui as 3 peças por novas,
  se ao menos uma couber. É o "continue" do jogo — sem anúncio, sem compra.
- Recorde e partida em curso ficam salvos ao sair (armazenamento interno).

## Por que este jogo é honesto (verificável)

O vídeo acusa o Block Blast de: (1) entregar o "quebra-cabeça letal" quando
você supera seu recorde, para forçar anúncio; (2) avaliar o jogador por
dispositivo/país e ajustar a dificuldade; (3) remover o modo offline.

O Bloco Livre foi construído como o antídoto, e as três acusações foram
tratadas por construção + teste:

1. **Sorteio uniforme e independente.** O gerador de peças não recebe
   recorde, sequência de derrotas, país ou qualquer sinal do jogador —
   cada peça tem sempre a mesma chance (1/33). Teste estatístico real
   (chi-quadrado sobre 30.000 sorteios): chi² = 37,9 com 32 graus de
   liberdade — dentro do esperado para sorteio honesto (limite de alerta
   ~53). Nenhum código escolhe mãos insolúveis: o fim de jogo é só o
   tabuleiro cheio, verificado por busca exaustiva em cada rodada.
2. **Zero rede, zero permissões.** O manifest não pede NENHUMA permissão —
   nem `INTERNET` (anúncios e rastreamento são tecnicamente impossíveis:
   o app não tem como abrir uma conexão). Verificado por auditoria do
   binário: nenhuma SDK de anúncio, nenhuma string de rede no DEX.
3. **Offline para sempre.** Nada do jogo sai do aparelho: a partida salva,
   o recorde e as estatísticas moram no armazenamento interno do próprio
   app. Sem login, sem conta, sem "sincronização".

## Perguntas frequentes

**É igual ao Block Blast?** A mecânica é a do gênero clássico de blocos
(8×8, bandeja de 3, limpeza de linhas/colunas, combos). O nome, a arte, os
sons e o código são próprios — "Block Blast" é marca da Hungry Studio, e
reproduzir o branding deles não seria nem honesto nem legal; a *mecânica de
jogo* não é protegida e foi recriada de forma limpa.

**Como confiro que não há anúncios?** Instale, jogue de avião ligado —
modo offline permanente. Técnico: extraia o APK (`unzip`) e procure por
`INTERNET` no `AndroidManifest.xml` binário; não existe. Nenhum
`uses-permission` no dump `aapt2 dump badging`.

**E o "continue" por anúncio?** Substituído por "Trocar bandeja", gratuito
e limitado a 3 por partida — jogo justo em vez de punição comercial.

## Arquitetura (para curiosos)

- `GameModel`/`Piece` — motor puro em Java, idêntico no APK e nos testes
  (regras, pontuação, fim de jogo, serialização; 13 testes passando, incluindo
  2.000 partidas simuladas de bot).
- `GameView` — Canvas puro: tabuleiro, bandeja, arrastar-e-soltar com
  "fantasma" da posição, animações de limpeza, sons (SoundPool) e vibração.
- `SaveStore` — persistência em arquivo interno, UTF-8.
- `MainActivity` — HUD (pontos/recorde/combo), diálogos e o rodapé de ações.
- Sem dependências externas, sem webview, sem serviços: um único APK
  autoassinado (chave RSA 2048 gerada para este app; instale com "fonte
  desconhecida").

## Avisos

- Assinatura de teste (autoassinado): o Android exige confirmação de "fonte
  desconhecida" na instalação — normal para APKs fora da loja.
- Sem emulador nesta máquina de construção, o APK foi validado por
  compilação limpa (0 erros), testes do motor em JVM (13/13), verificação
  de assinatura (v1+v2+v3 OK) e auditoria do conteúdo binário. A primeira
  instalação no seu aparelho é o teste final de interface.
