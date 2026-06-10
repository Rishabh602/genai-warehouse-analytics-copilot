# Import pandas for combining anomaly results
import pandas as pd

# Import benchmark function to classify KPI performance
from benchmark_engine import benchmark_kpi_summary


# Define KPIs that should be checked for anomalies
ANOMALY_KPIS = [
    "PickRate",
    "SelectionRate_Cases",
    "ReplenishmentRate",
    "IdleSelectionTime_pct",
    "OnTaskTime_pct",
    "Overtime_pct",
    "InventoryAccuracy_pct",
    "PickingErrorRate_pct",
    "OnTimeShipment_pct",
    "Absenteeism_pct",
    "SafetyIncidents",
    "EquipmentDowntime_Min",
    "CapacityUtilization_pct"
]


# Create business-friendly anomaly type labels
def get_anomaly_type(kpi):
    # Map KPI names to business issue categories
    anomaly_map = {
        "PickRate": "Productivity Issue",
        "SelectionRate_Cases": "Selection Productivity Issue",
        "ReplenishmentRate": "Replenishment Issue",
        "IdleSelectionTime_pct": "Idle Time Issue",
        "OnTaskTime_pct": "Labor Utilization Issue",
        "Overtime_pct": "Overtime Issue",
        "InventoryAccuracy_pct": "Inventory Accuracy Issue",
        "PickingErrorRate_pct": "Picking Quality Issue",
        "OnTimeShipment_pct": "Service Level Issue",
        "Absenteeism_pct": "Workforce Availability Issue",
        "SafetyIncidents": "Safety Issue",
        "EquipmentDowntime_Min": "Equipment Downtime Issue",
        "CapacityUtilization_pct": "Capacity Utilization Issue"
    }

    # Return mapped issue category or generic fallback
    return anomaly_map.get(kpi, "Operational Issue")


# Detect anomalies for one KPI at one hierarchy level
def detect_anomalies_for_kpi(group_by, kpi):
    # Get KPI values plus benchmark status from Benchmark Engine
    summary = benchmark_kpi_summary(group_by=group_by, kpi=kpi)

    # Keep only warning and critical records
    anomalies = summary[
        summary["Benchmark_Status"].isin(["Warning", "Critical"])
    ].copy()

    # Add KPI name so results from multiple KPIs can be combined
    anomalies["KPI"] = kpi

    # Add business-friendly anomaly type
    anomalies["Anomaly_Type"] = anomalies["KPI"].apply(get_anomaly_type)

    # Rename the KPI value column to a standard name for all KPI outputs
    anomalies = anomalies.rename(columns={kpi: "KPI_Value"})

    # Return clean anomaly table
    return anomalies


# Detect anomalies across multiple KPIs at selected hierarchy level
def detect_anomalies(group_by, kpis):
    # Store anomaly tables for each KPI
    anomaly_tables = []

    # Loop through each selected KPI
    for kpi in kpis:
        # Detect anomalies for the current KPI
        kpi_anomalies = detect_anomalies_for_kpi(group_by=group_by, kpi=kpi)

        # Add non-empty results to final list
        if not kpi_anomalies.empty:
            anomaly_tables.append(kpi_anomalies)

    # Return empty DataFrame if no anomalies were found
    if not anomaly_tables:
        return pd.DataFrame()

    # Combine anomaly tables across KPIs
    all_anomalies = pd.concat(anomaly_tables, ignore_index=True)

    # Return combined anomaly result
    return all_anomalies


# Count anomalies by hierarchy level
def get_anomaly_counts(group_by, kpis):
    # Detect all anomalies for selected KPIs and level
    anomalies = detect_anomalies(group_by=group_by, kpis=kpis)

    # Return empty DataFrame if there are no anomalies
    if anomalies.empty:
        return pd.DataFrame()

    # Convert group_by into list for consistent logic
    if isinstance(group_by, str):
        group_by = [group_by]

    # Count anomaly records by selected hierarchy level
    counts = (
        anomalies
        .groupby(group_by)
        .size()
        .reset_index(name="Anomaly_Count")
        .sort_values(by="Anomaly_Count", ascending=False)
    )

    # Return anomaly count table
    return counts


# Return most critical anomalies first
def get_critical_anomalies(group_by, kpis):
    # Detect all anomalies
    anomalies = detect_anomalies(group_by=group_by, kpis=kpis)

    # Return only critical anomalies
    critical = anomalies[
        anomalies["Benchmark_Status"] == "Critical"
    ].copy()

    # Return critical anomalies sorted by gap to target
    if "Gap_To_Target" in critical.columns:
        critical = critical.sort_values(by="Gap_To_Target")

    # Return critical anomaly table
    return critical


# Run quick tests only when this file is executed directly
if __name__ == "__main__":
    # Test anomaly detection at warehouse level
    print("\nWarehouse-level anomalies:")
    print(detect_anomalies(
        group_by="DC_ID",
        kpis=["PickRate", "Overtime_pct", "InventoryAccuracy_pct"]
    ).head())

    # Test anomaly count by manager
    print("\nAnomaly count by manager:")
    print(get_anomaly_counts(
        group_by="DC_Manager",
        kpis=ANOMALY_KPIS
    ).head())

    # Test critical anomalies by team leader
    print("\nCritical team leader anomalies:")
    print(get_critical_anomalies(
        group_by="Team_Leader",
        kpis=ANOMALY_KPIS
    ).head())