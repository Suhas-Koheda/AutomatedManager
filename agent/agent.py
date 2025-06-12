from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import  AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate,MessagesPlaceholder

from AutomatedManager.calendar.create_event import create_event
from AutomatedManager.calendar.read_calendar import read_calendar
from AutomatedManager.mail.util import get_sender, get_simple_email_body

tools=[create_event, read_calendar]

llm=ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2, max_output_tokens=1000)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that reads the mail and adds the event to the calendar  "
               "you will be having read and write access to the calendar through tools and also the structure of inputs to each tool is defined properly in the docstring. "
               "you can use tools whenever you need "),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

agent=create_tool_calling_agent(llm, tools=tools,prompt=prompt)

mailer_agent=AgentExecutor(agent=agent, tools=tools, verbose=True)
