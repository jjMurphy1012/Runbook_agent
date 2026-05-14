# RunbookAgent — Agent Instructions

Demo-grade AIOps portfolio project. See `docs/overview.md` for scope, architecture, delivery plan, and risks.

## Design Decisions (load on demand)

Read the linked file before changing the corresponding subsystem; do not infer from code alone.

- Reflection mode (Analyzer/Critic loop, not bull/bear) → `docs/design/reflection.md`
- Incident Memory (verified-only retrieval, anchoring guard) → `docs/design/memory.md`
- Redis (cache + rate limiter + event stream) → `docs/design/redis.md`
- JWT stateless auth (no Spring Session) → `docs/design/auth.md`

## Context Compaction

When the Codex context window indicator drops to roughly 30%, compact the conversation context before continuing. Preserve the current goal, decisions already made, files changed, open bugs, validation results, and the next concrete steps so the next turn can resume without re-discovery.

## Stage Workflow

When starting any multi-step task (anything that needs more than one edit/command to finish):

1. Call `TaskCreate` to list the concrete steps before touching code.
2. Mark each task `in_progress` when starting it and `completed` as soon as it's done — don't batch updates.
3. After all tasks are completed and before reporting the stage as done, invoke the `simplify` skill on the files changed during this stage. Apply its findings, then summarize.

This applies to feature work, refactors, and multi-file fixes. Skip only for trivial one-shot edits (single-line change, typo, single-file read).
