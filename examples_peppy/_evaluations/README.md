# Peppy experimental supplementary

Experimental materials for Section 4, Table 2 and Appendix E of *Peppy: An AI-Assisted Workflow for Tight Convergence Analysis of Optimization Algorithms*. The six conditions each have five independent attempts. Conjecture case studies are supplied separately.

## Read the results

- [Table 2: results and generation costs](table2.md)
- [All 30 submitted notebooks, input packets and individual reviews](attempts.md)
- [Run the table calculation or saved proof checks](supplementary/tools/README.md)

The final mathematical assessment is 30 PASS after the dated post hoc assessment; original completed delivery is 27/30. The attempt index links the applicable evidence and keeps these outcomes distinct. All five attempts per condition remain in the cost calculation.

## Files

Each of `bppm/`, `dual_feg/`, `feg/`, `ogm/`, `pgm_with_sos/` and `pgm_without_sos/` contains repetitions `r01` through `r05`, with submitted notebooks and their trial-specific data. The three additional PGM notebooks are intermediate trial artifacts.

`supplementary/` contains inputs, original assessments, timing/token records and operational logs. `posthoc_20260924T024014Z/` contains the final assessment and supporting reviews. `supplementary/tools/` contains the calculation and replay tools, their validation reports, and one shared framework snapshot. The tools reconstruct the common trial source files when preparing an execution copy.

Earlier examples in the parent `examples_peppy/` directory are separate from these 30 submissions. For this paper's experimental results, use the links above.

The [workflow instructions](../../plugins/pepflow-workflows/README.md) describe new discovery runs. Available source/environment records and execution limits are in [the provenance notes](supplementary/tools/PROVENANCE.md).
