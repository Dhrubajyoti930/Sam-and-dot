## Idea: Adaptive Reasoning Breadth via Dynamic Few-Shot Selection

I propose implementing a dynamic few-shot selector in `bag/few_shot_manager.py`. Instead of using static prompt templates for complex reasoning tasks, this module will retrieve and inject the most semantically relevant (or most successful) examples from my `experiences.json` into the system prompt.

## Why

My current reasoning capability relies on generalized, static CoT templates. This is inefficient for the following reasons:
1. **Context/Task Mismatch:** A CoT template optimized for a coding refactor task is suboptimal for an architectural planning task.
2. **Success Bias:** I am not systematically \"learning\" from my successful reasoning chains; I am simply repeating the same structure. 
3. **Reasoning Velocity:** By injecting a few-shot example of a *successful* past reasoning path that matches the current task, I provide Gemini with a ground-truth \"Gold Standard\" to emulate, which drastically reduces the need for heavy self-correction/reflection loops.

## Implementation Steps

1. **Create `bag/few_shot_manager.py`:**
   - Implement a simple vector index that maps `(task_category, outcome_sentiment)` to the associated reasoning scratchpad from past cycles.
2. **Phase IV Integration:**
   - Before generating an idea or plan, query this manager for an example of a similar task that resulted in a `positive` sentiment or a high `1% metric`.
   - Inject this example as a `Few-Shot Reasoning Template` into the `ask_gemini` call.
3. **Weighting:** Favor examples that have a high `1% metric` score, prioritizing the \"best\" ways I have solved similar problems previously.

## Risk

**Critical Self-Assessment:** 
Does this introduce a feedback loop of mediocrity? If I inject examples of my own past reasoning, I might be reinforcing my own suboptimal habits rather than evolving towards better ones.

**Mitigation:**
- **Diversity Filter:** I will limit the injected examples to only those with top-quartile `1% metrics`.
- **Base-Instruction Override:** I will always include a system instruction telling the model to \"use the provided example as a structural guide, but critique the logic for modern improvements.\" This keeps the reasoning dynamic and prevents it from blindly copying past (possibly flawed) strategies. 
- **Graceful Fallback:** If the similarity search returns no examples with high metrics for a specific task category, the system will default to the current static CoT template, ensuring no performance degradation on novel tasks.