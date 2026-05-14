# Diagnostic Reflection Mode

The diagnostic stage uses an Analyzer + Critic loop instead of a single-pass LLM call. This is the project's main differentiator.

A preset "bull vs bear" debate requires hardcoding opposing stances per alert type, does not generalize, and risks excluding the correct root cause. Reflection avoids this: the Analyzer freely diagnoses, and the Critic may point to any alternative direction — including ones the Analyzer never considered.

## Structure

```
Evidence → Analyzer → Critic → (converged?) → Finalizer
              ↑___________________|
                  loop, max 3 rounds
```

- **Analyzer**: Free-form diagnosis. First round unbiased. Later rounds see Critic feedback and may accept, reject, or partially revise.
- **Critic**: Reviews the analysis against the full evidence (not just the analysis text). Flags missed evidence, logic gaps, alternative hypotheses, correlation-vs-causation errors. Severity-graded.
- **Finalizer**: Synthesizes final diagnosis from all rounds after convergence.

## Convergence

Loop ends when any of:

- Critic reports no major or critical issues
- Two consecutive rounds produce substantially identical analyses
- `max_rounds=3` reached

## Prompt Guardrails

- Analyzer may reject Critic feedback with justification (prevents sycophantic collapse)
- Critic minor issues do not block convergence (prevents infinite nitpicking)
- Critic must cite specific evidence when proposing alternatives (prevents hand-waving)

## Cost Control

Reflection mode runs only when Triage flags `severity=HIGH` or `ambiguity_score>0.5`. Other alerts use single-pass diagnostic. Each reflection round's output is pushed as a distinct SSE event so the frontend renders the iteration as a visible conversation.
