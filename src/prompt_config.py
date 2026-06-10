# Few-shot examples help the LLM understand how to map user questions into structured intent
FEW_SHOT_EXAMPLES = [
    {
        "user_question": "Show top 10 employees by PickRate",
        "expected_output": {
            "intent": "ranking",
            "kpi": "PickRate",
            "group_by": "Employee_ID",
            "entity": None,
            "selected_values": [],
            "ranking_type": "top",
            "n": 10,
            "needs_chart": True,
            "needs_rag": False
        }
    },
    {
        "user_question": "Show bottom 5 managers by overtime",
        "expected_output": {
            "intent": "ranking",
            "kpi": "Overtime_pct",
            "group_by": "DC_Manager",
            "entity": None,
            "selected_values": [],
            "ranking_type": "bottom",
            "n": 5,
            "needs_chart": True,
            "needs_rag": False
        }
    },
    {
        "user_question": "Why is DC003 underperforming?",
        "expected_output": {
            "intent": "investigation",
            "kpi": None,
            "group_by": "DC_ID",
            "entity": "DC003",
            "selected_values": ["DC003"],
            "ranking_type": None,
            "n": None,
            "needs_chart": True,
            "needs_rag": True
        }
    },
    {
        "user_question": "Compare DC003 and DC006 by PickRate and Overtime",
        "expected_output": {
            "intent": "comparison",
            "kpi": None,
            "group_by": "DC_ID",
            "entity": None,
            "selected_values": ["DC003", "DC006"],
            "ranking_type": None,
            "n": None,
            "needs_chart": True,
            "needs_rag": False
        }
    },
    {
        "user_question": "What is the escalation process for high overtime?",
        "expected_output": {
            "intent": "sop_question",
            "kpi": "Overtime_pct",
            "group_by": None,
            "entity": None,
            "selected_values": [],
            "ranking_type": None,
            "n": None,
            "needs_chart": False,
            "needs_rag": True
        }
    },
    {
        "user_question": "Summarize operational risks for Q3",
        "expected_output": {
            "intent": "executive_summary",
            "kpi": None,
            "group_by": "DC_ID",
            "entity": None,
            "selected_values": [],
            "ranking_type": None,
            "n": None,
            "needs_chart": False,
            "needs_rag": True
        }
    }
]


# Structured output schema defines the JSON fields the LLM must return
INTENT_OUTPUT_SCHEMA = {
    "intent": "ranking | comparison | benchmark_check | anomaly_detection | recommendation | investigation | sop_question | executive_summary | chart_request | unknown",
    "kpi": "KPI name as string or null",
    "group_by": "Hierarchy level as string or null",
    "entity": "Single entity value as string or null",
    "selected_values": "List of entity values",
    "ranking_type": "top | bottom | null",
    "n": "Integer ranking size or null",
    "needs_chart": "Boolean",
    "needs_rag": "Boolean"
}


# Valid KPI names allowed in structured output
VALID_KPIS = [
    "SelectionRate_Cases",
    "PickRate",
    "ReplenishmentRate",
    "IdleSelectionTime_pct",
    "OnTaskTime_pct",
    "Overtime_pct",
    "LaborHours",
    "LaborCost_EUR",
    "OrdersProcessed",
    "UnitsProcessed",
    "ForecastVolume",
    "ActualVolume",
    "CapacityUtilization_pct",
    "EquipmentDowntime_Min",
    "InventoryAccuracy_pct",
    "PickingErrorRate_pct",
    "OnTimeShipment_pct",
    "Absenteeism_pct",
    "SafetyIncidents"
]


# Valid hierarchy levels allowed in structured output
VALID_GROUP_BY_FIELDS = [
    "DC_ID",
    "DC_Manager",
    "Team_Leader",
    "Team",
    "Shift",
    "Employee_ID",
    "Country",
    "Region"
]


# Format few-shot examples into readable text for prompt injection
def format_few_shot_examples():
    # Create empty text block for all examples
    examples_text = ""

    # Convert each example into clear prompt text
    for example in FEW_SHOT_EXAMPLES:
        examples_text += f"""
User question:
{example["user_question"]}

Expected JSON:
{example["expected_output"]}

---
"""

    # Return formatted examples for prompt templates
    return examples_text


# Return structured output instructions for the LLM
def get_structured_output_instructions():
    # Return schema and allowed values so the model follows consistent JSON structure
    return {
        "schema": INTENT_OUTPUT_SCHEMA,
        "valid_kpis": VALID_KPIS,
        "valid_group_by_fields": VALID_GROUP_BY_FIELDS
    }


# Run quick test only when this file is executed directly
if __name__ == "__main__":
    # Print few-shot examples to verify formatting
    print(format_few_shot_examples())

    # Print structured output instructions to verify schema
    print(get_structured_output_instructions())