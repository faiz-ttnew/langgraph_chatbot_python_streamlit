from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from dotenv import load_dotenv
import sqlite3
import requests
import os

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise ValueError(
        "GROQ_API_KEY is missing. Copy .env.example to .env, add your Groq API key, "
        "and restart the app."
    )

# -------------------
# 1. LLM
# -------------------
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
)

# Tools
# search_tool = DuckDuckGoSearchRun(region='us-en')
@tool
def search_tool(query: str) -> str:
    """Search the web for current information."""
    try:
        return DuckDuckGoSearchRun(region='us-en').run(query)
    except Exception as e:
        return f"Search failed: {e}"

@tool
def calculator(first_num:float, second_num:float, operation: str)->dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """

    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}

@tool
def get_stock_price(symbol: str) -> dict:
     """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
     url =  f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=31P1PRM32K5TTGCV"
     r = requests.get(url)
     return r.json()

@tool
def get_weahter(city: str)->dict:
     """
    Get current weather information for a city.
    Returns temperature, humidity, weather condition
    and wind speed.
    """
     api_key = os.getenv("OPEN_WEATHER_API_KEY")
     if not api_key:
        return {"error": "OPENWEATHER_API_KEY is missing"}
     url = "https://api.openweathermap.org/data/2.5/weather"

     params = {
         "q": city,
         'appid': api_key,
         'units': 'metric'
     }

     try:
         response = requests.get(url, params=params, timeout=10)
         response.raise_for_status()

         data = response.json()

         return {
             "city": data['name'],
             "temperature": data["main"]["temp"],
             "humidity": data["main"]["humidity"],
             "weather": data["weather"][0]["description"]
         }
     except (requests.RequestException, KeyError, IndexError, ValueError) as e:
        return {"error": str(e)}
         


tools = [search_tool, get_stock_price, calculator]
llm_with_tools = llm.bind_tools(tools)

#--------------
# 3. state
# -------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# -------------------
# 4. Nodes
# -------------------
def chat_node(state: ChatState):
    """LLM node that may answer or request a tool call."""
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {'messages': [response]}

tool_node = ToolNode(tools)

# -------------------
# 5. Checkpointer
# -------------------
conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

# -------------------
# 6. Graph
# -------------------
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, 'chat_node')

graph.add_conditional_edges('chat_node', tools_condition)
graph.add_edge('tools', 'chat_node')

chatbot = graph.compile(checkpointer=checkpointer)

# -------------------
# 7. Helper
# -------------------
def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)