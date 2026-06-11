# Import Streamlit for UI
import streamlit as st

# Import sys and os for project path handling
import sys
import os

# Import dotenv for environment variables
from dotenv import load_dotenv


# -----------------------------
# Project path setup
# -----------------------------

current_dir = os.path.dirname(__file__)

src_path = os.path.abspath(
    os.path.join(current_dir, "../src")
)

sys.path.insert(0, src_path)


# -----------------------------
# Import final project engines
# -----------------------------

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

from visualization_engine import (
    create_top_performer_chart,
    create_bottom_performer_chart,
    create_benchmark_chart,
    create_trend_chart,
    create_anomaly_chart
)

from langgraph_workflow import build_workflow


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
        "<i>Designed and developed by Rishabh</i>"
        "</div>",
        unsafe_allow_html=True
    )


# -----------------------------
# App overview
# -----------------------------

st.markdown(
    """
    This app is a GenAI-powered analytics assistant for warehouse operations.

    It helps users ask natural language questions about warehouse KPI performance, anomalies,
    trends, managers, teams, shifts, and employees.

    The app combines:

    - KPI analytics engine
    - Benchmark engine
    - Anomaly detection engine
    - Recommendation engine
    - RAG knowledge retrieval
    - LangGraph workflow orchestration
    - Interactive KPI visualizations
    """
)


st.info(
    "Business problem: Warehouse leaders often need to quickly understand KPI performance, "
    "identify operational issues, and explain anomalies across distribution centers, managers, "
    "teams, shifts, and employees. This copilot converts warehouse KPI data into "
    "business-ready operational insights."
)


st.markdown(
    """
    ### Example Questions You Can Ask

    - Which top 2 DC_Manager has the highest PickRate?
    - Tell 2 lowest PickRate warehouses
    - Show PickRate trend over time by Team
    - Which team leader has the most anomalies?
    - Show top 5 employees by PickRate
    - Show overtime trend across shifts
    """
)


with st.expander("Understanding The Demo Questions & KPIs"):
    st.markdown(
        """
        ### Warehouse Structure

        - **Distribution Center (DC)** → Warehouse or fulfillment center location
        - **DC_Manager** → Manager responsible for warehouse operations
        - **Team Leader** → Supervises warehouse operational teams
        - **Shift** → Work shift
        - **Employee_ID** → Individual warehouse employee identifier

        ### KPI Definitions

        - **PickRate** → Measures picking productivity and operational speed
        - **SelectionRate_Cases** → Number of warehouse cases selected
        - **ReplenishmentRate** → Inventory replenishment productivity
        - **Overtime_pct** → Percentage of overtime worked
        - **IdleSelectionTime_pct** → Percentage of non-productive idle time
        - **OnTaskTime_pct** → Percentage of productive operational time

        ### What Is Anomaly Detection?

        The system flags warning and critical KPI risks by comparing actual KPI performance
        against benchmark thresholds.
        """
    )


# -----------------------------
# Load data
# -----------------------------

@st.cache_data
def load_data():
    # Load final warehouse KPI CSV data
    return load_kpi_data()


df = load_data()


# -----------------------------
# Sidebar filters
# -----------------------------

st.sidebar.header("Analysis Controls")

group_by = st.sidebar.selectbox(
    "Select analysis level",
    [
        "DC_ID",
        "DC_Manager",
        "Team_Leader",
        "Team",
        "Shift",
        "Employee_ID",
        "Country",
        "Region"
    ]
)

kpi = st.sidebar.selectbox(
    "Select KPI",
    [
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
)

n = st.sidebar.slider(
    "Top/Bottom N",
    min_value=2,
    max_value=20,
    value=5
)


# -----------------------------
# Dashboard metrics
# -----------------------------

st.subheader("Operational Dashboard")

m1, m2, m3, m4 = st.columns(4)

m1.metric("KPI Records", len(df))
m2.metric("Warehouses", df["DC_ID"].nunique())
m3.metric("Employees", df["Employee_ID"].nunique())
m4.metric(f"Average {kpi}", round(df[kpi].mean(), 2))


# -----------------------------
# Executive summary
# -----------------------------

st.subheader("Executive Summary")

summary_text = generate_executive_summary(
    group_by=group_by,
    kpis=ANOMALY_KPIS
)

st.text(summary_text)


# -----------------------------
# KPI summary
# -----------------------------

st.subheader("KPI Summary")

summary_df = get_kpi_summary(
    group_by=group_by,
    kpis=[kpi]
)

st.dataframe(summary_df, use_container_width=True)


# -----------------------------
# Benchmark status
# -----------------------------

st.subheader("Benchmark Status")

benchmark_df = benchmark_kpi_summary(
    group_by=group_by,
    kpi=kpi
)

st.dataframe(benchmark_df, use_container_width=True)


# -----------------------------
# Top and bottom performers
# -----------------------------

col_top, col_bottom = st.columns(2)

with col_top:
    st.subheader(f"Top {n} by {kpi}")

    top_df = get_top_performers(
        kpi=kpi,
        group_by=group_by,
        n=n
    )

    st.dataframe(top_df, use_container_width=True)

with col_bottom:
    st.subheader(f"Bottom {n} by {kpi}")

    bottom_df = get_bottom_performers(
        kpi=kpi,
        group_by=group_by,
        n=n
    )

    st.dataframe(bottom_df, use_container_width=True)


# -----------------------------
# Anomaly counts
# -----------------------------

st.subheader("Anomaly Counts")

anomaly_counts = get_anomaly_counts(
    group_by=group_by,
    kpis=ANOMALY_KPIS
)

st.dataframe(anomaly_counts, use_container_width=True)


# -----------------------------
# Priority recommendations
# -----------------------------

st.subheader("Priority Recommendations")

recommendations = get_priority_recommendations(
    group_by=group_by,
    kpis=ANOMALY_KPIS
)

st.dataframe(recommendations, use_container_width=True)


# -----------------------------
# KPI visualizations
# -----------------------------

st.subheader("KPI Visualizations")

viz_tab1, viz_tab2, viz_tab3, viz_tab4 = st.tabs(
    [
        "Top / Bottom Performance",
        "Benchmark Distribution",
        "Trend Analysis",
        "Anomaly Overview"
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

        st.plotly_chart(fig_top, use_container_width=True)

    with chart_col2:
        fig_bottom = create_bottom_performer_chart(
            bottom_df=bottom_df,
            group_by=group_by,
            kpi=kpi,
            n=n
        )

        st.plotly_chart(fig_bottom, use_container_width=True)


with viz_tab2:
    if "Benchmark_Status" in benchmark_df.columns:
        fig_benchmark = create_benchmark_chart(
            benchmark_df=benchmark_df,
            kpi=kpi
        )

        st.plotly_chart(fig_benchmark, use_container_width=True)
    else:
        st.warning("Benchmark_Status column not found.")


with viz_tab3:
    if "Week_Number" in df.columns:
        fig_trend = create_trend_chart(
            df=df,
            kpi=kpi
        )

        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.warning("Week_Number column not available.")


with viz_tab4:
    if anomaly_counts is not None and not anomaly_counts.empty:
        fig_anomaly = create_anomaly_chart(
            anomaly_counts=anomaly_counts,
            group_by=group_by
        )

        st.plotly_chart(fig_anomaly, use_container_width=True)
    else:
        st.success("No anomalies detected.")


# -----------------------------
# Quick demo questions
# -----------------------------

st.subheader("Quick Demo Questions")

if "selected_question" not in st.session_state:
    st.session_state.selected_question = ""

col1, col2 = st.columns(2)

with col1:
    if st.button("Top Managers by PickRate"):
        st.session_state.selected_question = "Which top 2 DC_Manager has the highest PickRate?"

    if st.button("Overtime Trend by Shift"):
        st.session_state.selected_question = "Show overtime trend across shifts"

    if st.button("Lowest Performing Warehouses"):
        st.session_state.selected_question = "Tell 2 lowest PickRate warehouses"

with col2:
    if st.button("Team PickRate Trend"):
        st.session_state.selected_question = "Show PickRate trend over time by Team"

    if st.button("Top Employees"):
        st.session_state.selected_question = "Show top 5 employees by PickRate"

    if st.button("Most Anomalies"):
        st.session_state.selected_question = "Which team leader has the most anomalies?"


# -----------------------------
# Chat history
# -----------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if st.session_state.chat_history:
    st.subheader("Conversation History")

    for chat in st.session_state.chat_history:
        st.markdown(f"**You:** {chat['question']}")
        st.markdown(f"**Copilot:** {chat['answer']}")
        st.markdown("---")


# -----------------------------
# Question input
# -----------------------------

question = st.text_input(
    "Ask your warehouse KPI question:",
    value=st.session_state.selected_question,
    placeholder="Example: Show top 5 employees by PickRate"
)

# -----------------------------
# Run copilot
# -----------------------------

if st.button("Ask Copilot"):

    if question.strip() == "":
        st.warning("Please enter a question.")

    else:

        with st.spinner("Analyzing warehouse KPIs..."):

            workflow_app = build_workflow()

            question_lower = question.lower()

            if "trend" in question_lower:
                intent = "comparison"
                ranking_type = "top"

            elif "bottom" in question_lower or "lowest" in question_lower:
                intent = "ranking"
                ranking_type = "bottom"

            else:
                intent = "ranking"
                ranking_type = "top"

            workflow_state = {
                "user_question": question,
                "intent": intent,
                "kpi": kpi,
                "group_by": group_by,
                "ranking_type": ranking_type,
                "n": n,
                "needs_rag": False
            }

            config = {
                "configurable": {
                    "thread_id": "streamlit-session"
                }
            }

            result = workflow_app.invoke(
                workflow_state,
                config=config
            )

            answer = result.get("final_answer", "")

            st.subheader("AI Answer")
            st.write(answer)

            st.session_state.chat_history.append(
                {
                    "question": question,
                    "answer": str(answer)
                }
            )