---
html_theme.sidebar_secondary.remove: true
---

# PEPFlow

Welcome to <span class="brand-color">PEPFlow</span>!

<span class="brand-color">PEPFlow</span> builds on the Performance Estimation Problem (PEP) framework, a powerful approach for analyzing the convergence of optimization algorithms. In essence, PEP formulates performance guarantees of an algorithm into tractable optimization problems and helps provide analytical proofs of convergence. <span class="brand-color">PEPFlow</span> streamlines the entire PEP <span style="color:red; font-weight:bold">workflow</span>, making PEP-based analysis more accessible and efficient.


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


<span class="brand-color">PEPFlow</span> offers the following key features for building a systematic and interactive <span style="color:red; font-weight:bold">workflow</span>:
- automated process for formulating and solving PEPs;

- interactive dashboard to explore and search exact relaxations of primal PEPs;

- direct access to key mathematical objects for deriving and verifying analytical proofs.

<span class="brand-color">PEPFlow</span>, as well as this website, is under active development. Stay tuned!

```{toctree}
:hidden:
:maxdepth: 1

quickstart.ipynb
tutorial
api_reference
encyclopedia
```