import TickerInput from "./components/TickerInput";
import PipelineTracer from "./components/PipelineTracer";
import FinancialDashboard from "./components/FinancialDashboard";
import ScenarioTable from "./components/ScenarioTable";
import SensitivityHeatmap from "./components/SensitivityHeatmap";
import ValuationCard from "./components/ValuationCard";
import MonteCarloChart from "./components/MonteCarloChart";
import QualityChecks from "./components/QualityChecks";
import AdvisoryPanel from "./components/AdvisoryPanel";
import AgentTrace from "./components/AgentTrace";
import ExportButtons from "./components/ExportButtons";
import useAnalysis from "./hooks/useAnalysis";

export default function App() {
  const { data, loading, error, pipelineLog, runAnalysis } = useAnalysis();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-slate-900 text-white py-6 px-8">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              📊 CorpFinAI
            </h1>
            <p className="text-slate-400 mt-1">
              Corporate Finance Autopilot | Agentic Financial Analysis Pipeline
            </p>
          </div>
          <span className="text-xs text-slate-500 bg-slate-800 px-3 py-1 rounded-full">
            Hackathon Project | Not Investment Advice
          </span>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Ticker Input */}
        <TickerInput onSubmit={runAnalysis} loading={loading} />

        {/* Pipeline Progress (SSE live updates) */}
        {(loading || pipelineLog.length > 0) && (
          <PipelineTracer steps={pipelineLog} />
        )}

        {/* Error */}
        {error && (
          <div className="mt-6 bg-red-50 border border-red-200 rounded-xl p-4">
            <p className="text-red-700 font-medium">Analysis Failed</p>
            <p className="text-red-600 text-sm mt-1">{error}</p>
          </div>
        )}

        {/* Results */}
        {data && (
          <div className="space-y-6 mt-8">
            {/* Company Header */}
            <div className="bg-white rounded-xl shadow p-6">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    {data.company.name} ({data.ticker})
                  </h2>
                  <p className="text-gray-500 mt-1">
                    {data.company.sector} | {data.company.industry} |{" "}
                    {data.company.country}
                  </p>
                </div>
                {data.company.market_cap && (
                  <div className="text-right">
                    <div className="text-sm text-gray-500">Market Cap</div>
                    <div className="text-xl font-bold text-gray-800">
                      ${(data.company.market_cap / 1e9).toFixed(1)}B
                    </div>
                  </div>
                )}
              </div>
              <p className="mt-3 text-sm text-gray-600 leading-relaxed">
                {data.company.description?.slice(0, 400)}
                {data.company.description?.length > 400 ? "..." : ""}
              </p>
            </div>

            {/* Financial Dashboard - Charts */}
            <FinancialDashboard
              ratios={data.ratios}
              priceHistory={data.price_history}
            />

            {/* Valuation Summary */}
            <ValuationCard
              scenarios={data.scenarios}
              currentPrice={data.company.market_cap}
              comparables={data.comparables}
            />

            {/* Scenario Analysis */}
            <ScenarioTable scenarios={data.scenarios} />

            {/* Sensitivity Heatmap */}
            <SensitivityHeatmap cells={data.sensitivity} />

            {/* Monte Carlo Simulation */}
            <MonteCarloChart monteCarlo={data.monte_carlo} />

            {/* Quality Evaluation */}
            <QualityChecks checks={data.quality_checks} />

            {/* Strategic Advisory + Agent Analysis */}
            <AdvisoryPanel
              analysis={data.agent_analysis}
              advisory={data.advisory}
            />

            {/* Agent Reasoning Trace */}
            <AgentTrace traces={data.agent_traces} />

            {/* Export (PPTX + PDF) */}
            <ExportButtons ticker={data.ticker} />
          </div>
        )}
      </main>

      <footer className="text-center py-6 text-sm text-gray-400 border-t">
        CorpFinAI | Built for Assiduous Hackathon 2026 | Not Investment Advice
      </footer>
    </div>
  );
}
