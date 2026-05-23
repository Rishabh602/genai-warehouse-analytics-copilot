import re


def extract_top_bottom_n(question):

    question_lower = question.lower()

    number_match = re.search(
        r"(top|bottom|best|worst|highest|lowest)\s+(\d+)",
        question_lower
    )

    reverse_number_match = re.search(
        r"(\d+)\s+(top|bottom|best|worst|highest|lowest)",
        question_lower
    )

    if number_match:
        ranking_type_word = number_match.group(1)
        n = int(number_match.group(2))

    elif reverse_number_match:
        n = int(reverse_number_match.group(1))
        ranking_type_word = reverse_number_match.group(2)

    else:
        ranking_type_word = None
        n = None

    if ranking_type_word in ["top", "best", "highest"]:
        ranking_type = "top"

    elif ranking_type_word in ["bottom", "worst", "lowest"]:
        ranking_type = "bottom"

    else:
        ranking_type = None

    return ranking_type, n

def create_dynamic_summary(data, question, kpi_rules):

    all_kpis = list(kpi_rules.keys())
    question_lower = question.lower()

    ranking_type, n = extract_top_bottom_n(question)

    include_week = any(word in question_lower for word in [
        "week",
        "weekly",
        "trend",
        "over time",
        "wk"
    ])

    if "employee" in question_lower:

        group_columns = [
            "Distribution_Center",
            "DC_Manager",
            "Team",
            "Team_Leader",
            "Shift",
            "Employee_ID"
        ]

        summary_level = "Employee Level"

    elif "team leader" in question_lower or "leader" in question_lower:

        group_columns = [
            "Distribution_Center",
            "DC_Manager",
            "Team",
            "Team_Leader",
            "Shift"
        ]

        summary_level = "Team Leader Level"

    elif "team" in question_lower:

        group_columns = [
            "Distribution_Center",
            "DC_Manager",
            "Team",
            "Shift"
        ]

        summary_level = "Team Level"

    elif "dc_manager" in question_lower or "dc manager" in question_lower or "manager" in question_lower:

        group_columns = [
            "DC_Manager"
        ]

        summary_level = "DC Manager Level"

    elif "shift" in question_lower:

        group_columns = [
            "Distribution_Center",
            "Shift"
        ]

        summary_level = "Shift Level"

    else:

        group_columns = [
            "Distribution_Center"
        ]

        summary_level = "Distribution Center Level"

    if include_week:

        group_columns = ["Week"] + group_columns
        summary_level = "Weekly " + summary_level

    summary = data.groupby(group_columns)[all_kpis].mean().round(2).reset_index()

    anomaly_summary = data.groupby(group_columns)["Anomaly_Flag"].apply(
        lambda x: (x == "Anomaly").sum()
    ).reset_index(name="Anomaly_Count")

    summary = summary.merge(
        anomaly_summary,
        on=group_columns,
        how="left"
    )

    selected_kpi = None

    normalized_question = (
        question_lower
        .replace(" ", "")
        .replace("_", "")
        .replace("%", "")
    )

    for kpi in all_kpis:

        normalized_kpi = (
            kpi.lower()
            .replace(" ", "")
            .replace("_", "")
            .replace("%", "")
        )

        if normalized_kpi in normalized_question:
            selected_kpi = kpi
            break

    if selected_kpi is None:

        if "pickrate" in question_lower or "pick rate" in question_lower:
            selected_kpi = "PickRate"

        elif "selection" in question_lower:
            selected_kpi = "SelectionRate_Cases"

        elif "replenishment" in question_lower:
            selected_kpi = "ReplenishmentRate"

        elif "idle" in question_lower:
            selected_kpi = "IdleSelectionTime_pct"

        elif "ontask" in question_lower or "on task" in question_lower:
            selected_kpi = "OnTaskTime_pct"

        elif "overtime" in question_lower:
            selected_kpi = "Overtime_pct"

    if selected_kpi is not None:

        comparison = kpi_rules[selected_kpi]["comparison"]

        if ranking_type == "top":
            ascending = False if comparison == "higher" else True

        elif ranking_type == "bottom":
            ascending = True if comparison == "higher" else False

        else:
            ascending = False if comparison == "higher" else True

        summary = summary.sort_values(
            selected_kpi,
            ascending=ascending
        )

    else:

        summary = summary.sort_values(
            "Anomaly_Count",
            ascending=False
        )

    if ranking_type is not None and n is not None:
        summary = summary.head(n)

    return summary_level, summary