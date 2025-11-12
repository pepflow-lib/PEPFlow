# Tutorial

Performance Estimation Problems (PEP) [^1], [^2] offer a systematic framework for analyzing optimization algorithms. Instead of proving convergence rates on a case-by-case basis, PEP reformulates the search for the worst-case performance of an algorithm as a tractable optimization problem accessible to numerical solvers. Solving these problems numerically provides two complementary benefits:
- numerical evidence that illustrates the convergence behavior of the algorithm, and
- quantitative insights that can guide and support the derivation of analytical proofs.

<span class="brand-color">PEPFlow</span> is a Python package that offers a streamlined workflow for applying the PEP framework in practice. Its interactive environment allows users to move seamlessly from formulating PEP to obtaining numerical evidence of convergence and even extracting analytical proofs. The overall workflow is summarized in the diagram below:

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 425" width="100%" height="auto" preserveAspectRatio="xMidYMid meet">
  <defs>
    <!-- smaller arrowhead -->
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 z" fill="currentColor" />
    </marker>
  </defs>

  <!-- Row 1 -->
  <rect x="50" y="50" width="300" height="100" rx="20" ry="20" stroke="currentColor" fill="none" stroke-width="2"/>
  <text x="200" y="105" text-anchor="middle" font-size="20" fill="currentColor">Provide user input</text>

  <rect x="450" y="50" width="300" height="100" rx="20" ry="20" stroke="currentColor" fill="none" stroke-width="2"/>
  <text x="600" y="105" text-anchor="middle" font-size="20" fill="currentColor">Formulate Primal PEP</text>

  <rect x="850" y="50" width="300" height="100" rx="20" ry="20" stroke="currentColor" fill="none" stroke-width="2"/>
  <text x="1000" y="90" text-anchor="middle" font-size="20" fill="currentColor">Numerically verify</text>
  <text x="1000" y="120" text-anchor="middle" font-size="20" fill="currentColor">convergence rate</text>

  <!-- Row 2 -->
  <rect x="50" y="250" width="300" height="100" rx="20" ry="20" stroke="currentColor" fill="none" stroke-width="2"/>
  <text x="200" y="290" text-anchor="middle" font-size="20" fill="currentColor">Relax primal PEP</text>
  <text x="200" y="320" text-anchor="middle" font-size="20" fill="currentColor">via interactive dashboard</text>

  <rect x="450" y="250" width="300" height="100" rx="20" ry="20" stroke="currentColor" fill="none" stroke-width="2"/>
  <text x="600" y="305" text-anchor="middle" font-size="20" fill="currentColor">Find analytical proofs</text>

  <rect x="850" y="250" width="300" height="100" rx="20" ry="20" stroke="currentColor" fill="none" stroke-width="2"/>
  <text x="1000" y="305" text-anchor="middle" font-size="20" fill="currentColor">Verify analytical proofs</text>

  <!-- Arrows Row 1 -->
  <line x1="350" y1="100" x2="446" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="750" y1="100" x2="846" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Sequential arrow: Step 3 -> Step 4 (loop down and left) -->
  <path d="M1000 150 V200 H200 V246" fill="none" stroke="currentColor" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Row 2 arrows -->
  <line x1="350" y1="300" x2="446" y2="300" stroke="currentColor" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="750" y1="300" x2="846" y2="300" stroke="currentColor" stroke-width="2" marker-end="url(#arrow)"/>
</svg>

In this tutorial, we will walk through the complete PEP workflow, demonstrating how <span class="brand-color">PEPFlow</span> complements the PEP theory and serves as a practical tool for learning, experimentation, and research.

The rest of this tutorial is organized as follows.

```{toctree}
:maxdepth: 2

tutorial_notebooks/tutorial_part_1.ipynb
tutorial_notebooks/tutorial_part_2.ipynb
tutorial_notebooks/tutorial_part_3.md
```

[^1]: Y. Drori and M. Teboulle. Performance of first-order methods for smooth convex minimization: a novel approach. _Mathematical Programming_, 145(1-2):451–482, 2014.
[^2]: B. Goujaud, A. Dieuleveut, and A. B. Taylor. On fundamental proof structures in first-order optimization. In _62nd IEEE Conference on Decision and Control (CDC)_, 2023.
