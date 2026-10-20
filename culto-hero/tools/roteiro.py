"""Fonte única dos tempos do reel "Culto Hero" (usada por montar_voz.py, legendas.py, gerar_trilha.py e mixar_audio.py)."""

SR = 48000
TOTAL = 63.5
BEAT = 0.6  # 100 bpm

# início (s) de cada frase da locução no vídeo (f01..f20)
INICIO = [0.50, 4.00, 7.20, 10.90, 15.25, 17.20, 21.95, 24.55, 27.20, 29.80,
          31.70, 35.00, 36.40, 38.95, 43.85, 45.55, 48.05, 49.45, 52.50, 56.75]

# cortes de cena (s) — os mesmos valores aparecem no topo do script de index.html
CENAS = {
    "gancho": 0.0,        # fitas de aviso + placa "!"
    "motivo1": 3.85,      # numeral 1 · carrossel de tipos de homem · peões
    "incomoda": 15.1,     # glitch, trilha corta
    "motivo2": 17.0,      # numeral 2 · casa
    "motivo3": 24.4,      # numeral 3 · giroflex · celular · cadeado · saída
    "virada": 38.6,       # tudo congela e perde a cor · placa NÃO VÁ
    "risco": 45.4,        # a cor volta · medalhão H
    "convite": 48.0,      # DROP · logomarca HERO · data / hora / endereço
    "final": 56.35,       # trilha corta · dupla do flyer · carimbo AVISADO
    "carimbo": 59.25,
}

# blocos de legenda por frase (None = sem legenda: a própria tela mostra a frase em destaque)
BLOCOS = {
    1: ["Três motivos pra você", "não ir ao Culto Hero."],
    2: None,
    3: None,
    4: ["e você vai descobrir", "que não é tão diferente", "deles assim."],
    5: None,
    6: ["Segundo: você vai sair de lá", "com vontade de mudar", "umas coisas em casa."],
    7: None,
    8: None,
    9: ["você pode acabar", "fazendo amigo."],
    10: None,
    11: ["Daqueles que te ligam", "pra saber como você tá."],
    12: None, 13: None,
    14: None, 15: None,
    16: None,
    17: None, 18: None, 19: None, 20: None,
}
DESTAQUE = {"não", "Hero.", "homem", "tipo.", "diferente", "mudar", "casa.", "perigoso:", "amigo.", "ligam", "topa", "risco…"}
