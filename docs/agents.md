# Agents

[← Back to Main README](../README.md)

## Overview

This template includes AI agent functionality with both Streamlit GUI and FastAPI backend options. The agents are built using a modular architecture with support for different agent engines, workflows, and tools.

## ⚙️ Configuration

First, install the project dependencies:

```bash
uv sync
```

Then, create a `.env` file in the project root with your API key:

```bash
# Create .env file
echo "API_KEY=your_api_key_here" > .env
```

Replace `your_api_key_here` with your actual API key for the LLM provider you're using.

## 🚀 Running the Application

### Option 1: Streamlit GUI

To run the application with the Streamlit interface:

```bash
uv run streamlit run app/gui.py
```

This will start the Streamlit development server, typically on `http://localhost:8501`.

### Option 2: FastAPI Backend

To run the FastAPI backend server:

```bash
uv run fastapi dev app/main.py --port 8300
```

This will start the FastAPI development server on port 8300 (avoiding the default 8000 port).

## 🏗️ Agent Architecture

The agent system is organized into several key components:

### Core Components

- **Agent Manager** (`app/agent/agent_manager.py`) - Central management of agent instances
- **Engines** (`app/agent/engines/`) - Different agent execution engines
  - `react_agent.py` - ReAct (Reasoning and Acting) agent implementation
  - `guardrails.py` - Safety and validation layer
  - `routers.py` - Request routing for agent modes
  - `translators.py` - Input/output translation layer
- **Workflows** (`app/agent/workflows/`) - Agent workflow definitions
- **Tools** (`app/agent/tools/`) - Available tools and utilities
- **Prompts** (`app/agent/prompts/`) - Agent and worker prompt templates

### Key Features

- **Modular Design**: Easy to extend with new agent types and capabilities
- **Tool Integration**: Built-in tool registry and management system
- **Workflow Support**: Configurable agent workflows for different use cases
- **Safety Layer**: Guardrails for safe agent operation
- **API Integration**: RESTful API endpoints for agent interaction

---

[← Back to Main README](../README.md)
