from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
import sqlite3


load_dotenv()  # Load environment variables from .env

if not os.getenv("GROQ_API_KEY"):
    raise ValueError(
        "GROQ_API_KEY is missing. Copy .env.example to .env, add your Groq API key, "
        "and restart the app."
    )



llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {
        "messages": [response]
    }

connection = sqlite3.connect(
    database='chatbot.db',
    check_same_thread=False
)

# checkpointer
checkpointer = SqliteSaver(conn=connection)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)

graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    
    return list(all_threads)

# CONFIG = {'configurable': {'thread_id': 'thread-2'}}

# res = chatbot.invoke(
#                 {'messages': [HumanMessage(content='Hi, what is my name')]},
#                 config=CONFIG,
#             )
# print(res)

# print(chatbot.get_state(config=CONFIG).values['messages'])