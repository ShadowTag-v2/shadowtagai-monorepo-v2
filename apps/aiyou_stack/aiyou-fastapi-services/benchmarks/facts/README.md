# FACTS Benchmark Suite Implementation

This directory contains the implementation of the Google DeepMind FACTS Benchmark Suite for `shadowtag_v4-fastapi-services`.

## Overview

The FACTS Benchmark Suite evaluates LLM factuality across four dimensions:

1. **Parametric Knowledge**: Recall of internal knowledge.

2. **Grounding**: Ability to use provided context.

3. **Search**: Ability to use search tools for real-time info.

4. **Multimodal**: Factual accuracy with image inputs.

## Setup Instructions

### 1. Download Data

The actual datasets are hosted on Kaggle and must be downloaded manually (due to Kaggle's auth requirements).

1. Go to [FACTS Benchmark Suite on Kaggle](https://www.kaggle.com/benchmarks/google/facts).

2. Download the datasets for each benchmark (Parametric, Grounding, Search, Multimodal).

3. Extract them into the `data/` directory.

Expected structure:

```

benchmarks/facts/data/
  ├── grounding/
  │   └── ... (jsonl files)
  ├── parametric/
  │   └── ...
  ├── search/
  │   └── ...
  └── multimodal/
      └── ...

```

### 2. Run Evaluation

Use the `runner.py` script to run evaluations.

```bash
python benchmarks/facts/runner.py --benchmark all --model gemini-pro

```

## Implementation Details

The harness uses the `shadowtag_v4` agent framework to drive the models.

- **Parametric**: Direct question-answering.

- **Grounding**: Context + Question -> Answer.

- **Search**: Agent with search tool enabled.

- **Multimodal**: Agent with vision capabilities.
