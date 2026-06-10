# Import pandas for filtering and formatting recommendation tables
import pandas as pd

# Import recommendation rules from the central data loader
from data_loader import load_recommendation_rules

# Import anomaly detection output so recommendations can be linked to real issues
from anomaly_engine import detect_anomalies, ANOMALY_KPIS


# Load all recommendation rules from recommendation_rules.csv
def get_recommendation_rules():
    # Read business rules from CSV instead of hardcoding actions in Python
    rules = load_recommendation_rules()

    # Return rules table for downstream recommendation logic
    return rules


# Find recommendation rules for one KPI
def get_rules_for_kpi(kpi):
    # Load recommendation rules
    rules = get_recommendation_rules()

    # Keep rules matching the selected KPI
    matched_rules = rules[rules["KPI"] == kpi].copy()

    # Return matching rules
    return matched_rules


# Generate recommendations for one KPI issue
def recommend_for_kpi(kpi, severity=None):
    # Get rules related to selected KPI
    rules = get_rules_for_kpi(kpi)

    # If severity is provided, filter rules by severity
    if severity:
        rules = rules[rules["Severity"] == severity]

    # Return matching recommendations
    return rules


# Generate recommendations from anomaly output
def recommend_from_anomalies(group_by, kpis):
    # Detect anomalies using the anomaly engine
    anomalies = detect_anomalies(group_by=group_by, kpis=kpis)

    # Return empty DataFrame if no anomalies are found
    if anomalies.empty:
        return pd.DataFrame()

    # Load recommendation rules
    rules = get_recommendation_rules()

    # Join anomalies with recommendation rules using KPI and benchmark severity
    recommendations = anomalies.merge(
        rules,
        left_on=["KPI", "Benchmark_Status"],
        right_on=["KPI", "Severity"],
        how="left"
    )

    # Select useful columns for business output
    output_columns = [
        *([group_by] if isinstance(group_by, str) else group_by),
        "KPI",
        "KPI_Value",
        "Benchmark_Status",
        "Gap_To_Target",
        "Anomaly_Type",
        "Recommendation",
        "Suggested_Owner"
    ]

    # Keep only columns that exist after merge
    output_columns = [col for col in output_columns if col in recommendations.columns]

    # Return recommendation table
    return recommendations[output_columns]


# Get highest-priority recommendations only
def get_priority_recommendations(group_by, kpis):
    # Generate all recommendations from anomalies
    recommendations = recommend_from_anomalies(group_by=group_by, kpis=kpis)

    # Return empty DataFrame if no recommendations exist
    if recommendations.empty:
        return pd.DataFrame()

    # Keep only critical issues first
    priority = recommendations[
        recommendations["Benchmark_Status"] == "Critical"
    ].copy()

    # If no critical issues exist, return warning issues
    if priority.empty:
        priority = recommendations[
            recommendations["Benchmark_Status"] == "Warning"
        ].copy()

    # Return priority recommendations
    return priority


# Run quick tests only when this file is executed directly
if __name__ == "__main__":

    # Test loading recommendation rules
    print("\nRecommendation rules:")
    print(get_recommendation_rules().head())

    # Test KPI-specific recommendation lookup
    print("\nRules for PickRate:")
    print(get_rules_for_kpi("PickRate"))

    # Test recommendations from warehouse-level anomalies
    print("\nRecommendations from warehouse anomalies:")
    print(recommend_from_anomalies(
        group_by="DC_ID",
        kpis=["PickRate", "Overtime_pct", "InventoryAccuracy_pct"]
    ).head())

    # Test priority recommendations at manager level
    print("\nPriority recommendations by manager:")
    print(get_priority_recommendations(
        group_by="DC_Manager",
        kpis=ANOMALY_KPIS
    ).head())


