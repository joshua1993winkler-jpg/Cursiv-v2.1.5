# Example Knowledge Packets

These JSON files are starter templates for creating Cursiv agents.

## personal_principles.json
A personal principles agent. Load this to create an agent that knows your core
decision-making framework, identity anchor, and recovery protocol.

## knowledge_base.json
A frontier knowledge agent. Encodes the 6 Human Frontier knowledge domains
with their load priorities and source registry.

## Creating your own packet

Any JSON file can be a knowledge packet. The richer the content, the more
complete the agent that emerges from Academy.

Recommended fields:
- `name` — agent name
- `description` — what this agent knows
- `domain` — primary knowledge domain
- `identity_anchor` — one sentence defining what this agent IS

The Academy will extract everything else during the 8-phase process.
