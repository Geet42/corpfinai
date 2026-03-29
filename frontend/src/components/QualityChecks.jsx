import { useState } from "react";

export default function QualityChecks({ checks }) {
  const [expanded, setExpanded] = useState(false);

  if (!checks || checks.length === 0) return null;

  const passed = checks.filter((c) => c.passed).length;
  const total = checks.length;
  const allPassed = passed === total;

  return (
    <div className="bg-white rounded-xl shadow p-6">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between w-full"
      >
        <h3 className="text-lg font-semibold text-gray-700">
          🧪 Quality Evaluation ({passed}/{total} passed)
        </h3>
        <div className="flex items-center gap-2">
          <span
            className={`text-sm font-medium px-3 py-1 rounded-full ${
              allPassed
                ? "bg-green-100 text-green-700"
                : "bg-yellow-100 text-yellow-700"
            }`}
          >
            {allPassed ? "All Checks Passed" : `${total - passed} Issues`}
          </span>
          <span className="text-sm text-blue-500">
            {expanded ? "Collapse" : "Expand"}
          </span>
        </div>
      </button>

      {expanded && (
        <div className="mt-4 space-y-2">
          {checks.map((check, i) => (
            <div
              key={i}
              className={`flex items-start gap-3 p-3 rounded-lg ${
                check.passed
                  ? "bg-green-50"
                  : check.severity === "critical"
                  ? "bg-red-50"
                  : "bg-yellow-50"
              }`}
            >
              <span className="text-lg flex-shrink-0">{check.icon}</span>
              <div>
                <div className="font-medium text-sm text-gray-800">
                  {check.name}
                </div>
                <div className="text-xs text-gray-600 mt-0.5">
                  {check.detail}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <p className="text-xs text-gray-400 mt-3">
        Automated sanity checks on data completeness, ratio bounds, DCF model
        validity, scenario ordering, and cross-validation against market cap.
      </p>
    </div>
  );
}
