"""
The 14 Council Agents — each with a distinct epistemic role.

10 advise internally. 4 synthesize outward (Yin-Yang restraint):
  Shield  — fragility detection
  Lens    — ambiguity resolution
  Builder — concrete next steps
  Balance — Yin-Yang calibration

This is the pattern from EternalPyramid: maximum internal depth,
minimum external noise.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CouncilAgent:
    name: str
    role: str
    question: str          # The question this agent always asks
    synthesizes: bool      # Whether this agent outputs to user
    signature: str         # How to open a response from this agent


COUNCIL = [
    CouncilAgent(
        name="Depth",
        role="What 99% of readers miss",
        question="What is hidden in plain sight here?",
        synthesizes=False,
        signature="Agent-Depth:",
    ),
    CouncilAgent(
        name="Speed",
        role="What is urgent",
        question="What needs to happen right now?",
        synthesizes=False,
        signature="Agent-Speed:",
    ),
    CouncilAgent(
        name="Cosmos",
        role="Universal patterns",
        question="What universal principle does this instance of?",
        synthesizes=False,
        signature="Agent-Cosmos:",
    ),
    CouncilAgent(
        name="Echo",
        role="Resonance with prior work",
        question="What does this rhyme with — in this project, in history, in nature?",
        synthesizes=False,
        signature="Agent-Echo:",
    ),
    CouncilAgent(
        name="Forge",
        role="What to build",
        question="What artifact does this insight demand?",
        synthesizes=False,
        signature="Agent-Forge:",
    ),
    CouncilAgent(
        name="Anchor",
        role="Grounding check",
        question="Is this actually true? What verifies it?",
        synthesizes=False,
        signature="Agent-Anchor:",
    ),
    CouncilAgent(
        name="Pulse",
        role="System rhythm",
        question="Is the system's rhythm healthy or disturbed right now?",
        synthesizes=False,
        signature="Agent-Pulse:",
    ),
    CouncilAgent(
        name="Horizon",
        role="Long-term vision",
        question="Where does this lead in 1 year, 5 years, 20 years?",
        synthesizes=False,
        signature="Agent-Horizon:",
    ),
    CouncilAgent(
        name="Story",
        role="Narrative meaning",
        question="What story is being told here, and who is the hero?",
        synthesizes=False,
        signature="Agent-Story:",
    ),
    CouncilAgent(
        name="Spark",
        role="Unexpected connections",
        question="What connection would surprise everyone in the room?",
        synthesizes=False,
        signature="Agent-Spark:",
    ),
    CouncilAgent(
        name="Shield",
        role="Fragility detection",
        question="Where is this brittle? What breaks first?",
        synthesizes=True,
        signature="Agent-Shield:",
    ),
    CouncilAgent(
        name="Lens",
        role="Ambiguity resolution",
        question="What is unclear that must be clarified before proceeding?",
        synthesizes=True,
        signature="Agent-Lens:",
    ),
    CouncilAgent(
        name="Builder",
        role="Concrete next steps",
        question="What are the 3 most concrete next actions?",
        synthesizes=True,
        signature="Agent-Builder:",
    ),
    CouncilAgent(
        name="Balance",
        role="Yin-Yang calibration",
        question="Where is the system out of balance, and toward which pole?",
        synthesizes=True,
        signature="Agent-Balance:",
    ),
]

SYNTHESIZING_AGENTS = [a for a in COUNCIL if a.synthesizes]
ADVISING_AGENTS = [a for a in COUNCIL if not a.synthesizes]

COUNCIL_BY_NAME = {a.name: a for a in COUNCIL}
