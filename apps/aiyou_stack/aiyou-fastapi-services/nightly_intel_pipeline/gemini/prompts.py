"""
Gemini Extraction Prompts
=========================
Structured prompts for IntelEvent extraction.
"""

from .config import GEMINI_INGESTION_CONFIG

# Topic categories for classification
TOPIC_CATEGORIES = GEMINI_INGESTION_CONFIG["topic_categories"]
RISK_TAGS = GEMINI_INGESTION_CONFIG["risk_tags"]


INTEL_EVENT_EXTRACTION_PROMPT = """You are an intelligence analyst for a technology company focused on MLOps, AI infrastructure, and regulatory compliance.

Analyze the following document and extract structured intelligence data.

DOCUMENT:
{document_text}

---

EXTRACTION INSTRUCTIONS:

1. SOURCE TYPE: Classify as one of:
   - regulation: Laws, rules, CFR references
   - news: Press releases, news articles
   - rfp: Government/commercial procurement
   - competitor_doc: Competitor product/service info
   - blog: Technical blogs, tutorials
   - lawsuit: Legal filings, court cases
   - research: Academic papers
   - github: Code repositories
   - federal_register: Federal Register documents
   - industry: Industry reports

2. JURISDICTION: Geographic/legal scope:
   - US-FEDERAL, US-CA, US-NY, US-TX, US-FL, US-OTHER
   - EU, UK, GLOBAL, UNKNOWN

3. CHANGE TYPE: What kind of event:
   - new_law, amendment, guidance, announcement
   - proposed_rule, final_rule, enforcement
   - deadline, research_paper, code_release, update

4. TOPIC TAGS: Select from:
   {topic_categories}

5. RISK TAGS: Select applicable:
   {risk_tags}

6. IMPACTS: List specific business impacts (2-5 bullets)

7. JR ENGINE HINTS (for downstream scoring):
   - purpose_hint: How does this advance or threaten PNKLN revenue?
   - reasons_hint: What's the defensible business justification?
   - brakes_hint: What concerns/blockers should be considered?

OUTPUT FORMAT (JSON only, no markdown):
{{
  "source_type": "<type>",
  "jurisdiction": "<jurisdiction>",
  "effective_date": "<YYYY-MM-DD or null>",
  "topic_tags": ["<tag1>", "<tag2>"],
  "change_type": "<type>",
  "title": "<concise title>",
  "summary": "<2-3 sentence summary>",
  "impacts": ["<impact1>", "<impact2>"],
  "risk_tags": ["<tag1>"],
  "purpose_hint": "<1-2 sentences>",
  "reasons_hint": "<1-2 sentences>",
  "brakes_hint": ["<concern1>", "<concern2>"],
  "confidence": <0.0-1.0>
}}

Respond with ONLY the JSON object.""".format(
    topic_categories=", ".join(TOPIC_CATEGORIES),
    risk_tags=", ".join(RISK_TAGS),
)


DELTA_DETECTION_PROMPT = """You are analyzing changes between two versions of a document.

PREVIOUS VERSION:
{previous_text}

---

CURRENT VERSION:
{current_text}

---

ANALYSIS INSTRUCTIONS:

1. Identify what changed between versions
2. Classify the significance of changes
3. Highlight any deadline or compliance changes
4. Note removed content that may be important

OUTPUT FORMAT (JSON only):
{{
  "has_changes": <true/false>,
  "change_summary": "<1-2 sentence summary>",
  "changes": [
    {{
      "field": "<what changed>",
      "old_value": "<previous>",
      "new_value": "<current>",
      "significance": "<low/medium/high/critical>"
    }}
  ],
  "deadline_changes": [
    {{
      "type": "<new/modified/removed>",
      "date": "<YYYY-MM-DD>",
      "description": "<what the deadline is for>"
    }}
  ],
  "urgency": <1-5>,
  "action_required": "<none/review/immediate>"
}}

Respond with ONLY the JSON object."""


ARXIV_EXTRACTION_PROMPT = """You are analyzing an arXiv research paper for business intelligence.

PAPER METADATA:
{paper_metadata}

---

Focus on:
1. Novel techniques that could be productized
2. Benchmark improvements relevant to MLOps
3. Infrastructure implications
4. Competitive landscape insights

OUTPUT FORMAT (JSON only):
{{
  "source_type": "research",
  "jurisdiction": "GLOBAL",
  "effective_date": null,
  "topic_tags": ["<relevant topics>"],
  "change_type": "research_paper",
  "title": "<paper title>",
  "summary": "<key findings in 2-3 sentences>",
  "impacts": [
    "<productization opportunity>",
    "<competitive implication>",
    "<infrastructure consideration>"
  ],
  "risk_tags": [],
  "purpose_hint": "<how this advances AI/MLOps capabilities>",
  "reasons_hint": "<business justification for attention>",
  "brakes_hint": ["<implementation challenges>"],
  "confidence": <0.0-1.0>,
  "technical_details": {{
    "key_contribution": "<main innovation>",
    "benchmark_improvement": "<quantitative if available>",
    "applicable_domains": ["<domain1>", "<domain2>"]
  }}
}}

Respond with ONLY the JSON object."""


GITHUB_EXTRACTION_PROMPT = """You are analyzing a GitHub repository for strategic intelligence.

REPOSITORY CONTENT:
{repo_content}

---

Focus on:
1. Technology capabilities and architecture
2. Community health (stars, contributors, activity)
3. Integration potential with PNKLN stack
4. Competitive positioning

OUTPUT FORMAT (JSON only):
{{
  "source_type": "github",
  "jurisdiction": "GLOBAL",
  "effective_date": null,
  "topic_tags": ["<relevant topics>"],
  "change_type": "code_release",
  "title": "<repo name - brief description>",
  "summary": "<what it does, why it matters in 2-3 sentences>",
  "impacts": [
    "<integration opportunity>",
    "<competitive threat or advantage>",
    "<technical capability>"
  ],
  "risk_tags": [],
  "purpose_hint": "<how this could advance PNKLN capabilities>",
  "reasons_hint": "<why this deserves attention>",
  "brakes_hint": ["<adoption concerns>", "<maintenance concerns>"],
  "confidence": <0.0-1.0>,
  "repo_metrics": {{
    "stars": <number>,
    "language": "<primary language>",
    "maturity": "<early/growing/mature>",
    "activity": "<active/moderate/stale>"
  }}
}}

Respond with ONLY the JSON object."""


FEDERAL_REGISTER_EXTRACTION_PROMPT = """You are analyzing a Federal Register document for regulatory intelligence.

DOCUMENT:
{document_text}

---

CRITICAL: Pay attention to:
1. Effective dates and compliance deadlines
2. Comment periods and docket numbers
3. CFR references and affected regulations
4. Enforcement mechanisms and penalties
5. AI/technology-specific provisions

OUTPUT FORMAT (JSON only):
{{
  "source_type": "federal_register",
  "jurisdiction": "US-FEDERAL",
  "effective_date": "<YYYY-MM-DD or null>",
  "topic_tags": ["<relevant topics>"],
  "change_type": "<proposed_rule/final_rule/guidance/enforcement/announcement>",
  "title": "<document title>",
  "summary": "<key provisions in 2-3 sentences>",
  "impacts": [
    "<compliance requirement>",
    "<business process change>",
    "<cost/resource implication>"
  ],
  "risk_tags": ["<applicable risk tags>"],
  "purpose_hint": "<how this affects PNKLN operations/revenue>",
  "reasons_hint": "<why action may be needed>",
  "brakes_hint": ["<compliance risk>", "<deadline pressure>"],
  "confidence": <0.0-1.0>,
  "regulatory_details": {{
    "agency": "<issuing agency>",
    "document_type": "<RULE/PRORULE/NOTICE/PRESDOCU>",
    "docket_ids": ["<docket1>"],
    "cfr_references": ["<CFR ref1>"],
    "comment_deadline": "<YYYY-MM-DD or null>",
    "penalties": "<if mentioned>"
  }}
}}

Respond with ONLY the JSON object."""


def get_prompt_for_source_type(source_type: str) -> str:
    """
    Get the appropriate extraction prompt for a source type.

    Args:
        source_type: Type of source (arxiv, github, federal_register, etc.)

    Returns:
        Prompt template string
    """
    prompts = {
        "arxiv": ARXIV_EXTRACTION_PROMPT,
        "research": ARXIV_EXTRACTION_PROMPT,
        "github": GITHUB_EXTRACTION_PROMPT,
        "federal_register": FEDERAL_REGISTER_EXTRACTION_PROMPT,
    }

    return prompts.get(source_type, INTEL_EVENT_EXTRACTION_PROMPT)
