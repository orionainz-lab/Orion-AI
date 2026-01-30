"""
Phase 2: The Reliable Brain - AI Agents Module

This module provides LangGraph-based AI agents for code generation
with AST verification, integrated with Temporal for durability.

Components:
    - state: TypedDict state schema for LangGraph
    - config: Configuration dataclasses for LLM and LangGraph
    - nodes: Reasoning nodes (Plan, Generate, Verify, Correct)
    - graph_builder: LangGraph StateGraph construction
    - llm_clients: LLM integration (Claude, Gemini)
    - workflows: Temporal workflow definitions
    - activities: Temporal activity definitions

Architecture Pattern (ADR-007):
    LangGraph is imported INSIDE Temporal activities to avoid
    workflow sandbox restrictions. The workflow orchestrates
    activities, while activities execute LangGraph reasoning.

Example:
    from agents.workflows import CodeGenerationWorkflow
    # Workflow is registered in temporal/workers/worker.py
"""

__version__ = "0.2.0"
__phase__ = "Phase 2: The Reliable Brain"

# Note: Do NOT import LangGraph at package level
# LangGraph must be imported inside activities per ADR-007
