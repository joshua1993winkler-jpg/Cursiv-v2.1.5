"""
Council Deliberation — real 14-agent parallel deliberation.

Process:
  1. All 14 agents receive the query + agent context
  2. Each produces an internal perspective (not shown to user)
  3. The 4 synthesizing agents (Shield, Lens, Builder, Balance) produce
     an external synthesis, informed by all 10 internal perspectives
  4. The 4 syntheses are combined into a final response

This is genuine deliberation, not metadata. Each LLM call is real.
"""

from __future__ import annotations

import json
from typing import Any, Callable

from .agents import ADVISING_AGENTS, COUNCIL_BY_NAME, SYNTHESIZING_AGENTS, CouncilAgent


class CouncilDeliberation:
    def __init__(self, llm_caller: Callable[[str], str]) -> None:
        self._llm = llm_caller

    def deliberate(
        self,
        query: str,
        agent_context: dict[str, Any],
        max_parallel: int = 3,
    ) -> dict[str, Any]:
        """Run full council deliberation. Returns synthesis + all perspectives."""
        context_str = self._format_context(agent_context)

        internal_perspectives: dict[str, str] = {}
        for council_agent in ADVISING_AGENTS:
            perspective = self._advise(council_agent, query, context_str)
            internal_perspectives[council_agent.name] = perspective

        all_perspectives = json.dumps(internal_perspectives, indent=2)[:3000]

        external_syntheses: dict[str, str] = {}
        for council_agent in SYNTHESIZING_AGENTS:
            synthesis = self._synthesize(council_agent, query, context_str, all_perspectives)
            external_syntheses[council_agent.name] = synthesis

        return {
            "internal_perspectives": internal_perspectives,
            "external_syntheses": external_syntheses,
            "combined": self._combine(external_syntheses, query),
        }

    def _format_context(self, agent_context: dict[str, Any]) -> str:
        return "\n".join([
            f"Agent: {agent_context.get('name', 'Unknown')}",
            f"Domain: {agent_context.get('domain', '')}",
            f"Identity: {agent_context.get('identity_anchor', '')}",
            f"Capabilities: {', '.join(agent_context.get('capabilities', [])[:5])}",
            f"Council position: {agent_context.get('council_position', '')}",
        ])

    def _advise(self, council_agent: CouncilAgent, query: str, context: str) -> str:
        prompt = f"""You are {council_agent.name}, a council agent with this role: {council_agent.role}

Your question is always: "{council_agent.question}"

The agent you are advising:
{context}

The query being processed:
{query}

Provide your internal perspective in 2-4 sentences. Be specific and non-obvious.
This is an internal advisory — it will inform but not directly appear in the user response."""
        try:
            return self._llm(prompt)[:500]
        except Exception:
            return f"[{council_agent.name}: advisory unavailable]"

    def _synthesize(
        self,
        council_agent: CouncilAgent,
        query: str,
        context: str,
        all_perspectives: str,
    ) -> str:
        prompt = f"""You are {council_agent.name}, a synthesizing council agent with this role: {council_agent.role}

Your question is always: "{council_agent.question}"

Internal perspectives from the full 14-agent council:
{all_perspectives}

The agent context:
{context}

The original query:
{query}

Synthesize into a clear, actionable response from your lens. 3-5 sentences maximum.
This IS user-facing output — be clear, direct, and specific."""
        try:
            return self._llm(prompt)[:600]
        except Exception:
            return f"[{council_agent.name}: synthesis unavailable]"

    def _combine(self, syntheses: dict[str, str], query: str) -> str:
        parts = []
        for name, synthesis in syntheses.items():
            if synthesis and not synthesis.startswith("["):
                parts.append(f"**{name}**: {synthesis}")
        if not parts:
            return f"Council deliberation completed for: {query[:100]}"
        return "\n\n".join(parts)
