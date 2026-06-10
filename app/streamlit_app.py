import streamlit as st

# Import pandas for table display
import pandas as pd

# Import sys and os for project path handling
import sys
import os

# Import dotenv for environment variables
from dotenv import load_dotenv

# Add src folder to Python path
current_dir = os.path.dirname(__file__)

src_path = os.path.abspath(
    os.path.join(current_dir, "../src")
)

sys.path.insert(0, src_path)


# Import final project engines
from data_loader import load_kpi_data
from kpi_engine import get_kpi_summary, get_top_performers, get_bottom_performers
from benchmark_engine import benchmark_kpi_summary
from anomaly_engine import get_anomaly_counts, ANOMALY_KPIS
from recommendation_engine import get_priority_recommendations
from summary_engine import generate_executive_summary
from chart_engine import (
    get_top_n_chart_data,
    get_bottom_n_chart_data,
    get_benchmark_distribution_data,
    get_anomaly_chart_data
)
from langgraph_workflow import build_workflow


# Load environment variables
load_dotenv()


# Configure Streamlit page
st.set_page_config(
    page_title="GenAI Warehouse Operations Copilot",
    layout="wide"
)


# Create title layout
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


# App overview
st.markdown(
    """
    This app is a GenAI-powered analytics assistant for warehouse operations.

    It helps users ask natural language questions about warehouse KPI performance, anomalies,
    trends, managers, teams, shifts, and employees.

    The app combines:

    - KPI analytics engine
    - benchmark engine
    - anomaly detection engine
    - recommendation engine
    - RAG knowledge retrieval
    - LangGraph workflow orchestration
    - interactive KPI visualizations
    """
)


# Business problem section
st.info(
    "Business problem: Warehouse leaders often need to quickly understand KPI performance, "
    "identify operational issues, and explain anomalies across distribution centers, managers, "
    "teams, shifts, and employees. This copilot converts warehouse KPI data into "
    "business-ready operational insights."
)


# Example questions section
st.markdown(
    """
    ### Example Questions You Can Ask

    - Which top 2 DC_Manager has the highest PickRate?
    - Tell 2 lowest PickRate warehouses
    - Show chart comparing PickRate across DC_Manager
    - Show PickRate trend over time by Team
    - Which team leader has the most anomalies?
    - Show top 5 employees by PickRate
    - Show overtime trend across shifts
    """
)


# Demo guidance section
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


# Load KPI data using final data loader
@st.cache_data
def load_data():
    # Load final warehouse KPI CSV data
    return load_kpi_data()


# Store KPI data
df = load_data()


# Sidebar filters
st.sidebar.header("Analysis Controls")

# Select hierarchy level
group_by = st.sidebar.selectbox(
    "Select analysis level",
    ["DC_ID", "DC_Manager", "Team_Leader", "Team", "Shift", "Employee_ID", "Country", "Region"]
)

# Select KPI
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

# Select top/bottom ranking size
n = st.sidebar.slider(
    "Top/Bottom N",
    min_value=2,
    max_value=20,
    value=5
)


# Dashboard metrics
st.subheader("Operational Dashboard")

m1, m2, m3, m4 = st.columns(4)

m1.metric("KPI Records", len(df))
m2.metric("Warehouses", df["DC_ID"].nunique())
m3.metric("Employees", df["Employee_ID"].nunique())
m4.metric(f"Average {kpi}", round(df[kpi].mean(), 2))


# Executive summary
st.subheader("Executive Summary")

summary_text = generate_executive_summary(
    group_by=group_by,
    kpis=ANOMALY_KPIS
)

st.text(summary_text)


# KPI tables
st.subheader("KPI Summary")

summary_df = get_kpi_summary(
    group_by=group_by,
    kpis=[kpi]
)

st.dataframe(summary_df, use_container_width=True)


# Benchmark table
st.subheader("Benchmark Status")

benchmark_df = benchmark_kpi_summary(
    group_by=group_by,
    kpi=kpi
)

st.dataframe(benchmark_df, use_container_width=True)


# Top and bottom performers
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


# Anomaly counts
st.subheader("Anomaly Counts")

anomaly_counts = get_anomaly_counts(
    group_by=group_by,
    kpis=ANOMALY_KPIS
)

st.dataframe(anomaly_counts, use_container_width=True)


# Recommendations
st.subheader("Priority Recommendations")

recommendations = get_priority_recommendations(
    group_by=group_by,
    kpis=ANOMALY_KPIS
)

st.dataframe(recommendations, use_container_width=True)

# Quick demo questions
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


# Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# Show previous chat history
if st.session_state.chat_history:
    st.subheader("Conversation History")

    for chat in st.session_state.chat_history:
        st.markdown(f"**You:** {chat['question']}")
        st.markdown(f"**Copilot:** {chat['answer']}")
        st.markdown("---")


# Question input
question = st.text_input(
    "Ask your warehouse KPI question:",
    value=st.session_state.selected_question,
    placeholder="Example: Show top 5 employees by PickRate"
)


# Run copilot
if st.button("Ask Copilot"):
    if question.strip() == "":
        st.warning("Please enter a question.")

    else:
        with st.spinner("Analyzing warehouse KPIs..."):

            # Build LangGraph workflow
            workflow_app = build_workflow()

            # Temporary structured state until intent extraction is connected
            workflow_state = {
                "user_question": question,
                "intent": "ranking",
                "kpi": kpi,
                "group_by": group_by,
                "ranking_type": "top",
                "n": n,
                "needs_rag": False
            }

            # LangGraph memory config
            config = {
                "configurable": {
                    "thread_id": "streamlit-session"
                }
            }

            # Run LangGraph workflow
            result = workflow_app.invoke(
                workflow_state,
                config=config
            )

            # Get final workflow output
            answer = result.get("final_answer", {})

            # Show answer
            st.subheader("AI Answer")
            st.write(answer)

            # Save chat history
            st.session_state.chat_history.append(
                {
                    "question": question,
                    "answer": str(answer)
                }
            )