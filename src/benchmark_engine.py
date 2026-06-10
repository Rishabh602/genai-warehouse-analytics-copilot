# Import pandas only if future benchmark transformations need tabular operations
import pandas as pd

# Import benchmark loader from central data loader
from data_loader import load_benchmarks

# Import KPI summary function from KPI engine
from kpi_engine import get_kpi_summary


# Convert benchmark CSV into rules dictionary
def build_benchmark_rules():
    # Load benchmark thresholds from warehouse_benchmarks.csv
    benchmarks_df = load_benchmarks()

    # Create empty dictionary to store benchmark rules by KPI name
    rules = {}

    # Loop through each KPI benchmark row
    for _, row in benchmarks_df.iterrows():
        # Convert business direction into calculation-friendly logic
        if row["Direction"] == "Higher is better":
            comparison = "higher"
        elif row["Direction"] == "Lower is better":
            comparison = "lower"
        else:
            comparison = "balanced"

        # Store thresholds and interpretation for each KPI
        rules[row["KPI"]] = {
            "world_class": row["WorldClass"],
            "target": row["Target"],
            "warning": row["Warning"],
            "critical": row["Critical"],
            "comparison": comparison,
            "business_interpretation": row["Business_Interpretation"]
        }

    # Return benchmark configuration dictionary
    return rules


# Classify one KPI value using benchmark thresholds
def classify_kpi_value(kpi, value):
    # Build benchmark rules from CSV
    rules = build_benchmark_rules()

    # Return clear message if KPI has no benchmark
    if kpi not in rules:
        return "No Benchmark Available"

    # Get benchmark rule for selected KPI
    rule = rules[kpi]

    # Classify higher-is-better KPIs
    if rule["comparison"] == "higher":
        if value >= rule["world_class"]:
            return "World Class"
        elif value >= rule["target"]:
            return "On Target"
        elif value >= rule["critical"]:
            return "Warning"
        else:
            return "Critical"

    # Classify lower-is-better KPIs
    if rule["comparison"] == "lower":
        if value <= rule["world_class"]:
            return "World Class"
        elif value <= rule["target"]:
            return "On Target"
        elif value <= rule["critical"]:
            return "Warning"
        else:
            return "Critical"

    # Balanced KPIs need context-specific review
    return "Review Context"


# Calculate numeric gap from target
def calculate_gap_to_target(kpi, value):
    # Build benchmark rules from CSV
    rules = build_benchmark_rules()

    # Return None when KPI has no benchmark
    if kpi not in rules:
        return None

    # Get target threshold
    target = rules[kpi]["target"]

    # Gap is actual KPI value minus target
    return value - target


# Add benchmark status and gap to KPI summary
def benchmark_kpi_summary(group_by, kpi):
    # Get KPI summary from KPI engine at selected hierarchy level
    summary = get_kpi_summary(group_by=group_by, kpis=[kpi])

    # Add benchmark performance status
    summary["Benchmark_Status"] = summary[kpi].apply(
        lambda value: classify_kpi_value(kpi, value)
    )

    # Add numeric gap to target
    summary["Gap_To_Target"] = summary[kpi].apply(
        lambda value: calculate_gap_to_target(kpi, value)
    )

    # Return benchmarked KPI summary
    return summary


# Find entities in Warning or Critical status
def get_at_risk_entities(group_by, kpi):
    # Create benchmarked KPI summary
    summary = benchmark_kpi_summary(group_by=group_by, kpi=kpi)

    # Keep only warning and critical entities
    at_risk = summary[
        summary["Benchmark_Status"].isin(["Warning", "Critical"])
    ]

    # Return at-risk entities
    return at_risk


# Run quick tests only when this file is executed directly
if __name__ == "__main__":
    # Test benchmark rule loading
    rules = build_benchmark_rules()
    print("Benchmark rules loaded:", len(rules))

    # Test benchmark classification at warehouse level
    print("\nWarehouse PickRate benchmark summary:")
    print(benchmark_kpi_summary(group_by="DC_ID", kpi="PickRate").head())

    # Test benchmark classification at manager level
    print("\nManager Overtime benchmark summary:")
    print(benchmark_kpi_summary(group_by="DC_Manager", kpi="Overtime_pct").head())

    # Test at-risk team leaders by OnTaskTime
    print("\nAt-risk team leaders by OnTaskTime:")
    print(get_at_risk_entities(group_by="Team_Leader", kpi="OnTaskTime_pct").head())