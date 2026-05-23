# Build structured AI prompt

def build_warehouse_prompt(question, summary_level, context_table):

    # Convert KPI context table into text
    #adding head(15) so that query does not exceed token limit. Can be removed if we want to provide more context and are not concerned about token limits.
    context_text = context_table.head(15).to_string(index=False)
    #context_text = context_table.to_string(index=False)

    # Create grounded prompt for OpenAI

    prompt = f"""
You are a professional GenAI Warehouse Operations Copilot.

Your role is to analyze warehouse operational KPI data and provide business-friendly insights.

USER QUESTION:
{question}

SUMMARY LEVEL USED:
{summary_level}

RELEVANT KPI CONTEXT:
{context_text}

IMPORTANT INSTRUCTIONS:
1. Answer ONLY using the KPI context provided.
2. Do NOT invent information or numbers.
3. If the question cannot be answered from the provided KPI context, say it lies outside the scope of this project.
4. Mention relevant hierarchy levels where applicable.
5. Highlight anomaly patterns if relevant.
6. Keep answers concise and executive-friendly.
"""

    return prompt


# Main GenAI Copilot function

def ask_warehouse_copilot(
    question,
    data,
    kpi_rules,
    client,
    create_dynamic_summary
):

    try:

        # Handle empty question

        if question is None or question.strip() == "":

            return {
                "question": question,
                "moderation_status": "empty_question",
                "summary_level": None,
                "context_table": None,
                "prompt": None,
                "ai_answer": "Please enter a warehouse KPI question."
            }

        # Clean question text

        question_clean = question.lower().strip()


        # Handle greetings

        greetings = [
            "hi",
            "hello",
            "hey",
            "good morning",
            "good evening",
            "how are you"
        ]

        if question_clean in greetings:

            return {
                "question": question,
                "moderation_status": "greeting",
                "summary_level": None,
                "context_table": None,
                "prompt": None,
                "ai_answer": (
                    "Hello! I am your GenAI Warehouse Operations Copilot. "
                    "You can ask me questions about warehouse KPI performance, "
                    "anomalies, trends, managers, teams, shifts, and employees."
                )
            }


        # Validate warehouse analytics scope

        warehouse_keywords = [
            "kpi",
            "pickrate",
            "pick rate",
            "selection",
            "selectionrate",
            "selection rate",
            "replenishment",
            "overtime",
            "idle",
            "ontask",
            "on task",
            "warehouse",
            "distribution",
            "distribution center",
            "manager",
            "dc_manager",
            "team",
            "leader",
            "team leader",
            "employee",
            "shift",
            "dc",
            "trend",
            "weekly",
            "week",
            "anomaly",
            "anomalies",
            "performance",
            "productivity",
            "cases",
            "chart",
            "graph",
            "compare",
            "comparison",
            "top",
            "bottom",
            "highest",
            "lowest",
            "best",
            "worst"
        ]

        if not any(keyword in question_clean for keyword in warehouse_keywords):

            return {
                "question": question,
                "moderation_status": "out_of_scope",
                "summary_level": None,
                "context_table": None,
                "prompt": None,
                "ai_answer": (
                    "This question lies outside the scope of the Warehouse Operations Copilot project. "
                    "Please ask about warehouse KPIs, anomalies, trends, managers, teams, shifts, employees, or performance insights."
                )
            }


        # Run OpenAI moderation API

        moderation_response = client.moderations.create(
            model="omni-moderation-latest",
            input=question
        )

        moderation_result = moderation_response.results[0]

        if moderation_result.flagged:

            return {
                "question": question,
                "moderation_status": "blocked_by_openai_moderation",
                "summary_level": None,
                "context_table": None,
                "prompt": None,
                "ai_answer": "This question was blocked by OpenAI moderation checks."
            }


        # Create dynamic KPI summary

        summary_level, context_table = create_dynamic_summary(
            data=data,
            question=question,
            kpi_rules=kpi_rules
        )


        # Handle empty context

        if context_table is None or context_table.empty:

            return {
                "question": question,
                "moderation_status": "no_data",
                "summary_level": None,
                "context_table": None,
                "prompt": None,
                "ai_answer": (
                    "This question cannot be answered from the available dataset. "
                    "It lies outside the scope of this project."
                )
            }


        # Build AI prompt

        prompt = build_warehouse_prompt(
            question=question,
            summary_level=summary_level,
            context_table=context_table
        )


        # Generate OpenAI response

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional warehouse operations analytics copilot. "
                        "Answer only using the provided KPI context."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.2
        )


        # Extract AI answer

        ai_answer = response.choices[0].message.content


        # Return final response

        return {
            "question": question,
            "moderation_status": "approved",
            "summary_level": summary_level,
            "context_table": context_table,
            "prompt": prompt,
            "ai_answer": ai_answer
        }


    # Handle application errors

    except Exception as e:

        return {
            "question": question,
            "moderation_status": "error",
            "summary_level": None,
            "context_table": None,
            "prompt": None,
            "ai_answer": f"Error while processing request: {e}"
        }