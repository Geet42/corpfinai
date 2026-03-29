export default function AdvisoryPanel({ analysis, advisory }) {
  const text = advisory || analysis;
  if (!text) return null;

  // Parse inline markdown (bold, italic)
  const parseInline = (str) => {
    // Replace **text** with bold
    const parts = [];
    let remaining = str;
    let key = 0;
    
    while (remaining) {
      const boldMatch = remaining.match(/\*\*(.+?)\*\*/);
      if (boldMatch) {
        const idx = boldMatch.index;
        if (idx > 0) parts.push(remaining.slice(0, idx));
        parts.push(<strong key={key++} className="font-semibold text-slate-800">{boldMatch[1]}</strong>);
        remaining = remaining.slice(idx + boldMatch[0].length);
      } else {
        parts.push(remaining);
        break;
      }
    }
    return parts.length > 0 ? parts : str;
  };

  // Split into lines and parse
  const lines = text.split("\n");
  const elements = [];
  let listItems = [];
  
  const flushList = () => {
    if (listItems.length > 0) {
      elements.push(
        <ul key={elements.length} className="list-disc list-inside mb-3 space-y-1 ml-2">
          {listItems}
        </ul>
      );
      listItems = [];
    }
  };

  lines.forEach((line, i) => {
    const trimmed = line.trim();
    if (!trimmed) {
      flushList();
      return;
    }

    // Headings (#### > ### > ## > #)
    if (trimmed.startsWith("#### ")) {
      flushList();
      elements.push(
        <h5 key={i} className="font-semibold text-slate-700 mt-3 mb-2 text-sm">
          {parseInline(trimmed.slice(5))}
        </h5>
      );
    } else if (trimmed.startsWith("### ")) {
      flushList();
      elements.push(
        <h4 key={i} className="font-semibold text-slate-800 mt-4 mb-2">
          {parseInline(trimmed.slice(4))}
        </h4>
      );
    } else if (trimmed.startsWith("## ")) {
      flushList();
      elements.push(
        <h3 key={i} className="font-bold text-slate-800 mt-4 mb-2 text-base">
          {parseInline(trimmed.slice(3))}
        </h3>
      );
    } else if (trimmed.startsWith("# ")) {
      flushList();
      elements.push(
        <h2 key={i} className="font-bold text-slate-800 mt-4 mb-2 text-lg">
          {parseInline(trimmed.slice(2))}
        </h2>
      );
    }
    // Bullet points
    else if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      listItems.push(
        <li key={i} className="text-gray-700">{parseInline(trimmed.slice(2))}</li>
      );
    }
    // Numbered lists
    else if (/^\d+\.\s/.test(trimmed)) {
      listItems.push(
        <li key={i} className="text-gray-700">{parseInline(trimmed.replace(/^\d+\.\s/, ""))}</li>
      );
    }
    // Regular paragraph
    else {
      flushList();
      elements.push(
        <p key={i} className="mb-2 leading-relaxed">{parseInline(trimmed)}</p>
      );
    }
  });
  
  flushList();

  return (
    <div className="bg-white rounded-xl shadow p-6">
      <h3 className="text-lg font-semibold text-gray-700 mb-4">
        🏛️ Strategic Advisory & AI Analysis
      </h3>
      <div className="prose prose-sm max-w-none text-gray-700">
        {elements}
      </div>
      <div className="mt-4 p-3 bg-amber-50 rounded-lg border border-amber-200">
        <p className="text-xs text-amber-700">
          <strong>Disclaimer:</strong> This analysis is generated for educational
          purposes only by CorpFinAI. It does not constitute investment advice.
          All projections are estimates based on publicly available data and stated
          assumptions.
        </p>
      </div>
    </div>
  );
}
