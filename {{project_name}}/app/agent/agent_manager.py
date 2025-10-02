from typing import Any, Callable


class AgentManager:
    """Registry for agents, workers, and workflow components."""
    
    def __init__(self):
        self._agents: dict[str, Any] = {}
        self._factories: dict[str, tuple[Callable, dict]] = {}
    
    def register(self, name: str, agent_class: type, **config) -> 'AgentManager':
        """Register an agent with configuration (lazy initialization).
        
        Args:
            name: Unique agent identifier
            agent_class: Agent class to instantiate
            **config: Configuration parameters for agent constructor
            
        Returns:
            Self for method chaining
            
        Example:
            manager.register('router', GenericRouter, verbose=True, api_key="...")
        """
        self._factories[name] = (agent_class, config)
        return self
    
    def register_instance(self, name: str, instance: Any) -> 'AgentManager':
        """Register an existing agent instance.
        
        Args:
            name: Unique agent identifier
            instance: Agent instance to register
            
        Returns:
            Self for method chaining
        """
        self._agents[name] = instance
        return self
    
    async def initialize(self) -> None:
        """Initialize all registered agents from factories."""
        for name, (agent_class, config) in self._factories.items():
            if name not in self._agents:
                instance = agent_class(**config)
                if hasattr(instance, 'initialize') and callable(getattr(instance, 'initialize')):
                    init_method = getattr(instance, 'initialize')
                    if callable(init_method):
                        await init_method()
                self._agents[name] = instance
    
    def get(self, name: str) -> Any:
        """Get agent by name.
        
        Args:
            name: Agent identifier
            
        Returns:
            Agent instance
            
        Raises:
            KeyError: If agent not initialized
        """
        if name not in self._agents:
            raise KeyError(f"Agent '{name}' not initialized. Call initialize() first.")
        return self._agents[name]
    
    def has(self, name: str) -> bool:
        """Check if agent is registered.
        
        Args:
            name: Agent identifier
            
        Returns:
            True if agent exists in registry
        """
        return name in self._agents or name in self._factories
    
    def to_deps(self, **extra_deps) -> dict[str, Any]:
        """Convert all agents to dependencies dict for graph.
        
        Args:
            **extra_deps: Additional dependencies (e.g. message, language, target_language)
            
        Returns:
            Dictionary with agents + extra dependencies
            
        Example:
            deps = manager.to_deps(message='Hello', language='english')
        """
        deps = dict(self._agents)
        deps.update(extra_deps)
        return deps
    
    def clear(self) -> None:
        """Clear all registered agents and factories."""
        self._agents.clear()
        self._factories.clear()
    
    def list_agents(self) -> list[str]:
        """List all registered agent names."""
        return list(set(self._agents.keys()) | set(self._factories.keys()))
