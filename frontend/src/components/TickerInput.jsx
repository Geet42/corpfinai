import { useState } from "react";

export default function TickerInput({ onSubmit, loading }) {
  const [ticker, setTicker] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (ticker.trim()) {
      onSubmit(ticker.trim().toUpperCase());
    }
  };

  const quickTickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA"];

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <form onSubmit={handleSubmit} className="flex gap-3">
        <input
          type="text"
          value={ticker}
          onChange={(e) => setTicker(e.target.value.toUpperCase())}
          placeholder="Enter ticker symbol (e.g., AAPL)"
          className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-lg text-lg font-mono
                     focus:border-blue-500 focus:outline-none transition-colors"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !ticker.trim()}
          className="px-8 py-3 bg-slate-900 text-white rounded-lg font-semibold text-lg
                     hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed
                     transition-colors"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Analyzing...
            </span>
          ) : (
            "Analyze"
          )}
        </button>
      </form>
      <div className="flex gap-2 mt-3">
        <span className="text-sm text-gray-400">Quick:</span>
        {quickTickers.map((t) => (
          <button
            key={t}
            onClick={() => {
              setTicker(t);
              onSubmit(t);
            }}
            disabled={loading}
            className="px-3 py-1 text-sm bg-gray-100 text-gray-600 rounded-full
                       hover:bg-blue-50 hover:text-blue-600 disabled:opacity-50
                       transition-colors"
          >
            {t}
          </button>
        ))}
      </div>
    </div>
  );
}
