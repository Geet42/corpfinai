import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  AreaChart,
  Area,
} from "recharts";

const formatMillions = (v) => {
  if (Math.abs(v) >= 1e9) return `$${(v / 1e9).toFixed(1)}B`;
  if (Math.abs(v) >= 1e6) return `$${(v / 1e6).toFixed(0)}M`;
  return `$${v.toFixed(0)}`;
};

const formatPercent = (v) => `${(v * 100).toFixed(1)}%`;

export default function FinancialDashboard({ ratios, priceHistory }) {
  if (!ratios) return null;

  const periods = Object.keys(ratios).sort();

  const revenueData = periods.map((p) => ({
    period: p,
    Revenue: ratios[p]?.revenue || 0,
    EBITDA: ratios[p]?.ebitda || 0,
    "Net Income": ratios[p]?.net_income || 0,
  }));

  const marginData = periods.map((p) => ({
    period: p,
    "Gross Margin": ratios[p]?.gross_margin || 0,
    "EBITDA Margin": ratios[p]?.ebitda_margin || 0,
    "Net Margin": ratios[p]?.net_margin || 0,
    "FCF Margin": ratios[p]?.fcf_margin || 0,
  }));

  // Downsample price history to ~100 points
  const priceData = [];
  if (priceHistory?.dates?.length) {
    const step = Math.max(1, Math.floor(priceHistory.dates.length / 100));
    for (let i = 0; i < priceHistory.dates.length; i += step) {
      priceData.push({
        date: priceHistory.dates[i],
        price: priceHistory.close[i],
      });
    }
  }

  return (
    <div className="space-y-6">
      {/* Revenue / EBITDA / Net Income */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-700 mb-4">
          Revenue, EBITDA & Net Income
        </h3>
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={revenueData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="period" />
            <YAxis tickFormatter={formatMillions} />
            <Tooltip formatter={(v) => formatMillions(v)} />
            <Legend />
            <Bar dataKey="Revenue" fill="#1e3a5f" radius={[4, 4, 0, 0]} />
            <Bar dataKey="EBITDA" fill="#2c5f8a" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Net Income" fill="#60a5fa" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Margin Trends */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold text-gray-700 mb-4">
          Margin Trends
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={marginData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="period" />
            <YAxis tickFormatter={formatPercent} />
            <Tooltip formatter={(v) => formatPercent(v)} />
            <Legend />
            <Line type="monotone" dataKey="Gross Margin" stroke="#16a34a" strokeWidth={2} dot />
            <Line type="monotone" dataKey="EBITDA Margin" stroke="#2563eb" strokeWidth={2} dot />
            <Line type="monotone" dataKey="Net Margin" stroke="#7c3aed" strokeWidth={2} dot />
            <Line type="monotone" dataKey="FCF Margin" stroke="#ea580c" strokeWidth={2} dot />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Stock Price */}
      {priceData.length > 0 && (
        <div className="bg-white rounded-xl shadow p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">
            Stock Price (5Y)
          </h3>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={priceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
              <YAxis tickFormatter={(v) => `$${v.toFixed(0)}`} />
              <Tooltip formatter={(v) => `$${v.toFixed(2)}`} />
              <Area
                type="monotone"
                dataKey="price"
                stroke="#1e3a5f"
                fill="#dbeafe"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
