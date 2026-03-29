import { getExportUrl } from "../utils/api";

export default function ExportButtons({ ticker }) {
  if (!ticker) return null;

  const handleDownload = (format) => {
    window.open(getExportUrl(ticker, format), "_blank");
  };

  return (
    <div className="bg-white rounded-xl shadow p-6">
      <h3 className="text-lg font-semibold text-gray-700 mb-4">
        📥 Export Reports
      </h3>
      <div className="flex gap-4">
        <button
          onClick={() => handleDownload("pptx")}
          className="flex items-center gap-2 px-6 py-3 bg-orange-500 text-white rounded-lg
                     font-medium hover:bg-orange-600 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Download PPTX
        </button>
        <button
          onClick={() => handleDownload("pdf")}
          className="flex items-center gap-2 px-6 py-3 bg-red-600 text-white rounded-lg
                     font-medium hover:bg-red-700 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Download PDF Memo
        </button>
      </div>
      <p className="text-xs text-gray-400 mt-3">
        Presentation includes company overview, financial summary, scenario
        analysis, strategic advisory, and disclaimer.
      </p>
    </div>
  );
}
