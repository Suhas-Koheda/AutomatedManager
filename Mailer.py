from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Define the tool with individual arguments
@tool
def create_event(summary: str, start: str, end: str, location: str) -> str:
    """
    Creates a Google Calendar event.
    Requires: summary, start, end, location.
    """
    print("[TOOL CALLED]")
    print("Event Summary:", summary)
    print("Start:", start)
    print("End:", end)
    print("Location:", location)
    return "✅ Event created in calendar."

# Initialize the model
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,
    model_kwargs={
        "tools": [create_event],
        "tool_choice": {"function_call": {"name": "create_event"}}
    }
)

# Message to trigger tool use
messages = [
    HumanMessage(
        content="Schedule an event titled 'Namaste Jupiverse - Hackathon Edition (HYD)' on June 21st from 10 AM to 10 PM at CoKarma - Coworking Space, Kothaguda, Telangana"
    )
]

# Run model
response = llm.invoke(messages)

# Print result
print("LLM Content:", response.content)
if hasattr(response, "tool_calls"):
    print("Tool Calls:", response.tool_calls)
