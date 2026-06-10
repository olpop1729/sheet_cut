import type { PlotSeries } from "../types";

const TOOL_COLORS: Record<string, string> = {
  fp45: "#e74c3c",
  fm45: "#8e44ad",
  f0: "#2c3e50",
  v: "#27ae60",
  h: "#f39c12",
};

/** Coil-position strip: one tick per cut, colored by tool. */
export function PlotView({ series }: { series: PlotSeries }) {
  const events = series.events;
  if (events.length === 0) return <p className="muted">No events to plot.</p>;

  const maxPos = Math.max(...events.map((e) => e.position));
  const W = 1000;
  const H = 130;
  const left = 20;
  const right = 20;
  const span = W - left - right;
  const x = (pos: number) => left + (maxPos === 0 ? 0 : (pos / maxPos) * span);

  const toolsUsed = [...new Set(events.map((e) => e.tool ?? "?"))];

  return (
    <div>
      <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", height: "auto" }}>
        <rect x={left} y={40} width={span} height={36} fill="#eef1f5" stroke="#c9cfd9" />
        {events.map((e, i) => (
          <line
            key={i}
            x1={x(e.position)}
            x2={x(e.position)}
            y1={e.tool === "h" ? 48 : 40}
            y2={e.tool === "h" ? 68 : 76}
            stroke={TOOL_COLORS[e.tool ?? ""] ?? "#888"}
            strokeWidth={e.tool?.startsWith("f") ? 2.5 : 1.5}
          >
            <title>{`#${e.row} ${e.tool} @ ${e.position}`}</title>
          </line>
        ))}
        <text x={left} y={100} fontSize="11" fill="#75808f">0</text>
        <text x={W - right} y={100} fontSize="11" fill="#75808f" textAnchor="end">
          {maxPos.toFixed(2)} mm
        </text>
        {toolsUsed.map((t, i) => (
          <g key={t} transform={`translate(${left + i * 110}, 118)`}>
            <line x1={0} x2={16} y1={-4} y2={-4} stroke={TOOL_COLORS[t] ?? "#888"} strokeWidth={3} />
            <text x={22} y={0} fontSize="11" fill="#445060">{t}</text>
          </g>
        ))}
      </svg>
      <p className="muted">
        {events.length} cuts · pattern length{" "}
        {series.pattern_length != null ? `${series.pattern_length} mm` : "—"} · executable
        window rows {series.start_index ?? "—"}–{series.end_index ?? "—"}
      </p>
    </div>
  );
}
