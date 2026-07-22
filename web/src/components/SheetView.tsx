import { useMemo, useState } from "react";
import type { PlotEvent, PlotSeries } from "../types";

/**
 * Sheet visualization — SVG port of the legacy verify screen
 * (legacy/gui/visualize.py): the coil drawn as a sheet strip with every cut
 * at its physical position. Cut x-positions arrive precomputed from the
 * backend (accumulated feed minus each tool's distance from the V-notch).
 *
 * Geometry mirrors the legacy drawing: 200 mm visual sheet width, hole ⌀15
 * on the centerline, 90° V-notch from the top edge whose tip sits at
 * centerline minus the traverse value, shears as full-width dashed
 * diagonals (±45°) or verticals (f0).
 */

const SHEET_W = 200;
const HOLE_R = 7.5;
const PAD_TOP = 56; // label space above the sheet
const PAD_BOTTOM = 26;

const ZOOMS = [0.05, 0.1, 0.25, 0.5];

export function SheetView({ series }: { series: PlotSeries }) {
  const [windowOnly, setWindowOnly] = useState(true);
  const [pxPerMm, setPxPerMm] = useState(0.1);

  const hasWindow = series.start_index != null && series.end_index != null;
  const cuts = useMemo(() => {
    let events = series.events.filter((e) => e.kind != null && e.cut_x != null);
    if (windowOnly && hasWindow) {
      events = events.filter(
        (e) => e.row >= series.start_index! && e.row <= series.end_index!,
      );
    }
    return events;
  }, [series, windowOnly, hasWindow]);

  if (cuts.length === 0) {
    return <p className="muted">No cuts to draw.</p>;
  }

  const xs = cuts.map((e) => e.cut_x!);
  const minX = Math.min(...xs) - 150;
  const maxX = Math.max(...xs) + 150;
  const spanMm = maxX - minX;
  const width = Math.max(spanMm * pxPerMm, 300);
  const height = PAD_TOP + SHEET_W + PAD_BOTTOM;
  const X = (mm: number) => ((mm - minX) / spanMm) * width;
  // sheet-space y (0 = bottom edge, 200 = top edge) -> SVG y
  const Y = (mm: number) => PAD_TOP + (SHEET_W - mm);

  const showLabels = cuts.length <= 140;
  const label = (e: PlotEvent, color: string, tier: number) =>
    showLabels ? (
      <text
        x={X(e.cut_x!)}
        y={PAD_TOP - 8 - tier * 16}
        fontSize={9}
        fill={color}
        textAnchor="middle"
      >
        {`${e.tool}(${e.row}) @${e.cut_x!.toFixed(1)}`}
      </text>
    ) : null;

  return (
    <div>
      <div className="row">
        <h3 style={{ margin: 0 }}>Sheet view</h3>
        {hasWindow && (
          <label style={{ minWidth: 0 }}>
            <input
              type="checkbox"
              checked={windowOnly}
              onChange={(e) => setWindowOnly(e.target.checked)}
            />{" "}
            executable window only ({series.start_index}–{series.end_index})
          </label>
        )}
        <label style={{ minWidth: 0 }}>zoom</label>
        <select value={pxPerMm} onChange={(e) => setPxPerMm(Number(e.target.value))}>
          {ZOOMS.map((z) => (
            <option key={z} value={z}>
              {z} px/mm
            </option>
          ))}
        </select>
      </div>
      <div style={{ overflowX: "auto", border: "1px solid #e0e4ea", borderRadius: 6 }}>
        <svg width={width} height={height} role="img" aria-label="sheet view">
          {/* the sheet */}
          <rect
            x={0}
            y={Y(SHEET_W)}
            width={width}
            height={SHEET_W}
            fill="#e9ecf1"
            stroke="#1c2430"
            strokeWidth={1.5}
          />
          <line
            x1={0}
            y1={Y(SHEET_W / 2)}
            x2={width}
            y2={Y(SHEET_W / 2)}
            stroke="#9aa4b1"
            strokeWidth={0.6}
            strokeDasharray="8 4"
          />

          {cuts.map((e, i) => {
            const x = X(e.cut_x!);
            const tier = i % 2;
            if (e.kind === "hole") {
              return (
                <g key={e.row}>
                  <circle cx={x} cy={Y(SHEET_W / 2)} r={HOLE_R} fill="#1c64d9" opacity={0.85}>
                    <title>{`hole  row ${e.row}  @ ${e.cut_x!.toFixed(2)} mm`}</title>
                  </circle>
                  {label(e, "#1c64d9", tier)}
                </g>
              );
            }
            if (e.kind === "vnotch") {
              const tipY = SHEET_W / 2 - (e.v_travel ?? 0);
              const half = SHEET_W - tipY; // 90° notch from the top edge
              return (
                <g key={e.row}>
                  <polygon
                    points={`${X(e.cut_x! - half)},${Y(SHEET_W)} ${x},${Y(tipY)} ${X(e.cut_x! + half)},${Y(SHEET_W)}`}
                    fill="#d9534f"
                    opacity={0.85}
                  >
                    <title>
                      {`v-notch  row ${e.row}  @ ${e.cut_x!.toFixed(2)} mm` +
                        (e.v_travel != null
                          ? `  traverse ${e.v_travel}`
                          : "  (traverse per step level; see stats)")}
                    </title>
                  </polygon>
                  {label(e, "#d9534f", tier)}
                </g>
              );
            }
            // shear cuts: fp45 rises to the right, fm45 falls, f0 vertical
            const half =
              e.tool === "fp45" ? -SHEET_W / 2 : e.tool === "fm45" ? SHEET_W / 2 : 0;
            return (
              <g key={e.row}>
                <line
                  x1={X(e.cut_x! + half)}
                  y1={Y(0)}
                  x2={X(e.cut_x! - half)}
                  y2={Y(SHEET_W)}
                  stroke="#1e8e3e"
                  strokeWidth={2.5}
                  strokeDasharray="7 5"
                >
                  <title>{`${e.tool}  row ${e.row}  @ ${e.cut_x!.toFixed(2)} mm`}</title>
                </line>
                {label(e, "#1e8e3e", tier)}
              </g>
            );
          })}

          <text x={4} y={height - 8} fontSize={10} fill="#75808f">
            {minX.toFixed(0)} mm
          </text>
          <text x={width - 4} y={height - 8} fontSize={10} fill="#75808f" textAnchor="end">
            {maxX.toFixed(0)} mm
          </text>
        </svg>
      </div>
      <p className="muted">
        {cuts.length} cuts drawn · <span style={{ color: "#1e8e3e" }}>— — shear</span> ·{" "}
        <span style={{ color: "#d9534f" }}>▼ v-notch</span> ·{" "}
        <span style={{ color: "#1c64d9" }}>● hole</span>
        {!showLabels && " · labels hidden (too many cuts); hover for details"}
      </p>
    </div>
  );
}
