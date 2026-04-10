import logging
import unittest
from typing import Any

import apache_beam as beam
from apache_beam.pvalue import TaggedOutput

# Tags for multiple outputs
SUCCESS_TAG = "success"
FAILURE_TAG = "failure"


class ConsolidateFn(beam.DoFn):
    """
    Consolidates incoming data rows.
    """

    def process(self, row: dict[str, Any]) -> Any:
        try:
            # Type checking and validation logic
            if "id" not in row or "value" not in row:
                raise ValueError("Missing required fields 'id' or 'value'")

            # Transformation logic
            result = {
                "id": row["id"],
                "consolidated_value": str(row["value"]).upper(),
                "status": "consolidated",
            }
            yield result

        except Exception as e:
            # Emit to Dead Letter Queue
            error_record = {"row": row, "error": str(e), "pipeline_step": "ConsolidateFn"}
            yield TaggedOutput(FAILURE_TAG, error_record)


def run_pipeline(input_data: list[dict[str, Any]], runner: str = "DirectRunner"):
    with beam.Pipeline(runner=runner) as p:
        rows = p | "Create" >> beam.Create(input_data)

        results = rows | "Consolidate" >> beam.ParDo(ConsolidateFn()).with_outputs(
            FAILURE_TAG, main=SUCCESS_TAG
        )

        success = results[SUCCESS_TAG]
        failure = results[FAILURE_TAG]

        success | "PrintSuccess" >> beam.Map(lambda x: logging.info(f"Success: {x}"))
        failure | "PrintFailure" >> beam.Map(lambda x: logging.error(f"DLQ: {x}"))


# ---------------------------------------------------------
# UNIT TEST
# ---------------------------------------------------------
class GenericTest(unittest.TestCase):
    def test_consolidate_fn_success(self):
        fn = ConsolidateFn()
        valid_row = {"id": "123", "value": "test"}
        results = list(fn.process(valid_row))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["consolidated_value"], "TEST")

    def test_consolidate_fn_failure(self):
        fn = ConsolidateFn()
        invalid_row = {"id": "123"}  # Missing value
        results = list(fn.process(invalid_row))
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], TaggedOutput)
        self.assertEqual(results[0].tag, FAILURE_TAG)
        self.assertIn("Missing required fields", results[0].value["error"])


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    # If run directly, run tests then a sample pipeline
    unittest.main(exit=False)

    print("\nRunning Sample Pipeline...")
    sample_data = [
        {"id": "1", "value": "alpha"},
        {"id": "2"},  # Invalid
        {"id": "3", "value": "gamma"},
    ]
    run_pipeline(sample_data)
