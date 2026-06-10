# Import KPI Engine functions
from kpi_engine import (
    get_available_kpis,
    get_kpi_summary,
    get_top_performers,
    get_bottom_performers,
    compare_performance
)

# Import Benchmark Engine functions
from benchmark_engine import (
    benchmark_kpi_summary,
    get_at_risk_entities
)

# Import Recommendation Engine functions
from recommendation_engine import (
    recommend_from_anomalies,
    get_priority_recommendations
)


# Tool: return all available KPI fields
def available_kpis_tool():
    # Return numeric KPI columns available in the KPI dataset
    return get_available_kpis()


# Tool: summarize KPI values at a selected hierarchy level
def kpi_summary_tool(group_by, kpis):
    # Call KPI Engine and convert result to JSON-friendly records
    result = get_kpi_summary(group_by=group_by, kpis=kpis)
    return result.to_dict(orient="records")


# Tool: return top N performers for selected KPI and level
def top_performers_tool(kpi, group_by, n):
    # Call KPI Engine and convert result to JSON-friendly records
    result = get_top_performers(kpi=kpi, group_by=group_by, n=n)
    return result.to_dict(orient="records")


# Tool: return bottom N performers for selected KPI and level
def bottom_performers_tool(kpi, group_by, n):
    # Call KPI Engine and convert result to JSON-friendly records
    result = get_bottom_performers(kpi=kpi, group_by=group_by, n=n)
    return result.to_dict(orient="records")


# Tool: compare selected entities across selected KPIs
def compare_performance_tool(group_by, selected_values, kpis):
    # Call KPI Engine and convert result to JSON-friendly records
    result = compare_performance(
        group_by=group_by,
        selected_values=selected_values,
        kpis=kpis
    )
    return result.to_dict(orient="records")


# Tool: classify selected KPI against benchmark thresholds
def benchmark_summary_tool(group_by, kpi):
    # Call Benchmark Engine and convert result to JSON-friendly records
    result = benchmark_kpi_summary(group_by=group_by, kpi=kpi)
    return result.to_dict(orient="records")


# Tool: return Warning/Critical entities for selected KPI
def at_risk_entities_tool(group_by, kpi):
    # Call Benchmark Engine and convert result to JSON-friendly records
    result = get_at_risk_entities(group_by=group_by, kpi=kpi)
    return result.to_dict(orient="records")


# Tool: generate recommendations from detected anomalies
def recommendations_from_anomalies_tool(group_by, kpis):
    # Call Recommendation Engine and convert result to JSON-friendly records
    result = recommend_from_anomalies(group_by=group_by, kpis=kpis)
    return result.to_dict(orient="records")


# Tool: return highest-priority recommendations
def priority_recommendations_tool(group_by, kpis):
    # Call Recommendation Engine and convert result to JSON-friendly records
    result = get_priority_recommendations(group_by=group_by, kpis=kpis)
    return result.to_dict(orient="records")


# Central registry of all callable tools
TOOL_REGISTRY = {
    "available_kpis": available_kpis_tool,
    "kpi_summary": kpi_summary_tool,
    "top_performers": top_performers_tool,
    "bottom_performers": bottom_performers_tool,
    "compare_performance": compare_performance_tool,
    "benchmark_summary": benchmark_summary_tool,
    "at_risk_entities": at_risk_entities_tool,
    "recommendations_from_anomalies": recommendations_from_anomalies_tool,
    "priority_recommendations": priority_recommendations_tool
}


# Execute a tool by name with provided parameters
def run_tool(tool_name, **kwargs):
    # Validate that requested tool exists
    if tool_name not in TOOL_REGISTRY:
        raise ValueError(f"Unknown tool: {tool_name}")

    # Get the selected tool function
    tool_function = TOOL_REGISTRY[tool_name]

    # Run the selected tool with user/LLM-provided parameters
    return tool_function(**kwargs)


# Run quick tests only when this file is executed directly
if __name__ == "__main__":
    # Test KPI top performers tool
    print("\nTop 5 employees by PickRate:")
    print(run_tool(
        "top_performers",
        kpi="PickRate",
        group_by="Employee_ID",
        n=5
    ))

    # Test benchmark tool
    print("\nWarehouse PickRate benchmark:")
    print(run_tool(
        "benchmark_summary",
        group_by="DC_ID",
        kpi="PickRate"
    ))

    # Test recommendation tool
    print("\nPriority recommendations by manager:")
    print(run_tool(
        "priority_recommendations",
        group_by="DC_Manager",
        kpis=["PickRate", "Overtime_pct"]
    ))