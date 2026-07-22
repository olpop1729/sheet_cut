import { useEffect, useState } from "react";
import { api } from "../api";
import { ProfileSchematic } from "../components/ProfileSchematic";
import {
  OPEN_CODES,
  PATTERN_NAMES,
  STEPLAP_TYPES,
  TOOL_NAMES,
  type Profile,
  type ToolSpec,
} from "../types";

const blankTool = (): ToolSpec => ({
  name: "fp45",
  steplap_type: 0,
  steplap_count: 1,
  open_code: 0,
  is_skewed: false,
});

export function ProfilesPage() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [editing, setEditing] = useState<number | null>(null); // profile id or null=new
  const [name, setName] = useState("");
  const [tools, setTools] = useState<ToolSpec[]>([blankTool()]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const refresh = () => {
    api.listProfiles().then(setProfiles).catch((e) => setError(String(e.message)));
  };
  useEffect(refresh, []);

  const loadForEdit = (p: Profile) => {
    setEditing(p.id);
    setName(p.name);
    setTools(p.tools.map((t) => ({ ...t })));
    setError("");
    setNotice("");
  };

  const reset = () => {
    setEditing(null);
    setName("");
    setTools([blankTool()]);
    setError("");
    setNotice("");
  };

  const setTool = (i: number, patch: Partial<ToolSpec>) => {
    setTools((ts) => ts.map((t, j) => (j === i ? { ...t, ...patch } : t)));
  };

  const save = async () => {
    setError("");
    setNotice("");
    try {
      const saved = editing
        ? await api.updateProfile(editing, name, tools)
        : await api.createProfile(name, tools);
      setNotice(
        `Saved "${saved.name}" (${PATTERN_NAMES[saved.pattern_type] ?? saved.pattern_type})`,
      );
      setEditing(saved.id);
      refresh();
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const remove = async (id: number) => {
    setError("");
    try {
      await api.deleteProfile(id);
      if (editing === id) reset();
      refresh();
    } catch (e) {
      setError((e as Error).message);
    }
  };

  return (
    <>
      <div className="card">
        <h2>Profiles</h2>
        {profiles.length === 0 ? (
          <p className="muted">No profiles yet — create one below.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th><th>Name</th><th>Pattern</th><th>Tools</th><th>Step-lap tools</th><th></th>
              </tr>
            </thead>
            <tbody>
              {profiles.map((p) => (
                <tr key={p.id} className={`clickable ${editing === p.id ? "selected" : ""}`}>
                  <td onClick={() => loadForEdit(p)}>{p.id}</td>
                  <td onClick={() => loadForEdit(p)}>{p.name}</td>
                  <td onClick={() => loadForEdit(p)}>{PATTERN_NAMES[p.pattern_type] ?? p.pattern_type}</td>
                  <td onClick={() => loadForEdit(p)}>{p.tools.map((t) => t.name).join(" → ")}</td>
                  <td onClick={() => loadForEdit(p)}>{p.steplap_tool_count}</td>
                  <td>
                    <button className="ghost danger" onClick={() => remove(p.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="card">
        <h2>{editing ? `Edit profile #${editing}` : "New profile"}</h2>
        <div className="row">
          <label>Name</label>
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. yoke-660kV" />
          {editing && <button className="ghost" onClick={reset}>New instead</button>}
        </div>
        <div className="toolgrid">
          <table>
            <thead>
              <tr>
                <th>#</th><th>Tool</th><th>Step-lap type</th><th>Count</th><th>Open/close</th><th>Skewed</th><th></th>
              </tr>
            </thead>
            <tbody>
              {tools.map((t, i) => (
                <tr key={i}>
                  <td>{i + 1}</td>
                  <td>
                    <select value={t.name} onChange={(e) => setTool(i, { name: e.target.value })}>
                      {TOOL_NAMES.map((n) => <option key={n} value={n}>{n}</option>)}
                    </select>
                  </td>
                  <td>
                    <select
                      value={t.steplap_type}
                      onChange={(e) => setTool(i, { steplap_type: Number(e.target.value) })}
                    >
                      {Object.entries(STEPLAP_TYPES).map(([v, label]) => (
                        <option key={v} value={v}>{label}</option>
                      ))}
                    </select>
                  </td>
                  <td>
                    <input
                      type="number" min={1} value={t.steplap_count}
                      onChange={(e) => setTool(i, { steplap_count: Number(e.target.value) })}
                      style={{ width: 70 }}
                    />
                  </td>
                  <td>
                    <select
                      value={t.open_code}
                      onChange={(e) => setTool(i, { open_code: Number(e.target.value) })}
                    >
                      {Object.entries(OPEN_CODES).map(([v, label]) => (
                        <option key={v} value={v}>{label}</option>
                      ))}
                    </select>
                  </td>
                  <td>
                    <input
                      type="checkbox"
                      checked={t.is_skewed}
                      disabled={!(t.name === "s" && t.steplap_type === 2)}
                      onChange={(e) => setTool(i, { is_skewed: e.target.checked })}
                    />
                  </td>
                  <td>
                    <button
                      className="ghost danger"
                      disabled={tools.length === 1}
                      onClick={() => setTools((ts) => ts.filter((_, j) => j !== i))}
                    >
                      ✕
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="row" style={{ marginTop: 10 }}>
          <button className="ghost" onClick={() => setTools((ts) => [...ts, blankTool()])}>
            + Add tool
          </button>
          <button className="primary" onClick={save} disabled={!name.trim()}>
            {editing ? "Save changes" : "Create profile"}
          </button>
        </div>
        {error && <div className="error">{error}</div>}
        {notice && <div className="ok">{notice}</div>}

        <h3>Schematic</h3>
        <ProfileSchematic tools={tools} />
      </div>
    </>
  );
}
