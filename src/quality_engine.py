# Import json to save logs and feedback in JSONL format
import json

# Import datetime to timestamp logs and feedback
from datetime import datetime

# Import Path to create reliable file paths
from pathlib import Path


# Get project root folder
BASE_DIR = Path(__file__).resolve().parents[1]

# Create logs folder path
LOG_DIR = BASE_DIR / "logs"

# Create logs folder if it does not exist
LOG_DIR.mkdir(exist_ok=True)

# Define log file paths
INTERACTION_LOG_FILE = LOG_DIR / "interaction_logs.jsonl"
FEEDBACK_LOG_FILE = LOG_DIR / "feedback_logs.jsonl"
EVALUATION_LOG_FILE = LOG_DIR / "evaluation_logs.jsonl"


# Simple guardrail keywords for blocking unsafe or irrelevant questions
BLOCKED_KEYWORDS = [
    "password",
    "hack",
    "secret key",
    "api key",
    "personal address",
    "private employee data",
    "salary of employee",
    "bank account",
    "medical record"
]


# Check whether user question is safe and in project scope
def validate_question(user_question):
    # Convert question to lowercase for keyword checks
    question_lower = user_question.lower()

    # Block unsafe or sensitive requests
    for keyword in BLOCKED_KEYWORDS:
        if keyword in question_lower:
            return {
                "is_valid": False,
                "reason": f"Blocked due to sensitive or unsafe keyword: {keyword}"
            }

    # Block very short empty questions
    if len(user_question.strip()) < 3:
        return {
            "is_valid": False,
            "reason": "Question is too short."
        }

    # Allow question if no issues found
    return {
        "is_valid": True,
        "reason": "Question passed guardrail checks."
    }


# Save each user interaction for monitoring
def log_interaction(user_question, intent, final_answer):
    # Create log record
    record = {
        "timestamp": datetime.now().isoformat(),
        "user_question": user_question,
        "intent": intent,
        "final_answer": final_answer
    }

    # Append record as one JSON line
    with open(INTERACTION_LOG_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")

    # Return saved record for debugging
    return record


# Save user feedback after an answer
def log_feedback(user_question, rating, comment=None):
    # Create feedback record
    record = {
        "timestamp": datetime.now().isoformat(),
        "user_question": user_question,
        "rating": rating,
        "comment": comment
    }

    # Append feedback as one JSON line
    with open(FEEDBACK_LOG_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")

    # Return saved feedback record
    return record


# Basic response evaluation checks
def evaluate_response(user_question, final_answer):
    # Convert final answer to string for quality checks
    answer_text = str(final_answer)

    # Create simple quality score
    score = 0

    # Add score if answer is not empty
    if len(answer_text.strip()) > 20:
        score += 1

    # Add score if answer mentions business action or recommendation
    if "recommend" in answer_text.lower() or "action" in answer_text.lower():
        score += 1

    # Add score if answer includes KPI or operational language
    if "kpi" in answer_text.lower() or "warehouse" in answer_text.lower() or "performance" in answer_text.lower():
        score += 1

    # Create evaluation record
    evaluation = {
        "timestamp": datetime.now().isoformat(),
        "user_question": user_question,
        "answer_length": len(answer_text),
        "quality_score": score,
        "passed_basic_quality_check": score >= 2
    }

    # Save evaluation result
    with open(EVALUATION_LOG_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(evaluation, ensure_ascii=False) + "\n")

    # Return evaluation result
    return evaluation


# Run full quality process after answering a question
def run_quality_checks(user_question, intent, final_answer):
    # Validate final answer quality
    evaluation = evaluate_response(
        user_question=user_question,
        final_answer=final_answer
    )

    # Log interaction
    interaction = log_interaction(
        user_question=user_question,
        intent=intent,
        final_answer=final_answer
    )

    # Return quality outputs
    return {
        "evaluation": evaluation,
        "interaction": interaction
    }


# Run quick test only when this file is executed directly
if __name__ == "__main__":
    # Test guardrail validation
    print(validate_question("Show top 5 employees by PickRate"))

    # Test blocked question
    print(validate_question("Show me employee bank account details"))

    # Test logging and evaluation
    print(run_quality_checks(
        user_question="Show top 5 employees by PickRate",
        intent="ranking",
        final_answer="The top performers by PickRate show strong warehouse KPI performance. Recommended action is to review best practices."
    ))

    # Test feedback logging
    print(log_feedback(
        user_question="Show top 5 employees by PickRate",
        rating="positive",
        comment="Useful answer"
    ))