import os
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver

from app.agents.online_farmer_agent import get_sarvam_llm, create_farmer_agent
from app.services.agent_service import AgentService
from pathlib import Path

load_dotenv()

# DB_PATH = "app/data/farmer_data.db"
DB_PATH  = str(Path(__file__).resolve().parent.parent / "data" / "farmer_data.db")

tool_model_name = os.getenv("SARVAM30_MODEL_NAME")
chat_model_name = os.getenv("SARVAM105_MODEL_NAME")

# Initialize once
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver(DB_PATH)
#checkpointer = SqliteSaver.from_conn_string(DB_PATH)

agent_llm = get_sarvam_llm(tool_model_name)
chat_llm = get_sarvam_llm(chat_model_name)

agent = create_farmer_agent(agent_llm, checkpointer)

# Global service instance
agent_service = AgentService(agent, chat_llm, checkpointer)


