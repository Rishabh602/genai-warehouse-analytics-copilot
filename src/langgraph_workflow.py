# Import typing tools for defining the shared workflow state
from typing import TypedDict, Optional, List, Dict, Any

# Import LangGraph workflow components
from langgraph.graph import StateGraph, END

# Import LangGraph memory checkpointing
from langgraph.checkpoint.memory import MemorySaver

# Import the unified tool runner created in tool_engine.py
from tool_engine import run_tool

# Import RAG context retrieval
from rag_engine import retrieve_context

# Import executive summary generator
from summary_engine import generate_executive_summary


# Define the shared state passed between workflow nodes
class WorkflowState(TypedDict, total=False):
    user_question: str
    intent: str
    kpi: Optional[str]
    kpis: List[str]
    group_by: Optional[str]
    entity: Optional[str]
    selected_values: List[str]
    ranking_type: Optional[str]
    n: Optional[int]
    needs_rag: bool
    tool_result: Any
    benchmark_result: Any
    recommendation_result: Any
    rag_context: Optional[str]
    summary_result: Optional[str]
    final_answer: Optional[str]
    chat_history: List[Dict[str, str]]


# Prepare state before routing
def prepare_request(state: WorkflowState) -> WorkflowState:
    # Convert single KPI into KPI list for downstream engines
    if state.get("kpi") and not state.get("kpis"):
        state["kpis"] = [state["kpi"]]

    # Ensure selected_values exists as a list
    if "selected_values" not in state or state["selected_values"] is None:
        state["selected_values"] = []

    # Ensure chat history exists for memory-aware conversations
    if "chat_history" not in state or state["chat_history"] is None:
        state["chat_history"] = []

    # Return prepared state
    return state


# Decide which workflow path should run
def route_by_intent(state: WorkflowState) -> str:
    # Read intent extracted earlier by prompting / structured output layer
    intent = state.get("intent", "unknown")

    # Route ranking questions to KPI ranking tool
    if intent == "ranking":
        return "ranking"

    # Route comparison questions to KPI comparison tool
    if intent == "comparison":
        return "comparison"

    # Route benchmark questions to benchmark tool
    if intent == "benchmark_check":
        return "benchmark"

    # Route recommendation questions to recommendation tool
    if intent == "recommendation":
        return "recommendation"

    # Route investigation questions to multi-step investigation flow
    if intent == "investigation":
        return "investigation"

    # Route SOP questions directly to RAG
    if intent == "sop_question":
        return "rag"

    # Route executive summary questions to summary engine
    if intent == "executive_summary":
        return "summary"

    # Fallback route for unclear questions
    return "unknown"


# Run KPI ranking workflow
def run_ranking_node(state: WorkflowState) -> WorkflowState:
    # Pick top or bottom ranking based on user intent extraction
    if state.get("ranking_type") == "bottom":
        result = run_tool(
            "bottom_performers",
            kpi=state["kpi"],
            group_by=state["group_by"],
            n=state["n"]
        )
    else:
        result = run_tool(
            "top_performers",
            kpi=state["kpi"],
            group_by=state["group_by"],
            n=state["n"]
        )

    # Store tool result in workflow state
    state["tool_result"] = result

    # Return updated state
    return state


# Run KPI comparison workflow
def run_comparison_node(state: WorkflowState) -> WorkflowState:
    # Compare selected entities across selected KPIs
    result = run_tool(
        "compare_performance",
        group_by=state["group_by"],
        selected_values=state["selected_values"],
        kpis=state["kpis"]
    )

    # Store comparison result
    state["tool_result"] = result

    # Return updated state
    return state


# Run benchmark workflow
def run_benchmark_node(state: WorkflowState) -> WorkflowState:
    # Benchmark selected KPI at selected hierarchy level
    result = run_tool(
        "benchmark_summary",
        group_by=state["group_by"],
        kpi=state["kpi"]
    )

    # Store benchmark result
    state["benchmark_result"] = result

    # Return updated state
    return state


# Run recommendation workflow
def run_recommendation_node(state: WorkflowState) -> WorkflowState:
    # Generate recommendations from detected anomalies
    result = run_tool(
        "priority_recommendations",
        group_by=state["group_by"],
        kpis=state["kpis"]
    )

    # Store recommendation result
    state["recommendation_result"] = result

    # Return updated state
    return state


# Run investigation workflow
def run_investigation_node(state: WorkflowState) -> WorkflowState:
    # Generate benchmark result for the first selected KPI if available
    if state.get("kpi"):
        state["benchmark_result"] = run_tool(
            "benchmark_summary",
            group_by=state["group_by"],
            kpi=state["kpi"]
        )

    # Generate recommendations across selected KPIs
    state["recommendation_result"] = run_tool(
        "priority_recommendations",
        group_by=state["group_by"],
        kpis=state["kpis"]
    )

    # Return updated state
    return state


# Run RAG workflow
def run_rag_node(state: WorkflowState) -> WorkflowState:
    # Retrieve relevant SOP / knowledge-base context for the user question
    context = retrieve_context(
        question=state["user_question"],
        k=4
    )

    # Store retrieved context
    state["rag_context"] = context

    # Return updated state
    return state


# Run executive summary workflow
def run_summary_node(state: WorkflowState) -> WorkflowState:
    # Generate executive summary using selected hierarchy and KPIs
    summary = generate_executive_summary(
        group_by=state["group_by"],
        kpis=state["kpis"]
    )

    # Store summary result
    state["summary_result"] = summary

    # Return updated state
    return state


# Decide whether RAG is needed after investigation/recommendation
def route_rag_if_needed(state: WorkflowState) -> str:
    # Continue to RAG if structured intent says knowledge-base context is required
    if state.get("needs_rag"):
        return "rag"

    # Otherwise go directly to final answer
    return "final"


# Generate final response payload
def generate_final_answer_node(state: WorkflowState) -> WorkflowState:
    # Build final answer from workflow outputs
    final_answer = {
        "user_question": state.get("user_question"),
        "intent": state.get("intent"),
        "tool_result": state.get("tool_result"),
        "benchmark_result": state.get("benchmark_result"),
        "recommendation_result": state.get("recommendation_result"),
        "summary_result": state.get("summary_result"),
        "rag_context": state.get("rag_context")
    }

    # Store final answer in state
    state["final_answer"] = final_answer

    # Add current interaction to memory-friendly chat history
    state["chat_history"].append(
        {
            "user": state.get("user_question", ""),
            "assistant": str(final_answer)
        }
    )

    # Return final state
    return state


# Handle unknown or unsupported questions
def handle_unknown_node(state: WorkflowState) -> WorkflowState:
    # Return clear fallback message
    state["final_answer"] = {
        "message": "I could not confidently route this question. Please ask a warehouse KPI, benchmark, anomaly, recommendation, SOP, or summary question."
    }

    # Return updated state
    return state


# Build LangGraph workflow
def build_workflow():
    # Create LangGraph state graph
    workflow = StateGraph(WorkflowState)

    # Add workflow nodes
    workflow.add_node("prepare_request", prepare_request)
    workflow.add_node("run_ranking", run_ranking_node)
    workflow.add_node("run_comparison", run_comparison_node)
    workflow.add_node("run_benchmark", run_benchmark_node)
    workflow.add_node("run_recommendation", run_recommendation_node)
    workflow.add_node("run_investigation", run_investigation_node)
    workflow.add_node("run_rag", run_rag_node)
    workflow.add_node("run_summary", run_summary_node)
    workflow.add_node("generate_final_answer", generate_final_answer_node)
    workflow.add_node("handle_unknown", handle_unknown_node)

    # Define workflow starting point
    workflow.set_entry_point("prepare_request")

    # Route request based on structured intent
    workflow.add_conditional_edges(
        "prepare_request",
        route_by_intent,
        {
            "ranking": "run_ranking",
            "comparison": "run_comparison",
            "benchmark": "run_benchmark",
            "recommendation": "run_recommendation",
            "investigation": "run_investigation",
            "rag": "run_rag",
            "summary": "run_summary",
            "unknown": "handle_unknown"
        }
    )

    # Simple flows go directly to final answer
    workflow.add_edge("run_ranking", "generate_final_answer")
    workflow.add_edge("run_comparison", "generate_final_answer")
    workflow.add_edge("run_benchmark", "generate_final_answer")
    workflow.add_edge("run_summary", "generate_final_answer")

    # Recommendation and investigation may optionally use RAG
    workflow.add_conditional_edges(
        "run_recommendation",
        route_rag_if_needed,
        {
            "rag": "run_rag",
            "final": "generate_final_answer"
        }
    )

    workflow.add_conditional_edges(
        "run_investigation",
        route_rag_if_needed,
        {
            "rag": "run_rag",
            "final": "generate_final_answer"
        }
    )

    # RAG flow goes to final answer
    workflow.add_edge("run_rag", "generate_final_answer")

    # Unknown flow ends after fallback response
    workflow.add_edge("handle_unknown", END)

    # Final answer ends workflow
    workflow.add_edge("generate_final_answer", END)

    # Add memory checkpointing
    memory = MemorySaver()

    # Compile workflow with memory enabled
    app = workflow.compile(checkpointer=memory)

    # Return compiled workflow app
    return app


# Run quick test only when this file is executed directly
if __name__ == "__main__":
    # Build compiled LangGraph workflow
    app = build_workflow()

    # Create sample structured input that will later come from prompt/intent extraction
    sample_state = {
        "user_question": "Show top 5 employees by PickRate",
        "intent": "ranking",
        "kpi": "PickRate",
        "group_by": "Employee_ID",
        "ranking_type": "top",
        "n": 5,
        "needs_rag": False
    }

    # Use thread_id so LangGraph memory can track this conversation
    config = {
        "configurable": {
            "thread_id": "demo-session-1"
        }
    }

    # Run workflow
    result = app.invoke(sample_state, config=config)

    # Print final answer
    print(result["final_answer"])