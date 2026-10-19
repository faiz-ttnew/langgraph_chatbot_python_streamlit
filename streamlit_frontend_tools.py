import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph_tool_backend import chatbot
from uuid import uuid4

#**********************************Utility functions**********************************#
def generate_thread_id():
    thread_id =  uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    return chatbot.get_state(config={'configurable': {'thread_id': thread_id}}).values['messages']

# session state

#**********************************Session Setup**********************************#
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

if 'chat_titles' not in st.session_state:
    st.session_state['chat_titles'] = {}

add_thread(st.session_state['thread_id'])

#*******************************Sidebar UI******************************************#

st.sidebar.title("Langgraph Chatbot")
if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header("My Conversations")

# for thread_id in st.session_state['chat_threads'][::-1]:
#     if st.sidebar.button(str(thread_id)):
for thread_id in st.session_state['chat_threads'][::-1]:
    title = st.session_state['chat_titles'].get(
        thread_id, 'New Chat'
    )
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
    if current_thread not in st.session_state['chat_titles']:
        st.session_state['chat_titles'][current_thread] = user_input

    st.session_state['message_history'].append({
        'role': 'user', 'content': user_input
    })
    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    with st.chat_message('assistant'):
        status_slot = st.empty()          # placeholder shown above the answer
        status_holder = {"box": None}

        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            ):
                # 1) Model decided to call a tool -> show which one
                if isinstance(message_chunk, AIMessage):
                    for tc in getattr(message_chunk, "tool_call_chunks", []) or []:
                        if tc.get("name"):
                            label = f"🔧 Calling `{tc['name']}`..."
                            if status_holder["box"] is None:
                                status_holder["box"] = status_slot.status(label, expanded=False)
                            else:
                                status_holder["box"].update(label=label, state="running")

                # 2) Tool finished
                if isinstance(message_chunk, ToolMessage) and status_holder["box"] is not None:
                    status_holder["box"].update(
                        label=f"✅ `{message_chunk.name}` finished",
                        state="complete",
                    )

                # 3) Stream only assistant text tokens
                if isinstance(message_chunk, AIMessage) and message_chunk.content:
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

    # second add the message to message history
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    st.rerun()
