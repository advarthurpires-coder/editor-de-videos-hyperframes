# 1º Encontro da Melhor Idade — HERO Lagoinha Patrocínio

Jantar realizado em 23/10/2026. Tema da lembrancinha: Salmos 92:14, "Na velhice
ainda darão frutos; serão viçosos e vigorosos".

Material bruto recebido em 24/10/2026, em três lotes.

## Reel "Noite da Melhor Idade" (projeto HyperFrames)

Composição em `index.html` (HTML + GSAP), 1080x1920, 30 fps, 49 s. Trilha instrumental **original** de louvor
(síntese, sem músicas de terceiros: o Instagram não bloqueia nem silencia), Ré maior, 72 bpm. Todos os cortes caem
nos tempos da música (tempo = 0,8333 s; compasso = 3,3333 s).

| s | seção | o que aparece | transições |
|---|---|---|---|
| 0,0 | Abertura | mesa posta (video-21), título "Noite da MELHOR IDADE" | letras sobem, linha dourada |
| 3,3 | Preparo | brasas, churrasqueiro, taças, mesa ("Preparado com carinho…") | luz dourada, dissolve, zoom |
| 10,0 | Chegada | sorrisos e casal à mesa ("…para receber vocês.") | íris, dissolve |
| 13,3 | A Palavra | pregador e ouvintes + Salmos 92:14 palavra por palavra | luz, dissolve, zoom, íris |
| 26,7 | Comunhão (refrão) | jantar, cortes mais rápidos ("Comunhão", "Gratidão") | drop com luz, sobe, lateral |
| 36,7 | Rostos | 4 polaroides caindo no tempo ("Obrigado por cada história") | luz |
| 43,3 | Lembrancinha | card do encontro + versículo | dissolve |
| 46,25 | Final | "Até o próximo encontro", logos Lagoinha e HERO, 23•10•2026 | luz, poeira dourada |

### Pipeline
```bash
python3 -I tools/preparar_midia.py                 # recorta, amplia (464x832 -> 1080x1920) e corrige a cor
python3 -I tools/gerar_trilha.py assets/music/trilha_louvor.wav
python3 -I tools/mixar.py && bash tools/masterizar.sh   # -14 LUFS -> assets/media/mix_master.wav
npm run check
npx --yes hyperframes@0.8.149 render --quality high --fps 30 --output renders/melhor_idade_reel.mp4
```
Para trocar um plano: ajuste `CLIPES`/`FOTOS` em `tools/preparar_midia.py` e o `src` correspondente no `index.html`.

Para usar um louvor conhecido em vez da trilha original: poste o vídeo e escolha a música na biblioteca do
Instagram, baixando o volume do áudio original para zero (músicas com direitos autorais inseridas no próprio
arquivo costumam ser silenciadas ou bloqueadas).

## originais/fotos (21 JPG)

| Arquivo | Conteúdo |
|---|---|
| foto-01.jpg | Mesa longa, vista do fundo do salão, convidados jantando |
| foto-02.jpg | Ponta da mesa, travessas e Fanta em primeiro plano |
| foto-03.jpg | Mesa vista da cabeceira oposta (levemente desfocada) |
| foto-04.jpg | Mesa completa, servindo a carne |
| foto-05.jpg | Mesa completa, outro ângulo do serviço |
| foto-06.jpg | Detalhe dos pratos e do brinde "1º Encontro da Melhor Idade" |
| foto-07.jpg | Retrato: convidado de camiseta azul-marinho |
| foto-08.jpg | Retrato: casal sentado à mesa |
| foto-09.jpg | Fala de abertura, orador de costas para a câmera |
| foto-10.jpg | Pregador de terno falando à mesa, convidados de costas em primeiro plano |
| foto-11.jpg | Pregador de pé, gesto com os punhos fechados |
| foto-12.jpg | Pregador gesticulando, palmeira ao fundo (720x1280) |
| foto-13.jpg | Mesa posta completa, pregador ao fundo (melhor plano geral do ambiente) |
| foto-14.jpg | Lembrancinha: card "1º Encontro da Melhor Idade", Salmos 92:14, 23/10/2026 |
| foto-15.jpg | Pregador com o braço estendido, convidados ouvindo |
| foto-16.jpg | Retrato do casal (mesma cena da foto-08, outro arquivo) |
| foto-17.jpg | Pregador de mãos juntas, casal à mesa em primeiro plano |
| foto-18.jpg | Retrato: casal (camiseta vinho e blusa florida) |
| foto-19.jpg | Retrato: casal (camiseta do Brasil e blusa coral) |
| foto-20.jpg | Detalhe da mesa posta em diagonal, convidados ao fundo (720x1280) |
| foto-21.jpg | Mesa posta completa antes do jantar (1449x2576, a de maior resolução) |

## originais/videos (21 clipes, vertical, ~2min40s no total)

| Arquivo | Duração |
|---|---|
| video-01.mov | 6,5 s |
| video-02.mp4 | 6,3 s |
| video-03.mp4 | 12,4 s |
| video-04.mp4 | 9,3 s |
| video-05.mp4 | 8,6 s |
| video-06.mp4 | 7,5 s |
| video-07.mov | 22,5 s |
| video-08.mov | 3,7 s |
| video-09.mov | 6,9 s |
| video-10.mov | 8,7 s |
| video-11.mov | 7,5 s |
| video-12.mp4 | 4,4 s |
| video-13.mp4 | 13,4 s |
| video-14.mp4 | 9,0 s |
| video-15.mp4 | 10,2 s |
| video-16.mp4 | 1,4 s |
| video-17.mp4 | 4,7 s |
| video-18.mp4 | 4,5 s |
| video-19.mp4 | 6,3 s |
| video-20.mp4 | 4,5 s |
| video-21.mov | 6,2 s (720x1280) |

Quase todos os vídeos chegaram em baixa resolução (464x832; só o video-21 tem 720x1280), provavelmente comprimidos pelo
WhatsApp. Para um Reel em 1080x1920, o ideal é obter os arquivos originais do celular.
