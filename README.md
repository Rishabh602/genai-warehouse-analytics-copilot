# GenAI Warehouse Operations Copilot

This project is a prototype of a GenAI-powered warehouse analytics assistant built using Python, OpenAI, Streamlit, and Plotly.

The goal of the project was to explore how Large Language Models (LLMs) can be combined with traditional KPI analytics to help warehouse operations teams analyze performance data using natural language questions.

Instead of manually filtering dashboards, users can ask questions such as:

- Which managers have the highest PickRate?
- Show overtime trend across shifts
- Which teams have the most anomalies?
- Show top employees by productivity

The system dynamically aggregates warehouse KPI data, detects anomalies, generates business-friendly AI insights, and creates interactive visualizations.

---

# Why I Built This

Warehouse operations usually involve large KPI dashboards and manual analysis across managers, teams, shifts, and employees.

I wanted to experiment with how GenAI could act as an operational analytics copilot that explains warehouse performance in a more conversational and business-friendly way.

The focus of this project was not only AI responses, but also:
- dynamic KPI aggregation
- explainable AI grounding
- anomaly detection
- prompt engineering
- modular backend design
- interactive chart generation

---

# Main Features

- Dynamic warehouse KPI summarization
- AI-generated operational insights
- OpenAI integration
- KPI anomaly detection
- Trend analysis
- Top/bottom ranking detection
- Interactive Plotly charts
- Streamlit frontend
- Moderation and scope validation
- Explainable KPI context tables