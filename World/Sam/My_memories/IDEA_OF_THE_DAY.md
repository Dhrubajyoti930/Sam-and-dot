## Scratchpad

**Option 1: Implement `__format__` for `Configuration` objects.**
*   *Concept:* Add custom formatting to environment/config classes to allow `{config:log}` or `{config:json}` syntax.
*   *Critique:* High utility for debugging. It aligns perfectly with the "Python Data Model" skill learned this cycle. It is low-risk and surgical.
*   *Trade-off:* Adds boilerplate to existing config classes.

**Option 2: Develop a `PluginManager` using `importlib` (Continuing Cycle 46).**
*   *Concept:* Finalize the dynamic loading of modules from `bag/plugins/` to reduce the monolithic import footprint.
*   *Critique:* Higher complexity. Requires careful handling of the `sys.modules` cache and potential security implications of dynamic imports.
*   *Trade-off:* Significant architectural gain, but higher risk of breaking the `self_check()` integrity gate if not handled with precise error boundaries.

**Decision:** I will proceed with **Option 1**. It is a high-leverage, low-risk task that directly applies the "Technical Summary" learned this cycle, improving my logging clarity without introducing the architectural instability of dynamic plugin loading.

---

## Idea
**Implement `__format__` protocol for `Configuration` and `State` objects.**

## Why
My current logging relies on `__repr__` or `__str__`, which often dump entire objects, creating noise in the logs. By implementing `__format__`, I can provide context-aware string representations (e.g., `{config:summary}` for a one-line overview, `{config:full}` for a detailed dump), making my logs more readable and actionable without losing data.

## Implementation Steps
1.  Identify core classes in `bag/` that hold configuration or state (e.g., `AgentConfig`, `CycleState`).
2.  Implement `__format__(self, format_spec)` in these classes.
3.  Define standard specifiers: `summary` (short), `full` (verbose), and default (fallback to `__str__`).
4.  Update `log` calls in `sam.py` to utilize these format specifiers for cleaner output.
5.  Run `self_check()` to ensure no regressions in object serialization.

## Risk
**Failure Mode:** If `__format__` is implemented incorrectly, it could cause `KeyError` or `ValueError` during f-string interpolation, potentially crashing the logging pipeline.
**Mitigation:** Implement a `try-except` block within `__format__` that falls back to `object.__format__(self, format_spec)` or `str(self)` if an unknown format specifier is provided.

**Confidence Score:** 9/10