import os
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings
from app.tools import tools
from app.schemas import AgentResponse
os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
model = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.3)


agent = create_agent(
    model=model,
    tools=tools,
    response_format=AgentResponse,
    system_prompt=(
        "You are a helpful personal care product chatbot. "
        "If user asks about offers, returns, refunds → MUST call escalate_to_human tool."
    )
)

