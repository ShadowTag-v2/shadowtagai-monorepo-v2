# Testing an AI Scientist on Genomics: A Computational Biologist's Experience

**Dr. Kenji Tanaka** — Computational Genomics Researcher
**Date**: February 8, 2026
**System**: Kosmos AI Scientist (commit 6b309d3)
**Model**: DeepSeek Chat (via LiteLLM)

---

## Motivation and Setup

I study differential gene expression in cancer cell lines. My daily work involves RNA-seq pipelines, DESeq2 runs, and pathway enrichment analysis. When I heard about Kosmos — an "AI Scientist" system described in arXiv:2511.02824v2 that claims to autonomously run research cycles — I wanted to test it on a question I know well: *Which genes are differentially expressed between drug-treated and control cancer cell lines, and what biological pathways do they implicate?*

I prepared a 132-row dataset (`gene_expression_test.csv`) with seven columns: gene name, condition (treated vs. control), expression level, dose in micromolar, replicate number, log2 fold change, and adjusted p-value. This is the kind of table I'd generate from a real DESeq2 run. The genes include known cancer biology markers — CDKN1A, BAX, CASP3 on the apoptosis side; CCND1, MYC, CDK4 on the proliferation side — with realistic fold changes and p-values.

Setup was straightforward. Kosmos runs with a YAML persona file that specifies the research question, domain, dataset path, and model configuration. I pointed it at DeepSeek Chat through LiteLLM, gave it a $1 budget, and set it to 3 iterations.

## Getting It Running

The evaluation framework runs seven phases: pre-flight checks, a single-iteration smoke test, a 3-iteration full loop, a dataset test, quality scoring, a rigor scorecard, and a paper compliance gap analysis. All 37 checks passed in 538 seconds (about 9 minutes).

One important detail: this is v002. The first run (v001) also produced 37/37 passes, but a closer inspection revealed that every component artifact — hypotheses, literature results, experiment designs — contained enzyme kinetics content, not genomics. The evaluation framework had hardcoded biology defaults that weren't being overridden by my persona parameters. Those bugs have since been fixed (7 bugs across 3 files), and this v002 run is the first honest genomics evaluation.

## What It Produced

The system generated hypotheses that actually match my domain:

1. **p53 pathway activation**: "Treatment will significantly upregulate genes in the p53 signaling pathway (CDKN1A, BAX, PUMA) and downregulate cell cycle progression genes (CCNB1, CDC20)." This is a reasonable starting hypothesis — CDKN1A and BAX are exactly the kind of genes I'd expect to see upregulated by a cytotoxic drug.

2. **Inflammatory gene signature**: "Drug treatment will induce upregulation of interleukin and chemokine genes (IL6, IL8, CXCL1, CXCL2) associated with NF-kB signaling." This is more speculative but plausible — many cancer drugs trigger inflammatory responses.

3. **Metabolic reprogramming**: "The drug will cause downregulation of oxidative phosphorylation genes and upregulation of glycolysis genes, consistent with a Warburg-like metabolic shift." This is the kind of cross-domain hypothesis that shows the LLM has real biological knowledge.

The literature search found 49 papers from Semantic Scholar, including recent work on cancer biomarkers, immune signaling, and differentially expressed non-coding RNAs. The search query was derived from my research question (not hardcoded to "enzyme kinetics temperature" as it was in v001). ArXiv was rate-limited, so all papers came from one source.

Over 3 iterations, the system generated 9 hypotheses, completed 1 experiment, and reached all workflow phases: hypothesis generation, experiment design, execution, analysis, refinement, and convergence.

## What Worked

**Hypothesis quality is genuinely impressive.** The system cited specific gene names (CDKN1A, BAX, PUMA, IL6, CCNB1), specific pathways (p53, NF-kB, OXPHOS), and specific biological mechanisms (denaturation → apoptosis, metabolic reprogramming). These aren't vague hand-waves; they're testable claims that reference the right molecular biology.

**The pipeline architecture is sound.** The research cycle — hypothesize, design, execute, analyze, refine — mirrors how I actually work. The convergence detector prevents runaway loops. The workflow state machine tracks progress correctly. The data provider loaded my CSV without issues.

**Scientific rigor infrastructure is real.** The evaluation scored 7.88/10 on rigor features: novelty checking, power analysis, assumption testing (Shapiro-Wilk, Levene), effect size randomization, multi-format data loading, convergence criteria, reproducibility, and cost tracking. These aren't just checkboxes — the code is actually wired into the pipeline.

## What Didn't Work

**Experiment design falls back to raw LLM output.** The experiment designer has no template for "computational" experiment types in genomics. It fell back to an LLM-generated protocol that had 0 steps, no variables, no controls, and no statistical tests. This means the "experiment design" phase is essentially the LLM writing free-form text, not a structured scientific protocol. For my domain, I'd want it to produce something like: "Run DESeq2 with treated vs. control, filter by |log2FC| > 1 and padj < 0.05, then run GSEA on hallmark gene sets."

**Code execution failed.** The generated code expected a `df` variable in scope, but the executor didn't inject the data_path. The code itself looked reasonable — it imported pandas, scipy, and the Kosmos DataAnalyzer — but it couldn't actually run. This is a significant gap: the system generates code but can't execute it against my dataset.

**Only 1 experiment completed across 3 iterations.** Despite generating 9 hypotheses, only 1 was actually tested. The others were generated but never selected for experimentation. The system seems to converge too quickly rather than systematically testing each hypothesis.

**The quality scores are heuristic, not semantic.** Phase 5 scored hypothesis quality by keyword-matching ("specific", "mechanism", "testable") in the plan text, not by evaluating the actual hypotheses. This gives a Phase 3 score of 3/10 even though the hypotheses are domain-appropriate and scientifically reasonable.

## Model vs. Architecture

This is the key question: are the limitations I'm seeing due to the LLM (DeepSeek Chat) or the Kosmos architecture?

**Architecture problems** (would persist with a better model):
- No experiment design templates for genomics domain
- Code executor doesn't inject data_path into generated code scope
- Convergence is too aggressive (1 experiment across 3 iterations)
- Component tests were using hardcoded biology defaults (now fixed)
- NoveltyChecker can't access the database from subprocess context

**Model problems** (would likely improve with Claude or GPT-4):
- Experiment protocol structure (0 steps, no variables) suggests the LLM couldn't parse the expected output format
- Quality of generated analysis code might improve with a stronger code model
- Richer cross-hypothesis reasoning could lead to more experiments per iteration

My honest assessment: about 60% architecture, 40% model. DeepSeek Chat produced surprisingly good hypotheses with real gene names and pathways, which suggests the model is adequate for the science. But the architecture doesn't give the model enough structure to translate those hypotheses into executable experiments.

## Verdict

Kosmos is a real research pipeline with genuine scientific rigor features. The hypothesis generation is impressive — better than I expected from any LLM-based system. The literature integration works (when APIs cooperate). The convergence and workflow systems are well-engineered.

But it's not yet an autonomous scientist for genomics. The gap between "generates a good hypothesis" and "runs an experiment to test it" is where the system falls down. For my work, I'd need:

1. Domain-specific experiment templates (DESeq2 pipeline, pathway enrichment, volcano plots)
2. Working code execution with dataset injection
3. Less aggressive convergence — test more hypotheses before stopping
4. Results interpretation grounded in the actual data, not just statistical test outputs

The 37/37 evaluation score is mechanically correct — the pipeline runs, doesn't crash, and produces domain-appropriate output. But a passing score doesn't mean it replaced 4-6 months of my work. It replaced maybe an afternoon of literature review and hypothesis brainstorming. The hard part — designing rigorous experiments and interpreting results in biological context — still needs a human genomicist.

**Score: 5/10 for genomics research automation.** Promising foundation; not yet production-ready for my domain.
