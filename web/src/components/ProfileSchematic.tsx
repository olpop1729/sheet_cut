import type { ReactElement } from "react";
import type { ToolSpec } from "../types";

/**
 * Tool-sequence schematic — SVG port of the legacy Tkinter DisplayWindow
 * (legacy/gui/display_screen.py): a sheet strip with one glyph per tool at
 * x = 3i + 2 in legacy units, using the same glyph geometry and colors.
 * Segment labels run L1..L(n-1) left to right, matching the run screen's
 * length inputs (the legacy schematic numbered them in reverse).
 */
export function ProfileSchematic({ tools }: { tools: ToolSpec[] }) {
  const S = 30; // px per legacy unit
  const n = tools.length;
  const lastPos = 3 * (n - 1) + 2;
  const width = (lastPos + 6) * S;
  const yTop = 3.2;
  const yBottom = -3.2;
  const height = (yTop - yBottom) * S;
  // legacy coords are y-up; SVG is y-down
  const X = (x: number) => (x + 1) * S;
  const Y = (y: number) => (yTop - y) * S;

  const line = (
    key: string,
    x1: number,
    y1: number,
    x2: number,
    y2: number,
    color: string,
    dash?: string,
    w = 1.5,
  ) => (
    <line
      key={key}
      x1={X(x1)}
      y1={Y(y1)}
      x2={X(x2)}
      y2={Y(y2)}
      stroke={color}
      strokeWidth={w}
      strokeDasharray={dash}
    />
  );

  const glyphs: ReactElement[] = [];
  let spearFront = false; // legacy alternates the chevron direction per 's'
  tools.forEach((t, i) => {
    const p = 3 * i + 2;
    const k = `g${i}`;
    switch (t.name) {
      case "fp45":
        glyphs.push(line(k, p + 1, -1, p - 1, 1, "#1c2430"));
        break;
      case "fm45":
        glyphs.push(line(k, p - 1, -1, p + 1, 1, "#1c2430"));
        break;
      case "f0":
        glyphs.push(line(k, p, -1, p, 1, "#1c2430"));
        break;
      case "h":
        glyphs.push(
          <circle
            key={k}
            cx={X(p)}
            cy={Y(0)}
            r={0.2 * S}
            fill="none"
            stroke="#27ae60"
            strokeWidth={1.5}
          />,
        );
        break;
      case "v":
        glyphs.push(
          <g key={k}>
            {line(`${k}a`, p, 0, p - 1, 1, "#d9534f", undefined, 1.2)}
            {line(`${k}b`, p, 0, p + 1, 1, "#d9534f", undefined, 1.2)}
          </g>,
        );
        break;
      case "s":
        glyphs.push(
          spearFront ? (
            <g key={k}>
              {line(`${k}a`, p, 0, p - 1, 1, "#0aa2c0", undefined, 1.4)}
              {line(`${k}b`, p - 1, -1, p, 0, "#0aa2c0", undefined, 1.4)}
            </g>
          ) : (
            <g key={k}>
              {line(`${k}a`, p, 0, p + 1, 1, "#0aa2c0", undefined, 1.4)}
              {line(`${k}b`, p + 1, -1, p, 0, "#0aa2c0", undefined, 1.4)}
            </g>
          ),
        );
        spearFront = !spearFront;
        break;
      case "ys":
        glyphs.push(
          <g key={k}>
            {line(`${k}a`, p, 0, p + 1, 1, "#1c2430")}
            {line(`${k}b`, p + 1, -1, p - 1, 1, "#1c2430")}
          </g>,
        );
        break;
      default:
        break;
    }
    glyphs.push(
      <text key={`t${i}`} x={X(p)} y={Y(1.35)} fontSize={11} fill="#5a6675" textAnchor="middle">
        {t.name}
        {t.steplap_count > 1 ? ` ×${t.steplap_count}` : ""}
      </text>,
    );
  });

  const segments: ReactElement[] = [];
  for (let i = 0; i < n - 1; i++) {
    const a = 3 * i + 2;
    const b = 3 * (i + 1) + 2;
    segments.push(
      <g key={`seg${i}`}>
        <line
          x1={X(a) + 4}
          y1={Y(-2)}
          x2={X(b) - 4}
          y2={Y(-2)}
          stroke="#75808f"
          strokeWidth={1}
          markerStart="url(#arrL)"
          markerEnd="url(#arrR)"
        />
        <text x={X((a + b) / 2)} y={Y(-2.55)} fontSize={11} fill="#445060" textAnchor="middle">
          L{i + 1}
        </text>
      </g>,
    );
  }

  return (
    <div style={{ overflowX: "auto" }}>
      <svg width={width} height={height} role="img" aria-label="profile schematic">
        <defs>
          <marker id="arrR" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
            <path d="M0,0 L6,3 L0,6" fill="none" stroke="#75808f" />
          </marker>
          <marker id="arrL" markerWidth="8" markerHeight="8" refX="0" refY="3" orient="auto">
            <path d="M6,0 L0,3 L6,6" fill="none" stroke="#75808f" />
          </marker>
        </defs>
        {/* sheet strip: edges + centerline, feed arrow at the end */}
        <line x1={X(0)} y1={Y(1)} x2={X(lastPos + 3)} y2={Y(1)} stroke="#1c2430" strokeWidth={1.5} />
        <line
          x1={X(0)}
          y1={Y(-1)}
          x2={X(lastPos + 3)}
          y2={Y(-1)}
          stroke="#1c2430"
          strokeWidth={1.5}
        />
        <line
          x1={X(0)}
          y1={Y(0)}
          x2={X(lastPos + 3)}
          y2={Y(0)}
          stroke="#1c64d9"
          strokeWidth={1}
          strokeDasharray="6 3 1 3"
        />
        <line
          x1={X(lastPos + 3)}
          y1={Y(0)}
          x2={X(lastPos + 4.6)}
          y2={Y(0)}
          stroke="#1c2430"
          strokeWidth={1.2}
          markerEnd="url(#arrR)"
        />
        {glyphs}
        {segments}
      </svg>
    </div>
  );
}
