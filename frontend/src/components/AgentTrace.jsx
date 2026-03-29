import { useState } from "react";

function TraceStep({ trace, index }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-3 bg-gray-50
                   hover:bg-gray-100 transition-colors text-left"
      >
        <div className="flex items-center gap-3">
          <span className="bg-slate-700 text-white text-xs font-mono px-2 py-1 rounded">
            Step {index + 1}
          </span>
          <span className="text-sm font-medium text-gray-700">
            🔧 {trace.tool}
          </span>
        </div>
        <svg
          className={`w-4 h-4 text-gray-400 transition-transform ${
            open ? "rotate-180" : ""
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && (
        <div className="px-4 py-3 space-y-3 text-sm bg-white">
          {trace.thought && (
            <div>
              <span className="font-semibold text-purple-600">
                💭 Thought:
              </span>
              <pre className="mt-1 text-xs bg-purple-50 p-2 rounded whitespace-pre-wrap text-purple-800 max-h-40 overflow-y-auto">
                {trace.thought}
              </pre>
            </div>
          )}
          <div>
            <span className="font-semibold text-blue-600">
              ⚡ Action Input:
            </span>
            <pre className="mt-1 text-xs bg-blue-50 p-2 rounded whitespace-pre-wrap text-blue-800 max-h-40 overflow-y-auto">
              {trace.tool_input}
            </pre>
          </div>
          <div>
            <span className="font-semibold text-green-600">
              👁️ Observation:
            </span>
            <pre className="mt-1 text-xs bg-green-50 p-2 rounded whitespace-pre-wrap text-green-800 max-h-60 overflow-y-auto">
              {trace.observation}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

export default function AgentTrace({ traces }) {
  const [expanded, setExpanded] = useState(false);

  if (!traces || traces.length === 0) return null;

  return (
    <div className="bg-white rounded-xl shadow p-6">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between w-full"
      >
        <h3 className="text-lg font-semibold text-gray-700">
          🤖 Agent Reasoning Trace ({traces.length} steps)
        </h3>
        <span className="text-sm text-blue-500 hover:text-blue-700">
          {expanded ? "Collapse" : "Expand All"}
        </span>
      </button>
      <p className="text-xs text-gray-400 mt-1 mb-4">
        Observable AI reasoning: each step shows the agent's Thought, Action,
        and Observation
      </p>
      {expanded && (
        <div className="space-y-2">
          {traces.map((trace, i) => (
            <TraceStep key={i} trace={trace} index={i} />
          ))}
        </div>
      )}
    </div>
  );
}
