#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Gemini Ingestion Layer Analysis Runner

Orchestrates the full analysis workflow:
1. Generate input bundle
2. Submit to Gemini 2.0 Pro via Vertex AI
3. Parse and aggregate results
4. Generate summary report

Usage:
    python run_gemini_analysis.py [--output docs/analysis/report_YYYY-MM-DD.md]

Requirements:
    - Vertex AI API enabled
    - GOOGLE_APPLICATION_CREDENTIALS set
    - Gemini 2.0 Pro access
"""

import argparse
import asyncio
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path

# Try to import Vertex AI (graceful degradation if not available)
try:
  from google.cloud import aiplatform
  from vertexai.generative_models import GenerativeModel, Part

  VERTEX_AI_AVAILABLE = True
except ImportError:
  VERTEX_AI_AVAILABLE = False
  logging.warning(
    "Vertex AI SDK not available. Install with: pip install google-cloud-aiplatform"
  )

logging.basicConfig(
  level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GeminiAnalysisRunner:
  """Orchestrates Gemini Ingestion Layer analysis"""

  def __init__(
    self,
    project_id: str,
    location: str = "us-central1",
    model_name: str = "gemini-2.0-pro",
    output_path: Path | None = None,
  ):
    self.project_id = project_id
    self.location = location
    self.model_name = model_name
    self.output_path = output_path or self._default_output_path()

    if VERTEX_AI_AVAILABLE:
      aiplatform.init(project=project_id, location=location)
      self.model = GenerativeModel(model_name)
    else:
      self.model = None
      logger.warning("Vertex AI not initialized - using mock mode")

  def _default_output_path(self) -> Path:
    """Generate default output path with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d")
    return Path(f"docs/analysis/gemini_ingestion_analysis_{timestamp}.md")

  def generate_input_bundle(self) -> str:
    """Run prepare_analysis_input.sh to generate input"""
    logger.info("Generating analysis input bundle...")

    script_path = Path(__file__).parent / "prepare_analysis_input.sh"

    if not script_path.exists():
      raise FileNotFoundError(f"Input script not found: {script_path}")

    try:
      result = subprocess.run(
        ["bash", str(script_path)],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
      )

      input_bundle = result.stdout
      logger.info(f"Generated input bundle: {len(input_bundle)} characters")

      # Save to temp file
      temp_input = self.output_path.parent / "analysis_input_bundle.txt"
      temp_input.parent.mkdir(parents=True, exist_ok=True)
      temp_input.write_text(input_bundle, encoding="utf-8")

      logger.info(f"Input bundle saved to: {temp_input}")
      return input_bundle

    except subprocess.CalledProcessError as e:
      logger.error(f"Failed to generate input bundle: {e.stderr}")
      raise
    except subprocess.TimeoutExpired:
      logger.error("Input generation timed out after 60 seconds")
      raise

  def load_analysis_prompt(self) -> str:
    """Load Gemini Ingestion Analysis prompt template"""
    prompt_path = Path(__file__).parent.parent.parent / "GEMINI_INGESTION_ANALYSIS.md"

    if not prompt_path.exists():
      raise FileNotFoundError(f"Analysis prompt not found: {prompt_path}")

    with open(prompt_path, encoding="utf-8") as f:
      return f.read()

  async def run_gemini_analysis(self, input_bundle: str, prompt_template: str) -> str:
    """Submit to Gemini 2.0 Pro and get analysis"""
    logger.info("Submitting to Gemini 2.0 Pro...")

    if not VERTEX_AI_AVAILABLE or self.model is None:
      logger.warning("Vertex AI not available - returning mock analysis")
      return self._generate_mock_analysis()

    try:
      # Construct full prompt
      full_prompt = f"""{prompt_template}

---

## INPUT BUNDLE

{input_bundle}

---

Please analyze the PNKLN Intelligence Ingestion Layer based on the provided documentation
and generate a comprehensive analysis report following the structure defined above.

Focus on:
1. Architecture assessment with confidence scoring
2. Cost efficiency analysis
3. Ethical compliance review
4. Data quality evaluation
5. Operational reliability check
6. Integration health status
7. Top 5 risks (prioritized)
8. Top 5 optimization opportunities (with ROI)
9. Deployment recommendation
10. Actionable next steps

Ensure overall confidence score is calculated and displayed prominently.
"""

      # Generate content
      response = self.model.generate_content(
        full_prompt,
        generation_config={
          "temperature": 0.2,  # Lower temperature for analytical tasks
          "max_output_tokens": 8192,
        },
      )

      analysis_text = response.text
      logger.info(f"Received analysis: {len(analysis_text)} characters")

      return analysis_text

    except Exception as e:
      logger.error(f"Gemini API error: {e}", exc_info=True)
      raise

  def _generate_mock_analysis(self) -> str:
    """Generate mock analysis for testing without Vertex AI"""
    return f"""# Gemini Ingestion Layer Analysis Report (MOCK)
**Date**: {datetime.now().strftime("%Y-%m-%d")}
**Analyst**: Mock Mode (Vertex AI not available)
**Overall Confidence**: 65%

## Executive Summary
This is a mock analysis generated without actual Gemini processing.
Install google-cloud-aiplatform to run real analysis.

## 1. Architecture Assessment (Confidence: 70%)
### Strengths
- ✅ Well-structured modular design
- ✅ Clear separation of concerns

### Concerns
- ⚠️ Missing circuit breaker patterns
- ⚠️ Error recovery needs enhancement

## 2. Cost Efficiency Analysis (Confidence: 60%)
Estimated monthly cost of ~$1,280 is reasonable for 50-100 repositories.

## 3. Ethical Compliance Review (Confidence: 75%)
Rate limiting and robots.txt compliance well-designed.

## 4. Data Quality Evaluation (Confidence: 62%)
Tier classification system is sound but needs validation.

## 5. Operational Reliability Check (Confidence: 58%)
Monitoring and error handling could be improved.

## 6. Integration Health Status (Confidence: 68%)
Clean integration points with clear boundaries.

## Top 5 Risks
1. **[HIGH]** Single point of failure in embedding generation
2. **[MEDIUM]** API quota exhaustion not handled
3. **[MEDIUM]** Missing idempotency in BigQuery writes
4. **[LOW]** Cost overruns if volume spikes
5. **[LOW]** Source dependency on external APIs

## Top 5 Optimization Opportunities
1. **[HIGH ROI]** Add circuit breaker - prevents cascading failures
2. **[MEDIUM ROI]** Implement batch retries - reduces API costs
3. **[MEDIUM ROI]** Add deduplication layer - improves data quality
4. **[LOW ROI]** Optimize embedding batching - 10% cost reduction
5. **[LOW ROI]** Cache frequent queries - minor performance gain

## Deployment Recommendation
**APPROVED** with prerequisites:
1. Implement circuit breaker for collectors
2. Add idempotency keys to BigQuery writes
3. Set up monitoring dashboards

## Recommended Actions
**Short-term (0-3 months)**:
- Add error recovery mechanisms
- Implement basic monitoring
- Validate tier classification accuracy

**Long-term (3-12 months)**:
- Build historical trend analysis
- Optimize cost per item
- Expand source coverage
"""

  def save_analysis_report(self, analysis_text: str) -> Path:
    """Save analysis to markdown file"""
    self.output_path.parent.mkdir(parents=True, exist_ok=True)
    self.output_path.write_text(analysis_text, encoding="utf-8")

    logger.info(f"Analysis report saved to: {self.output_path}")
    return self.output_path

  def run_confidence_aggregation(self) -> dict:
    """Run aggregate_confidence.py on the generated report"""
    logger.info("Computing confidence scores...")

    script_path = Path(__file__).parent / "aggregate_confidence.py"

    try:
      result = subprocess.run(
        ["python3", str(script_path), str(self.output_path)],
        capture_output=True,
        text=True,
        timeout=30,
      )

      # Print output (includes summary)
      print(result.stdout)

      if result.returncode != 0:
        logger.warning(f"Confidence aggregation returned non-zero: {result.returncode}")
        logger.warning(result.stderr)

      # Load JSON metrics
      json_path = self.output_path.with_suffix(".confidence.json")
      if json_path.exists():
        with open(json_path) as f:
          return json.load(f)

      return {}

    except subprocess.TimeoutExpired:
      logger.error("Confidence aggregation timed out")
      raise
    except Exception as e:
      logger.error(f"Error running confidence aggregation: {e}")
      raise

  async def run_full_analysis(self) -> dict:
    """Execute complete analysis workflow"""
    logger.info("=" * 70)
    logger.info("GEMINI INGESTION LAYER ANALYSIS - FULL WORKFLOW")
    logger.info("=" * 70)

    # Step 1: Generate input
    input_bundle = self.generate_input_bundle()

    # Step 2: Load prompt template
    prompt_template = self.load_analysis_prompt()

    # Step 3: Run Gemini analysis
    analysis_text = await self.run_gemini_analysis(input_bundle, prompt_template)

    # Step 4: Save report
    report_path = self.save_analysis_report(analysis_text)

    # Step 5: Aggregate confidence scores
    metrics = self.run_confidence_aggregation()

    logger.info("=" * 70)
    logger.info("ANALYSIS COMPLETE")
    logger.info(f"Report: {report_path}")
    logger.info(f"Overall Confidence: {metrics.get('overall_confidence', 'N/A')}%")
    logger.info(
      f"Status: {'✅ APPROVED' if metrics.get('approved') else '❌ NEEDS WORK'}"
    )
    logger.info("=" * 70)

    return metrics


async def main():
  """CLI entry point"""
  parser = argparse.ArgumentParser(description="Run Gemini Ingestion Layer Analysis")
  parser.add_argument(
    "--project-id", default="your-gcp-project-id", help="GCP project ID for Vertex AI"
  )
  parser.add_argument(
    "--location", default="us-central1", help="GCP location for Vertex AI"
  )
  parser.add_argument("--output", type=Path, help="Output path for analysis report")
  parser.add_argument("--model", default="gemini-2.0-pro", help="Gemini model name")

  args = parser.parse_args()

  try:
    runner = GeminiAnalysisRunner(
      project_id=args.project_id,
      location=args.location,
      model_name=args.model,
      output_path=args.output,
    )

    metrics = await runner.run_full_analysis()

    # Exit with appropriate code
    sys.exit(0 if metrics.get("approved") else 1)

  except Exception as e:
    logger.error(f"Analysis failed: {e}", exc_info=True)
    sys.exit(2)


if __name__ == "__main__":
  import sys

  asyncio.run(main())
