from typing import Dict
from .base import BaseAgentAdapter, DispatchOptions, AgentIdentity
from .cline_adapter import ClineAdapter
from .opencode_adapter import OpenCodeAdapter
from .agy_adapter import AgyAdapter

REGISTRY: Dict[str, BaseAgentAdapter] = {
    "cline": ClineAdapter(),
    "opencode": OpenCodeAdapter(),
    "agy": AgyAdapter()
}

def get_adapter(name: str) -> BaseAgentAdapter:
    if name not in REGISTRY:
        raise ValueError(f"Unknown agent '{name}'. Supported agents: {list(REGISTRY.keys())}")
    return REGISTRY[name]

__all__ = ["REGISTRY", "get_adapter", "BaseAgentAdapter", "DispatchOptions", "AgentIdentity"]
