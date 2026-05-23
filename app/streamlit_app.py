# Import libraries

import streamlit as st
import pandas as pd
import sys
import os
from dotenv import load_dotenv
from openai import OpenAI


# Add src folder to Python path

current_dir = os.path.dirname(__file__)

src_path = os.path.abspath(
    os.path.join(current_dir, "../src")
)

sys.path.insert(0, src_path)


# Import project engines

from kpi_engine import kpi_rules
from anomaly_engine import detect_anomaly
from summary_engine import create_dynamic_summary, extract_top_bottom_n
from ai_engine import ask_warehouse_copilot
from chart_engine import detect_chart_intent, create_chart_data, create_dynamic_chart


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

    - KPI rule engine
    - anomaly detection
    - dynamic data aggregation
    - OpenAI-powered business explanation
    - interactive Plotly charts
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


# Basic access control

APP_PASSWORD = st.secrets.get("APP_PASSWORD", "")

password = st.text_input(
    "Enter access password:",
    type="password"
)

if password != APP_PASSWORD:
    st.warning("Please enter the correct password to access the copilot.")
    st.stop()


# Load API key

load_dotenv()

api_key = st.secrets.get(
    "OPENAI_API_KEY",
    os.getenv("OPENAI_API_KEY")
)


# Create OpenAI client

client = OpenAI(api_key=api_key)


# Build dataset file path

dataset_path = os.path.abspath(
    os.path.join(
        current_dir,
        "../datasets/Step 1. synthetic_warehouse_kpi_data.xlsx"
    )
)


# Load warehouse KPI dataset

df = pd.read_excel(dataset_path)


# Apply anomaly detection

df[["Anomaly_Flag", "Anomaly_Reason"]] = df.apply(
    lambda row: pd.Series(
        detect_anomaly(
            row=row,
            kpi_rules=kpi_rules
        )
    ),
    axis=1
)


# Initialize chat history

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# Initialize selected question

if "selected_question" not in st.session_state:
    st.session_state.selected_question = ""


# Display previous chat history

if st.session_state.chat_history:
    st.subheader("Conversation History")

    for chat in reversed(st.session_state.chat_history):
        st.markdown(f"**You:** {chat['question']}")
        st.markdown(f"**Copilot:** {chat['answer']}")
        st.markdown("---")


# Sample question buttons

st.subheader("Quick Demo Questions")

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


# Question input box

question = st.text_input(
    "Ask your warehouse KPI question:",
    value=st.session_state.selected_question,
    placeholder="Example: Show chart comparing PickRate across DC_Manager"
)


# Run copilot after button click

if st.button("Ask Copilot"):

    if question.strip() == "":
        st.warning("Please enter a question.")

    else:
        with st.spinner("Analyzing warehouse KPIs..."):

            result = ask_warehouse_copilot(
                question=question,
                data=df,
                kpi_rules=kpi_rules,
                client=client,
                create_dynamic_summary=create_dynamic_summary
            )

            st.subheader("AI Answer")

            st.write(
                result.get("ai_answer")
            )

            st.session_state.chat_history.append(
                {
                    "question": question,
                    "answer": result.get("ai_answer")
                }
            )

            chart_intent = detect_chart_intent(question)

            fig = None

            if chart_intent["chart_required"]:

                chart_data, chart_intent = create_chart_data(
                    data=df,
                    question=question,
                    kpi_rules=kpi_rules,
                    extract_top_bottom_n=extract_top_bottom_n
                )

                fig = create_dynamic_chart(
                    chart_data=chart_data,
                    chart_intent=chart_intent
                )

                if fig is not None:
                    st.subheader("Interactive Chart")

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

            if result.get("context_table") is not None:

                st.info(
                    "The AI response above was generated using the following aggregated warehouse KPI data."
                )

                st.dataframe(
                    result.get("context_table")
                )