from fastapi import APIRouter
from app.schemas import ChatRequest, ChatResponse
from app.agent import agent
from app.utils import get_chat_history
from app.constant import DEMO_SESSION_ID
route = APIRouter()

@route.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    history = get_chat_history(DEMO_SESSION_ID)
    messages = []

    for msg in history.messages:
        if msg.type == "human":
            messages.append({"role": "user", "content": msg.content})
        else:
            messages.append({"role": "assistant", "content": msg.content})

    messages.append({"role": "user", "content": request.message})

    response = agent.invoke({
        "messages": messages
    })
    print("Agent Response:", response)
    structured_output = response.get("structured_response")

    if not structured_output:
        structured_output = {
            "answer": "Sorry, I couldn't process your request.",
            "products": None,
            "source": "error"
        }

    history.add_user_message(request.message)
    history.add_ai_message(structured_output.answer)
    return ChatResponse(response=structured_output.answer)


@route.get("/health")
async def health_check():
    return {"status": "healthy"}