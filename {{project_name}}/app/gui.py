import asyncio
import time
import os

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError
from openai import AuthenticationError
from pydantic_core._pydantic_core import ValidationError

try:
    from app.config import settings
    os.environ["API_KEY"] = settings.api_key
except (ValidationError, AttributeError):
    # Try to authenticate with streamlit secrets
    # if .env doesn't provide an api key
    try:
        os.environ["API_KEY"] = st.secrets["API_KEY"]
    except StreamlitSecretNotFoundError:
        st.warning("Provide a valid API key.")
        raise

try:
    if "MCP_URL" in st.secrets:
        os.environ["MCP_URL"] = st.secrets["MCP_URL"]
except StreamlitSecretNotFoundError:
    # No secrets file found, use config defaults
    pass

from app.agent.factories.workflow_factory import WorkflowAgentFactory
from app.agent.workflows.agent_workflow import user_assistant_graph
from app.agent.workflows.nodes import StartNode
from app.agent.workflows.generation_events import WorkflowState


if "chats" not in st.session_state:
    st.session_state.chats = 1
if "active_chat" not in st.session_state:
    st.session_state.active_chat = 1


def geticon(chat_number: int) -> str:
    return '📌' if chat_number == st.session_state.active_chat else '💤'


# ---------------------------------------------------------------

st.title(":robot: Your AI Assistant :robot:")


st.divider()


# ---------- sidebar ----------

with st.sidebar:
    st.header("Settings")
    
    use_mcp = st.checkbox(
        "Enable MCP Server", 
        value=settings.mcp_enabled,
        help="Enable Model Context Protocol server integration"
    )
    
    if use_mcp:
        url = st.text_input("MCP URL", "http://127.0.0.1:8000/mcp")
        settings.mcp_url = url
        os.environ["MCP_URL"] = url
    
    st.divider()
    
    if st.button("New chat", icon="💡"):
        st.session_state.chats += 1
        st.session_state.active_chat = st.session_state.chats
    
    st.divider()
    
    for chat_nr in range(1, st.session_state["chats"] + 1):
        if st.button(f"Chat {chat_nr}",
                     key=f"chat{chat_nr}", icon=geticon(chat_nr)):
            st.session_state.active_chat = chat_nr
            st.rerun()

# -----------------------------


if f"messages{st.session_state["active_chat"]}" not in st.session_state:
    st.session_state[f"messages{st.session_state["chats"]}"] = []

for message in st.session_state[f"messages{st.session_state["active_chat"]}"]:
    with st.chat_message(message["role"]):
        st.markdown(message["text"])

if prompt := st.chat_input("Ask me something"):
    st.session_state[f"messages{st.session_state["active_chat"]}"].append({"role": "human", "text": prompt})

    with st.chat_message("human"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        try:
            with st.spinner("running...", show_time=True):
                mcp_url = settings.mcp_url if use_mcp else None
                
                manager = asyncio.run(WorkflowAgentFactory.create_manager(
                    use_mcp=use_mcp,
                    mcp_url=mcp_url,
                    target_language=settings.default_language
                ))
                
                initial_state = WorkflowState()
                
                result = asyncio.run(
                    user_assistant_graph.run(
                        start_node=StartNode(),
                        state=initial_state,
                        deps=manager.to_deps(
                            message=prompt,
                            language=settings.default_language
                        )
                    )
                )
                
                response = result.output
        except AuthenticationError:
            st.warning("Please provide an api key in .env")
            response = ""
            raise
        except (ExceptionGroup, RuntimeError) as e:
            st.warning(f"Failed to connect with agent or MCP server: {e}")
            response = ""
            raise

        # Split response into chunks to imitate AI behaviour
        for chunk in response.split():
            full_response += chunk + " "
            time.sleep(0.04)
            placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)
        st.session_state[f"messages{st.session_state["active_chat"]}"].append({"role": "assistant", "text": full_response})


# ---------------------------------------------------------------
