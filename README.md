# Python AI Kit

A production-ready framework for building AI agents that actually work in production.

## 🚀 Quick Start

To use this template, run:

```bash
copier copy . <target_path_of_create_project>
```

This will generate a new project based on the template with all the necessary files and structure.

## Features

### Core Framework
- **Multi-agent orchestration** - Built-in support for coordinating multiple specialized agents with defined workflows and error handling
- **State management** - Persistent memory across sessions using dedicated database storage and thread preservation
- **Observability by default** - Integrated logging, tracing, and monitoring with Pydantic Logfire or Opik
- **Structured prompt management** - Modular, versioned prompts with POML patterns instead of monolithic strings

### Development & Testing
- **Automated evaluation pipeline** - Integrated Ragas/Opik evaluators with quantifiable metrics, not "by feel" testing
- **Prompt versioning system** - Track changes, rollback, and compare prompt iterations using database or JSON storage
- **Built-in testing patterns** - Standard test structures for agentic logic, not just code structure
- **Code standards enforcement** - Pre-configured linters and formatters that understand AI agent patterns

### Production Readiness
- **Security hardened** - Fernet encryption for API keys, SOPS standard support, no exposed credentials
- **Artifact management** - Proper handling of RAG contents, static files, and model storage without cluttering repos
- **Workflow control** - Template-based routing with custom error handling and predictable execution paths
- **MLOps pipeline** - Deployment patterns for custom models and retraining workflows

### Integration & Compatibility
- **Curated tool ecosystem** - Pre-integrated best-of-breed tools that actually work together
- **Framework flexibility** - Strong core with optional features, avoiding both barebones implementations and bloated abstractions
- **Standard interfaces** - Consistent APIs across components, minimal manual adjustments needed

## Why Use Python AI Kit

**You're tired of stitching tools together.** Every AI agent project feels like forcing incompatible blocks to work. You spend more time debugging integrations than building features.

**You can't review prompt changes with confidence.** Merge requests for prompts are guesswork. Small changes cause unpredictable behavior. You have no baseline to compare against.

**Your agents lose context between sessions.** Users complain that the agent "forgets" previous conversations. You've bolted on hacky state management that breaks under load.

**Testing is a manual nightmare.** You ask your agent arbitrary questions and judge responses subjectively. There are no metrics. You can't prove your changes made things better or worse.

**You can't explain why the agent did something.** When things go wrong in production, you have no visibility into the decision chain. This is a non-starter in regulated industries.

**You're rebuilding patterns from scratch every time.** There's no standard way to structure agents. Every project starts at zero. Code reviews are inconsistent because there's no established patterns.

**Security is an afterthought.** API keys in environment variables. Secrets committed to repos. You know it's wrong but there's no easy alternative baked in.

This framework solves these problems by integrating proven solutions into a cohesive platform. Not another thin wrapper - battle-tested patterns for the entire development lifecycle.

## 📚 Documentation

- [**API Architecture**](docs/api-architecture.md) - Learn about the database, repositories, services, and API design patterns
- [**Agents**](docs/agents.md) - Instructions for running and working with AI agents

## 🎯 Project Types

This template generates projects optimized for:

- **Microservice API** - Lightweight, focused services with minimal dependencies
- **Monolith Service API** - Full-featured applications with comprehensive architecture layers
- **MCP Server** - Model Context Protocol servers for AI tool integration
- **AI Agent** - Intelligent agent systems with workflow and tool management

Each generated project includes modern Python tooling, comprehensive testing, and production-ready architecture patterns.

## 📁 Project Structure

The generated project includes:
- FastAPI-based API with proper architecture layers
- SQLAlchemy database models and repositories
- Service layer with error handling
- AI agent integration with Streamlit GUI
- Comprehensive testing setup
- Modern Python tooling (uv, ruff, etc.)

---

*For detailed information about specific components, please refer to the linked documentation pages above.*