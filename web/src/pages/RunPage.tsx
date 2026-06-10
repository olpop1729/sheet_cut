import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import { PATTERN_NAMES, type GenerationSummary, type Profile } from "../types";

export function RunPage({ onOpenGeneration }: { onOpenGeneration: (id: number) => void }) {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [profileId, setProfileId] = useState<number | "">("");
  const [lengths, setLengths] = useState<string[]>([]);
  const [distances, setDistances] = useState<string[]>([]);
  const [layers, setLayers] = useState("1");
  const [startSheet, setStartSheet] = useState("1");
  const [scrap, setScrap] = useState("0");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<GenerationSummary | null>(null);

  useEffect(() => {
    api.listProfiles().then(setProfiles).catch((e) => setError(String(e.message)));
  }, []);

  const profile = useMemo(
    () => profiles.find((p) => p.id === profileId) ?? null,
    [profiles, profileId],
  );

  // The run screen sizes its inputs from the profile, like the legacy GUI:
  // len(tools)-1 segment lengths, one distance per step-lap tool.
  useEffect(() => {
    if (!profile) return;
    setLengths(Array(Math.max(profile.tools.length - 1, 1)).fill(""));
    setDistances(Array(profile.steplap_tool_count).fill("0"));
    setResult(null);
    setError("");
  }, [profile]);

  const needsScrap = profile != null && [3, 4, 5].includes(profile.pattern_type);

  const run = async () => {
    if (!profile) return;
    setBusy(true);
    setError("");
    setResult(null);
    try {
      const summary = await api.generate(profile.id, {
        length_list: lengths.map(Number),
        steplap_distances: distances.map(Number),
        layers: Number(layers),
        start_sheet: Number(startSheet),
        scrap_length: needsScrap ? Number(scrap) : 0,
      });
      setResult(summary);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const numbersOk =
    lengths.every((v) => v.trim() !== "" && !Number.isNaN(Number(v))) &&
    distances.every((v) => v.trim() !== "" && !Number.isNaN(Number(v)));

  return (
    <div className="card">
      <h2>Run a cut program</h2>
      <div className="row">
        <label>Profile</label>
        <select
          value={profileId}
          onChange={(e) => setProfileId(e.target.value === "" ? "" : Number(e.target.value))}
        >
          <option value="">— select —</option>
          {profiles.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name} ({PATTERN_NAMES[p.pattern_type] ?? p.pattern_type})
            </option>
          ))}
        </select>
      </div>

      {profile && (
        <>
          <h3>Segment lengths (mm)</h3>
          {lengths.map((v, i) => (
            <div className="row" key={i}>
              <label>L{i + 1}</label>
              <input type="number" value={v} step="0.01"
                onChange={(e) => setLengths((ls) => ls.map((x, j) => (j === i ? e.target.value : x)))} />
            </div>
          ))}

          {distances.length > 0 && <h3>Step-lap distances (mm)</h3>}
          {distances.map((v, i) => (
            <div className="row" key={i}>
              <label>Step-lap {i + 1}</label>
              <input type="number" value={v} step="0.01"
                onChange={(e) => setDistances((ds) => ds.map((x, j) => (j === i ? e.target.value : x)))} />
            </div>
          ))}

          <h3>Run parameters</h3>
          <div className="row">
            <label>Layers</label>
            <input type="number" min={1} value={layers} onChange={(e) => setLayers(e.target.value)} />
          </div>
          <div className="row">
            <label>Start sheet</label>
            <input type="number" min={1} value={startSheet} onChange={(e) => setStartSheet(e.target.value)} />
          </div>
          {needsScrap && (
            <div className="row">
              <label>Scrap length</label>
              <input type="number" min={0} value={scrap} onChange={(e) => setScrap(e.target.value)} />
            </div>
          )}

          <div className="row" style={{ marginTop: 10 }}>
            <button className="primary" onClick={run} disabled={busy || !numbersOk}>
              {busy ? "Generating…" : "Generate"}
            </button>
          </div>
        </>
      )}

      {error && <div className="error">{error}</div>}
      {result && (
        <div className="ok">
          Generated #{result.id}: {result.row_count} steps
          {result.sheet_count != null && <> · {result.sheet_count} sheets</>}
          {result.pattern_length != null && <> · pattern {result.pattern_length} mm</>}
          {" · "}
          <a href={api.artifactUrl(result.id)}>download .xlsx</a>
          {" · "}
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              onOpenGeneration(result.id);
            }}
          >
            inspect
          </a>
        </div>
      )}
    </div>
  );
}
