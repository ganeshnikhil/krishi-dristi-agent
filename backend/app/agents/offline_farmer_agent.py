import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain.agents import create_agent
from langchain.messages import SystemMessage, HumanMessage

# Your actual agriculture tools
from app.tools.yield_tool import YieldPredictionInternalTool
from app.tools.crop_tool import CropRecommendationInternalTool
from app.tools.fertilizer_tool import FertilizerPredictionTool
from app.tools.rain_fall import RainfallPredictionTool
from app.tools.weather_tool import WeatherInfoTool
from app.tools.soil_tool import SoilInfoTool
from app.tools.general_info_tool import ExternalKnowledgeSearchTool
from app.tools.farm_advice_tool import FarmPracticeRAGTool
from app.tools.goverment_schema_tool import GovSchemeRAGTool

load_dotenv()

# -----------------------------
# TOOLS CONFIGURATION
# -----------------------------
TOOLS = [
    YieldPredictionInternalTool(),
    CropRecommendationInternalTool(),
    FertilizerPredictionTool(),
    RainfallPredictionTool(),
    WeatherInfoTool(),
    SoilInfoTool(),
    ExternalKnowledgeSearchTool(),
    FarmPracticeRAGTool(),
    GovSchemeRAGTool()
]

# -----------------------------
# LFM 2.5 LLM SETUP
# -----------------------------
def get_offline_llm():
    """
    Configured for Liquid AI LFM 2.5 Thinking.
    Uses low temperature to ensure stable reasoning traces.
    """
    return ChatOllama(
        model="lfm2.5-thinking:latest",
        temperature=0.1,  # Recommended for reasoning models
        top_p=0.1,
        streaming=True
    )

# -----------------------------
# SYSTEM PROMPT (Optimized for LFM Reasoning)
# -----------------------------
def get_agent_system_prompt() -> str:
    return (
        "You are an expert Indian Agriculture Advisor. "
        "You have a 'thinking' capability—use it to plan which tools to call.\n\n"
        "RULES:\n"
        "1. Always check tools first for weather, soil, or crop advice.\n"
        "2. If the user asks about crops, use 'CropPredictionInternalTool'.\n"
        "3. If the user asks about government aid, use 'GovSchemeRAGTool'.\n"
        "4. Respond in the same language as the user (Hindi, Marathi, etc.).\n"
        "5. Keep the final answer simple and helpful for a farmer."
    )

# -----------------------------
# AGENT CREATION
# -----------------------------
def create_farmer_agent(llm, checkpointer: SqliteSaver):
    # LFM 2.5 is sensitive to prompt structure. 
    # create_agent handles the ChatML formatting for Ollama.
    return create_agent(
        model=llm,
        tools=TOOLS,
        system_prompt=get_agent_system_prompt(),
        checkpointer=checkpointer,
        debug=True # Highly recommended to see the 'Thinking' process in console
    )

# -----------------------------
# MAIN EXECUTION
# -----------------------------
if __name__ == "__main__":
    DB_PATH = "farmer_data_lfm.db"

    with SqliteSaver.from_conn_string(DB_PATH) as checkpointer:
        llm = get_offline_llm()
        agent = create_farmer_agent(llm, checkpointer)

        print("🧠 LFM 2.5 Thinking Agent Ready! (Local & Private)")
        print(f"📦 Database: {DB_PATH}\n")

        while True:
            current_user = input("Enter User ID: ").strip()
            if not current_user: continue

            user_query = input(f"[{current_user}] You: ").strip()
            if user_query.lower() in ["exit", "quit"]:
                break

            try:
                config = {"configurable": {"thread_id": current_user}}
                
                # The response will contain the thinking trace + final tool call/answer
                response = agent.invoke(
                    {"messages": [HumanMessage(content=user_query)]},
                    config=config
                )
                
                last_msg = response["messages"][-1]
                print(f"\nAgent: {last_msg.content}\n")

            except Exception as e:
                print(f"❌ Error: {e}\n")