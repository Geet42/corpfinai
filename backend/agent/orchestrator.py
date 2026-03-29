from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent
from agent.tools.data_retriever import retrieve_company_data, retrieve_financial_statements
from agent.tools.calculator import run_scenario_analysis, run_sensitivity
from agent.tools.chart_tool import get_chart_data
from agent.tools.rag_search import search_10k_filing
from config import settings
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class CorpFinAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=settings.OPENAI_API_KEY,
        )
        self.tools = [
            retrieve_company_data,
            retrieve_financial_statements,
            run_scenario_analysis,
            run_sensitivity,
            get_chart_data,
            search_10k_filing,
        ]
        
        self.agent = create_react_agent(self.llm, self.tools)

    def analyze(self, ticker: str, query: str = None) -> Dict:
        """Run the agent and return results with full traces."""
        if not query:
            query = (
                f"Analyze {ticker}:\n"
                "1. Get company profile and financial data\n"
                "2. Search 10-K for risk factors\n"
                "3. Provide a brief investment summary"
            )

        try:
            result = self.agent.invoke({"messages": [("user", query)]})
            
            # Extract traces from messages
            traces = []
            for msg in result.get("messages", []):
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tc in msg.tool_calls:
                        traces.append({
                            "thought": "Tool call",
                            "tool": tc.get("name", "unknown"),
                            "tool_input": str(tc.get("args", {})),
                            "observation": "",
                        })
                elif hasattr(msg, 'content') and hasattr(msg, 'name'):
                    # Tool response
                    if traces:
                        traces[-1]["observation"] = str(msg.content)[:2000]
            
            # Get final response
            final_msg = result["messages"][-1] if result.get("messages") else None
            analysis = final_msg.content if final_msg and hasattr(final_msg, 'content') else "Analysis complete."

            return {
                "analysis": analysis,
                "traces": traces,
                "steps_taken": len(traces),
            }
        except Exception as e:
            logger.error(f"Agent failed for {ticker}: {e}", exc_info=True)
            return {
                "analysis": (
                    f"Agent analysis encountered an error: {str(e)}. "
                    "The deterministic financial model results above are still valid."
                ),
                "traces": [{"thought": "Error occurred", "tool": "none",
                            "tool_input": "", "observation": str(e)}],
                "steps_taken": 0,
            }
