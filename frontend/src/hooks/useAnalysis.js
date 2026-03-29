import { useState, useCallback, useRef } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function useAnalysis() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pipelineLog, setPipelineLog] = useState([]);
  const eventSourceRef = useRef(null);

  const runAnalysis = useCallback((ticker) => {
    // Close any existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    setLoading(true);
    setError(null);
    setData(null);
    setPipelineLog([]);

    const url = `${API_BASE}/api/analyze/${ticker.toUpperCase()}/stream`;
    const es = new EventSource(url);
    eventSourceRef.current = es;

    es.addEventListener("step", (e) => {
      const step = JSON.parse(e.data);
      setPipelineLog((prev) => {
        // Update existing step or add new
        const existing = prev.findIndex((s) => s.step === step.step);
        if (existing >= 0 && step.status === "complete") {
          const updated = [...prev];
          updated[existing] = step;
          return updated;
        }
        if (existing >= 0) return prev;
        return [...prev, step];
      });
    });

    es.addEventListener("complete", (e) => {
      const result = JSON.parse(e.data);
      setData(result);
      setLoading(false);
      es.close();
    });

    es.addEventListener("error", (e) => {
      // SSE error event
      if (e.data) {
        try {
          const err = JSON.parse(e.data);
          setError(err.message || "Pipeline failed");
        } catch {
          setError("Pipeline failed. Check backend logs.");
        }
      } else {
        // Connection error - fallback to POST endpoint
        es.close();
        console.warn("SSE connection failed, falling back to POST");
        fallbackAnalysis(ticker.toUpperCase());
        return;
      }
      setLoading(false);
      es.close();
    });

    // Timeout safety - if no complete event in 5 minutes
    setTimeout(() => {
      if (es.readyState !== EventSource.CLOSED) {
        es.close();
        if (!data) {
          fallbackAnalysis(ticker.toUpperCase());
        }
      }
    }, 300000);
  }, []);

  const fallbackAnalysis = async (ticker) => {
    try {
      setPipelineLog([{ step: "ingestion", status: "running" }]);
      const res = await fetch(`${API_BASE}/api/analyze/${ticker}`, {
        method: "POST",
      });
      const result = await res.json();
      if (!res.ok) throw new Error(result.detail || "Analysis failed");
      setData(result);
      setPipelineLog(result.pipeline_log || []);
    } catch (err) {
      setError(err.message || "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, pipelineLog, runAnalysis };
}
