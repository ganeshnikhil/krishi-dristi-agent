from langchain.messages import HumanMessage
from app.agents.router_logic import get_routing_decision
from app.agents.online_farmer_agent import call_chat_only
import asyncio

class AgentService:
    def __init__(self, agent, chat_llm, checkpointer):
        self.agent = agent
        self.chat_llm = chat_llm
        self.checkpointer = checkpointer

    async def run(self, user_query: str, user_id: str):
        config = {"configurable": {"thread_id": user_id}}

        decision = get_routing_decision(user_query)

        if decision == "TOOL":
            response = await asyncio.to_thread(
                self.agent.invoke,
                {"messages": [HumanMessage(content=user_query)]},
                config
            )
            return response["messages"][-1].content, "TOOL"

        else:
            result = call_chat_only(
                self.chat_llm,
                user_query,
                config,
                self.checkpointer
            )
            return result, "CHAT"