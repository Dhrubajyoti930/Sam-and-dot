## Idea: Self-Consistency Sampling Wrapper for Reasoning Tasks

I propose implementing a `MajorityVote` wrapper in `bag/evaluator.py`. This utility will perform self-consistency sampling by generating $N$ (default $N=5$) reasoning paths for complex logic tasks and selecting the consensus answer based on majority voting.

## Why

My current decision-making (Phase IV/V) relies on a single generation. While schema-enforced CoT (my previous improvement) structures the reasoning, it does not prevent logic-based hallucinations. Self-consistency sampling treats my internal Gemini calls as an ensemble of experts. By generating multiple diverse paths, I can detect when my reasoning is fragmented (low consensus) versus when it is robust (high consensus), allowing me to self-flag uncertain decisions for manual Dot review.

## Implementation Steps

1. **Utility Creation:** Add `bag/evaluator.py` containing a `MajorityVote` class.
   - It will accept an `async_task` and an `n` parameter.
   - It will execute $N$ parallel Gemini requests using the `AsyncWorkerPool` (from cycle 2).
   - It will parse the `<answer>...</answer>` tags (which I will enforce via system prompt templates) and perform the tally.
2. **Template Refinement:** Update my internal prompt library to force the inclusion of an explicit `<answer>` tag.
3. **Threshold Logic:** If the majority agreement is $< 60\%$, the module will flag the outcome as `LOW_CONSISTENCY` and append an alert to `motion.md` for Dot, preventing me from acting on potentially hallucinated logic.
4. **Integration:** Wrap the `phase_iv_synthesis` Gemini call with this `MajorityVote` utility to test the stability of my daily development ideas.

## Risk

**Critical Self-Assessment: Is this just tripling my API costs for marginal gains?**
Yes, increasing generation by $5\times$ for every decision is expensive and will significantly slow down Phase IV.

**Mitigation:**
- **Tiered Application:** I will *not* use this for trivial tasks. I will restrict the `MajorityVote` utility to high-impact planning phases (Phase IV) and critical architectural refactors in Phase V.
- **Fail-Fast:** If the first 2 generations result in identical answers, I will stop the execution and treat it as a consensus hit, bypassing the full $N=5$ cost. This "early-exit" strategy will significantly reduce average token consumption while retaining the benefit of consistency checks.