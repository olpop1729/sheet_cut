import { useMemo, useState } from "react";
import type { Piece, PlotEvent, PlotSeries } from "../types";

/**
 * Resulting pieces — what actually comes off the line, for the ground worker.
 *
 * Each lamination is the strip region between two consecutive shear cuts;
 * the shared cut line's angle shapes the trailing end of one piece and the
 * leading end of the next (fp45 rises to the right, fm45 falls, f0 square).
 *
 * A v-notch is a punch: its triangular cutout spans ±(width − tip height)
 * around its center, so it is drawn on EVERY piece that footprint overlaps,
 * clipped to that piece's outline — this is what forms spear points (shear
 * line + notch arm meeting at the centerline) and notched seats on the two
 * sheets adjacent to a boundary notch.
 *
 * Pieces are laid out in production order. Because 45-degree ends of
 * neighboring pieces occupy the same x-range (they share one cut line), the
 * gap between pieces is at least the end overlap, so sheets never draw over
 * each other. The zoom is ISOTROPIC (same px/mm on both axes) so 45-degree
 * ends always look like 45 degrees. Centerline lengths in the labels are
 * exact; the coil width is a nominal drawing value until the real width is
 * entered.
 */

const PAD_X = 12;
const LABEL_H = 40;
const HOLE_R_MM = 7.5;

const SCALES = [0.1, 0.25, 0.5, 1];
const MAX_PIECES = 60;

interface EndOffsets {
  bottom: number;
  top: number;
}

function endOffsets(tool: string, w: number): EndOffsets {
  if (tool === "fp45") return { bottom: -w / 2, top: w / 2 };
  if (tool === "fm45") return { bottom: w / 2, top: -w / 2 };
  return { bottom: 0, top: 0 };
}

function pieceTitle(p: Piece): string {
  const lines = [
    `piece #${p.index}: ${p.center_length} mm centerline`,
    `left end ${p.left.tool} (row ${p.left.row}) @ ${p.left.x.toFixed(2)} mm`,
    `right end ${p.right.tool} (row ${p.right.row}) @ ${p.right.x.toFixed(2)} mm`,
  ];
  for (const h of p.holes) lines.push(`hole @ ${h.offset.toFixed(2)} mm from left end`);
  for (const n of p.notches) {
    lines.push(
      `v-notch @ ${n.offset.toFixed(2)} mm from left end` +
        (n.travel != null ? `, traverse ${n.travel}` : " (traverse per step level)"),
    );
  }
  return lines.join("\n");
}

/**
 * Vertical tip offset (mm from centerline) of a piece end, if a v-notch arm
 * crosses the end's shear line: an fm45 edge ("\") is crossed by a notch's
 * right arm, an fp45 edge ("/") by a left arm, meeting at
 * center ± (Δx − travel)/2. Null when no notch arm reaches the end (f0 ends,
 * or the notch is out of range) — the end is then a plain straight cut.
 */
function tipOffset(
  endTool: string,
  endX: number,
  notches: PlotEvent[],
  w: number,
): number | null {
  let best: { off: number; dist: number } | null = null;
  for (const n of notches) {
    const t = n.v_travel ?? 0;
    const dist = Math.abs(n.cut_x! - endX);
    if (dist > w / 2 + t) continue; // arm cannot reach this end
    let off: number;
    if (endTool === "fm45") {
      off = (endX - n.cut_x! - t) / 2;
    } else if (endTool === "fp45") {
      off = (n.cut_x! - endX - t) / 2;
    } else {
      continue;
    }
    if (off < -t || off > w / 2) continue; // crossing not on the arm / sheet
    if (!best || dist < best.dist) best = { off, dist };
  }
  return best ? best.off : null;
}

const DETAIL_BOX = 104;
const MAX_DETAIL_BODIES = 8;

/** Magnified view of one piece end so mm-scale tip offsets become visible. */
function EndDetail({
  piece,
  end,
  notches,
  w,
  zoom,
}: {
  piece: Piece;
  end: "L" | "R";
  notches: PlotEvent[];
  w: number;
  zoom: number;
}) {
  const edge = end === "L" ? piece.left : piece.right;
  const c = w / 2;
  const half = DETAIL_BOX / 2;
  const X = (mm: number) => half + (mm - edge.x) * zoom;
  const Y = (mm: number) => half + (c - mm) * zoom;

  const lo = endOffsets(piece.left.tool, w);
  const ro = endOffsets(piece.right.tool, w);
  const quad = [
    `${X(piece.left.x + lo.bottom)},${Y(0)}`,
    `${X(piece.right.x + ro.bottom)},${Y(0)}`,
    `${X(piece.right.x + ro.top)},${Y(w)}`,
    `${X(piece.left.x + lo.top)},${Y(w)}`,
  ].join(" ");
  const off = tipOffset(edge.tool, edge.x, notches, w);

  return (
    <div style={{ textAlign: "center" }}>
      <svg
        width={DETAIL_BOX}
        height={DETAIL_BOX}
        style={{ border: "1px solid #d8dce3", borderRadius: 4, background: "#fff" }}
        role="img"
        aria-label={`piece ${piece.index} ${end === "L" ? "left" : "right"} end detail`}
      >
        <polygon points={quad} fill="#c9d4e2" stroke="#3b4a5e" strokeWidth={1.2} />
        {notches.map((n) => {
          const t = n.v_travel ?? 0;
          const tipY = c - t;
          const armHalf = w - tipY;
          return (
            <polygon
              key={n.row}
              points={`${X(n.cut_x! - armHalf)},${Y(w)} ${X(n.cut_x!)},${Y(tipY)} ${X(n.cut_x! + armHalf)},${Y(w)}`}
              fill="#fff"
              stroke="#d9534f"
              strokeWidth={1}
            />
          );
        })}
        <line
          x1={0}
          x2={DETAIL_BOX}
          y1={Y(c)}
          y2={Y(c)}
          stroke="#1c64d9"
          strokeWidth={0.8}
          strokeDasharray="5 3"
        />
      </svg>
      <div className="muted" style={{ fontSize: 11, marginTop: 2 }}>
        #{piece.index} {end === "L" ? "front" : "rear"}
        {off != null ? ` tip ${off >= 0 ? "+" : ""}${off.toFixed(2)}` : ""}
      </div>
    </div>
  );
}

export function PiecesView({ series }: { series: PlotSeries }) {
  const [windowOnly, setWindowOnly] = useState(true);
  const [fitView, setFitView] = useState(true);
  const [scale, setScale] = useState(0.25);
  const [sheetW, setSheetW] = useState(200);

  const hasWindow = series.start_index != null && series.end_index != null;
  const all = useMemo(() => {
    if (windowOnly && hasWindow) {
      return series.pieces.filter(
        (p) => p.left.row >= series.start_index! && p.right.row <= series.end_index!,
      );
    }
    return series.pieces;
  }, [series, windowOnly, hasWindow]);
  const pieces = all.slice(0, MAX_PIECES);

  // every v-notch punch in the program; footprint overlap decides which
  // pieces it appears on, independent of the piece that "owns" it
  const vNotches = useMemo(
    () => series.events.filter((e) => e.kind === "vnotch" && e.cut_x != null),
    [series],
  );

  if (pieces.length === 0) {
    return (
      <div>
        <h3 style={{ marginBottom: 4 }}>Resulting pieces</h3>
        <p className="muted">
          No complete piece in this view — a piece needs two shear cuts.
          {hasWindow && " Try disabling the window filter."}
        </p>
        {hasWindow && (
          <label className="muted">
            <input
              type="checkbox"
              checked={windowOnly}
              onChange={(e) => setWindowOnly(e.target.checked)}
            />{" "}
            executable window only
          </label>
        )}
      </div>
    );
  }

  const w = sheetW;
  const s = scale;

  // magnified end views for spear/fish patterns, where the tip geometry is
  // millimetre-scale and invisible at whole-piece zoom
  const showDetails = [3, 4, 5].includes(series.pattern_type);
  const detailBodies = showDetails
    ? pieces.filter((p) => p.center_length > 50).slice(0, MAX_DETAIL_BODIES)
    : [];
  const maxTravel = vNotches.reduce((m, n) => Math.max(m, Math.abs(n.v_travel ?? 0)), 0);
  const detailZoom = (DETAIL_BOX - 16) / Math.max(30, 6 * maxTravel + 10);

  // neighboring 45-degree ends share one cut line and overlap by up to w mm
  // in x; keep the exploded gap larger so sheets never draw over each other
  const gap = w * s + 14;
  const origin = pieces[0].left.x - w / 2;
  const spanMm = pieces[pieces.length - 1].right.x + w / 2 - origin;
  const width = spanMm * s + (pieces.length + 1) * gap + 2 * PAD_X;
  const bodyH = w * s; // strictly isotropic so end angles stay true
  const height = bodyH + LABEL_H + 8;
  const X = (mm: number, k: number) => PAD_X + (mm - origin) * s + (k + 1) * gap;
  const Y = (mm: number) => 4 + (w - mm) * s; // sheet y (0=bottom) -> px

  const notchGeometry = (n: PlotEvent) => {
    const tipY = w / 2 - (n.v_travel ?? 0);
    return { tipY, half: w - tipY };
  };

  return (
    <div>
      <div className="row">
        <h3 style={{ margin: 0 }}>Resulting pieces</h3>
        {hasWindow && (
          <label style={{ minWidth: 0 }}>
            <input
              type="checkbox"
              checked={windowOnly}
              onChange={(e) => setWindowOnly(e.target.checked)}
            />{" "}
            executable window only
          </label>
        )}
        <label style={{ minWidth: 0 }}>
          <input
            type="checkbox"
            checked={fitView}
            onChange={(e) => setFitView(e.target.checked)}
          />{" "}
          fit view
        </label>
        <label style={{ minWidth: 0 }}>zoom</label>
        <select
          value={scale}
          disabled={fitView}
          onChange={(e) => setScale(Number(e.target.value))}
        >
          {SCALES.map((z) => (
            <option key={z} value={z}>
              {z} px/mm
            </option>
          ))}
        </select>
        <label style={{ minWidth: 0 }}>coil width (mm)</label>
        <input
          type="number"
          min={20}
          step={10}
          value={sheetW}
          onChange={(e) => setSheetW(Math.max(Number(e.target.value) || 200, 20))}
          style={{ width: 80 }}
        />
      </div>

      <div style={{ overflowX: "auto", border: "1px solid #e0e4ea", borderRadius: 6 }}>
        <svg
          viewBox={`0 0 ${width} ${height}`}
          style={fitView ? { width: "100%", height: "auto" } : { width, height }}
          role="img"
          aria-label="resulting pieces"
        >
          {pieces.map((p, k) => {
            const lo = endOffsets(p.left.tool, w);
            const ro = endOffsets(p.right.tool, w);
            const xbl = X(p.left.x + lo.bottom, k);
            const xtl = X(p.left.x + lo.top, k);
            const xbr = X(p.right.x + ro.bottom, k);
            const xtr = X(p.right.x + ro.top, k);
            const quad = `${xbl},${Y(0)} ${xbr},${Y(0)} ${xtr},${Y(w)} ${xtl},${Y(w)}`;
            const clipId = `piececlip-${p.index}`;
            const fill = k % 2 === 0 ? "#c9d4e2" : "#bac7d8";
            const centerPx = (xbl + xtl + xbr + xtr) / 4;
            const notches = vNotches.filter((n) => {
              const { half } = notchGeometry(n);
              return n.cut_x! + half > p.left.x && n.cut_x! - half < p.right.x;
            });
            return (
              <g key={p.index}>
                <defs>
                  <clipPath id={clipId}>
                    <polygon points={quad} />
                  </clipPath>
                </defs>
                <g clipPath={`url(#${clipId})`}>
                  <polygon points={quad} fill={fill} stroke="#3b4a5e" strokeWidth={1.4}>
                    <title>{pieceTitle(p)}</title>
                  </polygon>
                  {notches.map((n) => {
                    const { tipY, half } = notchGeometry(n);
                    return (
                      <polygon
                        key={`n${n.row}`}
                        points={`${X(n.cut_x! - half, k)},${Y(w)} ${X(n.cut_x!, k)},${Y(tipY)} ${X(n.cut_x! + half, k)},${Y(w)}`}
                        fill="#f5f6f8"
                        stroke="#d9534f"
                        strokeWidth={1.2}
                      >
                        <title>
                          {`v-notch (row ${n.row}) @ ${n.cut_x!.toFixed(2)} mm` +
                            (n.v_travel != null
                              ? `, traverse ${n.v_travel}`
                              : " (traverse per step level)")}
                        </title>
                      </polygon>
                    );
                  })}
                  {p.holes.map((h) => (
                    <circle
                      key={`h${h.row}`}
                      cx={X(h.x, k)}
                      cy={Y(w / 2)}
                      r={Math.max(HOLE_R_MM * s, 2)}
                      fill="#f5f6f8"
                      stroke="#3b4a5e"
                      strokeWidth={1.2}
                    >
                      <title>{`hole (row ${h.row}) @ ${h.offset.toFixed(2)} mm from left end`}</title>
                    </circle>
                  ))}
                </g>
                <text
                  x={centerPx}
                  y={bodyH + 24}
                  fontSize={11}
                  fill="#344050"
                  textAnchor="middle"
                  fontWeight={600}
                >
                  #{p.index}
                </text>
                <text x={centerPx} y={bodyH + 38} fontSize={10} fill="#75808f" textAnchor="middle">
                  {p.center_length} mm
                </text>
              </g>
            );
          })}
        </svg>
      </div>
      <p className="muted">
        {pieces.length}
        {all.length > pieces.length ? ` of ${all.length}` : ""} pieces in production order,
        left → right; each gap is a shear cut. White circles/wedges are removed material —
        a v-notch near a boundary appears on every sheet it reaches. Lengths are centerline
        mm; end angles use the nominal coil width.
        {all.length > pieces.length && " Showing the first " + MAX_PIECES + "."}
      </p>

      {detailBodies.length > 0 && (
        <>
          <h3 style={{ marginBottom: 4 }}>End details (×{detailZoom.toFixed(1)})</h3>
          <div className="row" style={{ alignItems: "flex-start" }}>
            {detailBodies.map((p) => (
              <div key={p.index} className="row" style={{ gap: 4, marginBottom: 0 }}>
                <EndDetail piece={p} end="L" notches={vNotches} w={w} zoom={detailZoom} />
                <EndDetail piece={p} end="R" notches={vNotches} w={w} zoom={detailZoom} />
              </div>
            ))}
          </div>
          <p className="muted">
            Magnified piece ends against the strip centerline (dashed). The tips sit above
            or below it by the step-lap: when the rear tip is up, the front tip is down,
            stepping one step-lap distance per layer. Tip values are mm from the centerline.
          </p>
        </>
      )}
    </div>
  );
}
