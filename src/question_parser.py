import re


KPI_ALIASES = {
    "pickrate": "PickRate",
    "pick rate": "PickRate",
    "replenishment": "ReplenishmentRate",
    "replenishmentrate": "ReplenishmentRate",
    "selection": "SelectionRate_Cases",
    "selectionrate": "SelectionRate_Cases",
    "overtime": "Overtime_pct",
    "idle": "IdleSelectionTime_pct",
    "idle time": "IdleSelectionTime_pct",
    "on task": "OnTaskTime_pct",
    "ontask": "OnTaskTime_pct",
    "accuracy": "InventoryAccuracy_pct",
    "error": "PickingErrorRate_pct",
    "shipment": "OnTimeShipment_pct",
    "absenteeism": "Absenteeism_pct",
    "safety": "SafetyIncidents",
    "downtime": "EquipmentDowntime_Min",
    "capacity": "CapacityUtilization_pct"
}


GROUP_ALIASES = {
    "employee": "Employee_ID",
    "employees": "Employee_ID",
    "manager": "DC_Manager",
    "managers": "DC_Manager",
    "team leader": "Team_Leader",
    "team leaders": "Team_Leader",
    "team": "Team",
    "teams": "Team",
    "shift": "Shift",
    "shifts": "Shift",
    "warehouse": "DC_ID",
    "warehouses": "DC_ID",
    "dc": "DC_ID",
    "country": "Country",
    "region": "Region"
}


def extract_n(question, default_n=5):
    match = re.search(r"\b(top|bottom|lowest|highest)\s+(\d+)", question.lower())

    if match:
        return int(match.group(2))

    return default_n


def parse_question(question, default_kpi, default_group_by, default_n):
    question_lower = question.lower()

    selected_kpi = default_kpi
    selected_group_by = default_group_by

    for keyword, kpi in KPI_ALIASES.items():
        if keyword in question_lower:
            selected_kpi = kpi
            break

    for keyword, group_by in GROUP_ALIASES.items():
        if keyword in question_lower:
            selected_group_by = group_by
            break

    if "trend" in question_lower or "over time" in question_lower:
        intent = "trend"
    elif "bottom" in question_lower or "lowest" in question_lower:
        intent = "ranking"
    elif "top" in question_lower or "highest" in question_lower:
        intent = "ranking"
    elif "anomal" in question_lower:
        intent = "anomaly"
    elif "recommend" in question_lower or "action" in question_lower:
        intent = "recommendation"
    else:
        intent = "ranking"

    ranking_type = "bottom" if "bottom" in question_lower or "lowest" in question_lower else "top"

    n = extract_n(
        question=question,
        default_n=default_n
    )

    return {
        "intent": intent,
        "kpi": selected_kpi,
        "group_by": selected_group_by,
        "ranking_type": ranking_type,
        "n": n
    }