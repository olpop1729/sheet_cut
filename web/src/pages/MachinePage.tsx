import { useEffect, useState } from "react";
import { api } from "../api";
import type { MachineConfigValues, MachineConfigVersion } from "../types";

const FIELDS: { key: keyof MachineConfigValues; label: string }[] = [
  { key: "offset_fp45", label: "Offset FP45" },
  { key: "offset_fm45", label: "Offset FM45" },
  { key: "offset_f0", label: "Offset F0" },
  { key: "offset_v_lat", label: "Offset V lateral" },
  { key: "distance_hole_vnotch", label: "Hole ↔ V-notch distance" },
  { key: "distance_shear_vnotch", label: "Shear ↔ V-notch distance" },
  { key: "coil_length", label: "Coil length" },
];

export function MachinePage() {
  const [values, setValues] = useState<Record<string, string> | null>(null);
  const [version, setVersion] = useState<number | null>(null);
  const [comment, setComment] = useState("");
  const [history, setHistory] = useState<MachineConfigVersion[]>([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = () => {
    api
      .getMachineConfig()
      .then((row) => {
        setVersion(row.version);
        setValues(
          Object.fromEntries(FIELDS.map(({ key }) => [key, String(row.config[key])])),
        );
      })
      .catch((e) => setError(String(e.message)));
    api.machineConfigHistory().then(setHistory).catch(() => undefined);
  };
  useEffect(load, []);

  const save = async () => {
    if (!values) return;
    setError("");
    setNotice("");
    try {
      const config = Object.fromEntries(
        FIELDS.map(({ key }) => [key, Number(values[key])]),
      ) as unknown as MachineConfigValues;
      const row = await api.updateMachineConfig(config, comment);
      setNotice(`Saved calibration v${row.version}`);
      setComment("");
      load();
    } catch (e) {
      setError((e as Error).message);
    }
  };

  return (
    <>
      <div className="card">
        <h2>Machine calibration {version != null && <span className="muted">(v{version})</span>}</h2>
        <p className="muted">
          Every save creates a new version; generations record the calibration they used.
        </p>
        {values &&
          FIELDS.map(({ key, label }) => (
            <div className="row" key={key}>
              <label>{label}</label>
              <input
                type="number"
                step="0.001"
                value={values[key]}
                onChange={(e) => setValues((v) => ({ ...v!, [key]: e.target.value }))}
              />
            </div>
          ))}
        <div className="row">
          <label>Change note</label>
          <input
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="why this calibration changed"
            style={{ width: 320 }}
          />
        </div>
        <button className="primary" onClick={save} disabled={!values}>
          Save as new version
        </button>
        {error && <div className="error">{error}</div>}
        {notice && <div className="ok">{notice}</div>}
      </div>

      <div className="card">
        <h2>History</h2>
        <table>
          <thead>
            <tr>
              <th>v</th><th>FP45</th><th>FM45</th><th>F0</th><th>V lat</th>
              <th>Hole↔V</th><th>Shear↔V</th><th>Coil</th><th>Note</th><th>When</th>
            </tr>
          </thead>
          <tbody>
            {history.map((h) => (
              <tr key={h.version}>
                <td>{h.version}</td>
                <td>{h.config.offset_fp45}</td>
                <td>{h.config.offset_fm45}</td>
                <td>{h.config.offset_f0}</td>
                <td>{h.config.offset_v_lat}</td>
                <td>{h.config.distance_hole_vnotch}</td>
                <td>{h.config.distance_shear_vnotch}</td>
                <td>{h.config.coil_length}</td>
                <td>{h.comment}</td>
                <td>{new Date(h.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
