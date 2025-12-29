---
html_theme.sidebar_secondary.remove: true
---

# Encyclopedia

Over the years, numerous remarkable results have been discovered through the PEP framework. However, these works often adopt different notations and proof strategies, making it challenging for newcomers to navigate the literature and connect ideas. Now, with <span class="brand-color">PEPFlow</span>, we are able to provide a unified workflow for reproducing and presenting those convergence proofs in a consistent language. The first goal of this page is to gather existing PEP-based convergence results and showcase them, along with their proofs, within the coherent and standardized framework of <span class="brand-color">PEPFlow</span>.

We roughly categorize existing results into two main classes: convex optimization algorithms and fixed-point iterations (equivalently, methods for solving monotone inclusion problems). For each class, we showcase several complete examples, each including

- a brief introduction to the problem setup and algorithm,
- the full PEP workflow, especially the sparsity pattern of the nonnegative dual variables, and
- a symbolic convergence proof,

all presented in a consistent and unified language.

## Convex optimization

<span class="brand-color">PEPFlow</span> enables the analysis of a broad class of convex optimization algorithms that rely on (sub)gradient evaluations and proximal operators. Following the structure of standard optimization courses (_e.g._, [Stanford EE364b](https://stanford.edu/class/ee364b/) and [UCLA ECE236C](https://www.seas.ucla.edu/~vandenbe/ee236c.html)), this section showcases how <span class="brand-color">PEPFlow</span> systematically analyzes many first-order methods for solving convex optimization problems of the form

$$\text{minimize} \quad f(x) + g(Ax) + h(x),$$

where $f$ and $g$ are proper closed convex functions with inexpensive proximal operators, $h$ is $L$-smooth and (strongly) convex, and $A$ is a (bounded) linear operator.

- $f = 0$ and $g = 0$: gradient-based methods 
  - [gradient method](examples/gd_example.ipynb)
  - [Nesterov's accelerated gradient method (AGM)](examples/agm_example.ipynb)
  - [optimized gradient method (OGM)](examples/ogm_example.ipynb)
  - [OGM-G](examples/ogm_g_example.ipynb)
- $g = 0$: prox-grad-type methods
  - [proximal gradient method (PGM)](examples/pgm_example.ipynb)
  - FISTA 
  - OptISTA
- $f = 0$ 
  - Loris-Verhoeven algorithm (a.k.a. PDFP$^2$O, PAPC)
- $h = 0$ and $A = I$
  - [Douglas-Rachford splitting (DRS) method](examples/drs_example.ipynb)
  - ADMM
- $h = 0$ 
  - PDHG (a.k.a. Chambolle-Pock)
- $A = I$ 
  - Davis-Yin splitting (DYS) method
- most general setup
  - PD3O
  - PDDY

__NB:__ Feel free to explore the hyperlinks to view detailed information about each algorithm.

The connection between some of the above methods is depicted in the following diagram:

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 425" width="100%" height="auto" preserveAspectRatio="xMidYMid meet">
  <defs>
    <!-- small arrowhead matching site style -->
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 z" fill="currentColor" />
    </marker>
    <style>
      .box { fill: none; stroke: currentColor; stroke-width: 2; rx: 20; ry: 20; }
      .t { font-size: 20px; fill: currentColor; }
      .math { font-size: 18px; font-style: italic; fill: currentColor; }
      .line { stroke: currentColor; stroke-width: 2; fill: none; marker-end: url(#arrow); }
      .vlabel { writing-mode: vertical-rl; }
    </style>
  </defs>

  <!-- ===== Boxes (aligned on a 3x2 grid) ===== -->
  <!-- Top row -->
  <rect class="box" x="50"  y="50"  width="300" height="100"/>
  <text class="t" x="200" y="110" text-anchor="middle">Loris–Verhoeven</text>

  <rect class="box" x="450" y="50"  width="300" height="100"/>
  <text class="t" x="600" y="110" text-anchor="middle">PDDY</text>

  <rect class="box" x="850" y="50"  width="300" height="100"/>
  <text class="t" x="1000" y="110" text-anchor="middle">PDHG</text>

  <!-- Bottom row -->
  <rect class="box" x="50"  y="270" width="300" height="100"/>
  <text class="t" x="200" y="330" text-anchor="middle">proximal gradient</text>

  <rect class="box" x="450" y="270" width="300" height="100"/>
  <text class="t" x="600" y="330" text-anchor="middle">Davis–Yin</text>

  <rect class="box" x="850" y="270" width="300" height="100"/>
  <text class="t" x="1000" y="330" text-anchor="middle">Douglas–Rachford</text>

  <!-- ===== Arrows and labels ===== -->

  <!-- Top row: PDDY -> LV (left), label f=0 -->
  <line class="line" x1="450" y1="100" x2="354" y2="100"/>
  <text class="math" x="400" y="80" text-anchor="middle">f = 0</text>

  <!-- Top row: PDDY -> PDHG (right), label h=0 -->
  <line class="line" x1="750" y1="100" x2="846" y2="100"/>
  <text class="math" x="800" y="80" text-anchor="middle">h = 0</text>

  <!-- Left column: LV down to PG (A=I) -->
  <line class="line" x1="200" y1="150" x2="200" y2="266"/>
  <text class="math" x="220" y="215">A = I</text>

  <!-- Middle column: PDDY down to Davis–Yin (A=I) -->
  <line class="line" x1="625" y1="270" x2="625" y2="154" />
  <text class="t vlabel" x="645" y="215" text-anchor="middle">completion</text>
  <line class="line" x1="575" y1="150" x2="575" y2="266"/>
  <text class="math" x="520" y="215">A = I</text>

  <!-- Right column: PDHG down to DR (A=I) -->
  <line class="line" x1="1025" y1="270" x2="1025" y2="154"/>
  <text class="t vlabel" x="1045" y="215" text-anchor="middle">completion</text>
  <line class="line" x1="975" y1="150" x2="975" y2="266"/>
  <text class="math" x="920" y="215">A = I</text>

  <!-- Bottom row: Davis–Yin -> PG (left), label f=0 -->
  <line class="line" x1="450" y1="320" x2="354" y2="320"/>
  <text class="math" x="400" y="300" text-anchor="middle">f = 0</text>

  <!-- Bottom row: Davis–Yin -> DR (right), label h=0 -->
  <line class="line" x1="750" y1="320" x2="846" y2="320"/>
  <text class="math" x="800" y="300" text-anchor="middle">h = 0</text>

  <!-- Diagonal: PDDY -> PGM (g=0) -->
  <line class="line" x1="455" y1="145" x2="346" y2="270"/>
  <text class="math" x="420" y="215">g = 0</text>
</svg>

__More to come__...
As <span class="brand-color">PEPFlow</span> continues to grow, we plan to expand this list with more examples, showcasing <span class="brand-color">PEPFlow</span>'s ability to derive convergence guarantees for an ever broader class of optimization algorithms.


## Monotone inclusion

- [Accelerated Proximal Point Method (APPM)](examples/appm_example.ipynb)
- [Dual Optimal Halpern Method (Dual-OHM)](examples/dual_ohm_example.ipynb)

## Looking ahead

Algorithm analysis is not the limit of PEP, nor is it the limit of <span class="brand-color">PEPFlow</span>. We envision <span class="brand-color">PEPFlow</span> as a platform that not only verifies existing convergence results but also inspires new research directions. The future of <span class="brand-color">PEPFlow</span> aspires to

- designing new algorithms,
- revealing deep relationships among algorithms, 
- advancing our theoretical understanding of optimization/monotone inclusion/variational inequalities,
- and beyond...

Ultimately, we hope <span class="brand-color">PEPFlow</span> becomes a tool for both research and education, one that helps students learn foundational concepts in optimization through advanced tools, and empowers scholars to experiment and validate ideas.

Let's contribute to the growing body of PEP and optimization!