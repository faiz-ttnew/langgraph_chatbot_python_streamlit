import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph_backend import chatbot
from uuid import uuid4

#**********************************Utility functions**********************************#
def generate_thread_id():
    thread_id =  uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    st.session_state['message_history'] = []


# session state

#**********************************Session Setup**********************************#
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

#*******************************Sidebar UI******************************************#

st.sidebar.title("Langgraph Chatbot")
if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header("My Conversations")

st.sidebar.text(st.session_state['thread_id'])

#*******************************Main UI******************************************#

# loading he conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:
    # first add the message to message history
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
