# Import Libraries

import plotly.express as px


# Detect Chart Intent

def detect_chart_intent(question):

    question_lower = question.lower()

    chart_keywords = [
        "chart",
        "graph",
        "plot",
        "visualize",
        "visualization",
        "trend",
        "dashboard"
    ]

    # Detect whether chart is required
    chart_required = any(
        keyword in question_lower
        for keyword in chart_keywords
    )

    # Auto-enable charts for ranking/comparison questions
    if any(word in question_lower for word in [
        "compare",
        "comparison",
        "top",
        "bottom",
        "highest",
        "lowest",
        "best",
        "worst"
    ]):
        chart_required = True

    # Detect chart type
    if "trend" in question_lower or "over time" in question_lower:

        chart_type = "line"

    elif "compare" in question_lower or "comparison" in question_lower:

        chart_type = "bar"

    elif "distribution" in question_lower:

        chart_type = "histogram"

    else:

        chart_type = "bar"

    # Detect time-based requirement
    time_based = any(
        word in question_lower
        for word in [
            "weekly",
            "trend",
            "over time",
            "week"
        ]
    )

    return {
        "chart_required": chart_required,
        "chart_type": chart_type,
        "time_based": time_based
    }


# Create Chart Data

def create_chart_data(
    data,
    question,
    kpi_rules,
    extract_top_bottom_n
):

    chart_intent = detect_chart_intent(question)

    detected_kpi = None

    question_lower = question.lower()

    # Detect KPI from question
    for kpi in kpi_rules.keys():

        normalized_kpi = (
            kpi.lower()
            .replace("_", "")
            .replace("%", "")
        )

        normalized_question = (
            question_lower
            .replace(" ", "")
            .replace("_", "")
        )

        if normalized_kpi in normalized_question:

            detected_kpi = kpi
            break

        # Fallback KPI detection for natural language terms

    if detected_kpi is None:

        if "pickrate" in question_lower or "pick rate" in question_lower:
            detected_kpi = "PickRate"

        elif "selection" in question_lower:
            detected_kpi = "SelectionRate_Cases"

        elif "replenishment" in question_lower:
            detected_kpi = "ReplenishmentRate"

        elif "idle" in question_lower:
            detected_kpi = "IdleSelectionTime_pct"

        elif "ontask" in question_lower or "on task" in question_lower:
            detected_kpi = "OnTaskTime_pct"

        elif "overtime" in question_lower:
            detected_kpi = "Overtime_pct"
            
    chart_intent["detected_kpi"] = detected_kpi


    time_based = chart_intent["time_based"]

    ranking_type, n = extract_top_bottom_n(question)

    # Handle missing KPI
    if detected_kpi is None:

        return None, "No KPI detected in question."

    # Detect aggregation level
    if "manager" in question_lower or "dc_manager" in question_lower:

        group_columns = ["DC_Manager"]

    elif "team leader" in question_lower or "leader" in question_lower:

        group_columns = ["Team_Leader"]

    elif "team" in question_lower:

        group_columns = ["Team"]

    elif "shift" in question_lower:

        group_columns = ["Shift"]

    elif "employee" in question_lower:

        group_columns = ["Employee_ID"]

    else:

        group_columns = ["Distribution_Center"]

    # Handle week sorting
    if time_based:

        data = data.copy()

        data["Week_Number"] = (
            data["Week"]
            .str.replace("WK", "", regex=False)
            .astype(int)
        )

        group_columns = ["Week_Number", "Week"] + group_columns

    # Create aggregated chart dataset
    chart_data = (
        data
        .groupby(group_columns)[detected_kpi]
        .mean()
        .round(2)
        .reset_index()
    )

    # Sort weeks correctly
    if time_based:

        chart_data = chart_data.sort_values("Week_Number")

    # Apply ranking logic
    comparison = kpi_rules[detected_kpi]["comparison"]

    if ranking_type == "top":

        ascending = False if comparison == "higher" else True

    elif ranking_type == "bottom":

        ascending = True if comparison == "higher" else False

    else:

        ascending = False if comparison == "higher" else True

    chart_data = chart_data.sort_values(
        detected_kpi,
        ascending=ascending
    )

    # Apply top/bottom filtering
    if ranking_type is not None and n is not None:

        chart_data = chart_data.head(n)

    return chart_data, chart_intent


# Create Interactive Chart

def create_dynamic_chart(chart_data, chart_intent):

    # Handle empty chart data
    if chart_data is None:

        return None

    detected_kpi = chart_intent["detected_kpi"]

    time_based = chart_intent["time_based"]

    # Create line chart for trends
    if time_based:

        chart_data = chart_data.sort_values("Week_Number")

        color_columns = [
            col for col in chart_data.columns
            if col not in [
                "Week_Number",
                "Week",
                detected_kpi
            ]
        ]

        color_axis = (
            color_columns[0]
            if len(color_columns) > 0
            else None
        )

        fig = px.line(
            chart_data,
            x="Week",
            y=detected_kpi,
            color=color_axis,
            markers=True,
            title=f"{detected_kpi} Trend Over Time"
        )

        # Force proper week order
        fig.update_xaxes(
            categoryorder="array",
            categoryarray=chart_data["Week"].unique()
        )

    # Create bar chart for comparisons
    else:

        x_axis = [
            col for col in chart_data.columns
            if col not in [
                detected_kpi,
                "Week_Number"
            ]
        ][0]

        fig = px.bar(
            chart_data,
            x=x_axis,
            y=detected_kpi,
            title=f"{detected_kpi} by {x_axis}"
        )

    return fig