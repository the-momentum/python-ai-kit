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
    if "MCP_URLS" in st.secrets:
        mcp_urls = st.secrets["MCP_URLS"]
        if isinstance(mcp_urls, str):
            mcp_urls = [url.strip() for url in mcp_urls.split(",") if url.strip()]
        os.environ["MCP_URLS"] = ",".join(mcp_urls)
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
if "mcp_urls" not in st.session_state:
    st.session_state.mcp_urls = []
if "default_language" not in st.session_state:
    st.session_state.default_language = settings.default_language


def geticon(chat_number: int) -> str:
    return '📌' if chat_number == st.session_state.active_chat else '💤'


# ---------------------------------------------------------------

st.title(":robot: Your AI Assistant :robot:")

st.divider()


# ---------- sidebar ----------

with st.sidebar:
    st.header("Settings")
    
    # Language settings
    selected_language = st.text_input(
        "🌍 Language",
        value=st.session_state.default_language,
        placeholder="e.g. english, polish, español, 中文, français...",
        help="Language for AI responses and interface. You can use any language name."
    )
    
    if selected_language and selected_language != st.session_state.default_language:
        st.session_state.default_language = selected_language
        st.rerun()
    
    # MCP settings
    use_mcp = st.checkbox(
        "📡 Enable MCP Servers", 
        value=settings.mcp_enabled,
        help="Enable Model Context Protocol server integration"
    )
    
    if use_mcp:
        if not st.session_state.mcp_urls:
            st.info("📡 No MCP servers configured. Add URLs below to enable MCP integration.")
        else:
            st.info(f"📡 {len(st.session_state.mcp_urls)} MCP server(s) configured")
        
        # Display current URLs
        for i, url in enumerate(st.session_state.mcp_urls):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text_input(f"URL {i+1}", value=url, key=f"mcp_url_{i}", disabled=True)
            with col2:
                if st.button("🗑️", key=f"delete_{i}", help="Delete this URL"):
                    st.session_state.mcp_urls.pop(i)
                    st.rerun()
        
        # Add new URL
        new_url = st.text_input("Add new MCP URL", placeholder="http://127.0.0.1:8000/mcp")
        if st.button("Add URL") and new_url:
            if not new_url.startswith(('http://', 'https://')):
                st.error("URL must start with http:// or https://")
            elif new_url in st.session_state.mcp_urls:
                st.warning("URL already exists")
            else:
                st.session_state.mcp_urls.append(new_url)
                st.rerun()
        
        # Test MCP connection button
        if st.button("Test MCP Connection", help="Test if MCP servers are reachable", disabled=not st.session_state.mcp_urls):
            with st.spinner("Testing MCP connections..."):
                try:
                    test_manager = asyncio.run(WorkflowAgentFactory.create_manager(
                        use_mcp=True,
                        mcp_urls=st.session_state.mcp_urls,
                        language=st.session_state.default_language
                    ))
                    st.success("✅ All MCP servers are reachable!")
                except Exception as e:
                    st.error(f"❌ MCP connection failed: {str(e)}")
                    st.info("Check if your MCP servers are running and URLs are correct.")
        
        settings.mcp_urls = st.session_state.mcp_urls.copy()
    
    st.divider()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("New chat", icon="💡"):
            st.session_state.chats += 1
            st.session_state.active_chat = st.session_state.chats
    with col2:
        if st.button("🗑️", help="Delete current chat", disabled=st.session_state.chats <= 1):
            # Delete current chat
            current_chat = st.session_state.active_chat
            if current_chat in st.session_state:
                del st.session_state[f"messages{current_chat}"]
            
            # If deleting the last chat, create a new one
            if st.session_state.chats == 1:
                st.session_state.chats = 1
                st.session_state.active_chat = 1
            else:
                # Shift chat numbers down
                for i in range(current_chat + 1, st.session_state.chats + 1):
                    if f"messages{i}" in st.session_state:
                        st.session_state[f"messages{i-1}"] = st.session_state[f"messages{i}"]
                        del st.session_state[f"messages{i}"]
                
                st.session_state.chats -= 1
                if st.session_state.active_chat > st.session_state.chats:
                    st.session_state.active_chat = st.session_state.chats
            
            st.rerun()
    
    st.divider()
    
    for chat_nr in range(1, st.session_state["chats"] + 1):
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"Chat {chat_nr}",
                         key=f"chat{chat_nr}", icon=geticon(chat_nr)):
                st.session_state.active_chat = chat_nr
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"delete_chat{chat_nr}", help="Delete this chat", disabled=st.session_state.chats <= 1):
                # Delete specific chat
                if f"messages{chat_nr}" in st.session_state:
                    del st.session_state[f"messages{chat_nr}"]
                
                # Shift remaining chats down
                for i in range(chat_nr + 1, st.session_state.chats + 1):
                    if f"messages{i}" in st.session_state:
                        st.session_state[f"messages{i-1}"] = st.session_state[f"messages{i}"]
                        del st.session_state[f"messages{i}"]
                
                st.session_state.chats -= 1
                if st.session_state.active_chat >= chat_nr and st.session_state.active_chat > 1:
                    st.session_state.active_chat -= 1
                elif st.session_state.active_chat > st.session_state.chats:
                    st.session_state.active_chat = st.session_state.chats
                
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
                mcp_urls = st.session_state.mcp_urls if use_mcp else None
                
                # Try with MCP first, fallback to without MCP if it fails
                try:
                    manager = asyncio.run(WorkflowAgentFactory.create_manager(
                        use_mcp=use_mcp,
                        mcp_urls=mcp_urls,
                        language=st.session_state.default_language
                    ))
                except Exception as mcp_error:
                    if use_mcp and ("MCP" in str(mcp_error) or "mcp" in str(mcp_error)):
                        st.warning("MCP servers failed, running without MCP...")
                        manager = asyncio.run(WorkflowAgentFactory.create_manager(
                            use_mcp=False,
                            mcp_urls=None,
                            language=st.session_state.default_language
                        ))
                    else:
                        raise mcp_error
                
                initial_state = WorkflowState()
                
                result = asyncio.run(
                    user_assistant_graph.run(
                        start_node=StartNode(),
                        state=initial_state,
                        deps=manager.to_deps(
                            message=prompt,
                            language=st.session_state.default_language
                        )
                    )
                )
                
                response = result.output
        except AuthenticationError:
            st.warning("Please provide an api key in .env")
            response = ""
            raise
        except (ExceptionGroup, RuntimeError) as e:
            error_msg = str(e)
            if "MCP" in error_msg or "mcp" in error_msg:
                st.warning(f"Failed to connect to MCP servers. Please check your URLs: {st.session_state.mcp_urls}")
                st.info("You can disable MCP servers or fix the URLs in the sidebar.")
            else:
                st.warning(f"Failed to connect with agent: {error_msg}")
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