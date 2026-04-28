#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import logging
import unittest
from collections.abc import Iterable
from typing import Any

try:
    import apache_beam as beam
    from apache_beam.pvalue import TaggedOutput
except ImportError:
    # Fallback mock for pure Python testing outside the Beam SDK environment
    class TaggedOutput:
        def __init__(self, tag, value):
            self.tag = tag
            self.value = value

    class beam:
        DoFn = object

        def Map(f):
            return f

        @staticmethod
        def Create(l):  # noqa: E741
            return l


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FAILURE_TAG = "failure"


class ValidateTransactionFn(beam.DoFn):
    """Validates the structure and type integrity of an incoming transaction log.
    Routes invalid records to a Dead Letter Queue via TaggedOutput.
    """

    def process(self, element: dict[str, Any]) -> Iterable[Any]:
        try:
            # Type and schema validation
            if not isinstance(element, dict):
                raise ValueError(f"Expected dict, got {type(element)}")

            tx_id = element.get("tx_id")
            amount = element.get("amount")

            if not tx_id:
                raise ValueError("Missing 'tx_id'")
            if amount is None or not isinstance(amount, (int, float)):
                raise ValueError(f"Invalid 'amount': {amount}")

            # Enhance element
            element["status"] = "validated"
            yield element

        except Exception as e:
            logger.warning(f"Validation failed for element {element}: {e}")
            yield TaggedOutput(FAILURE_TAG, {"error": str(e), "raw_payload": element})


# ==============================================================================
# Unit Tests
# ==============================================================================


class GenericTest(unittest.TestCase):
    def setUp(self):
        self.fn = ValidateTransactionFn()

    def test_successful_validation(self):
        valid_payload = {"tx_id": "req_123", "amount": 250.50}
        results = list(self.fn.process(valid_payload))
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], dict)
        self.assertEqual(results[0]["status"], "validated")

    def test_failure_routing_dlq_missing_tx(self):
        invalid_payload = {"amount": 100.0}
        results = list(self.fn.process(invalid_payload))
        self.assertEqual(len(results), 1)
        # Should be a TaggedOutput wrapped for DLQ
        self.assertIsInstance(results[0], TaggedOutput)
        self.assertEqual(results[0].tag, FAILURE_TAG)
        self.assertIn("Missing 'tx_id'", results[0].value["error"])

    def test_failure_routing_dlq_invalid_type(self):
        invalid_payload = ["not", "a", "dict"]
        results = list(self.fn.process(invalid_payload))  # type: ignore
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], TaggedOutput)
        self.assertEqual(results[0].tag, FAILURE_TAG)
        self.assertIn("Expected dict", results[0].value["error"])


if __name__ == "__main__":
    unittest.main()
