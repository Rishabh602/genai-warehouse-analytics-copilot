# Import CrewAI Agent class
from crewai import Agent

# Import dotenv so CrewAI can access OPENAI_API_KEY from .env
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()


# Create KPI Analyst Agent
def create_kpi_analyst_agent():
    # This agent explains KPI performance using results from KPI Engine
    return Agent(
        role="KPI Analyst",
        goal="Analyze warehouse KPI performance across warehouses, managers, teams, shifts, and employees.",
        backstory=(
            "You are an experienced warehouse analytics specialist. "
            "You interpret productivity, labor, quality, service, and safety KPIs using structured data outputs."
        ),
        verbose=True,
        allow_delegation=False
    )


# Create Benchmark Analyst Agent
def create_benchmark_analyst_agent():
    # This agent explains whether KPI performance is healthy, warning, or critical
    return Agent(
        role="Benchmark Analyst",
        goal="Evaluate KPI performance against benchmark thresholds and explain performance status.",
        backstory=(
            "You specialize in operational benchmarking. "
            "You compare KPI results against target, warning, critical, and world-class thresholds."
        ),
        verbose=True,
        allow_delegation=False
    )


# Create Investigation Agent
def create_investigation_agent():
    # This agent investigates root causes using KPI, benchmark, anomaly, and recommendation outputs
    return Agent(
        role="Performance Investigation Agent",
        goal="Investigate operational performance issues and identify likely root causes.",
        backstory=(
            "You are a warehouse performance investigator. "
            "You connect KPI trends, benchmark failures, anomaly signals, and operational context to explain why performance declined."
        ),
        verbose=True,
        allow_delegation=False
    )


# Create SOP Expert Agent
def create_sop_expert_agent():
    # This agent uses retrieved SOP/RAG context to explain operational procedures
    return Agent(
        role="SOP Expert",
        goal="Use operational SOP and knowledge-base context to provide grounded process guidance.",
        backstory=(
            "You are an operations process expert. "
            "You answer only using retrieved SOP, benchmark, and investigation playbook context."
        ),
        verbose=True,
        allow_delegation=False
    )


# Create Recommendation Agent
def create_recommendation_agent():
    # This agent converts detected issues into practical business actions
    return Agent(
        role="Recommendation Agent",
        goal="Recommend practical corrective actions and ownership for warehouse performance issues.",
        backstory=(
            "You specialize in turning operational insights into action plans. "
            "You recommend next steps, responsible owners, and escalation paths based on anomaly and recommendation-rule outputs."
        ),
        verbose=True,
        allow_delegation=False
    )


# Create all CrewAI agents in one registry
def create_all_agents():
    # Return all agents in a dictionary so LangGraph or future orchestration can call them
    return {
        "kpi_analyst": create_kpi_analyst_agent(),
        "benchmark_analyst": create_benchmark_analyst_agent(),
        "investigation_agent": create_investigation_agent(),
        "sop_expert": create_sop_expert_agent(),
        "recommendation_agent": create_recommendation_agent()
    }


# Run quick test only when this file is executed directly
if __name__ == "__main__":
    # Create all agents
    agents = create_all_agents()

    # Print agent names to confirm creation
    for agent_name, agent in agents.items():
        print(f"{agent_name}: {agent.role}")