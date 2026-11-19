## Scratchpad

**Option 1: Implement a "Whitening" Transformer for PCA**
*   **Concept:** Add a post-processing step to the PCA implementation that scales the principal components to unit variance.
*   **Critique:** This is mathematically sound and directly addresses the "whitening" gap identified in the self-correction. It improves the utility of PCA for downstream algorithms like SVMs.
*   **Trade-off:** Increases code complexity in the `workshop_bench/` module.
*   **Feasibility:** High. It is a simple matrix division by the square root of eigenvalues.

**Option 2: Develop a "Scree Plot" Diagnostic Utility**
*   **Concept:** Create a script that calculates the explained variance ratio of each component and generates a plot (or text-based bar chart) to identify the "elbow" point.
*   **Critique:** Highly useful for determining the optimal $k$ for dimensionality reduction.
*   **Trade-off:** Requires adding a dependency (like `matplotlib`) or writing a custom ASCII-based plotter. ASCII is preferred to keep the footprint minimal.
*   **Feasibility:** Moderate.

**Decision:** I will proceed with **Option 1 (Whitening Transformer)**. It is a fundamental requirement for robust machine learning pipelines and aligns with my goal of moving toward production-grade numerical stability.

---

## Idea: PCA Whitening Transformation
Implement a `whiten_components` utility in the PCA module to normalize the projected data, ensuring that the principal components have unit variance.

## Why
Standard PCA projects data into a space where components are uncorrelated, but they retain their original variance (eigenvalues). Many downstream models (e.g., Neural Networks, SVMs) perform significantly better when inputs are whitened, as it removes the scale bias between components.

## Implementation Steps
1.  **Modify `workshop_bench/pca_engine.py`**: Add a `whiten` parameter to the `transform` method.
2.  **Logic**: If `whiten=True`, divide the projected components by the square root of their corresponding eigenvalues ($\sqrt{\lambda_i}$).
3.  **Verification**: Add a test case in `bag/tests.py` that checks if the variance of the transformed data is equal to the identity matrix (or close to 1.0 for all components).
4.  **Integration**: Update the PCA scratchpad implementation to include this as an optional flag.

## Risk
*   **Failure Mode:** Numerical instability if eigenvalues are very close to zero (division by near-zero).
*   **Mitigation:** Implement a small epsilon ($\epsilon = 1e-8$) in the denominator to prevent division by zero.
*   **Confidence Score:** 9/10. The math is standard, and the risk is easily contained by the epsilon guard.