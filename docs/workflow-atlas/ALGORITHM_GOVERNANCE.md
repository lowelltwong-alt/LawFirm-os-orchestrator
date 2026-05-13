# Algorithm Governance for Workflow Atlas

## Rule

Every workflow improvement must pass a subtraction-first review before it can become an automation candidate.

## Musk Algorithm gate

1. Question every requirement.
2. Delete the part or process if possible.
3. Simplify and optimize what remains.
4. Accelerate cycle time only after deletion and simplification.
5. Automate last.

## Skill quality rubric

A skill is good when it is short, scoped, testable, evidence-aware, fail-closed, and explicit about what it must not do.

A skill is weak when it hides authority, assumes facts, asks broad questions, repeats generic instructions, or bypasses validation.

## Algorithm quality rubric

An algorithm is good when it is correct enough for its risk tier, simple on the other side of complexity, deterministic where authority matters, measurable, and cheaper than the human rework it removes.

## Reference algorithm examples to study

- Binary search: eliminate half the search space each step.
- Dijkstra: find shortest paths with explicit cost and frontier discipline.
- A-star: focus search by combining known cost and heuristic distance.
- Dynamic programming: cache repeated subproblems instead of recomputing.
- MapReduce: split independent work, compute locally, combine deterministically.
- Kalman filter: update belief by balancing prediction and measurement uncertainty.
- PageRank: infer importance from graph structure and repeated propagation.
- CRDTs: allow distributed updates that converge without central coordination.
- Control charts: distinguish common-cause noise from special-cause signals.
- Pareto analysis: focus improvement on the few causes creating most defects.

## Grading questions

- Does the skill reduce context load?
- Does the skill prevent authority confusion?
- Does the algorithm improve the current bottleneck?
- Does the algorithm require evidence before action?
- Does the solution delete work before automating work?
- Does it preserve Exception Lake and Semantic Substrate boundaries?
