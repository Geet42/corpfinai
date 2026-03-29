import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

export default function MonteCarloChart({ monteCarlo }) {
  if (!monteCarlo || monteCarlo.error || !monteCarlo.histogram) return null;

  const {
    n_simulations,
    mean_price,
    median_price,
    std_dev,
    percentile_5,
    percentile_25,
    percentile_75,
    percentile_95,
    min_price,
    max_price,
    histogram,
  } = monteCarlo;

  return (
    <div className="bg-white rounded-xl shadow p-6">
      <h3 className="text-lg font-semibold text-gray-700 mb-2">
        🎲 Monte Carlo Simulation ({n_simulations.toLocaleString()} runs)
      </h3>
      <p className="text-sm text-gray-400 mb-4">
        Probability distribution of implied share prices with randomized
        assumptions (growth, margins, WACC, terminal growth)
      </p>

      {/* Stats cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
        <div className="bg-red-50 rounded-lg p-3 text-center">
          <div className="text-xs text-red-500">5th Percentile</div>
          <div className="text-lg font-bold text-red-700">
            ${percentile_5.toLocaleString()}
          </div>
        </div>
        <div className="bg-orange-50 rounded-lg p-3 text-center">
          <div className="text-xs text-orange-500">25th Percentile</div>
          <div className="text-lg font-bold text-orange-700">
            ${percentile_25.toLocaleString()}
          </div>
        </div>
        <div className="bg-blue-50 rounded-lg p-3 text-center ring-2 ring-blue-300">
          <div className="text-xs text-blue-500">Median</div>
          <div className="text-lg font-bold text-blue-700">
            ${median_price.toLocaleString()}
          </div>
        </div>
        <div className="bg-green-50 rounded-lg p-3 text-center">
          <div className="text-xs text-green-500">75th Percentile</div>
          <div className="text-lg font-bold text-green-700">
            ${percentile_75.toLocaleString()}
          </div>
        </div>
        <div className="bg-emerald-50 rounded-lg p-3 text-center">
          <div className="text-xs text-emerald-500">95th Percentile</div>
          <div className="text-lg font-bold text-emerald-700">
            ${percentile_95.toLocaleString()}
          </div>
        </div>
      </div>

      {/* Histogram */}
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={histogram}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 9 }}
            interval={Math.floor(histogram.length / 8)}
          />
          <YAxis label={{ value: "Frequency", angle: -90, position: "insideLeft", fontSize: 12 }} />
          <Tooltip
            formatter={(v) => [`${v} simulations`, "Count"]}
            labelFormatter={(l) => `Price Range: ${l}`}
          />
          <Bar dataKey="count" fill="#3b82f6" radius={[2, 2, 0, 0]} />
          <ReferenceLine
            x={histogram.find(
              (h) => h.bin_start <= mean_price && h.bin_end >= mean_price
            )?.label}
            stroke="#ef4444"
            strokeWidth={2}
            strokeDasharray="5 5"
            label={{ value: "Mean", position: "top", fill: "#ef4444", fontSize: 11 }}
          />
        </BarChart>
      </ResponsiveContainer>

      {/* Summary stats */}
      <div className="mt-4 flex flex-wrap gap-4 text-sm text-gray-500">
        <span>Mean: <strong>${mean_price.toLocaleString()}</strong></span>
        <span>Std Dev: <strong>${std_dev.toLocaleString()}</strong></span>
        <span>Range: <strong>${min_price.toLocaleString()} - ${max_price.toLocaleString()}</strong></span>
      </div>
    </div>
  );
}
