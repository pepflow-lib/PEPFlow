# Summary

This tutorial demonstrates the complete workflow of PEP to derive convergence proofs of an optimization algorithm.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 425" width="100%" height="auto" preserveAspectRatio="xMidYMid meet">
  <defs>
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
  <text x="200" y="290" text-anchor="middle" font-size="20">
    <tspan fill="red">Relax</tspan>
    <tspan fill="currentColor"> primal PEP</tspan>
  </text>
  <text x="200" y="320" text-anchor="middle" font-size="20" fill="currentColor">via interactive dashboard</text>

  <rect x="450" y="250" width="300" height="100" rx="20" ry="20" stroke="currentColor" fill="none" stroke-width="2"/>
  <text x="600" y="305" text-anchor="middle" font-size="20">
    <tspan fill="red">Find</tspan>
    <tspan fill="currentColor"> analytical proofs</tspan>
  </text>

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

After the user provides the four ingredients of convergence analysis, <span class="brand-color">PEPFlow</span> automatically formulates both Primal PEP and Dual PEP and solves them solve them numerically using CVXPY.

To obtain an analytical convergence proof, however, several steps still require human interaction. The user is encouraged to use the interactive dashboard to explore and gain intuition about the sparsity pattern of the dual variable $\lambda$, and to identify its symbolic expression — a step that still relies on human intelligence.

Once $\lambda$ is determined, the remaining task is to verify that the other dual variable, $S$, is positive semidefinite. This verification is largely mechanical: it involves decomposing the inner product $\langle G, S \rangle$ into a sum of squares, which corresponds to performing the Cholesky factorization of $S$.

Moreover, <span class="brand-color">PEPFlow</span> offers a user-friendly interface for symbolic verification of convergence proofs.
Two key features in <span class="brand-color">PEPFlow</span> make this workflow intuitive and efficient:

- an interactive dashboard for visualizing and exploring sparsity patterns of $\lambda$;

- In <span class="brand-color">PEPFlow</span>, all function values and inner products are represented in terms of __coordinates__ of <span class="brand-color">basis variables</span>. <span class="brand-color">PEPFlow</span> enables users to access these quantities simply by their name tags, while all computations are handled automatically in coordinates---eliminating the need to manually construct or verify coefficients in the Primal PEP.