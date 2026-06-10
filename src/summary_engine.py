# Import pandas for table handling
import pandas as pd

# Import anomaly and recommendation outputs
from anomaly_engine import detect_anomalies, get_anomaly_counts, ANOMALY_KPIS
from recommendation_engine import get_priority_recommendations


# Build a short executive summary for a selected business level
def generate_executive_summary(group_by, kpis):
    # Detect anomalies for selected level and KPIs
    anomalies = detect_anomalies(group_by=group_by, kpis=kpis)

    # Count anomalies by selected hierarchy level
    anomaly_counts = get_anomaly_counts(group_by=group_by, kpis=kpis)

    # Generate priority recommendations from detected anomalies
    recommendations = get_priority_recommendations(group_by=group_by, kpis=kpis)

    # Return simple message if there are no anomalies
    if anomalies.empty:
        return "No major operational risks detected for the selected scope."

    # Count total anomalies
    total_anomalies = len(anomalies)

    # Count critical anomalies
    critical_count = len(anomalies[anomalies["Benchmark_Status"] == "Critical"])

    # Count warning anomalies
    warning_count = len(anomalies[anomalies["Benchmark_Status"] == "Warning"])

    # Identify top risk entity if anomaly counts exist
    if not anomaly_counts.empty:
        top_risk_entity = anomaly_counts.iloc[0].to_dict()
    else:
        top_risk_entity = {}

    # Extract first few priority recommendations
    if not recommendations.empty:
        top_recommendations = recommendations["Recommendation"].dropna().unique().tolist()[:3]
    else:
        top_recommendations = []

    # Build summary text
    summary = f"""
Executive Summary:
Detected {total_anomalies} operational risk signals.

Severity Mix:
- Critical issues: {critical_count}
- Warning issues: {warning_count}

Top Risk Area:
{top_risk_entity}

Recommended Management Actions:
{top_recommendations}
"""

    # Return executive summary text
    return summary


# Run quick tests only when this file is executed directly
if __name__ == "__main__":
    # Test summary at warehouse level using core operational KPIs
    print(generate_executive_summary(
        group_by="DC_ID",
        kpis=[
            "PickRate",
            "Overtime_pct",
            "IdleSelectionTime_pct",
            "InventoryAccuracy_pct",
            "OnTimeShipment_pct"
        ]
    ))

    # Test summary at manager level using all anomaly KPIs
    print(generate_executive_summary(
        group_by="DC_Manager",
        kpis=ANOMALY_KPIS
    ))