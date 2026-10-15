import React from "react";
import { Img, staticFile } from "remotion";
import { project } from "./camera";
import { T } from "./timeline";
import {
  Appear,
  Card3D,
  CheckBox,
  GOLD_TEXT,
  IconBuilding,
  IconClock,
  IconPerson,
  Micro,
  Roller,
  SANS,
  SERIF,
  Serif,
  StampMark,
  Tag,
} from "./ui";
import { MARKERS, RAIL_Z } from "./World";
import { C, clamp, easeInCubic, easeInOutCubic, easeOutBack, easeOutCubic, LEAD, lerp, pop, ramp, win } from "./util";

const L = LEAD;

const PenSvg = () => (
  <svg width="230" height="230" viewBox="0 0 230 230" style={{ filter: "drop-shadow(0 12px 16px rgba(3,8,20,0.6))", overflow: "visible" }}>
    <defs>
      <linearGradient id="pg" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stopColor="#F0DCAA" />
        <stop offset="0.5" stopColor="#B8975A" />
        <stop offset="1" stopColor="#7E6233" />
      </linearGradient>
      <linearGradient id="pb" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stopColor="#2A4470" />
        <stop offset="0.5" stopColor="#0D1F3C" />
        <stop offset="1" stopColor="#060F20" />
      </linearGradient>
    </defs>
    <g transform="translate(14 206) rotate(-45)">
      <path d="M0 0 L22 -11 L22 11 Z" fill="url(#pg)" />
      <rect x="22" y="-13" width="26" height="26" rx="3" fill="url(#pg)" />
      <rect x="48" y="-15" width="200" height="30" rx="15" fill="url(#pb)" />
      <rect x="140" y="-16" width="14" height="32" fill="url(#pg)" />
      <rect x="150" y="-22" width="90" height="7" rx="3" fill="url(#pg)" />
    </g>
  </svg>
);

const LupaSvg = () => (
  <svg width="260" height="260" viewBox="0 0 260 260" style={{ filter: "drop-shadow(0 22px 22px rgba(3,8,20,0.5))", overflow: "visible", transform: "translate(-50%,-50%)" }}>
    <defs>
      <linearGradient id="lg" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stopColor="#F0DCAA" />
        <stop offset="0.5" stopColor="#B8975A" />
        <stop offset="1" stopColor="#7E6233" />
      </linearGradient>
      <radialGradient id="lglass" cx="0.35" cy="0.3" r="0.8">
        <stop offset="0" stopColor="rgba(255,255,255,0.55)" />
        <stop offset="0.5" stopColor="rgba(220,235,255,0.12)" />
        <stop offset="1" stopColor="rgba(220,235,255,0.05)" />
      </radialGradient>
    </defs>
    <line x1="170" y1="170" x2="240" y2="240" stroke="#0D1F3C" strokeWidth="26" strokeLinecap="round" />
    <line x1="160" y1="160" x2="182" y2="182" stroke="url(#lg)" strokeWidth="30" strokeLinecap="round" />
    <circle cx="100" cy="100" r="78" fill="url(#lglass)" stroke="url(#lg)" strokeWidth="16" />
    <path d="M52 78 A55 55 0 0 1 92 46" stroke="rgba(255,255,255,0.8)" strokeWidth="7" fill="none" strokeLinecap="round" />
  </svg>
);

// ======================= CENA 1 · GANCHO =======================
const Scene1 = ({ t }: { t: number }) => (
  <>
    <Appear t={t} a={T.amanha - L} b={T.seisDias - 0.12} y={400} dy={60} blur={14}>
      <Serif size={190}>AMANHÃ</Serif>
    </Appear>
    <Appear t={t} a={T.amanha + 0.32} b={T.seisDias - 0.12} y={540} dy={40}>
      <Serif size={120} gold>
        NADA MUDA
      </Serif>
    </Appear>
    <Appear t={t} a={T.seisDias - L} b={T.cuidado - 0.08} y={480} dy={0} inDur={0.25} scaleFrom={1.35} blur={18}>
      <div style={{ display: "flex", alignItems: "center", gap: 26 }}>
        <Serif size={330} gold>
          6
        </Serif>
        <Serif size={170}>DIAS</Serif>
      </div>
    </Appear>
  </>
);

// ======================= CENA 2 · ALERTA =======================
const Scene2 = ({ t }: { t: number }) => {
  const cardsOut = ramp(t, T.entender - L - 0.05, T.entender + 0.35, easeInCubic);
  const card = (label: string, icon: React.ReactNode, start: number, side: -1 | 1) => {
    if (t < start || cardsOut >= 1) return null;
    const k = pop(t, start, 0.55);
    const sway = Math.sin((t - start) * 2.4 + side) * 5;
    return (
      <div
        style={{
          position: "absolute",
          left: 540 + side * 215,
          top: 700,
          transform: `translate(-50%,-50%) translateY(${(1 - k) * 120 - cardsOut * 60}px) scale(${(0.6 + 0.4 * k) * (1 - cardsOut * 0.35)})`,
          opacity: clamp(k * 1.5) * (1 - cardsOut),
        }}
      >
        <Card3D w={380} h={380} ry={-side * 16 + sway} rx={6} z={-cardsOut * 300}>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%", gap: 26 }}>
            {icon}
            <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 48, letterSpacing: "0.16em", color: C.navy }}>{label}</div>
          </div>
        </Card3D>
      </div>
    );
  };
  return (
    <>
      <Appear t={t} a={T.cuidado - L} b={T.cobrar - 0.05} y={950} dy={30} inDur={0.3}>
        <Serif size={150}>CUIDADO</Serif>
      </Appear>
      <Appear t={t} a={T.cobrar - L} b={T.entender + 0.2} y={360} dy={30}>
        <Micro size={34}>ANTES DE</Micro>
      </Appear>
      {card("COBRAR", <IconPerson size={130} />, T.cobrar - L, -1)}
      {card("MUDAR", <IconBuilding size={130} />, T.mudar - L, 1)}
      <Appear t={t} a={T.entender - L} b={11.75} y={380} dy={40} blur={12}>
        <Serif size={150}>ENTENDA</Serif>
      </Appear>
      <Appear t={t} a={T.oQue - L} b={11.75} y={560} dy={30}>
        <Serif size={112}>O QUE VALE</Serif>
      </Appear>
      <Appear t={t} a={T.quando - L} b={11.75} y={690} dy={30}>
        <Serif size={112} gold>
          QUANDO VALE
        </Serif>
      </Appear>
    </>
  );
};

// ======================= CENA 3 · POR QUE AINDA NÃO VALE =======================
const SenadoCard = ({ t }: { t: number }) => {
  const a = T.senado - L;
  const b = T.n75 + 0.75;
  if (t < a || t > b) return null;
  const k = ramp(t, a, a + 0.8, easeOutCubic);
  const out = ramp(t, b - 0.4, b, easeInCubic);
  const rx = lerp(38, 7, k) + Math.sin(t * 0.9) * 1.5;
  const ry = lerp(-24, -9, k) + Math.sin(t * 0.7) * 2;
  const rz = lerp(-8, -2, k);
  // marca-texto sobre "75 votos favoráveis e apenas um contrário"
  const hl1 = ramp(t, T.n75 - L, T.n75 + 0.3, easeInOutCubic);
  const hl2 = ramp(t, T.n75 + 0.25, T.n75 + 0.55, easeInOutCubic);
  const S = 860 / 1270; // escala do recorte do parágrafo
  const up = ramp(t, T.doisTurnos - L - 0.1, T.doisTurnos + 0.3, easeInOutCubic);
  return (
    <div
      style={{
        position: "absolute",
        left: 540,
        top: lerp(640, 560, up),
        transform: `translate(-50%,-50%) translateY(${(1 - k) * 200}px) scale(${lerp(0.7, 1, k) * (1 - out * 0.3)})`,
        opacity: clamp(k * 1.4) * (1 - out),
      }}
    >
      <Card3D w={920} rx={rx} ry={ry} rz={rz} style={{ borderColor: "rgba(184,151,90,0.9)", background: "#FBFAF7" }}>
        <div style={{ background: "#337AB5", height: 118, display: "flex", alignItems: "center", paddingLeft: 26 }}>
          <Img src={staticFile("senado_cabecalho.png")} style={{ height: 118, width: "auto", objectFit: "cover", objectPosition: "left" }} />
        </div>
        <div style={{ padding: "26px 30px 8px" }}>
          <Img src={staticFile("senado_titulo.png")} style={{ width: 860 * (1120 / 1270), display: "block" }} />
          <div style={{ height: 3, background: C.gold, opacity: 0.6, margin: "16px 0 18px" }} />
          <div style={{ position: "relative", width: 860 }}>
            {/* destaques ficam sob o texto (multiply) */}
            <div style={{ position: "absolute", left: 745 * S, top: 228 * S, height: 62 * S, width: 485 * S * hl1, background: "rgba(214,178,105,0.55)", borderRadius: 6 }} />
            <div style={{ position: "absolute", left: 8 * S, top: 290 * S, height: 62 * S, width: 470 * S * hl2, background: "rgba(214,178,105,0.55)", borderRadius: 6 }} />
            <Img src={staticFile("senado_paragrafo.png")} style={{ width: 860, display: "block", mixBlendMode: "multiply", position: "relative" }} />
          </div>
        </div>
        <div style={{ fontFamily: SANS, fontSize: 22, fontWeight: 500, letterSpacing: "0.08em", color: "#4A5670", padding: "8px 30px 22px" }}>
          Fonte: Agência Senado · 14/10/2026
        </div>
      </Card3D>
    </div>
  );
};

const Scene3 = ({ t }: { t: number }) => {
  const placar = T.n75 + 0.65;
  const count = ramp(t, placar, placar + 0.8, easeOutCubic);
  return (
    <>
      <SenadoCard t={t} />
      {/* dois turnos no mesmo dia */}
      {[0, 1].map((n) => {
        const a = T.doisTurnos - L + n * 0.22;
        if (t < a || t > T.n75 - 0.05) return null;
        const k = pop(t, a, 0.4);
        const out = ramp(t, T.n75 - 0.35, T.n75 - 0.05, easeInCubic);
        return (
          <div
            key={n}
            style={{
              position: "absolute",
              left: 540 + (n ? 190 : -190),
              top: 930,
              transform: `translate(-50%,-50%) scale(${(1.5 - 0.5 * k) * (1 - out * 0.4)}) rotate(${(1 - k) * (n ? 8 : -8)}deg)`,
              opacity: clamp(k * 2) * (1 - out),
            }}
          >
            <Tag filled size={40}>
              {n ? "2º TURNO" : "1º TURNO"}
            </Tag>
          </div>
        );
      })}
      <Appear t={t} a={T.mesmoDia - L} b={T.n75 - 0.05} y={1040} dy={20} outDur={0.25}>
        <Micro size={34} color={C.gold}>
          — MESMO DIA —
        </Micro>
      </Appear>
      {/* placar gigante */}
      <Appear t={t} a={placar - 0.05} b={T.emenda - 0.02} y={600} dy={0} scaleFrom={1.25} inDur={0.25} blur={14}>
        <div style={{ display: "flex", alignItems: "center", gap: 30 }}>
          <Roller value={count * 75} digits={2} size={300} gold />
          <Serif size={160} style={{ opacity: 0.85 }}>
            ×
          </Serif>
          <Roller value={count * 1} digits={1} size={300} />
        </div>
        <Micro size={30} style={{ marginTop: 10 }}>
          VOTOS NO SENADO · 2 TURNOS
        </Micro>
      </Appear>
      {/* emenda constitucional */}
      <Appear t={t} a={T.emenda - L} b={T.congresso - 0.05} y={lerp(560, 400, ramp(t, T.sancao - L - 0.1, T.sancao + 0.2))} dy={40}>
        <div
          style={{
            padding: "22px 46px",
            border: `3px solid ${C.gold}`,
            borderRadius: 18,
            background: "rgba(12,27,51,0.7)",
            boxShadow: "0 20px 60px rgba(3,8,20,0.6)",
          }}
        >
          <Micro size={28} color={C.gold} style={{ marginBottom: 8 }}>
            PEC =
          </Micro>
          <Serif size={64}>EMENDA CONSTITUCIONAL</Serif>
        </div>
      </Appear>
      {/* sanção riscada */}
      <Appear t={t} a={T.sancao - L} b={T.congresso - 0.05} y={700} dy={30}>
        <Micro size={32} color={C.gold} style={{ marginBottom: 14 }}>
          NÃO TEM
        </Micro>
        <div style={{ position: "relative", display: "inline-block" }}>
          <Serif size={150}>SANÇÃO</Serif>
          <div
            style={{
              position: "absolute",
              left: -20,
              top: "52%",
              height: 12,
              borderRadius: 6,
              width: `calc(${ramp(t, T.sancao + 0.35, T.sancao + 0.95, easeInOutCubic) * 100}% + 40px)`,
              background: "linear-gradient(90deg,#E2C88F,#B8975A)",
              boxShadow: "0 0 24px rgba(184,151,90,0.7)",
              transform: "rotate(-3deg)",
            }}
          />
          {(() => {
            const k = ramp(t, T.sancao + 0.35, T.sancao + 0.95, easeInOutCubic);
            const op = ramp(t, T.sancao - 0.05, T.sancao + 0.3) * (1 - ramp(t, T.sancao + 1.1, T.sancao + 1.4));
            return (
              <div style={{ position: "absolute", left: `calc(${k * 100}% + ${-20 + 40 * k}px)`, top: "54%", transform: `translate(-14px, -206px) rotate(${Math.sin(t * 18) * 2 * (k > 0 && k < 1 ? 1 : 0)}deg)`, transformOrigin: "14px 206px", opacity: op }}>
                <PenSvg />
              </div>
            );
          })()}
        </div>
        <Micro size={28} style={{ marginTop: 18, opacity: 0.85 }}>
          DO PRESIDENTE
        </Micro>
      </Appear>
      {/* promulgação */}
      <Appear t={t} a={T.congresso - L} b={T.prazos - 0.12} y={480} dy={30}>
        <Micro size={34}>O CONGRESSO PROMULGA</Micro>
      </Appear>
      {t >= T.promulga - 0.03 && t < T.prazos - 0.12 && (
        <div style={{ position: "absolute", left: 540, top: 700, transform: "translate(-50%,-50%)", opacity: 1 - ramp(t, T.prazos - 0.4, T.prazos - 0.12) }}>
          <StampMark t={t} hit={T.promulga - 0.03} size={80}>
            PROMULGAÇÃO
          </StampMark>
        </div>
      )}
      <Appear t={t} a={T.promulga + 0.45} b={T.prazos - 0.12} y={900} dy={20}>
        <div style={{ transform: `scale(${1 + Math.sin(t * 7) * 0.025})` }}>
          <Tag size={30}>
            <span style={{ display: "inline-block", width: 14, height: 14, borderRadius: 7, background: C.gold, marginRight: 16, opacity: 0.5 + 0.5 * Math.sin(t * 7), verticalAlign: "middle" }} />
            PREVISTA PARA OS PRÓXIMOS DIAS
          </Tag>
        </div>
      </Appear>
      {/* prazos */}
      <Appear t={t} a={T.prazos - L} b={24.2} y={1010} dy={30}>
        <Micro size={32} color={C.gold} style={{ marginBottom: 10 }}>
          SÓ ENTÃO
        </Micro>
        <Serif size={86}>OS PRAZOS CORREM</Serif>
      </Appear>
    </>
  );
};

// ======================= CENA 4 · O CALENDÁRIO =======================
const MarkerLabel = ({ t, idx, a, b }: { t: number; idx: number; a: number; b: number }) => {
  const vis = win(t, a, b, 0.3, 0.3);
  if (vis <= 0) return null;
  const m = MARKERS[idx];
  const p = project(t, [m.x, 1.22, RAIL_Z]);
  if (!p.visible || p.x < 150 || p.x > 930 || p.y < 420) return null;
  const k = pop(t, a, 0.5);
  return (
    <div style={{ position: "absolute", left: clamp(p.x, 250, 830), top: p.y - 40, transform: `translate(-50%,-100%) scale(${0.7 + 0.3 * k})`, opacity: vis, textAlign: "center" }}>
      <div style={{ padding: "16px 30px", borderRadius: 16, background: "rgba(12,27,51,0.78)", border: `2.5px solid ${C.gold}`, boxShadow: "0 18px 50px rgba(3,8,20,0.6)" }}>
        <Serif size={74} gold>
          {m.label}
        </Serif>
        <Micro size={24} style={{ marginTop: 6 }}>
          {m.sub}
        </Micro>
      </div>
      <div style={{ width: 3, height: 34, background: C.gold, margin: "0 auto" }} />
    </div>
  );
};

const Scene4 = ({ t }: { t: number }) => {
  // contador de horas 44 → 42 → 40
  const hv = lerp(lerp(44, 42, ramp(t, T.h42 - L, T.h42 + 0.45, easeInOutCubic)), 40, 0) - 2 * ramp(t, T.h40 - L, T.h40 + 0.45, easeInOutCubic);
  const cUp = ramp(t, T.m14 - L - 0.3, T.m14 + 0.3, easeInOutCubic);
  const flash = Math.max(0, 1 - Math.abs(t - (T.h40 + 0.25)) / 0.4);
  return (
    <>
      <MarkerLabel t={t} idx={0} a={T.doisMeses - L} b={25.95} />
      <MarkerLabel t={t} idx={1} a={T.doisMeses + 0.55} b={26.3} />
      <MarkerLabel t={t} idx={2} a={T.m14 - L} b={34.7} />
      <Appear t={t} a={T.doisMeses - L} b={25.95} y={330} dy={20}>
        <Micro size={32}>DEPOIS DA PROMULGAÇÃO</Micro>
      </Appear>
      {/* 5x2 */}
      <Appear t={t} a={T.folgas - L + 0.25} b={T.m14 - 0.1} y={lerp(420, 330, ramp(t, T.h44 - L - 0.2, T.h44 + 0.2))} dy={0} scaleFrom={1.3} blur={16}>
        <div style={{ transform: `scale(${lerp(1, 0.62, ramp(t, T.h44 - L - 0.2, T.h44 + 0.2, easeInOutCubic))})` }}>
          <Serif size={280} gold>
            5x2
          </Serif>
          <Micro size={34} style={{ marginTop: 6 }}>
            2 FOLGAS POR SEMANA
          </Micro>
        </div>
      </Appear>
      {/* contador */}
      <Appear t={t} a={T.h44 - L} b={T.salario - 0.2} y={lerp(640, 420, cUp)} dy={30} scaleFrom={1.15}>
        <Micro size={30} color={C.gold} style={{ marginBottom: 4 }}>
          JORNADA SEMANAL
        </Micro>
        <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "center", filter: `drop-shadow(0 0 ${flash * 50}px rgba(232,208,154,${flash}))` }}>
          <Roller value={hv} digits={2} size={250} gold={t > T.h40 - L} />
          <Serif size={150} style={{ marginBottom: 30, marginLeft: 6 }}>
            h
          </Serif>
        </div>
      </Appear>
      <Appear t={t} a={T.h40 - L} b={T.salario - 0.2} y={720} dy={20}>
        <Micro size={28}>EM ATÉ 14 MESES</Micro>
      </Appear>
      {/* salário */}
      <Appear t={t} a={T.salario - L + 0.15} b={36.3} y={1040} dy={30}>
        <Micro size={30} color={C.gold} style={{ marginBottom: 8 }}>
          SEM REDUÇÃO DE
        </Micro>
        <Serif size={120}>SALÁRIO</Serif>
      </Appear>
    </>
  );
};

// ======================= CENA 5 · QUEM TRABALHA =======================
const Scene5 = ({ t }: { t: number }) => (
  <>
    <Appear t={t} a={36.25} b={T.preferencia - 0.1} y={560} dy={30} scaleFrom={1.15}>
      <Serif size={130}>AS 2</Serif>
      <Serif size={130} gold>
        FOLGAS
      </Serif>
    </Appear>
    <Appear t={t} a={T.preferencia - L} b={T.menos40 - 0.1} y={400} dy={30}>
      <Tag size={34}>PREFERENCIALMENTE</Tag>
    </Appear>
    <Appear t={t} a={T.domingo - L} b={T.menos40 - 0.1} y={990} dy={30}>
      <div style={{ display: "flex", gap: 26, alignItems: "baseline" }}>
        <Serif size={96}>NO</Serif>
        <Serif size={120} gold>
          DOMINGO
        </Serif>
      </div>
    </Appear>
    <Appear t={t} a={T.menos40 - L} b={T.tambem - 0.05} y={360} dy={30}>
      <Micro size={32}>QUEM JÁ TRABALHA</Micro>
    </Appear>
    <Appear t={t} a={T.menos40 + 0.5} b={T.tambem - 0.05} y={1000} dy={30}>
      <Micro size={32} style={{ marginBottom: 10 }}>
        40 HORAS OU MENOS
      </Micro>
      <Serif size={92} gold>
        NÃO PERDE NADA
      </Serif>
    </Appear>
    <Appear t={t} a={T.tambem - L} b={43.45} y={960} dy={30}>
      <Serif size={104}>TAMBÉM GANHA</Serif>
      <Serif size={104} gold style={{ marginTop: 8 }}>
        AS 2 FOLGAS
      </Serif>
    </Appear>
  </>
);

// ======================= CENA 6 · EXCEÇÕES (tambor) =======================
const MonthGrid = ({ t }: { t: number }) => {
  // folgas compensadas: semanas irregulares que fecham média de 2 por semana
  const rest = new Set([6, 10, 11, 13, 20, 26, 27, 30]);
  const a = T.compensar + 1.1;
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 54px)", gap: 8, justifyContent: "center" }}>
      {Array.from({ length: 28 }).map((_, n) => {
        const appear = ramp(t, a + n * 0.02, a + n * 0.02 + 0.2);
        const isRest = rest.has(n) || n === 27;
        const order = [...rest].sort((x, y) => x - y).indexOf(n);
        const lit = isRest ? ramp(t, a + 0.7 + Math.max(0, order) * 0.16, a + 0.9 + Math.max(0, order) * 0.16) : 0;
        return (
          <div
            key={n}
            style={{
              height: 40,
              borderRadius: 8,
              opacity: appear,
              transform: `scale(${0.6 + 0.4 * appear})`,
              border: `2px solid rgba(13,31,60,${0.18 + lit * 0.4})`,
              background: lit > 0 ? `rgba(184,151,90,${lit})` : "rgba(13,31,60,0.05)",
              boxShadow: lit > 0.5 ? `0 0 ${16 * lit}px rgba(184,151,90,0.6)` : undefined,
            }}
          />
        );
      })}
    </div>
  );
};

const Drum = ({ t }: { t: number }) => {
  const a = T.saude - L;
  const b = 61.55;
  if (t < a - 0.1 || t > b) return null;
  const inK = ramp(t, a - 0.1, a + 0.5, easeOutCubic);
  const out = ramp(t, b - 0.35, b, easeInCubic);
  const dimK = ramp(t, T.hoje - 0.45, T.hoje - 0.1, easeInOutCubic);
  const rot =
    -120 * ramp(t, T.profissionais - L - 0.2, T.profissionais + 0.45, (x) => easeOutBack(x, 1.1)) -
    120 * ramp(t, T.micro - L - 0.2, T.micro + 0.45, (x) => easeOutBack(x, 1.1));
  const R = 520;
  const face = (k: number, content: React.ReactNode) => (
    <div
      style={{
        position: "absolute",
        left: -440,
        top: -290,
        width: 880,
        height: 580,
        transform: `rotateY(${k * 120}deg) translateZ(${R}px)`,
        backfaceVisibility: "hidden",
        background: "radial-gradient(120% 90% at 20% 10%, #FFFFFF 0%, #F7F5F0 45%, #E9E3D6 100%)",
        borderRadius: 28,
        border: `3px solid ${C.gold}`,
        boxShadow: "0 40px 80px rgba(3,8,20,0.6), inset 0 0 0 10px rgba(184,151,90,0.12)",
        color: C.navy,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: "34px 40px",
        boxSizing: "border-box",
        gap: 18,
      }}
    >
      {content}
    </div>
  );
  const chip = (txt: string, at: number) => {
    const k = pop(t, at - L, 0.4);
    return (
      <div style={{ opacity: clamp(k * 2), transform: `translateY(${(1 - k) * 20}px) scale(${0.8 + 0.2 * k})`, padding: "10px 20px", borderRadius: 12, background: C.navy, color: C.gold, fontFamily: SANS, fontWeight: 600, fontSize: 30, letterSpacing: "0.1em" }}>
        {txt}
      </div>
    );
  };
  const reveal = (at: number, node: React.ReactNode) => {
    const k = ramp(t, at - L, at - L + 0.4, easeOutCubic);
    return <div style={{ opacity: k, transform: `translateY(${(1 - k) * 24}px)`, textAlign: "center" }}>{node}</div>;
  };
  const dots = ".".repeat(1 + (Math.floor(t * 3) % 3));
  return (
    <div style={{ position: "absolute", left: 540, top: 890, perspective: 1900, opacity: inK * (1 - out) * (1 - 0.92 * dimK), transform: `scale(${(0.85 + 0.15 * inK) * (1 - out * 0.2) * (1 - 0.12 * dimK)})` }}>
      <div style={{ position: "relative", transformStyle: "preserve-3d", transform: `translateZ(${-R}px) rotateX(${-4 + Math.sin(t * 0.8) * 1.5}deg) rotateY(${rot + Math.sin(t * 0.6) * 3}deg)` }}>
        {face(
          0,
          <>
            <div style={{ display: "flex", gap: 12 }}>
              {chip("SAÚDE", T.saude)}
              {chip("SEGURANÇA", 44.14)}
              {chip("TRANSPORTE", 44.76)}
            </div>
            {reveal(
              T.compensar,
              <div style={{ fontFamily: SERIF, fontWeight: 700, fontSize: 54, lineHeight: 1 }}>
                COMPENSAÇÃO <span style={GOLD_TEXT}>POR ACORDO</span>
              </div>,
            )}
            <MonthGrid t={t} />
            {reveal(
              T.media,
              <div style={{ padding: "10px 26px", borderRadius: 999, background: "linear-gradient(180deg,#DCC08A,#B8975A)", fontFamily: SANS, fontWeight: 700, fontSize: 28, letterSpacing: "0.08em", color: C.navy }}>
                MÉDIA: 2 FOLGAS POR SEMANA
              </div>,
            )}
          </>,
        )}
        {face(
          1,
          <>
            <Micro size={30} color={C.navy} style={{ textShadow: "none", marginTop: 10 }}>
              PROFISSIONAIS COM DIPLOMA
            </Micro>
            {reveal(
              T.diploma + 0.4,
              <div style={{ fontFamily: SERIF, fontWeight: 700, fontSize: 70, lineHeight: 1 }}>NÍVEL SUPERIOR</div>,
            )}
            {reveal(
              T.mil21,
              <div style={{ fontFamily: SERIF, fontWeight: 700, fontSize: 56, lineHeight: 1.05 }}>
                + SALÁRIO ACIMA DE
                <br />
                <span style={{ ...GOLD_TEXT, fontSize: 92 }}>R$ 21 MIL</span>
              </div>,
            )}
            {reveal(
              T.fora,
              <div style={{ display: "flex", alignItems: "center", gap: 18, marginTop: 6, padding: "12px 26px", borderRadius: 16, background: C.navy }}>
                <IconClock size={60} crossed />
                <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 32, letterSpacing: "0.08em", color: C.offWhite }}>FORA DO CONTROLE DE JORNADA</div>
              </div>,
            )}
          </>,
        )}
        {face(
          2,
          <>
            <div style={{ fontFamily: SERIF, fontWeight: 700, fontSize: 70, lineHeight: 1, textAlign: "center", marginTop: 6 }}>
              MICRO E PEQUENAS
              <br />
              EMPRESAS<span style={GOLD_TEXT}>?</span>
            </div>
            {reveal(
              T.lei,
              <div style={{ width: 520, padding: "20px 28px", background: "#FFFFFF", borderRadius: 12, border: "2px solid rgba(13,31,60,0.2)", boxShadow: "0 16px 30px rgba(13,31,60,0.18)", transform: "rotate(-1.5deg)" }}>
                <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 32, letterSpacing: "0.12em", ...GOLD_TEXT }}>LEI COMPLEMENTAR</div>
                <div style={{ height: 3, background: C.gold, margin: "10px 0 14px", opacity: 0.6 }} />
                {[0.9, 0.75, 0.82].map((w, n) => (
                  <div key={n} style={{ height: 12, width: `${w * 100}%`, background: "rgba(13,31,60,0.14)", borderRadius: 6, marginBottom: 10 }} />
                ))}
                <div style={{ fontFamily: SERIF, fontWeight: 700, fontSize: 60, lineHeight: 0.6, color: C.gold, textAlign: "left", height: 30 }}>{dots}</div>
              </div>,
            )}
            {reveal(T.lei + 0.9, <Micro size={26} color={C.navy} style={{ textShadow: "none" }}>VAI DEFINIR A TRANSIÇÃO</Micro>)}
          </>,
        )}
      </div>
    </div>
  );
};

const Scene6 = ({ t }: { t: number }) => (
  <>
    <Drum t={t} />
    {t >= T.hoje - 0.03 && t < 62.25 && (
      <div style={{ position: "absolute", left: 540, top: 760, transform: "translate(-50%,-50%)", opacity: 1 - ramp(t, 61.95, 62.25) }}>
        <StampMark t={t} hit={T.hoje - 0.03} size={66} rot={-7}>
          VALE A REGRA DE HOJE
        </StampMark>
      </div>
    )}
  </>
);

// ======================= CENA 7 · O ALERTA =======================
const Contract = ({ t }: { t: number }) => (
  <Card3D w={720} h={500} rx={30} ry={8} rz={-3} style={{ background: "#FBFAF7", overflow: "visible" }}>
    {t > T.assine - L && (
      <div
        style={{
          position: "absolute",
          left: 170 + 400 * ramp(t, T.assine, T.assine + 2.3, easeInOutCubic) + Math.sin(t * 3) * 8,
          top: 300,
          transform: `translateZ(90px) rotateX(-30deg) scale(${pop(t, T.assine - L, 0.45)})`,
          opacity: 1 - ramp(t, T.empresario - 0.6, T.empresario - 0.3),
          zIndex: 5,
        }}
      >
        <LupaSvg />
      </div>
    )}
    <div style={{ padding: "34px 44px" }}>
      <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 30, letterSpacing: "0.16em", color: C.navy }}>ADITIVO CONTRATUAL</div>
      <div style={{ fontFamily: SANS, fontWeight: 500, fontSize: 22, letterSpacing: "0.12em", color: C.gold, marginTop: 6 }}>ALTERAÇÃO DE ESCALA</div>
      <div style={{ height: 3, background: C.gold, margin: "16px 0 22px", opacity: 0.6 }} />
      {[0.95, 0.88, 0.92, 0.7, 0.9, 0.6].map((w, n) => (
        <div key={n} style={{ height: 12, width: `${w * 100}%`, background: "rgba(13,31,60,0.13)", borderRadius: 6, marginBottom: 14 }} />
      ))}
      <div style={{ marginTop: 40, display: "flex", alignItems: "flex-end", gap: 16 }}>
        <div style={{ fontFamily: SANS, fontSize: 22, letterSpacing: "0.1em", color: "#4A5670" }}>ASSINATURA</div>
        <div style={{ flex: 1, height: 3, background: C.navy, opacity: 0.6, position: "relative" }}>
          <div style={{ position: "absolute", left: 0, top: -6, height: 14, width: `${ramp(t, T.assine, T.assine + 2.1) * 100}%`, background: "rgba(184,151,90,0.45)", borderRadius: 7 }} />
        </div>
      </div>
    </div>
  </Card3D>
);

const Clipboard = ({ t }: { t: number }) => {
  const items = [
    { txt: "ESCALAS", at: T.escalas },
    { txt: "HORAS EXTRAS", at: T.horasExtras },
    { txt: "BANCO DE HORAS", at: T.banco },
  ];
  return (
    <Card3D w={640} h={560} rx={8} ry={-14} rz={2} style={{ background: "#FBFAF7" }}>
      <div style={{ position: "absolute", left: "50%", top: -8, width: 200, height: 52, transform: "translateX(-50%)", background: "linear-gradient(180deg,#DCC08A,#9A7A43)", borderRadius: "0 0 16px 16px" }} />
      <div style={{ padding: "74px 54px 40px" }}>
        <div style={{ fontFamily: SERIF, fontWeight: 700, fontSize: 64, color: C.navy }}>MAPEIE</div>
        <div style={{ height: 3, background: C.gold, margin: "12px 0 30px", opacity: 0.6 }} />
        {items.map((it) => {
          const k = ramp(t, it.at - L, it.at + 0.35, easeOutCubic);
          return (
            <div key={it.txt} style={{ display: "flex", alignItems: "center", gap: 26, marginBottom: 30 }}>
              <CheckBox k={k} size={62} />
              <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 40, letterSpacing: "0.08em", color: k > 0.5 ? C.navy : "rgba(13,31,60,0.45)" }}>{it.txt}</div>
            </div>
          );
        })}
      </div>
    </Card3D>
  );
};

const Scene7 = ({ t }: { t: number }) => {
  const join = ramp(t, T.antesMudar - L - 0.3, T.antesMudar + 0.5, easeInOutCubic);
  const leftIn = ramp(t, T.empregado - L - 0.3, T.empregado + 0.3, easeOutCubic);
  const leftAway = ramp(t, T.empresario - L - 0.5, T.empresario, easeInCubic) * (1 - join);
  const rightIn = ramp(t, T.empresario - L - 0.3, T.empresario + 0.3, easeOutCubic);
  const end = ramp(t, 74.3, 74.6, easeInCubic);
  if (t < T.empregado - L - 0.3 || t > 74.6) return null;
  const lx = lerp(540, 300, join) - leftAway * 900 - (1 - leftIn) * 400;
  const rx = lerp(540, 790, join) + (1 - rightIn) * 900;
  const sc = lerp(1, 0.52, join);
  const cy = lerp(780, 640, join);
  return (
    <div style={{ opacity: 1 - end }}>
      <Appear t={t} a={T.empregado - L} b={T.empresario - 0.3} y={330} dy={20}>
        <Tag size={30}>SE VOCÊ É EMPREGADO</Tag>
      </Appear>
      <Appear t={t} a={T.assine - L} b={T.empresario - 0.3} y={460} dy={30}>
        <Serif size={96}>NÃO ASSINE</Serif>
        <Serif size={96} gold style={{ marginTop: 4 }}>
          SEM ENTENDER
        </Serif>
      </Appear>
      <div style={{ position: "absolute", left: lx, top: cy + 70 * (1 - join), transform: `translate(-50%,-50%) scale(${sc})`, opacity: leftIn * (1 - leftAway) }}>
        <Contract t={t} />
      </div>
      <Appear t={t} a={T.empresario - L} b={T.antesMudar - 0.3} y={330} dy={20}>
        <Tag size={30}>SE VOCÊ É EMPRESÁRIO</Tag>
      </Appear>
      <div style={{ position: "absolute", left: rx, top: cy, transform: `translate(-50%,-50%) scale(${sc})`, opacity: rightIn }}>
        <Clipboard t={t} />
      </div>
      <Appear t={t} a={T.antesMudar - L + 0.2} b={74.6} y={380} dy={20}>
        <Micro size={32}>ANTES DE MUDAR A JORNADA</Micro>
      </Appear>
      <Appear t={t} a={T.advogado - L - 0.5} b={74.6} y={980} dy={30} outDur={0.2}>
        <Serif size={100}>CONVERSE COM</Serif>
        <Serif size={100} gold style={{ marginTop: 6 }}>
          SEU ADVOGADO
        </Serif>
      </Appear>
    </div>
  );
};

// ======================= CENA 8 · TEMA QUENTE =======================
const PageCalendar = ({ t }: { t: number }) => {
  const flip = ramp(t, T.volto + 0.25, T.volto + 0.9, easeInOutCubic);
  const page = (m: string, extra: React.CSSProperties) => (
    <div
      style={{
        position: "absolute",
        inset: 0,
        background: "radial-gradient(120% 90% at 20% 10%, #FFFFFF 0%, #F7F5F0 50%, #E9E3D6 100%)",
        borderRadius: 24,
        border: `3px solid ${C.gold}`,
        overflow: "hidden",
        backfaceVisibility: "hidden",
        ...extra,
      }}
    >
      <div style={{ height: 90, background: C.navy, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <Micro size={30} color={C.gold}>
          2026
        </Micro>
      </div>
      <div style={{ fontFamily: SERIF, fontWeight: 700, fontSize: 190, color: C.navy, textAlign: "center", lineHeight: "250px" }}>{m}</div>
    </div>
  );
  return (
    <div style={{ perspective: 1400 }}>
      <div style={{ width: 400, height: 360, position: "relative", transformStyle: "preserve-3d", transform: `rotateX(12deg) rotateY(${-14 + Math.sin(t) * 4}deg)`, boxShadow: "0 40px 80px rgba(3,8,20,0.6)", borderRadius: 24 }}>
        {page("NOV", {})}
        {page("OUT", { transformOrigin: "50% 0%", transform: `rotateX(${flip * 175}deg)`, zIndex: 2 })}
        {[0.2, 0.4, 0.6, 0.8].map((x) => (
          <div key={x} style={{ position: "absolute", left: `${x * 100}%`, top: -14, width: 14, height: 34, marginLeft: -7, borderRadius: 7, background: "linear-gradient(180deg,#E2C88F,#8E703C)", transform: "translateZ(4px)" }} />
        ))}
      </div>
    </div>
  );
};

const Scene8 = ({ t }: { t: number }) => {
  const streak = ramp(t, T.quente - 0.25, T.quente + 0.8, (x) => x);
  const steps = ["PROMULGAÇÃO", "+2 MESES", "+14 MESES"];
  return (
    <>
      {streak > 0 && streak < 1 && (
        <div
          style={{
            position: "absolute",
            left: lerp(-700, 1100, streak),
            top: 380,
            width: 700,
            height: 600,
            transform: "rotate(-18deg)",
            background: "linear-gradient(90deg, rgba(255,220,150,0) 0%, rgba(255,220,150,0.55) 50%, rgba(255,220,150,0) 100%)",
            filter: "blur(30px)",
            mixBlendMode: "screen",
          }}
        />
      )}
      <Appear t={t} a={T.quente - L} b={79.7} y={440} dy={40} blur={16}>
        <Serif size={150}>TEMA</Serif>
        <Serif size={170} gold style={{ marginTop: 4 }}>
          QUENTE
        </Serif>
      </Appear>
      <Appear t={t} a={76.05 - L} b={79.7} y={760} dy={20}>
        <Micro size={32}>MUITO ATUAL</Micro>
      </Appear>
      <Appear t={t} a={77.31 - L} b={79.7} y={830} dy={20}>
        <Micro size={32} color={C.gold}>
          EXTREMA IMPORTÂNCIA
        </Micro>
      </Appear>
      <Appear t={t} a={T.volto - L - 0.1} b={83.3} y={330} dy={20}>
        <Tag size={30}>SÉRIE 6x1</Tag>
      </Appear>
      <Appear t={t} a={T.volto - L - 0.1} b={83.3} y={620} dy={60} scaleFrom={0.8}>
        <PageCalendar t={t} />
      </Appear>
      {t > T.volto + 0.3 && t < 83.3 && (
        <div style={{ position: "absolute", left: 540, top: 920, transform: "translate(-50%,-50%)", display: "flex", alignItems: "center", opacity: 1 - ramp(t, 83.0, 83.3) }}>
          {steps.map((s, n) => {
            const at = T.volto + 0.7 + n * 0.5;
            const k = pop(t, at, 0.45);
            const lineK = ramp(t, at + 0.15, at + 0.5);
            return (
              <React.Fragment key={s}>
                <div style={{ textAlign: "center", opacity: clamp(k * 2), transform: `scale(${0.6 + 0.4 * k})` }}>
                  <div style={{ width: 34, height: 34, margin: "0 auto 12px", borderRadius: 17, background: "radial-gradient(circle at 35% 35%, #F0D9A6, #B8975A 60%, #8E703C)", boxShadow: `0 0 ${24 * k}px rgba(232,208,154,0.9)` }} />
                  <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 26, letterSpacing: "0.08em", color: C.white, whiteSpace: "nowrap", width: 230 }}>{s}</div>
                </div>
                {n < 2 && <div style={{ width: 40, height: 3, margin: "0 0 40px", background: `linear-gradient(90deg, ${C.gold} ${lineK * 100}%, rgba(184,151,90,0.2) ${lineK * 100}%)` }} />}
              </React.Fragment>
            );
          })}
        </div>
      )}
      <Appear t={t} a={T.atualizacoes - L} b={83.3} y={1060} dy={20} outDur={0.2}>
        <Micro size={30} color={C.gold} spacing={0.14}>
          ATUALIZAÇÕES AO LONGO DO MÊS
        </Micro>
      </Appear>
    </>
  );
};

// ======================= CENA 9 · CTA + ASSINATURA =======================
const Scene9 = ({ t }: { t: number }) => {
  const sym = ramp(t, T.finale + 0.85, T.finale + 1.2, easeOutCubic);
  const txt = ramp(t, T.finale + 1.0, T.finale + 1.3, easeOutCubic);
  const shimmer = ramp(t, T.finale + 0.9, T.finale + 1.5);
  const settle = ramp(t, T.finale + 0.85, T.finale + 1.25, easeInOutCubic);
  return (
    <>
      <Appear t={t} a={T.segue - L} b={T.finale + 0.2} y={440} dy={30}>
        <Serif size={112}>SIGA O PERFIL</Serif>
        <div style={{ display: "inline-block", marginTop: 22, padding: "14px 34px", borderRadius: 999, background: "rgba(12,27,51,0.85)", border: `2px solid rgba(184,151,90,0.7)` }}>
          <span style={{ fontFamily: SANS, fontWeight: 500, fontSize: 46, letterSpacing: "0.02em", ...GOLD_TEXT }}>@adv.arthurpiresnascimento</span>
        </div>
      </Appear>
      <Appear t={t} a={T.comente6x1 - L} b={T.finale + 0.2} y={790} dy={0} scaleFrom={1.3} inDur={0.3}>
        <div style={{ transform: `scale(${1 + 0.035 * Math.sin((t - T.comente6x1) * 6)})` }}>
          <div
            style={{
              padding: "30px 70px",
              borderRadius: 999,
              background: "linear-gradient(180deg,#E2C88F,#B8975A 60%,#9A7A43)",
              boxShadow: `0 20px 60px rgba(184,151,90,${0.35 + 0.2 * Math.sin((t - T.comente6x1) * 6)})`,
              fontFamily: SANS,
              fontWeight: 700,
              fontSize: 76,
              letterSpacing: "0.06em",
              color: C.navy,
            }}
          >
            COMENTE 6x1
          </div>
        </div>
      </Appear>
      <Appear t={t} a={T.checklist - L} b={T.finale + 0.2} y={940} dy={20}>
        <Micro size={36}>E RECEBA O CHECKLIST COMPLETO</Micro>
      </Appear>
      {sym > 0 && (
        <>
          <div style={{ position: "absolute", left: 540, top: lerp(800, 700, settle), transform: `translate(-50%,-50%) scale(${lerp(1.5, 1, settle)})`, opacity: sym }}>
            <Img src={staticFile("simbolo_dourado.png")} style={{ width: 420, display: "block", filter: "drop-shadow(0 20px 40px rgba(3,8,20,0.6))" }} />
            {/* brilho que atravessa o símbolo */}
            <div style={{ position: "absolute", inset: 0, overflow: "hidden", WebkitMaskImage: `url(${staticFile("simbolo_dourado.png")})`, WebkitMaskSize: "100% 100%" }}>
              <div style={{ position: "absolute", top: -100, bottom: -100, width: 120, left: lerp(-200, 560, shimmer), transform: "rotate(20deg)", background: "linear-gradient(90deg, rgba(255,255,255,0), rgba(255,250,230,0.85), rgba(255,255,255,0))" }} />
            </div>
          </div>
          <div style={{ position: "absolute", left: 540, top: 1030, transform: `translate(-50%,-50%) translateY(${(1 - txt) * 20}px)`, opacity: txt, textAlign: "center", whiteSpace: "nowrap" }}>
            <div style={{ fontFamily: SANS, fontWeight: 500, fontSize: 54, letterSpacing: "0.14em", color: C.white }}>ARTHUR PIRES NASCIMENTO</div>
            <div style={{ height: 3, width: 760 * txt, margin: "20px auto", background: C.gold }} />
            <div style={{ fontFamily: SANS, fontWeight: 400, fontSize: 26, letterSpacing: "0.42em", color: C.white, opacity: 0.9 }}>ADVOCACIA ESPECIALIZADA</div>
          </div>
        </>
      )}
    </>
  );
};

export const Scenes = ({ t }: { t: number }) => (
  <>
    {t < 6 && <Scene1 t={t} />}
    {t > 5 && t < 12 && <Scene2 t={t} />}
    {t > 11 && t < 24.5 && <Scene3 t={t} />}
    {t > 23.5 && t < 37.2 && <Scene4 t={t} />}
    {t > 35 && t < 43.6 && <Scene5 t={t} />}
    {t > 43 && t < 62.3 && <Scene6 t={t} />}
    {t > 61 && t < 74.8 && <Scene7 t={t} />}
    {t > 74 && t < 83.5 && <Scene8 t={t} />}
    {t > 83 && <Scene9 t={t} />}
  </>
);


