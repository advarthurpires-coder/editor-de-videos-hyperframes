import { wordAt, TOTAL_SEC } from "./util";

// Âncoras: início real das palavras em palavras_tempos_versaoB.json.
export const T = {
  amanha: wordAt("amanhã"),
  seisDias: wordAt("6"),
  cuidado: wordAt("cuidado"),
  cobrar: wordAt("cobrar"),
  mudar: wordAt("mudar"),
  entender: wordAt("entender"),
  oQue: wordAt("que", 1, 9.4),
  quando: wordAt("quando"),

  senado: wordAt("senado"),
  doisTurnos: wordAt("dois"),
  mesmoDia: wordAt("mesmo"),
  n75: wordAt("75"),
  emenda: wordAt("emenda"),
  sancao: wordAt("sanção"),
  congresso: wordAt("congresso"),
  promulga: wordAt("promulga"),
  prazos: wordAt("prazos"),

  doisMeses: wordAt("dois", 1, 24),
  folgas: wordAt("folgas"),
  h44: wordAt("44"),
  h42: wordAt("42"),
  m14: wordAt("14"),
  h40: wordAt("40"),
  salario: wordAt("salário", 1, 34),

  preferencia: wordAt("preferência"),
  domingo: wordAt("domingo"),
  menos40: wordAt("40", 2),
  tambem: wordAt("também"),

  saude: wordAt("saúde"),
  compensar: wordAt("compensar"),
  media: wordAt("média"),
  profissionais: wordAt("profissionais"),
  diploma: wordAt("diploma"),
  mil21: wordAt("21"),
  fora: wordAt("fora"),
  micro: wordAt("micro"),
  lei: wordAt("lei"),
  complementar: wordAt("complementar"),
  hoje: wordAt("hoje"),

  empregado: wordAt("empregado"),
  assine: wordAt("assine"),
  empresario: wordAt("empresário"),
  escalas: wordAt("escalas"),
  horasExtras: wordAt("horas", 1, 69.5),
  banco: wordAt("banco"),
  antesMudar: wordAt("antes", 1, 71),
  advogado: wordAt("advogado"),

  quente: wordAt("quente"),
  volto: wordAt("volto"),
  atualizacoes: wordAt("atualizações"),

  segue: wordAt("segue"),
  comente6x1: wordAt("6x1", 2),
  checklist: wordAt("checklist"),
  finale: 87.0,
  end: TOTAL_SEC,
};

export const SCENES = {
  s1: [0, 5.5],
  s2: [5.5, 11.6],
  s3: [11.6, 24.2],
  s4: [24.2, 35.3],
  s5: [35.3, 43.3],
  s6: [43.3, 61.4],
  s7: [61.4, 74.5],
  s8: [74.5, 83.3],
  s9: [83.3, TOTAL_SEC],
} as const;

export const CHAPTERS = [
  { n: 1, label: "POR QUE AINDA NÃO VALE", from: SCENES.s3[0], to: SCENES.s3[1] },
  { n: 2, label: "O CALENDÁRIO", from: SCENES.s4[0], to: SCENES.s4[1] },
  { n: 3, label: "QUEM TRABALHA", from: SCENES.s5[0], to: SCENES.s5[1] },
  { n: 4, label: "EXCEÇÕES", from: SCENES.s6[0], to: SCENES.s6[1] },
  { n: 5, label: "O ALERTA", from: SCENES.s7[0], to: SCENES.s7[1] },
];
