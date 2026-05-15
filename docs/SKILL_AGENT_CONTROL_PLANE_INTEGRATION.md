# Skill-Agent Control Plane Integration

The Orchestrator may call registered skills, agents, tools, and workflows through bounded adapters. It must not own canonical skill lifecycle, quality scoring policy, graph truth, or workflow composition semantics.

Each Orchestrator adapter or public endpoint must be discoverable through the AI front door and skill-agent graph.

Every non-read-only endpoint must carry idempotency and approval policy metadata.
