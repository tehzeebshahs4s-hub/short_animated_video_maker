import React, { useState, useEffect, useRef } from "react";

const API = import.meta.env.VITE_API_BASE || "";

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [draft, setDraft] = useState(false);
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const pollRef = useRef(null);

  useEffect(() => {
    if (!jobId) return;
    const poll = async () => {
      try {
        const r = await fetch(`${API}/api/jobs/${jobId}`);
        const text = await r.text();
        let j;
        try { j = JSON.parse(text); } catch (e) { setError("Backend not reachable."); return; }
        if (!r.ok) { setError(j.detail || j.error || "failed"); return; }
        setStatus(j);
        if (j.stage === "done" || j.stage === "error") {
          clearInterval(pollRef.current);
          pollRef.current = null;
          setBusy(false);
        }
      } catch (e) {
        setError(String(e));
      }
    };
    poll();
    pollRef.current = setInterval(poll, 2000);
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [jobId]);

  const submit = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    setBusy(true);
    setError(null);
    setStatus(null);
    setJobId(null);
    try {
      const r = await fetch(`${API}/api/jobs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: prompt.trim(), draft }),
      });
      const text = await r.text();
      let j;
      try { j = JSON.parse(text); } catch (e) {
        throw new Error("Backend not reachable (got HTML instead of JSON). Set up the Python app in StackCP panel or VITE_API_BASE.");
      }
      if (!r.ok) throw new Error(j.detail || j.error || "failed");
      setJobId(j.jobId);
    } catch (e) {
      setError(String(e));
      setBusy(false);
    }
  };

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: 32, fontFamily: "sans-serif" }}>
      <h1>Prompt2Video</h1>
      <p style={{ color: "#555" }}>Generate a 3-5 minute animated explainer video from a prompt.</p>
      <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={4}
          placeholder="e.g. Explain how photosynthesis works to a 10-year-old"
          style={{ padding: 12, fontSize: 16, borderRadius: 8, border: "1px solid #ccc" }}
        />
        <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <input type="checkbox" checked={draft} onChange={(e) => setDraft(e.target.checked)} />
          Draft mode (skip image generation, faster)
        </label>
        <button disabled={busy} style={{ padding: "12px 24px", fontSize: 16, borderRadius: 8, background: "#2563eb", color: "white", border: "none", cursor: busy ? "not-allowed" : "pointer" }}>
          {busy ? "Generating..." : "Generate Video"}
        </button>
      </form>

      {error && <div style={{ color: "red", marginTop: 16 }}>{error}</div>}

      {status && (
        <div style={{ marginTop: 24, padding: 16, border: "1px solid #ddd", borderRadius: 8 }}>
          <div><b>Job:</b> {status.jobId}</div>
          <div><b>Stage:</b> {status.stage}</div>
          <div style={{ margin: "8px 0" }}>
            <div style={{ background: "#eee", borderRadius: 4, overflow: "hidden", height: 12 }}>
              <div style={{ width: `${status.percent || 0}%`, background: "#2563eb", height: "100%" }} />
            </div>
            <small>{status.percent || 0}%</small>
          </div>
          <div style={{ color: "#555" }}>{status.message}</div>
          {status.error && <div style={{ color: "red" }}>{status.error}</div>}
          {status.stage === "done" && status.outputUrl && (
            <div style={{ marginTop: 16 }}>
              <video src={status.outputUrl} controls style={{ width: "100%", borderRadius: 8 }} />
              <div style={{ marginTop: 8 }}>
                <a href={status.outputUrl} download>Download MP4</a>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
