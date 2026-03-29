export default function SensitivityHeatmap({ cells }) {
  if (!cells || cells.length === 0) return null;

  // Build matrix from flat list
  const waccValues = [...new Set(cells.map((c) => c.wacc))].sort();
  const growthValues = [...new Set(cells.map((c) => c.terminal_growth))].sort();

  const cellMap = {};
  cells.forEach((c) => {
    cellMap[`${c.wacc}-${c.terminal_growth}`] = c.implied_price;
  });

  // Find min/max for color scaling
  const validPrices = cells
    .map((c) => c.implied_price)
    .filter((p) => p > 0);
  const minPrice = Math.min(...validPrices);
  const maxPrice = Math.max(...validPrices);

  const getColor = (price) => {
    if (price <= 0) return "bg-gray-200 text-gray-400";
    const ratio = (price - minPrice) / (maxPrice - minPrice || 1);
    if (ratio > 0.75) return "bg-green-200 text-green-900";
    if (ratio > 0.5) return "bg-green-100 text-green-800";
    if (ratio > 0.25) return "bg-yellow-100 text-yellow-800";
    return "bg-red-100 text-red-800";
  };

  return (
    <div className="bg-white rounded-xl shadow p-6">
      <h3 className="text-lg font-semibold text-gray-700 mb-2">
        Sensitivity Analysis: WACC vs Terminal Growth
      </h3>
      <p className="text-sm text-gray-400 mb-4">
        Implied share price at different WACC and terminal growth rate
        combinations
      </p>
      <div className="overflow-x-auto">
        <table className="text-sm w-full">
          <thead>
            <tr>
              <th className="py-2 px-3 text-left text-gray-500 font-medium">
                WACC \ Growth
              </th>
              {growthValues.map((g) => (
                <th key={g} className="py-2 px-3 text-center text-gray-500 font-medium">
                  {(g * 100).toFixed(1)}%
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {waccValues.map((w) => (
              <tr key={w}>
                <td className="py-2 px-3 font-medium text-gray-600">
                  {(w * 100).toFixed(0)}%
                </td>
                {growthValues.map((g) => {
                  const price = cellMap[`${w}-${g}`] || 0;
                  return (
                    <td
                      key={g}
                      className={`py-2 px-3 text-center font-mono text-sm rounded ${getColor(
                        price
                      )}`}
                    >
                      {price > 0 ? `$${price.toLocaleString()}` : "N/A"}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
