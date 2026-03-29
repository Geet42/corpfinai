const STEPS = [
  { key: "ingestion", label: "Data Ingestion", icon: "📥" },
  { key: "storage", label: "Database Storage", icon: "💾" },
  { key: "rag_ingest", label: "RAG Indexing", icon: "🔍" },
  { key: "financial_analysis", label: "Financial Analysis", icon: "📊" },
  { key: "monte_carlo", label: "Monte Carlo Sim", icon: "🎲" },
  { key: "ai_analysis", label: "AI Agent Analysis", icon: "🤖" },
  { key: "output_generation", label: "Output Generation", icon: "📄" },
  { key: "evaluation", label: "Quality Checks", icon: "🧪" },
];

export default function PipelineTracer({ steps }) {
  const stepMap = {};
  (steps || []).forEach((s) => {
    stepMap[s.step] = s;
  });

  return (
    <div className="bg-white rounded-xl shadow p-6 mt-6">
      <h3 className="text-lg font-semibold text-gray-700 mb-4">
        Pipeline Progress
      </h3>
      <div className="flex items-center justify-between">
        {STEPS.map((step, i) => {
          const status = stepMap[step.key]?.status || "pending";
          const isRunning = status === "running";
          const isComplete = status === "complete";
          const info = stepMap[step.key]?.data || "";

          return (
            <div key={step.key} className="flex items-center">
              <div className="flex flex-col items-center">
                <div
                  className={`w-12 h-12 rounded-full flex items-center justify-center text-xl
                    ${isComplete ? "bg-green-100 ring-2 ring-green-500" : ""}
                    ${isRunning ? "bg-blue-100 ring-2 ring-blue-500 animate-pulse-slow" : ""}
                    ${!isComplete && !isRunning ? "bg-gray-100" : ""}
                  `}
                >
                  {isComplete ? "✅" : isRunning ? "⏳" : step.icon}
                </div>
                <span className="text-xs mt-1 text-gray-500 text-center max-w-[100px]">
                  {step.label}
                </span>
                {info && (
                  <span className="text-[10px] text-gray-400 mt-0.5 text-center max-w-[120px]">
                    {info}
                  </span>
                )}
              </div>
              {i < STEPS.length - 1 && (
                <div
                  className={`w-16 h-0.5 mx-1 ${
                    isComplete ? "bg-green-400" : "bg-gray-200"
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
