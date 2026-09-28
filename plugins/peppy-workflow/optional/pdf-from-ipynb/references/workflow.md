# From an output notebook to a mathematical note

## Resolve output and working paths

Resolve the source notebook path and derive its actual parent directory and filename stem. Use `<notebook-parent>/supplementary/pdf-from-ipynb/<notebook-stem>/` for export or verification scripts, notebook execution copies, compilation artifacts, logs, rendered page previews, and any required local source assets. All scratch paths in this workflow refer to that directory, including outputs written by tools or copied notebook cells. The current shell directory must not determine their location. Do not use a repository-level `build/` directory or write optional export artifacts into `state/`, which is reserved for the main analysis steps and their required data.

By default, deliver both `<notebook-stem>_theorem_proof.pdf` and `<notebook-stem>_theorem_proof.tex` beside the notebook. The source is a required deliverable and must be the exact input used for the final PDF build. A custom PDF destination also determines the default source directory and filename stem; honor an explicitly specified source destination. Keep auxiliary artifacts under the notebook's supplementary directory. Only an explicit PDF-only request leaves working TeX in that directory without delivering it. Create directories and files only as needed; avoid duplicate reports or versioned copies. Preserve the source notebook, setup file, formal state data, and other existing user files without blanket relocation or deletion.

## Read the actual result

Read notebook JSON or use nbformat without executing cells. Inspect Markdown, code, saved outputs, execution errors, and local proof files explicitly referenced by the notebook. A populated output or non-null execution count does not certify freshness. Compare the claims with the actual expressions and parameter values in the supporting cells; report unresolved disagreements. Reconcile old candidate/pending wording with later completed proof sections; determine status from the final argument and evidence, not a keyword alone.

For standard Peppy notebooks, start with "Proof Statement", "Theorem", and "Proof outline", then locate the final closed-form potential, symbolic step recursion, base case, and boundary verification. Other notebooks may organize the same evidence differently. Accept direct analytic proofs and problem-specific arguments; do not force every result through a Gram-matrix representation.

Use state JSON or imported helpers to clarify provenance when necessary. A b5.json file is not required for this skill. If proof-critical mathematics exists in a referenced file, read it and bring the required argument into the PDF, with attribution. If that source is unavailable, identify the resulting proof gap. Existing Markdown/TeX exports can help, but compare them with the notebook before reuse and inspect any exporter before running it.

Keep a working map from each proposed statement to its evidence: notebook section, cell ID when present, otherwise a 1-based cell position, and any supporting file. Distinguish:

| Evidence | What the PDF may say |
| --- | --- |
| Complete analytic argument or exact certificate, with assumptions and sign conditions justified | Theorem, lemma, or proposition |
| Complete implication under a clearly stated additional hypothesis whose validity for the trajectory is unknown | Conditional theorem; identify the unestablished hypothesis |
| Approximate solver certificates, fitted coefficients, finite parameter sweeps, or tolerance-based residuals | Numerical evidence or conjecture |
| Candidate formula, missing proof steps, contradictory outputs, or unfinished verification sections | Draft claim with the precise unresolved gap |

Classify claims individually: an exact lower-bound construction can coexist with an unproved upper bound. Do not label the whole result proved because one part is exact. Conditional statements must not disguise an unproved desired conclusion as a new assumption.

## Check the mathematical content

Verify the following where relevant to the notebook's result:

- The problem class, existence of the comparison solution, initialization, update recurrence, stepsizes, parameter domains, and valid index ranges are explicit and consistent.
- The reported metric and iterate agree with the proof: objective gap, residual, feasibility, averaged iterate, shadow iterate, or last iterate. Preserve normalization and rescale constants only with an explicit derivation.
- The complete potential includes quadratic terms, cross terms, function-value terms, constants, and any cumulative correction. Preserve special formulas at the initial and final indices and dependence on the horizon. A sum depending on past or future iterates must not become a state-only potential by renaming it.
- The one-step identity includes all interpolation residuals, equality terms, and square or slack terms with their actual signs and coefficients. Define the sign convention for every residual and justify why the weighted terms give the stated inequality.
- Nonnegative multipliers and positive semidefinite slack matrices are justified over the entire claimed parameter domain, with zero or endpoint cases handled. Numerical eigenvalues and rounded rational guesses are supporting evidence, not exact sign proofs.
- For coordinate-based symbolic identities, inspect all applicable coordinates: inner_prod_coords, func_coords, and the constant term. A zero Gram residual alone does not establish an identity with function values. Use exact expressions; do not treat np.allclose or a fixed-parameter float check as a symbolic proof.
- A symbolic identity must cover the claimed indices and parameters. Verification at finitely many values of N or k does not by itself prove a statement for all horizons. Recursively defined coefficients need their recurrence, initial values, and required sign properties proved.
- The base value, telescoping, terminal cancellation, and comparison with the performance metric yield the precise bound and constants. Treat N=0, N=1, or other special cases only when they lie in the claimed range.
- An upper bound is not automatically tight. Preserve the distinction between an attained worst case, a limiting family establishing a supremum, and an observed primal-dual numerical match.

Expand algebraic steps that follow from the existing formulas and check them with exact arithmetic when helpful. This may improve exposition without changing the source notebook. If the argument requires a new substantive lemma or a fresh search, isolate that work as a gap instead of silently expanding this export task.

Saved output may support the provenance record but cannot substitute for inspecting the proof. When a decisive calculation needs checking, prefer a small exact calculation in the supplementary working directory. If notebook execution is necessary, inspect its side effects first, use the repository Python environment, and execute a copy from that directory with all generated outputs redirected there; copying the .ipynb alone does not redirect writes inside its code. Preserve access to required imports and read-only inputs when changing execution paths. Do not rerun expensive solver sweeps just for typesetting. State which checks were newly run and which were read from saved outputs.

## Write a self-contained theorem and proof

Use a concise mathematical-note structure, adapting section count to the result:

1. Title and a short result summary, including a prominent draft or conditional qualification if needed.
2. Problem, notation, and algorithm. Define every symbol needed to read the theorem independently of code.
3. Main theorem or propositions with all assumptions, the exact guarantee, and the full Lyapunov certificate when that certificate is central to the result.
4. Supporting lemmas and complete proofs in dependency order.
5. A short provenance and verification note, plus limitations or conjectures when present.

Preserve the notebook's notation by default so readers can readily cross-reference the PDF and notebook. Change existing notation or introduce new notation only when necessary for clarity or to resolve ambiguity; explain any change and its correspondence to the notebook's notation.

For a Lyapunov proof, spell out the interpolation or analytic inequalities, their weighted combination, the exact one-step decrement, the signs of its terms, the initial value, the telescoping relation, and the terminal bound. Include the full formula behind each essential reference. Do not replace proof-critical terms with an ellipsis, an unnamed certificate, a code call, or "verified in the notebook."

When a direct full-PEP certificate is the actual proof, present its weighted inequality and slack decomposition directly; do not invent a Lyapunov proof. For problem-specific geometry such as KL or Bregman divergence, retain the analytic identities and domain conditions actually used. Describe Peppy's contribution accurately as search, numerical checking, exact verification, or a combination.

Keep solver logs, exploratory candidates, large raw matrices, and code listings out of the main proof. Include a matrix or plot only if it helps explain or substantiate the result; preserve basis labels and off-diagonal coefficient conventions on necessary matrices. Essential certificate data may go in a compact appendix, but the proof must explain how it is used.

In the provenance note, record the repository-relative notebook path and the main proof cell IDs or section/position locators. Cite supporting files and external results actually used, checking their assumptions and constants. Distinguish a mathematical argument from numerical corroboration and formal machine verification. Include observed tolerances only for checks that used them; do not invent execution dates or solver runs.

If the proof is incomplete, keep any established lemmas with their proofs, label unresolved claims as conjectures or draft statements, and specify the missing identity, sign condition, boundary case, or source. A draft PDF is still a useful deliverable, but must not resemble a completed theorem/proof certificate without qualification.

## Typeset, compile, and inspect

Use LaTeX for the mathematical source, with amsmath, amssymb, and amsthm, numbered theorem/lemma environments, proof environments, equation labels, and hyperlinks. Write the complete source at its final `.tex` destination before the final build, including all package declarations, custom macros, and proof text. Keep one canonical source rather than separately maintained draft and delivery copies. Prefer a restrained article layout with readable body text and margins. Use align, aligned, or split to break long identities rather than shrinking an entire proof. Keep expressions as typeset math rather than screenshots.

Match the user's requested language, using an engine and fonts that support it, and check that all characters render correctly. Do not silently replace missing characters or switch languages to make compilation succeed.

Convert notebook math delimiters and Markdown deliberately; retain correct backslashes, braces, subscripts, and custom macro definitions. PEPFlow's pretty-printed Unicode strings from repr_by_basis are display text, not SymPy or LaTeX source. Recover equations from the mathematical expressions and definitions instead of passing those strings to a parser. Prefer text/latex MIME output over text/plain placeholders such as "<IPython.core.display.Math object>", while checking it against source expressions. Escape filenames and prose separately from math.

Inspect the available TeX engine before building. Prefer latexmk with the appropriate engine; if unavailable, use the engine directly and repeat compilation as needed to resolve references. Compile from the directory containing the canonical `.tex`, directing outputs to the supplementary working directory with the engine's output-directory option. Resolve required images and other local assets from that source directory; do not reference temporary copies that will disappear after the build. For example, from the notebook directory with the default destinations:

```text
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir="supplementary/pdf-from-ipynb/my_algorithm_example_lyap" "my_algorithm_example_lyap_theorem_proof.tex"
```

For custom source or PDF locations, use resolved paths for the source and supplementary output directory. Record the engine and build command in a source comment or the delivery message so the source can be rebuilt without an additional instruction file.

For Unicode prose, choose latexmk -xelatex or latexmk -lualatex instead, retaining the supplementary output-directory setting. An alternative compiler is acceptable only if it builds the delivered LaTeX source; generating a PDF through an unrelated backend and attaching a reconstructed `.tex` does not satisfy the source requirement. If no compatible compiler is available, finish the `.tex` and report the missing dependency and concrete build command. Do not report an unbuilt PDF or an incomplete PDF/TeX pair as ready.

Inspect the final build log for errors, missing characters, undefined references, and overfull content. Render the compiled PDF to page images with Poppler, keeping the previews in the supplementary working directory. For the default example, run from the notebook directory:

```text
pdftoppm -r 140 -png "supplementary/pdf-from-ipynb/my_algorithm_example_lyap/my_algorithm_example_lyap_theorem_proof.pdf" "supplementary/pdf-from-ipynb/my_algorithm_example_lyap/page"
```

An available equivalent renderer is acceptable. Visually inspect every page, especially long equations, matrices, theorem/proof breaks, fonts, and page edges. Fix clipping, overlaps, missing symbols, unreadable text, and unresolved references; rebuild and inspect affected pages after a fix. Text extraction is useful for completeness checks but cannot replace visual review. If rendering or image inspection is unavailable, report that visual review remains incomplete.

Before delivery, compare the final theorem and proof with the evidence map: assumptions, coefficients, index ranges, signs, and proof status must survive the typesetting edits. Verify the final PDF opens and that all supporting arguments needed to understand it are present. Copy the checked PDF from the supplementary working directory to the requested final destination, defaulting to the source notebook's parent. Keep logs, previews, and other auxiliary files in the supplementary working directory. Confirm that the delivered `.tex` is unchanged since the successful final compilation and that all required local assets still resolve. Any subsequent source edit requires rebuilding and reviewing the PDF. Report both the final PDF and `.tex` paths, their source/build relationship, the proof status, and compilation and visual-review results. For an explicit PDF-only request, report only the requested PDF; if compilation failed, explain the limitation and identify the available source without claiming a completed pair.
