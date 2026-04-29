# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AiURCM Document AI Integration
Processes compliance documents using Google Document AI and triggers Judge 6 analysis
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from google.api_core.client_options import ClientOptions
from google.cloud import documentai_v1 as documentai
from google.cloud import pubsub_v1, storage

logger = logging.getLogger(__name__)


@dataclass
class DocumentProcessingResult:
    """Result of Document AI processing"""

    document_id: str
    text_content: str
    entities: list[dict[str, Any]]
    confidence: float
    pages: int
    processing_time_ms: int


class DocumentAIProcessor:
    """Google Document AI integration for AiURCM compliance pipeline.

    Handles:
    - Document upload and processing
    - OCR and form parsing
    - Entity extraction
    - Integration with LangGraph via Pub/Sub
    """

    def __init__(
        self,
        project_id: str,
        location: str = "us",
        ocr_processor_id: str = None,
        form_parser_processor_id: str = None,
        pubsub_topic: str = "judge-6-document-processing",
    ):
        self.project_id = project_id
        self.location = location
        self.ocr_processor_id = ocr_processor_id
        self.form_parser_processor_id = form_parser_processor_id
        self.pubsub_topic = pubsub_topic

        # Initialize clients
        opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
        self.documentai_client = documentai.DocumentProcessorServiceClient(client_options=opts)
        self.storage_client = storage.Client(project=project_id)
        self.pubsub_publisher = pubsub_v1.PublisherClient()

        # Topic path for Pub/Sub
        self.topic_path = self.pubsub_publisher.topic_path(project_id, pubsub_topic)

    def process_document_from_gcs(
        self,
        bucket_name: str,
        file_path: str,
        mime_type: str = "application/pdf",
        use_form_parser: bool = False,
    ) -> DocumentProcessingResult:
        """Process a document from Cloud Storage using Document AI.

        Args:
            bucket_name: GCS bucket name
            file_path: Path to file in bucket
            mime_type: MIME type of document
            use_form_parser: Use form parser instead of OCR

        Returns:
            DocumentProcessingResult with extracted content

        """
        start_time = datetime.utcnow()

        # Download document from GCS
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(file_path)
        document_content = blob.download_as_bytes()

        # Select processor
        processor_id = self.form_parser_processor_id if use_form_parser else self.ocr_processor_id
        processor_name = self.documentai_client.processor_path(
            self.project_id,
            self.location,
            processor_id,
        )

        # Create request
        raw_document = documentai.RawDocument(content=document_content, mime_type=mime_type)

        request = documentai.ProcessRequest(name=processor_name, raw_document=raw_document)

        # Process document
        logger.info(f"Processing document: gs://{bucket_name}/{file_path}")
        result = self.documentai_client.process_document(request=request)
        document = result.document

        # Extract text and entities
        text_content = document.text
        entities = self._extract_entities(document)

        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        result = DocumentProcessingResult(
            document_id=f"{bucket_name}/{file_path}",
            text_content=text_content,
            entities=entities,
            confidence=self._calculate_average_confidence(document),
            pages=len(document.pages),
            processing_time_ms=int(processing_time),
        )

        logger.info(
            f"Processed {result.pages} pages, "
            f"extracted {len(entities)} entities, "
            f"confidence: {result.confidence:.2f}, "
            f"time: {result.processing_time_ms}ms",
        )

        return result

    def process_document_sync(
        self,
        document_content: bytes,
        mime_type: str = "application/pdf",
        use_form_parser: bool = False,
    ) -> DocumentProcessingResult:
        """Process a document synchronously (for small documents < 20MB).

        Args:
            document_content: Raw document bytes
            mime_type: MIME type
            use_form_parser: Use form parser instead of OCR

        Returns:
            DocumentProcessingResult

        """
        start_time = datetime.utcnow()

        processor_id = self.form_parser_processor_id if use_form_parser else self.ocr_processor_id
        processor_name = self.documentai_client.processor_path(
            self.project_id,
            self.location,
            processor_id,
        )

        raw_document = documentai.RawDocument(content=document_content, mime_type=mime_type)
        request = documentai.ProcessRequest(name=processor_name, raw_document=raw_document)

        result = self.documentai_client.process_document(request=request)
        document = result.document

        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        return DocumentProcessingResult(
            document_id=f"inline-{datetime.utcnow().isoformat()}",
            text_content=document.text,
            entities=self._extract_entities(document),
            confidence=self._calculate_average_confidence(document),
            pages=len(document.pages),
            processing_time_ms=int(processing_time),
        )

    def process_and_trigger_Cor.Claude_Code_6(
        self,
        bucket_name: str,
        file_path: str,
        mime_type: str = "application/pdf",
        use_form_parser: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Process document and publish to Pub/Sub for Judge 6 analysis.

        Args:
            bucket_name: GCS bucket
            file_path: File path in bucket
            mime_type: MIME type
            use_form_parser: Use form parser
            metadata: Additional metadata to pass to Judge 6

        Returns:
            Pub/Sub message ID

        """
        # Process document
        result = self.process_document_from_gcs(
            bucket_name=bucket_name,
            file_path=file_path,
            mime_type=mime_type,
            use_form_parser=use_form_parser,
        )

        # Prepare message for Judge 6
        message_data = {
            "document_id": result.document_id,
            "document_content": result.text_content,
            "entities": result.entities,
            "confidence": result.confidence,
            "pages": result.pages,
            "processing_time_ms": result.processing_time_ms,
            "source": {"bucket": bucket_name, "path": file_path, "mime_type": mime_type},
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }

        # Publish to Pub/Sub
        message_json = json.dumps(message_data).encode("utf-8")
        future = self.pubsub_publisher.publish(self.topic_path, message_json)
        message_id = future.result()

        logger.info(f"Published to Pub/Sub: message_id={message_id}, doc={result.document_id}")

        return message_id

    def _extract_entities(self, document: documentai.Document) -> list[dict[str, Any]]:
        """Extract entities from Document AI result.

        Args:
            document: Document AI document

        Returns:
            List of entities with type, text, confidence

        """
        entities = []

        for entity in document.entities:
            entities.append(
                {
                    "type": entity.type_,
                    "text": entity.mention_text,
                    "confidence": entity.confidence,
                    "page_refs": [
                        {
                            "page": ref.page,
                            "bounding_box": self._extract_bounding_box(ref.bounding_poly),
                        }
                        for ref in entity.page_anchor.page_refs
                    ]
                    if entity.page_anchor
                    else [],
                },
            )

        return entities

    def _extract_bounding_box(self, bounding_poly) -> dict[str, float]:
        """Extract bounding box coordinates"""
        if not bounding_poly or not bounding_poly.vertices:
            return {}

        vertices = bounding_poly.vertices
        return {
            "x_min": min(v.x for v in vertices),
            "y_min": min(v.y for v in vertices),
            "x_max": max(v.x for v in vertices),
            "y_max": max(v.y for v in vertices),
        }

    def _calculate_average_confidence(self, document: documentai.Document) -> float:
        """Calculate average confidence score"""
        if not document.entities:
            return 1.0  # OCR without entities

        confidences = [e.confidence for e in document.entities if e.confidence > 0]
        return sum(confidences) / len(confidences) if confidences else 0.0


class CloudFunctionHandler:
    """Cloud Function handler for processing documents uploaded to GCS.

    Triggered by Cloud Storage object finalization events.
    """

    def __init__(self, project_id: str):
        self.processor = DocumentAIProcessor(project_id=project_id)

    def handle_gcs_event(self, event: dict[str, Any], context: Any):
        """Handle Cloud Storage trigger event.

        Event structure:
        {
            'bucket': 'bucket-name',
            'name': 'path/to/file.pdf',
            'contentType': 'application/pdf',
            ...
        }
        """
        bucket_name = event["bucket"]
        file_path = event["name"]
        mime_type = event.get("contentType", "application/pdf")

        logger.info(f"Processing GCS event: gs://{bucket_name}/{file_path}")

        try:
            # Determine processor type based on file path or content type
            use_form_parser = "forms" in file_path.lower()

            # Process and trigger Judge 6
            message_id = self.processor.process_and_trigger_Cor.Claude_Code_6(
                bucket_name=bucket_name,
                file_path=file_path,
                mime_type=mime_type,
                use_form_parser=use_form_parser,
                metadata={
                    "event_id": context.event_id if hasattr(context, "event_id") else None,
                    "event_type": context.event_type if hasattr(context, "event_type") else None,
                },
            )

            logger.info(f"Successfully triggered Judge 6: message_id={message_id}")

        except Exception as e:
            logger.error(f"Failed to process document: {e}", exc_info=True)
            raise


# Cloud Function entry point
def process_compliance_document(event, context):
    """Cloud Function entry point for Document AI processing.

    Triggered by: Cloud Storage object finalization
    Triggers: Pub/Sub message to Judge 6 orchestrator
    """
    import os

    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        raise ValueError("GCP_PROJECT_ID environment variable not set")

    handler = CloudFunctionHandler(project_id=project_id)
    handler.handle_gcs_event(event, context)


# Example usage
if __name__ == "__main__":
    import os

    project_id = os.getenv("GCP_PROJECT_ID", "pnkln-prod")
    processor = DocumentAIProcessor(project_id=project_id)

    # Example: Process a document from GCS
    message_id = processor.process_and_trigger_Cor.Claude_Code_6(
        bucket_name="pnkln-compliance-docs",
        file_path="intake/sample-fda-policy.pdf",
        mime_type="application/pdf",
    )

    print(f"Document processing triggered: message_id={message_id}")
