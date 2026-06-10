# WarehouseGPT – Enterprise Warehouse Performance Investigation Copilot

## Overview

WarehouseGPT is a GenAI-powered warehouse operations copilot designed to help warehouse leaders investigate operational performance, identify anomalies, benchmark KPIs, and receive actionable recommendations through natural language interaction.

The solution combines traditional analytics with Generative AI to transform warehouse KPI data into business-ready operational insights.

---

## Business Problem

Warehouse operations generate large volumes of KPI data across distribution centers, managers, teams, shifts, and employees.

Although dashboards can show performance metrics, they often do not explain:

* Why performance deteriorated
* Which areas require attention
* What operational risks exist
* What corrective actions should be taken

WarehouseGPT acts as an AI-powered investigation assistant that helps users analyze warehouse performance more efficiently.

---

## Key Features

### KPI Analytics Engine

* Dynamic KPI aggregation
* Multi-level hierarchy analysis
* Top and bottom performer identification
* KPI trend analysis

### Benchmark Engine

* Compare KPI performance against operational benchmarks
* KPI classification:

  * World Class
  * On Target
  * Warning
  * Critical

### Anomaly Detection Engine

* Detect abnormal warehouse performance
* Identify KPI deviations
* Highlight operational risks

### Recommendation Engine

* Generate operational improvement recommendations
* Link KPI issues to corrective actions
* Provide business-friendly guidance

### Executive Summary Engine

* Generate management-ready summaries
* Convert KPI results into business language

### Visualization Engine

* Interactive Plotly charts
* Top and bottom performer analysis
* KPI trend visualizations
* Benchmark distribution charts
* Anomaly overview dashboards

### Retrieval-Augmented Generation (RAG)

* Search warehouse operational documents
* Retrieve SOP guidance
* Provide grounded AI responses

### LangGraph Workflow

* Multi-step workflow orchestration
* Memory-enabled AI interactions
* Structured decision flow

### Streamlit User Interface

* Interactive analytics dashboard
* Natural language question answering
* KPI exploration and visualization

---

## Architecture

WarehouseGPT follows a modular architecture:

```text
User -> Streamlit UI ->LangGraph Workflow ->
   │
   ├── KPI Engine
   ├── Benchmark Engine
   ├── Anomaly Engine
   ├── Recommendation Engine
   ├── Summary Engine
   ├── Visualization Engine
   └──
```
