import plotly.express as px


def create_top_performer_chart(top_df, group_by, kpi, n):

    fig = px.bar(
        top_df,
        x=group_by,
        y=kpi,
        text=kpi,
        title=f"Top {n} {group_by} by {kpi}"
    )

    fig.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    return fig


def create_bottom_performer_chart(bottom_df, group_by, kpi, n):

    fig = px.bar(
        bottom_df,
        x=group_by,
        y=kpi,
        text=kpi,
        title=f"Bottom {n} {group_by} by {kpi}"
    )

    fig.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    return fig


def create_benchmark_chart(benchmark_df, kpi):

    benchmark_distribution = (
        benchmark_df
        .groupby("Benchmark_Status")
        .size()
        .reset_index(name="Count")
    )

    fig = px.bar(
        benchmark_distribution,
        x="Benchmark_Status",
        y="Count",
        text="Count",
        title=f"{kpi} Benchmark Distribution"
    )

    return fig


def create_trend_chart(df, kpi):

    trend_df = (
        df.groupby("Week_Number")[kpi]
        .mean()
        .reset_index()
        .sort_values("Week_Number")
    )

    fig = px.line(
        trend_df,
        x="Week_Number",
        y=kpi,
        markers=True,
        title=f"{kpi} Weekly Trend"
    )

    return fig


def create_anomaly_chart(anomaly_counts, group_by):

    anomaly_column = anomaly_counts.columns[-1]

    fig = px.bar(
        anomaly_counts.head(15),
        x=group_by,
        y=anomaly_column,
        text=anomaly_column,
        title=f"Anomaly Overview by {group_by}"
    )

    return fig