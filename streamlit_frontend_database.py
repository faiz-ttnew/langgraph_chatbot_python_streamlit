import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph_database_backend import chatbot, retrieve_all_threads
from uuid import uuid4

#**********************************Utility functions**********************************#
def generate_thread_id():
    thread_id =  uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    # add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    return chatbot.get_state(config={'configurable': {'thread_id': thread_id}}).values.get('messages',[])

# get chat title from db
def get_chat_title(thread_id):
    # Check if title already exists in session state
    if thread_id in st.session_state['chat_titles']:
        return st.session_state['chat_titles'][thread_id]

    # Retrieve messages from SQLite through LangGraph
    messages = load_conversation(thread_id)

    # Find first user message
    for message in messages:
        if isinstance(message, HumanMessage):

            title = message.content

            # Save title in session state
            st.session_state['chat_titles'][thread_id] = title

            return title

        return 'New Chat'

# session state

#**********************************Session Setup**********************************#
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

if 'chat_titles' not in st.session_state:
    st.session_state['chat_titles'] = {}

# add_thread(st.session_state['thread_id'])

#*******************************Sidebar UI******************************************#

st.sidebar.title("Langgraph Chatbot")
if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header("My Conversations")

# for thread_id in st.session_state['chat_threads'][::-1]:
#     if st.sidebar.button(str(thread_id)):
for thread_id in st.session_state['chat_threads'][::-1]:
    
    title = get_chat_title(thread_id)

    if st.sidebar.button(title, key=str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        temp_messages= []

        for message in messages:
            if isinstance(message, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_messages.append({'role': role, 'content':message.content})
        st.session_state['message_history'] = temp_messages

#*******************************Main UI******************************************#

# loading he conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:
    # first add the message to message history
    current_thread = st.session_state['thread_id']
    # Register thread only when user sends a message
    add_thread(current_thread)

    if current_thread not in st.session_state['chat_titles']:
        st.session_state['chat_titles'][current_thread] = user_input

    st.session_state['message_history'].append({
        'role': 'user', 'content': user_input
    })
    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    with st.chat_message('assistant'):

        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
        )

    # second add the message to message history
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    st.rerun()
