import re


KPI_ALIASES = {
    "total safety incidents": "SafetyIncidents",
    "safety incidents": "SafetyIncidents",
    "safetyincidents": "SafetyIncidents",
    "safety": "SafetyIncidents",

    "replenishmentrate": "ReplenishmentRate",
    "replenishment": "ReplenishmentRate",

    "selectionrate": "SelectionRate_Cases",
    "selection": "SelectionRate_Cases",

    "pickrate": "PickRate",
    "pick rate": "PickRate",
    "picking": "PickRate",

    "overtime": "Overtime_pct",

    "idle selection time": "IdleSelectionTime_pct",
    "idle time": "IdleSelectionTime_pct",
    "idle": "IdleSelectionTime_pct",

    "on task time": "OnTaskTime_pct",
    "on task": "OnTaskTime_pct",
    "ontask": "OnTaskTime_pct",

    "inventory accuracy": "InventoryAccuracy_pct",
    "accuracy": "InventoryAccuracy_pct",

    "picking error": "PickingErrorRate_pct",
    "error": "PickingErrorRate_pct",

    "on time shipment": "OnTimeShipment_pct",
    "shipment": "OnTimeShipment_pct",

    "absenteeism": "Absenteeism_pct",
    "downtime": "EquipmentDowntime_Min",
    "equipment downtime": "EquipmentDowntime_Min",
    "capacity": "CapacityUtilization_pct",
    "capacity utilization": "CapacityUtilization_pct"
}


GROUP_ALIASES = {
    "team leader": "Team_Leader",
    "team leaders": "Team_Leader",
    "employees": "Employee_ID",
    "employee": "Employee_ID",
    "managers": "DC_Manager",
    "manager": "DC_Manager",
    "teams": "Team",
    "team": "Team",
    "shifts": "Shift",
    "shift": "Shift",
    "warehouses": "DC_ID",
    "warehouse": "DC_ID",
    "dc": "DC_ID",
    "country": "Country",
    "region": "Region"
}


def extract_n(question, default_n=5):
    question_lower = question.lower()

    match = re.search(r"\b(top|bottom|lowest|highest)\s+(\d+)", question_lower)
    if match:
        return int(match.group(2))

    match = re.search(r"\b(\d+)\s+(lowest|highest|top|bottom)", question_lower)
    if match:
        return int(match.group(1))

    return default_n


def parse_question(question, default_kpi, default_group_by, default_n):
    question_lower = question.lower()

    selected_kpi = default_kpi
    selected_group_by = default_group_by

    for keyword, detected_kpi in KPI_ALIASES.items():
        if keyword in question_lower:
            selected_kpi = detected_kpi
            break

    for keyword, detected_group in GROUP_ALIASES.items():
        if keyword in question_lower:
            selected_group_by = detected_group
            break

    trend_keywords = [
        "trend",
        "weekly",
        "week",
        "weeks",
        "over time",
        "time series",
        "movement",
        "change over time"
    ]

    if any(keyword in question_lower for keyword in trend_keywords):
        intent = "trend"
    elif "anomal" in question_lower:
        intent = "anomaly"
    elif "recommend" in question_lower or "action" in question_lower:
        intent = "recommendation"
    else:
        intent = "ranking"

    if (
        "bottom" in question_lower
        or "lowest" in question_lower
        or "worst" in question_lower
        or "underperform" in question_lower
    ):
        ranking_type = "bottom"
    else:
        ranking_type = "top"

    n = extract_n(question, default_n)

    return {
        "intent": intent,
        "kpi": selected_kpi,
        "group_by": selected_group_by,
        "ranking_type": ranking_type,
        "n": n,
        "needs_recommendation": True
    }