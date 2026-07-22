import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import { PlotView } from "../components/PlotView";
import { SheetView } from "../components/SheetView";
import {
  PATTERN_NAMES,
  type GenerationDetail,
  type GenerationSummary,
  type PlotSeries,
  type StepsPage,
} from "../types";

const PAGE = 25;

export function GenerationsPage({
  selectedId,
  onSelect,
}: {
  selectedId: number | null;
  onSelect: (id: number | null) => void;
}) {
  const [items, setItems] = useState<GenerationSummary[]>([]);
  const [detail, setDetail] = useState<GenerationDetail | null>(null);
  const [plot, setPlot] = useState<PlotSeries | null>(null);
  const [steps, setSteps] = useState<StepsPage | null>(null);
  const [offset, setOffset] = useState(0);
  const [error, setError] = useState("");

  useEffect(() => {
    api.listGenerations().then(setItems).catch((e) => setError(String(e.message)));
  }, []);

  const open = useCallback(
    (id: number) => {
      setError("");
      setDetail(null);
      setPlot(null);
      setSteps(null);
      setOffset(0);
      Promise.all([api.getGeneration(id), api.getPlot(id), api.getSteps(id, 0, PAGE)])
        .then(([d, p, s]) => {
          setDetail(d);
          setPlot(p);
          setSteps(s);
        })
        .catch((e) => setError(String(e.message)));
    },
    [],
  );

  useEffect(() => {
    if (selectedId != null) open(selectedId);
  }, [selectedId, open]);

  const page = (newOffset: number) => {
    if (!detail) return;
    setOffset(newOffset);
    api.getSteps(detail.id, newOffset, PAGE).then(setSteps).catch((e) => setError(String(e.message)));
  };

  return (
    <>
      <div className="card">
        <h2>Generations</h2>
        {items.length === 0 ? (
          <p className="muted">Nothing generated yet.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th><th>Profile</th><th>Pattern</th><th>Steps</th><th>Sheets</th><th>Created</th><th></th>
              </tr>
            </thead>
            <tbody>
              {items.map((g) => (
                <tr
                  key={g.id}
                  className={`clickable ${detail?.id === g.id ? "selected" : ""}`}
                >
                  <td onClick={() => onSelect(g.id)}>{g.id}</td>
                  <td onClick={() => onSelect(g.id)}>{g.profile_name}</td>
                  <td onClick={() => onSelect(g.id)}>{PATTERN_NAMES[g.pattern_type] ?? g.pattern_type}</td>
                  <td onClick={() => onSelect(g.id)}>{g.row_count}</td>
                  <td onClick={() => onSelect(g.id)}>{g.sheet_count ?? "—"}</td>
                  <td onClick={() => onSelect(g.id)}>{new Date(g.created_at).toLocaleString()}</td>
                  <td><a href={api.artifactUrl(g.id)}>.xlsx</a></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {error && <div className="error">{error}</div>}
      </div>

      {detail && (
        <div className="card">
          <h2>
            Generation #{detail.id} — {detail.profile_name}
          </h2>
          <div className="stats">
            <div><b>{PATTERN_NAMES[detail.pattern_type] ?? detail.pattern_type}</b><span>pattern</span></div>
            <div><b>{detail.row_count}</b><span>table rows</span></div>
            <div><b>{detail.sheet_count ?? "—"}</b><span>sheet count</span></div>
            <div><b>{detail.pattern_length ?? "—"}</b><span>pattern length (mm)</span></div>
            <div><b>{detail.start_index ?? "—"}–{detail.end_index ?? "—"}</b><span>executable window</span></div>
            <div>
              <b><a href={api.artifactUrl(detail.id)}>download</a></b>
              <span>{detail.artifact_path}</span>
            </div>
          </div>

          {plot && <SheetView series={plot} />}
          {plot && (
            <>
              <h3>Coil overview</h3>
              <PlotView series={plot} />
            </>
          )}

          {steps && (
            <>
              <h3>Step table</h3>
              <div className="toolgrid">
                <table>
                  <thead>
                    <tr>
                      <th>#</th>
                      {steps.columns.map((c) => <th key={c}>{c}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {steps.rows.map((row, i) => (
                      <tr key={i}>
                        <td>{steps.offset + i + 1}</td>
                        {row.map((cell, j) => <td key={j}>{cell ?? ""}</td>)}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="pager">
                <button className="ghost" disabled={offset === 0} onClick={() => page(Math.max(offset - PAGE, 0))}>
                  ← Prev
                </button>
                <span className="muted">
                  rows {steps.offset + 1}–{Math.min(steps.offset + PAGE, steps.total_rows)} of {steps.total_rows}
                </span>
                <button
                  className="ghost"
                  disabled={offset + PAGE >= steps.total_rows}
                  onClick={() => page(offset + PAGE)}
                >
                  Next →
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </>
  );
}
