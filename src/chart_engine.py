# Import KPI engine functions
from kpi_engine import (
    get_top_performers,
    get_bottom_performers,
    compare_performance
)

# Import benchmark engine functions
from benchmark_engine import benchmark_kpi_summary

# Import anomaly engine functions
from anomaly_engine import get_anomaly_counts

# Import KPI data loader
from data_loader import load_kpi_data


# Prepare top performer chart data
def get_top_n_chart_data(kpi, group_by, n):

    # Retrieve top performers
    chart_data = get_top_performers(
        kpi=kpi,
        group_by=group_by,
        n=n
    )

    # Return chart-ready dataframe
    return chart_data


# Prepare bottom performer chart data
def get_bottom_n_chart_data(kpi, group_by, n):

    # Retrieve bottom performers
    chart_data = get_bottom_performers(
        kpi=kpi,
        group_by=group_by,
        n=n
    )

    # Return chart-ready dataframe
    return chart_data


# Prepare comparison chart data
def get_comparison_chart_data(group_by, selected_values, kpis):

    # Compare selected entities
    chart_data = compare_performance(
        group_by=group_by,
        selected_values=selected_values,
        kpis=kpis
    )

    # Return chart-ready dataframe
    return chart_data


# Prepare benchmark distribution chart data
def get_benchmark_distribution_data(group_by, kpi):

    # Get KPI summary with benchmark classification
    benchmark_data = benchmark_kpi_summary(
        group_by=group_by,
        kpi=kpi
    )

    # Count status categories
    distribution = (
        benchmark_data
        .groupby("Benchmark_Status")
        .size()
        .reset_index(name="Count")
    )

    # Return distribution table
    return distribution


# Prepare anomaly count chart data
def get_anomaly_chart_data(group_by, kpis):

    # Get anomaly counts
    anomaly_data = get_anomaly_counts(
        group_by=group_by,
        kpis=kpis
    )

    # Return anomaly count table
    return anomaly_data


# Prepare weekly trend chart data
def get_trend_chart_data(kpi, group_by, entity_value):

    # Load KPI fact table
    df = load_kpi_data()

    # Filter selected entity
    df = df[df[group_by] == entity_value]

    # Aggregate KPI by week
    trend_data = (
        df.groupby("Week_Number")[kpi]
        .mean()
        .reset_index()
        .sort_values("Week_Number")
    )

    # Return trend dataset
    return trend_data


# Run tests only when executed directly
if __name__ == "__main__":

    print("\nTop Employees by PickRate")
    print(
        get_top_n_chart_data(
            kpi="PickRate",
            group_by="Employee_ID",
            n=10
        ).head()
    )

    print("\nBottom Managers by Overtime")
    print(
        get_bottom_n_chart_data(
            kpi="Overtime_pct",
            group_by="DC_Manager",
            n=5
        ).head()
    )

    print("\nWarehouse Comparison")
    print(
        get_comparison_chart_data(
            group_by="DC_ID",
            selected_values=["DC003", "DC006", "DC008"],
            kpis=["PickRate", "Overtime_pct"]
        )
    )

    print("\nBenchmark Distribution")
    print(
        get_benchmark_distribution_data(
            group_by="DC_ID",
            kpi="PickRate"
        )
    )

    print("\nAnomaly Counts")
    print(
        get_anomaly_chart_data(
            group_by="DC_Manager",
            kpis=["PickRate", "Overtime_pct"]
        ).head()
    )