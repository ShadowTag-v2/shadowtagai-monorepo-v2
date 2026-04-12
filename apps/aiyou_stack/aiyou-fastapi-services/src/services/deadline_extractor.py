"""
Deadline Extraction Service
AI/ML-powered extraction of deadlines from legal documents
"""

import re
from datetime import date, datetime, timedelta
from enum import StrEnum
from typing import Any

# NLP imports
import spacy
import torch
from transformers import pipeline


class ExtractionMethod(StrEnum):
    """Methods used for deadline extraction"""

    RULE_BASED = "rule_based"
    NER_MODEL = "ner_model"
    LLM_EXTRACTION = "llm_extraction"
    HYBRID = "hybrid"


class DeadlineExtractor:
    """
    Extracts deadlines from legal documents using multiple approaches:
    1. Rule-based pattern matching
    2. Named Entity Recognition (NER)
    3. LLM-based extraction
    4. Hybrid ensemble approach
    """

    def __init__(self, model_path: str | None = None):
        """
        Initialize the deadline extractor

        Args:
            model_path: Path to custom trained model (optional)
        """
        # Load SpaCy model for NLP
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except OSError:
            print("Downloading SpaCy model...")
            import subprocess

            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_lg"])
            self.nlp = spacy.load("en_core_web_lg")

        # Initialize transformers pipeline for named entity recognition
        self.ner_pipeline = None
        if torch.cuda.is_available():
            self.ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", device=0)
        else:
            self.ner_pipeline = pipeline("ner", model="dslim/bert-base-NER")

        # Deadline patterns (rule-based)
        self.deadline_patterns = [
            # "within X days"
            r"within\s+(\d+)\s+days?",
            # "X days after/from"
            r"(\d+)\s+days?\s+(?:after|from|following)",
            # "no later than"
            r"no\s+later\s+than\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
            # "on or before"
            r"on\s+or\s+before\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
            # "due by/on"
            r"due\s+(?:by|on)\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
            # "shall file/respond/answer within"
            r"shall\s+(?:file|respond|answer|submit)\s+.*?within\s+(\d+)\s+days?",
            # Federal Rules citation patterns
            r"(?:FRCP|Fed\.\s*R\.\s*Civ\.\s*P\.)\s*(\d+)\([a-z]\)(?:\((\d+)\))?",
            # Specific date mentions
            r"deadline\s+(?:is|of)\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
            # Calendar date patterns
            r"(\d{1,2}/\d{1,2}/\d{2,4})",
            r"(\d{4}-\d{2}-\d{2})",
        ]

        # Trigger event patterns
        self.trigger_patterns = [
            r"service\s+of\s+(?:the\s+)?(?:summons|complaint|process)",
            r"receipt\s+of\s+(?:the\s+)?(?:notice|order|motion)",
            r"filing\s+of\s+(?:the\s+)?(?:complaint|motion|petition)",
            r"entry\s+of\s+(?:the\s+)?(?:judgment|order)",
        ]

        # Legal deadline keywords
        self.deadline_keywords = [
            "deadline",
            "due date",
            "time limit",
            "shall file",
            "must respond",
            "answer",
            "reply",
            "motion",
            "within",
            "no later than",
            "on or before",
            "statute of limitations",
            "time period",
        ]

    def extract_from_text(
        self,
        text: str,
        jurisdiction: str,
        document_type: str,
        service_date: date | None = None,
        filing_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """
        Extract all deadlines from document text

        Args:
            text: Document text
            jurisdiction: Legal jurisdiction
            document_type: Type of document
            service_date: Date of service (if applicable)
            filing_date: Filing date (if applicable)

        Returns:
            List of extracted deadlines with metadata
        """
        deadlines = []

        # Run all extraction methods
        rule_based = self._extract_rule_based(text, service_date, filing_date)
        ner_based = self._extract_ner_based(text, service_date, filing_date)

        # Combine and deduplicate
        all_extractions = rule_based + ner_based
        deadlines = self._deduplicate_deadlines(all_extractions)

        # Calculate confidence scores
        for deadline in deadlines:
            deadline["confidence"] = self._calculate_confidence(deadline, text)
            deadline["requires_review"] = deadline["confidence"] < 0.7

        return deadlines

    def _extract_rule_based(
        self, text: str, service_date: date | None, filing_date: date | None
    ) -> list[dict[str, Any]]:
        """Extract deadlines using rule-based pattern matching"""
        deadlines = []

        # Process text with SpaCy
        self.nlp(text)

        # Search for deadline patterns
        for pattern in self.deadline_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                # Extract context around the match
                start_pos = max(0, match.start() - 200)
                end_pos = min(len(text), match.end() + 200)
                context = text[start_pos:end_pos]

                # Identify deadline type from context
                deadline_type = self._identify_deadline_type(context)

                # Identify trigger event
                trigger_event = self._identify_trigger_event(context)

                # Calculate deadline date
                deadline_date = self._calculate_deadline_date(
                    match.group(0), service_date, filing_date, trigger_event
                )

                if deadline_date:
                    deadlines.append(
                        {
                            "deadline_date": deadline_date,
                            "deadline_type": deadline_type,
                            "trigger_event": trigger_event,
                            "description": context.strip(),
                            "extraction_method": ExtractionMethod.RULE_BASED,
                            "raw_match": match.group(0),
                            "confidence_factors": {
                                "pattern_match": True,
                                "context_clarity": self._assess_context_clarity(context),
                            },
                        }
                    )

        return deadlines

    def _extract_ner_based(
        self, text: str, service_date: date | None, filing_date: date | None
    ) -> list[dict[str, Any]]:
        """Extract deadlines using Named Entity Recognition"""
        deadlines = []

        # Split text into chunks (NER models have token limits)
        chunks = self._chunk_text(text, max_length=512)

        for chunk in chunks:
            # Run NER
            entities = self.ner_pipeline(chunk)

            # Look for date entities near deadline keywords
            for _i, entity in enumerate(entities):
                if entity["entity"].endswith("DATE"):
                    # Check surrounding context for deadline keywords
                    context_start = max(0, entity["start"] - 100)
                    context_end = min(len(chunk), entity["end"] + 100)
                    context = chunk[context_start:context_end]

                    # Check if this is a deadline mention
                    if any(keyword in context.lower() for keyword in self.deadline_keywords):
                        deadline_type = self._identify_deadline_type(context)
                        trigger_event = self._identify_trigger_event(context)

                        # Try to parse the date
                        deadline_date = self._parse_date_entity(entity["word"])

                        if deadline_date:
                            deadlines.append(
                                {
                                    "deadline_date": deadline_date,
                                    "deadline_type": deadline_type,
                                    "trigger_event": trigger_event,
                                    "description": context.strip(),
                                    "extraction_method": ExtractionMethod.NER_MODEL,
                                    "raw_match": entity["word"],
                                    "confidence_factors": {
                                        "ner_score": entity.get("score", 0.0),
                                        "keyword_match": True,
                                    },
                                }
                            )

        return deadlines

    def _chunk_text(self, text: str, max_length: int = 512) -> list[str]:
        """Split text into chunks for NER processing"""
        # Split by sentences using SpaCy
        doc = self.nlp(text)
        sentences = [sent.text for sent in doc.sents]

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_length:
                current_chunk += " " + sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _identify_deadline_type(self, context: str) -> str:
        """Identify the type of deadline from context"""
        context_lower = context.lower()

        type_keywords = {
            "response": ["answer", "respond", "response", "reply"],
            "filing": ["file", "filing", "submit"],
            "motion": ["motion", "move"],
            "discovery": ["discovery", "interrogatories", "requests for production"],
            "appeal": ["appeal", "appellate"],
            "payment": ["payment", "pay", "fee"],
            "hearing": ["hearing", "appear", "appearance"],
            "notice": ["notice", "notify"],
        }

        for deadline_type, keywords in type_keywords.items():
            if any(keyword in context_lower for keyword in keywords):
                return deadline_type

        return "other"

    def _identify_trigger_event(self, context: str) -> str:
        """Identify the event that triggers the deadline"""
        for pattern in self.trigger_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(0)

        return "Unknown trigger event"

    def _calculate_deadline_date(
        self,
        match_text: str,
        service_date: date | None,
        filing_date: date | None,
        trigger_event: str,
    ) -> date | None:
        """Calculate the actual deadline date from extracted information"""

        # Try to extract number of days
        days_match = re.search(r"(\d+)\s+days?", match_text, re.IGNORECASE)
        if days_match:
            num_days = int(days_match.group(1))

            # Determine base date
            base_date = None
            if "service" in trigger_event.lower() and service_date:
                base_date = service_date
            elif "filing" in trigger_event.lower() and filing_date:
                base_date = filing_date
            elif service_date:
                base_date = service_date
            elif filing_date:
                base_date = filing_date
            else:
                base_date = date.today()

            # Calculate deadline (simple version - will be enhanced by rule engine)
            return base_date + timedelta(days=num_days)

        # Try to extract specific date
        date_match = re.search(r"([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})", match_text)
        if date_match:
            try:
                date_str = f"{date_match.group(1)} {date_match.group(2)} {date_match.group(3)}"
                return datetime.strptime(date_str, "%B %d %Y").date()
            except ValueError:
                try:
                    return datetime.strptime(date_str, "%b %d %Y").date()
                except ValueError:
                    pass

        # Try slash or dash format
        slash_match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", match_text)
        if slash_match:
            try:
                month, day, year = slash_match.groups()
                if len(year) == 2:
                    year = f"20{year}"
                return date(int(year), int(month), int(day))
            except ValueError:
                pass

        dash_match = re.search(r"(\d{4})-(\d{2})-(\d{2})", match_text)
        if dash_match:
            try:
                year, month, day = dash_match.groups()
                return date(int(year), int(month), int(day))
            except ValueError:
                pass

        return None

    def _parse_date_entity(self, date_text: str) -> date | None:
        """Parse a date entity recognized by NER"""
        # Try common date formats
        formats = [
            "%B %d, %Y",
            "%b %d, %Y",
            "%m/%d/%Y",
            "%Y-%m-%d",
            "%d-%m-%Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_text.strip(), fmt).date()
            except ValueError:
                continue

        return None

    def _deduplicate_deadlines(self, deadlines: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Remove duplicate deadline extractions"""
        unique_deadlines = []
        seen_dates = set()

        # Sort by confidence factors if available
        deadlines.sort(
            key=lambda x: (
                x.get("confidence_factors", {}).get("pattern_match", False),
                x.get("confidence_factors", {}).get("ner_score", 0.0),
            ),
            reverse=True,
        )

        for deadline in deadlines:
            deadline_date = deadline["deadline_date"]
            deadline_type = deadline["deadline_type"]

            # Create a unique key
            key = (deadline_date, deadline_type)

            if key not in seen_dates:
                seen_dates.add(key)
                unique_deadlines.append(deadline)

        return unique_deadlines

    def _calculate_confidence(self, deadline: dict[str, Any], full_text: str) -> float:
        """
        Calculate confidence score for extracted deadline

        Factors:
        - Extraction method used
        - Pattern match quality
        - NER score
        - Context clarity
        - Presence of multiple confirming indicators
        """
        confidence = 0.5  # Base confidence

        factors = deadline.get("confidence_factors", {})

        # Method-based confidence
        if deadline["extraction_method"] == ExtractionMethod.RULE_BASED:
            if factors.get("pattern_match"):
                confidence += 0.2

        elif deadline["extraction_method"] == ExtractionMethod.NER_MODEL:
            ner_score = factors.get("ner_score", 0.0)
            confidence += ner_score * 0.3

        # Context clarity
        context_clarity = factors.get("context_clarity", 0.5)
        confidence += context_clarity * 0.2

        # Check for confirming indicators
        description = deadline.get("description", "").lower()
        confirming_keywords = ["must", "shall", "required", "ordered", "deadline"]
        keyword_count = sum(1 for keyword in confirming_keywords if keyword in description)
        confidence += min(keyword_count * 0.05, 0.2)

        # Cap confidence
        return min(confidence, 1.0)

    def _assess_context_clarity(self, context: str) -> float:
        """Assess how clear and unambiguous the context is"""
        clarity_score = 0.5

        # Check for clear deadline language
        strong_indicators = ["must file", "shall respond", "ordered to", "deadline is"]
        if any(indicator in context.lower() for indicator in strong_indicators):
            clarity_score += 0.3

        # Check for ambiguous language
        weak_indicators = ["may", "could", "might", "suggested"]
        if any(indicator in context.lower() for indicator in weak_indicators):
            clarity_score -= 0.2

        # Check for specific dates vs relative dates
        if re.search(r"[A-Za-z]+\s+\d{1,2},?\s+\d{4}", context):
            clarity_score += 0.2

        return max(0.0, min(clarity_score, 1.0))


class DocumentProcessor:
    """Process legal documents and extract text"""

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF using OCR if needed"""
        # TODO: Implement PDF text extraction
        # Use PyPDF2 for text PDFs
        # Use Tesseract OCR for scanned PDFs
        # Use Google Cloud Vision API for complex documents
        return ""

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX"""
        # TODO: Implement DOCX text extraction
        # Use python-docx library
        return ""

    @staticmethod
    def extract_text_from_image(file_path: str) -> str:
        """Extract text from image using OCR"""
        # TODO: Implement OCR
        # Use Google Cloud Vision API or Tesseract
        return ""
