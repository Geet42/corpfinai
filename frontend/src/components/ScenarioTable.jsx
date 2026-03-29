const fmt = (v, type) => {
  if (v === null || v === undefined) return "N/A";
  if (type === "pct") return `${(v * 100).toFixed(1)}%`;
  if (type === "dollar") return `$${v.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
  if (type === "millions") {
    if (Math.abs(v) >= 1e9) return `$${(v / 1e9).toFixed(1)}B`;
    if (Math.abs(v) >= 1e6) return `$${(v / 1e6).toFixed(0)}M`;
    return `$${v.toFixed(0)}`;
  }
  return v;
};

export default function ScenarioTable({ scenarios }) {
  if (!scenarios || scenarios.length === 0) return null;

  const rows = [
    { label: "Revenue Growth", key: "revenue_growth_rate", type: "pct", from: "assumptions" },
    { label: "EBITDA Margin", key: "ebitda_margin", type: "pct", from: "assumptions" },
    { label: "Capex % Revenue", key: "capex_percent_revenue", type: "pct", from: "assumptions" },
    { label: "WACC", key: "wacc", type: "pct", from: "assumptions" },
    { label: "Terminal Growth", key: "terminal_growth_rate", type: "pct", from: "assumptions" },
    { label: "DCF Enterprise Value", key: "dcf_value", type: "millions", from: "root" },
    { label: "Implied Share Price", key: "implied_share_price", type: "dollar", from: "root" },
    { label: "EV/EBITDA Multiple", key: "ev_ebitda_multiple", type: null, from: "root" },
  ];

  const colorMap = { Base: "bg-blue-50", Upside: "bg-green-50", Downside: "bg-red-50" };

  return (
    <div className="bg-white rounded-xl shadow p-6">
      <h3 className="text-lg font-semibold text-gray-700 mb-4">
        Scenario Analysis: Base / Upside / Downside
      </h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b-2 border-gray-200">
              <th className="text-left py-3 px-4 font-semibold text-gray-600">
                Metric
              </th>
              {scenarios.map((s) => (
                <th
                  key={s.assumptions.label}
                  className={`text-center py-3 px-4 font-semibold ${
                    colorMap[s.assumptions.label] || ""
                  }`}
                >
                  {s.assumptions.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr
                key={row.key}
                className={i % 2 === 0 ? "bg-gray-50" : "bg-white"}
              >
                <td className="py-2.5 px-4 font-medium text-gray-700">
                  {row.label}
                </td>
                {scenarios.map((s) => {
                  const val =
                    row.from === "assumptions"
                      ? s.assumptions[row.key]
                      : s[row.key];
                  return (
                    <td
                      key={s.assumptions.label}
                      className={`text-center py-2.5 px-4 ${
                        colorMap[s.assumptions.label] || ""
                      }`}
                    >
                      {row.type ? fmt(val, row.type) : val?.toFixed(1)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {/* Projected Revenue by Year */}
      <div className="mt-6">
        <h4 className="text-sm font-semibold text-gray-500 mb-2">
          Projected Revenue by Year
        </h4>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 px-4 text-gray-500">Year</th>
                {scenarios.map((s) => (
                  <th key={s.assumptions.label} className="text-center py-2 px-4 text-gray-500">
                    {s.assumptions.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Object.keys(scenarios[0]?.projected_revenue || {})
                .sort()
                .map((year, i) => (
                  <tr key={year} className={i % 2 === 0 ? "bg-gray-50" : ""}>
                    <td className="py-2 px-4 font-medium">{year}</td>
                    {scenarios.map((s) => (
                      <td key={s.assumptions.label} className="text-center py-2 px-4">
                        {fmt(s.projected_revenue[year], "millions")}
                      </td>
                    ))}
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
