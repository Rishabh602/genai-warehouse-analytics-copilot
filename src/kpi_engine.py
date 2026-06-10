# Import pandas for tabular KPI calculations
import pandas as pd

# Import only KPI data loader because this engine calculates KPI values, not benchmark status
from data_loader import load_kpi_data


# Validate that requested columns exist in the dataset
def validate_columns(df, columns):
    # Convert one column string into a list so the rest of the logic is consistent
    if isinstance(columns, str):
        columns = [columns]

    # Find columns requested by user/caller but missing in the dataset
    missing_columns = [col for col in columns if col not in df.columns]

    # Stop execution early with a clear message if columns are wrong
    if missing_columns:
        raise ValueError(f"Missing columns in KPI dataset: {missing_columns}")

    # Return clean validated column list
    return columns


# Return numeric KPI columns available in the KPI fact table
def get_available_kpis():
    # Load KPI fact table
    df = load_kpi_data()

    # Select numeric columns only because KPI calculations need numeric fields
    numeric_columns = df.select_dtypes(include="number").columns.tolist()

    # Return numeric KPI list for dynamic user-driven analysis
    return numeric_columns


# Calculate KPI summary at any selected business level
def get_kpi_summary(group_by, kpis):
    # Load main KPI fact table
    df = load_kpi_data()

    # Validate user-selected hierarchy level such as DC_ID, DC_Manager, Team_Leader, Shift, Employee_ID
    group_by = validate_columns(df, group_by)

    # Validate user-selected KPI or KPI list such as PickRate, Overtime_pct, OnTaskTime_pct
    kpis = validate_columns(df, kpis)

    # Aggregate KPI values at the selected business level
    summary = df.groupby(group_by)[kpis].mean().reset_index()

    # Return summary table for downstream engines, agents, or UI
    return summary


# Get top performers using KPI, hierarchy level, and ranking size supplied by caller/user
def get_top_performers(kpi, group_by, n):
    # Build KPI summary for the selected KPI and hierarchy level
    summary = get_kpi_summary(group_by=group_by, kpis=[kpi])

    # Sort high-to-low because top performers have highest KPI value
    result = summary.sort_values(by=kpi, ascending=False).head(n)

    # Return top N performers
    return result


# Get bottom performers using KPI, hierarchy level, and ranking size supplied by caller/user
def get_bottom_performers(kpi, group_by, n):
    # Build KPI summary for the selected KPI and hierarchy level
    summary = get_kpi_summary(group_by=group_by, kpis=[kpi])

    # Sort low-to-high because bottom performers have lowest KPI value
    result = summary.sort_values(by=kpi, ascending=True).head(n)

    # Return bottom N performers
    return result


# Compare selected entities at any hierarchy level
def compare_performance(group_by, selected_values, kpis):
    # Build KPI summary for selected hierarchy and KPIs
    summary = get_kpi_summary(group_by=group_by, kpis=kpis)

    # Convert group_by into list for consistent filtering logic
    if isinstance(group_by, str):
        group_by = [group_by]

    # Use first group-by column as the filter field
    filter_column = group_by[0]

    # Keep only the selected entities requested by caller/user
    result = summary[summary[filter_column].isin(selected_values)]

    # Return filtered comparison result
    return result


# Run quick tests only when this file is executed directly
if __name__ == "__main__":
    # Show available numeric KPI columns
    print("Available KPIs:")
    print(get_available_kpis())

    # Test manager-level KPI summary
    print("\nManager-level PickRate summary:")
    print(get_kpi_summary(group_by="DC_Manager", kpis=["PickRate"]).head())

    # Test top 10 employees by PickRate
    print("\nTop 10 employees by PickRate:")
    print(get_top_performers(kpi="PickRate", group_by="Employee_ID", n=10))

    # Test bottom 3 team leaders by Overtime
    print("\nBottom 3 team leaders by Overtime:")
    print(get_bottom_performers(kpi="Overtime_pct", group_by="Team_Leader", n=3))

    # Test selected DC comparison
    print("\nCompare selected DCs:")
    print(compare_performance(
        group_by="DC_ID",
        selected_values=["DC003", "DC006", "DC008"],
        kpis=["PickRate", "Overtime_pct", "InventoryAccuracy_pct"]
    ))