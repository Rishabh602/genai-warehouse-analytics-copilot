import streamlit as st
import sys
import os
from dotenv import load_dotenv
import plotly.express as px


# -----------------------------
# Project path setup
# -----------------------------

current_dir = os.path.dirname(__file__)

src_path = os.path.abspath(
    os.path.join(current_dir, "../src")
)

sys.path.insert(0, src_path)


# -----------------------------
# Import project engines
# -----------------------------

from question_parser import parse_question
from data_loader import load_kpi_data

from kpi_engine import (
    get_kpi_summary,
    get_top_performers,
    get_bottom_performers
)

from benchmark_engine import benchmark_kpi_summary

from anomaly_engine import (
    get_anomaly_counts,
    ANOMALY_KPIS
)

from recommendation_engine import get_priority_recommendations
from summary_engine import generate_executive_summary
from rag_engine import retrieve_context

from visualization_engine import (
    create_top_performer_chart,
    create_bottom_performer_chart,
    create_benchmark_chart
)


# -----------------------------
# Environment setup
# -----------------------------

load_dotenv()


# -----------------------------
# Page config
# -----------------------------

st.set_page_config(
    page_title="GenAI Warehouse Operations Copilot",
    layout="wide"
)


# -----------------------------
# Header
# -----------------------------

col1, col2 = st.columns([5, 1])

with col1:
    st.title("GenAI Warehouse Operations Copilot")

with col2:
    st.markdown(
        "<div style='text-align: right; padding-top: 25px;'>"
        "<i>Designed for demo purposes</i>"
        "</div>",
        unsafe_allow_html=True
    )


# -----------------------------
# App overview
# -----------------------------

st.markdown(
    """
    This GenAI-powered warehouse operations copilot helps leaders investigate KPI performance,
    identify anomalies, benchmark operations, retrieve SOP guidance, and generate recommended
    actions using natural language.
    """
)

st.info(
    "Business problem: Warehouse leaders often need fast answers across distribution centers, "
    "managers, teams, shifts, and employees. This copilot converts warehouse KPI data into "
    "business-ready operational insights."
)


# -----------------------------
# Demo explanation
# -----------------------------

with st.expander("Understanding the Demo Questions, KPIs, and Data"):

    st.markdown(
        """
        ### Warehouse Structure

        - **DC_ID** → Warehouse / distribution center
        - **DC_Manager** → Manager responsible for warehouse operations
        - **Team_Leader** → Supervises warehouse teams
        - **Team** → Operational team group
        - **Shift** → Morning / Evening / Night shift
        - **Employee_ID** → Individual warehouse employee

        ### KPI Definitions

        - **PickRate** → Picking productivity and speed
        - **SelectionRate_Cases** → Number of selected warehouse cases
        - **ReplenishmentRate** → Replenishment productivity
        - **Overtime_pct** → Overtime percentage
        - **IdleSelectionTime_pct** → Non-productive idle time
        - **OnTaskTime_pct** → Productive working time
        - **InventoryAccuracy_pct** → Inventory accuracy
        - **PickingErrorRate_pct** → Picking errors
        - **OnTimeShipment_pct** → On-time shipment performance
        - **Absenteeism_pct** → Absenteeism rate
        - **SafetyIncidents** → Safety issue count
        - **EquipmentDowntime_Min** → Equipment downtime minutes
        - **CapacityUtilization_pct** → Warehouse capacity utilization

        ### Example Questions

        - Show top 5 employees by ReplenishmentRate
        - Show overtime trend across shifts
        - Tell 3 lowest performing warehouses by PickRate
        - Which team leader has the most anomalies?
        """
    )


# -----------------------------
# Load data
# -----------------------------

@st.cache_data
def load_data():
    return load_kpi_data()


with st.spinner("Loading WarehouseGPT demo data..."):
    df = load_data()


# Detect available week column once
if "Week_Number" in df.columns:
    week_column = "Week_Number"
elif "Week" in df.columns:
    week_column = "Week"
else:
    week_column = None


# -----------------------------
# Sidebar filters
# -----------------------------

st.subheader("Analysis Controls")

control_col1, control_col2, control_col3 = st.columns(3)

with control_col1:
    group_by = st.selectbox(
        "Select analysis level",
        ["DC_ID", "DC_Manager", "Team_Leader", "Team", "Shift", "Employee_ID", "Country", "Region"]
    )

with control_col2:
    kpi = st.selectbox(
        "Select KPI",
        [
            "PickRate", "SelectionRate_Cases", "ReplenishmentRate",
            "IdleSelectionTime_pct", "OnTaskTime_pct", "Overtime_pct",
            "InventoryAccuracy_pct", "PickingErrorRate_pct",
            "OnTimeShipment_pct", "Absenteeism_pct", "SafetyIncidents",
            "EquipmentDowntime_Min", "CapacityUtilization_pct"
        ]
    )

with control_col3:
    n = st.slider(
        "Top/Bottom N",
        min_value=2,
        max_value=20,
        value=5
    )


# -----------------------------
# Executive dashboard
# -----------------------------

# -----------------------------
# Executive dashboard
# -----------------------------

st.subheader("Executive Dashboard")

st.caption(
    "Use the sidebar to change the KPI shown in the dashboard and visual overview."
)

m1, m2, m3, m4 = st.columns(4)

m1.metric("KPI Records", len(df))
m2.metric("Warehouses", df["DC_ID"].nunique())
m3.metric("Employees", df["Employee_ID"].nunique())
m4.metric(
    f"Average {kpi}",
    round(df[kpi].mean(), 2)
)


# -----------------------------
# KPI Visual Overview
# -----------------------------

st.subheader("KPI Visual Overview")

top_df = get_top_performers(
    kpi=kpi,
    group_by=group_by,
    n=n
)

bottom_df = get_bottom_performers(
    kpi=kpi,
    group_by=group_by,
    n=n
)

viz_tab1, viz_tab2, viz_tab3 = st.tabs(
    [
        "Top / Bottom Performance",
        "Weekly Trend",
        "Benchmark Snapshot"
    ]
)


with viz_tab1:

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig_top = create_top_performer_chart(
            top_df=top_df,
            group_by=group_by,
            kpi=kpi,
            n=n
        )

        st.plotly_chart(
            fig_top,
            use_container_width=True,
            key="dashboard_top_chart"
        )

    with chart_col2:
        fig_bottom = create_bottom_performer_chart(
            bottom_df=bottom_df,
            group_by=group_by,
            kpi=kpi,
            n=n
        )

        st.plotly_chart(
            fig_bottom,
            use_container_width=True,
            key="dashboard_bottom_chart"
        )


with viz_tab2:

    if week_column is not None:

        dashboard_trend_df = (
            df
            .groupby(week_column)[kpi]
            .mean()
            .reset_index()
            .sort_values(week_column)
        )

        fig_dashboard_trend = px.line(
            dashboard_trend_df,
            x=week_column,
            y=kpi,
            markers=True,
            title=f"{kpi} Weekly Trend"
        )

        st.plotly_chart(
            fig_dashboard_trend,
            use_container_width=True,
            key="dashboard_weekly_trend_chart"
        )

    else:
        st.warning("Week column is not available in the dataset.")


with viz_tab3:

    benchmark_df_light = benchmark_kpi_summary(
        group_by=group_by,
        kpi=kpi
    )

    if "Benchmark_Status" in benchmark_df_light.columns:

        fig_benchmark = create_benchmark_chart(
            benchmark_df=benchmark_df_light,
            kpi=kpi
        )

        st.plotly_chart(
            fig_benchmark,
            use_container_width=True,
            key="dashboard_benchmark_chart"
        )

    else:
        st.warning("Benchmark_Status column not found.")


# -----------------------------
# Copilot section
# -----------------------------

st.subheader("Ask the Copilot")

st.markdown(
    """
    Ask questions about warehouse performance, productivity, anomalies,
    trends, managers, teams, shifts, and employees.

    **You can type your own question or click one of the example questions below.**
    """
)

st.info(
    """
    Examples:

    • Show top 5 employees by ReplenishmentRate

    • Show overtime trend across shifts

    • Tell 3 lowest performing warehouses by PickRate

    • Which team leader has the most anomalies?
    """
)


if "selected_question" not in st.session_state:
    st.session_state.selected_question = ""


col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Top 5 Employees by ReplenishmentRate"):
        st.session_state.selected_question = (
            "Show top 5 employees by ReplenishmentRate"
        )

with col2:
    if st.button("Overtime Trend Across Shifts"):
        st.session_state.selected_question = (
            "Show overtime trend across shifts"
        )

with col3:
    if st.button("Lowest Warehouses by PickRate"):
        st.session_state.selected_question = (
            "Tell 3 lowest performing warehouses by PickRate"
        )


question = st.text_input(
    "Ask your warehouse KPI question:",
    value=st.session_state.selected_question,
    placeholder="Example: Show overtime trend across shifts"
)


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# -----------------------------
# Run copilot
# -----------------------------

if st.button("Ask Copilot"):

    if question.strip() == "":
        st.warning("Please enter a question.")

    else:

        with st.spinner("Analyzing warehouse KPIs and retrieving operational guidance..."):

            parsed_question = parse_question(
                question=question,
                default_kpi=kpi,
                default_group_by=group_by,
                default_n=n
            )

            selected_kpi = parsed_question["kpi"]
            selected_group_by = parsed_question["group_by"]
            selected_n = parsed_question["n"]
            intent = parsed_question["intent"]
            ranking_type = parsed_question["ranking_type"]

            question_lower = question.lower()

            if (
                "trend" in question_lower
                or "weekly" in question_lower
                or "week" in question_lower
                or "over time" in question_lower
                or "time series" in question_lower
            ):
                intent = "trend"

            rag_context = retrieve_context(
                question=question,
                k=3
            )

            if intent == "trend":

                if week_column is None:
                    answer_text = (
                        "I understood this as a trend question, but the dataset does not contain "
                        "a Week or Week_Number column."
                    )

                    st.subheader("AI Answer")
                    st.write(answer_text)

                else:
                    trend_df = (
                        df
                        .groupby([week_column, selected_group_by])[selected_kpi]
                        .mean()
                        .reset_index()
                        .sort_values(week_column)
                    )

                    fig = px.line(
                        trend_df,
                        x=week_column,
                        y=selected_kpi,
                        color=selected_group_by,
                        markers=True,
                        title=f"{selected_kpi} Weekly Trend by {selected_group_by}"
                    )

                    answer_text = (
                        f"Weekly trend analysis completed for **{selected_kpi}** across "
                        f"**{selected_group_by}**. The chart below shows how the KPI moved over time."
                    )

                    st.subheader("AI Answer")
                    st.write(answer_text)

                    st.subheader("Analysis Chart")
                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                        key=f"copilot_trend_{selected_kpi}_{selected_group_by}_{selected_n}"
                    )

                    st.subheader("Analysis Data")
                    st.dataframe(trend_df, use_container_width=True)

            elif intent == "ranking":

                if ranking_type == "bottom":
                    result_df = get_bottom_performers(
                        kpi=selected_kpi,
                        group_by=selected_group_by,
                        n=selected_n
                    )

                    fig = create_bottom_performer_chart(
                        bottom_df=result_df,
                        group_by=selected_group_by,
                        kpi=selected_kpi,
                        n=selected_n
                    )

                    answer_text = (
                        f"Bottom {selected_n} ranking completed for **{selected_kpi}** "
                        f"at **{selected_group_by}** level."
                    )

                else:
                    result_df = get_top_performers(
                        kpi=selected_kpi,
                        group_by=selected_group_by,
                        n=selected_n
                    )

                    fig = create_top_performer_chart(
                        top_df=result_df,
                        group_by=selected_group_by,
                        kpi=selected_kpi,
                        n=selected_n
                    )

                    answer_text = (
                        f"Top {selected_n} ranking completed for **{selected_kpi}** "
                        f"at **{selected_group_by}** level."
                    )

                st.subheader("AI Answer")
                st.write(answer_text)

                st.subheader("Analysis Chart")
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    key=f"copilot_ranking_{selected_kpi}_{selected_group_by}_{ranking_type}_{selected_n}"
                )
                st.subheader("Analysis Data")
                st.dataframe(result_df, use_container_width=True)


            elif intent == "anomaly":

                anomaly_counts = get_anomaly_counts(
                    group_by=selected_group_by,
                    kpis=ANOMALY_KPIS
                )

                anomaly_col = anomaly_counts.columns[-1]

                fig = px.bar(
                    anomaly_counts.head(selected_n),
                    x=selected_group_by,
                    y=anomaly_col,
                    text=anomaly_col,
                    title=f"Top {selected_n} Anomaly Counts by {selected_group_by}"
                )

                answer_text = (
                    f"Anomaly analysis completed for **{selected_group_by}**. "
                    f"The chart below shows the groups with the highest anomaly counts."
                )

                st.subheader("AI Answer")
                st.write(answer_text)

                st.subheader("Analysis Chart")
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    key=f"copilot_anomaly_{selected_group_by}_{selected_n}"
                )

                with st.expander("View Anomaly Data"):
                    st.dataframe(anomaly_counts, use_container_width=True)


            elif intent == "recommendation":

                recommendations = get_priority_recommendations(
                    group_by=selected_group_by,
                    kpis=ANOMALY_KPIS
                )

                answer_text = (
                    f"Recommendation analysis completed for **{selected_group_by}**. "
                    f"The table below shows prioritized management actions."
                )

                st.subheader("AI Answer")
                st.write(answer_text)

                st.subheader("Recommended Management Actions")
                st.dataframe(recommendations, use_container_width=True)


            else:

                answer_text = (
                    "I understood the question, but this analysis type is not fully connected yet."
                )

                st.subheader("AI Answer")
                st.write(answer_text)


            st.subheader("Knowledge Base Recommendation")
            st.write(rag_context)

            recommendations = get_priority_recommendations(
                group_by=selected_group_by,
                kpis=[selected_kpi]
            )

            st.dataframe(
                recommendations,
                use_container_width=True
            )
            st.success(
            f"Analysis completed successfully for {selected_kpi}"
            )
            st.session_state.chat_history.append(
                {
                    "question": question,
                    "answer": answer_text
                }
            )


# -----------------------------
# Conversation history
# -----------------------------

if st.session_state.chat_history:

    with st.expander("Conversation History"):

        for chat in st.session_state.chat_history:
            st.markdown(f"**You:** {chat['question']}")
            st.markdown(f"**Copilot:** {chat['answer']}")
            st.markdown("---")

