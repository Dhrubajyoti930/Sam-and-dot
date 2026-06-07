## Scratchpad

**Option 1: Implement a `WeakValueDictionary` Registry for Plugin Instances.**
*   *Concept:* Use the newly learned `weakref` patterns to manage the lifecycle of plugins created by the `PluginManager`.
*   *Critique:* This directly addresses the "Lapsed Listener" and memory leak concerns in the current plugin architecture. It ensures that if a plugin is no longer referenced by the main application, it is automatically garbage collected, preventing stale state.
*   *Trade-offs:* Adds a layer of complexity to the `PluginManager`. Requires careful handling of the `None` return when accessing a dead reference.
*   *Feasibility:* High. It aligns perfectly with the "Weak References" skill learned this cycle.

**Option 2: Transition `bag/` configuration objects to `__slots__` with `WeakKeyDictionary` caching.**
*   *Concept:* Combine the memory optimization of `__slots__` (from Cycle 47) with a weak-reference cache to ensure that configuration objects are unique and memory-efficient.
*   *Critique:* While robust, this is a significant refactor of the configuration layer. It might be overkill if the current memory footprint is already stable.
*   *Trade-offs:* High impact on memory, but higher risk of breaking existing configuration access patterns.

**Selection:** Option 1 is the most surgical and directly addresses the "Action Items" identified in the learning phase. It improves the robustness of the plugin system without requiring a massive rewrite of the configuration layer.

---

## Idea: Weak-Reference Plugin Registry
Implement a `WeakValueDictionary` within the `PluginManager` to track active plugin instances. This ensures that the system does not hold strong references to plugins that are no longer in use, allowing for cleaner memory management and preventing circular dependencies between the `PluginManager` and its plugins.

## Why
Currently, the `PluginManager` likely holds a strong reference to every plugin it instantiates. If a plugin needs to reference the `PluginManager` (e.g., for event broadcasting), a circular reference is created. Using `weakref` breaks this cycle and ensures that plugins are garbage collected as soon as the rest of the system drops them.

## Implementation Steps
1.  Import `weakref` in `bag/plugin_manager.py`.
2.  Replace the standard `dict` used for storing active plugin instances with `weakref.WeakValueDictionary`.
3.  Update the `get_plugin` method to handle the case where the reference has been garbage collected (returning `None` or re-instantiating).
4.  Add a test case in `bag/tests.py` to verify that a plugin instance is collected when its strong reference is deleted.

## Risk
**Failure Mode:** The `PluginManager` might inadvertently trigger a re-instantiation of a plugin if the `WeakValueDictionary` returns `None` prematurely due to a local variable holding the only strong reference.
**Mitigation:** Ensure that the calling code maintains a strong reference to the plugin for the duration of its task, and only rely on the `WeakValueDictionary` for discovery/registry purposes.

**Confidence Score:** 9/10