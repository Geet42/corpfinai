const fmtPrice = (v) =>
  v ? `$${v.toLocaleString(undefined, { maximumFractionDigits: 2 })}` : "N/A";

const fmtBillions = (v) => {
  if (!v) return "N/A";
  if (Math.abs(v) >= 1e12) return `$${(v / 1e12).toFixed(2)}T`;
  if (Math.abs(v) >= 1e9) return `$${(v / 1e9).toFixed(1)}B`;
  if (Math.abs(v) >= 1e6) return `$${(v / 1e6).toFixed(0)}M`;
  return `$${v.toFixed(0)}`;
};

export default function ValuationCard({ scenarios, currentPrice, comparables }) {
  if (!scenarios || scenarios.length === 0) return null;

  const base = scenarios.find((s) => s.assumptions.label === "Base");
  const upside = scenarios.find((s) => s.assumptions.label === "Upside");
  const downside = scenarios.find((s) => s.assumptions.label === "Downside");

  const mc = currentPrice || 0;

  return (
    <div className="bg-white rounded-xl shadow p-6">
      <h3 className="text-lg font-semibold text-gray-700 mb-4">
        Valuation Summary
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {/* Downside */}
        {downside && (
          <div className="bg-red-50 rounded-lg p-4 text-center">
            <div className="text-sm text-red-600 font-medium">Downside</div>
            <div className="text-2xl font-bold text-red-700 mt-1">
              {fmtPrice(downside.implied_share_price)}
            </div>
            <div className="text-xs text-red-500 mt-1">
              EV: {fmtBillions(downside.dcf_value)}
            </div>
          </div>
        )}
        {/* Base */}
        {base && (
          <div className="bg-blue-50 rounded-lg p-4 text-center ring-2 ring-blue-300">
            <div className="text-sm text-blue-600 font-medium">Base Case</div>
            <div className="text-2xl font-bold text-blue-700 mt-1">
              {fmtPrice(base.implied_share_price)}
            </div>
            <div className="text-xs text-blue-500 mt-1">
              EV: {fmtBillions(base.dcf_value)}
            </div>
          </div>
        )}
        {/* Upside */}
        {upside && (
          <div className="bg-green-50 rounded-lg p-4 text-center">
            <div className="text-sm text-green-600 font-medium">Upside</div>
            <div className="text-2xl font-bold text-green-700 mt-1">
              {fmtPrice(upside.implied_share_price)}
            </div>
            <div className="text-xs text-green-500 mt-1">
              EV: {fmtBillions(upside.dcf_value)}
            </div>
          </div>
        )}
      </div>

      {/* Comparables */}
      {comparables && (
        <div className="border-t pt-4 mt-2">
          <h4 className="text-sm font-semibold text-gray-500 mb-3">
            Current Market Multiples
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {comparables.ev_ebitda && (
              <div className="bg-gray-50 rounded p-3 text-center">
                <div className="text-xs text-gray-500">EV/EBITDA</div>
                <div className="text-lg font-bold text-gray-800">
                  {comparables.ev_ebitda.toFixed(1)}x
                </div>
              </div>
            )}
            {comparables.pe_ratio && (
              <div className="bg-gray-50 rounded p-3 text-center">
                <div className="text-xs text-gray-500">P/E Ratio</div>
                <div className="text-lg font-bold text-gray-800">
                  {comparables.pe_ratio.toFixed(1)}x
                </div>
              </div>
            )}
            {comparables.market_cap && (
              <div className="bg-gray-50 rounded p-3 text-center">
                <div className="text-xs text-gray-500">Market Cap</div>
                <div className="text-lg font-bold text-gray-800">
                  {fmtBillions(comparables.market_cap)}
                </div>
              </div>
            )}
            {comparables.enterprise_value && (
              <div className="bg-gray-50 rounded p-3 text-center">
                <div className="text-xs text-gray-500">Enterprise Value</div>
                <div className="text-lg font-bold text-gray-800">
                  {fmtBillions(comparables.enterprise_value)}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <p className="text-xs text-gray-400 mt-4">
        All valuations are estimates for educational purposes only. Not
        investment advice.
      </p>
    </div>
  );
}
