import langextract as lx
import pipeline_dp
from fastapi import APIRouter
from google.cloud import bigquery
from pydantic import BaseModel, Field

router = APIRouter()


class HDISignal(BaseModel):
    artifact: str = Field(description="Visual artifact e.g., temporal_flicker, impossible_geometry")
    user_id_raw: str = Field(description="For DP anonymization")


@router.post("/process-dataset")
async def process_b2b_dataset(daily_comments: list[str]):
    """
    Nightly CRON endpoint. Extracts chaos into the Human Deception Index.
    """
    extracted_data = []

    # 1. Pipeline: LangExtract parsing of chaotic unstructured comments
    for thread in daily_comments:
        result = lx.extract(
            text_or_documents=thread,
            prompt_description="Extract the exact visual artifacts that fooled users in these comments.",
            schema=HDISignal,
            model_id="gemini-3-flash-preview",
        )
        if hasattr(result, "extractions") and result.extractions:
            extracted_data.extend(result.extractions)

    # 2. Pipeline: Differential Privacy (EU AI Act Compliance)
    accountant = pipeline_dp.NaiveBudgetAccountant(total_epsilon=1.0, total_delta=1e-5)
    dp_engine = pipeline_dp.LocalDPEngine(accountant)

    params = pipeline_dp.AggregateParams(
        noise_kind=pipeline_dp.NoiseKind.LAPLACE,
        metrics=[pipeline_dp.Metrics.COUNT],
        max_partitions_contributed=1,
        max_contributions_per_partition=1,
    )

    data_extractors = pipeline_dp.DataExtractors(
        privacy_id_extractor=lambda x: x.user_id_raw,
        partition_extractor=lambda x: x.artifact,
        value_extractor=lambda x: 1,
    )

    anonymized_data = list(dp_engine.aggregate(extracted_data, params, data_extractors))

    # 3. Pipeline: Insert to BigQuery HDI Sandbox
    try:
        client = bigquery.Client(project="shadowtag-omega-v4")

        # Ensure BigQuery exact schema matches the anonymized tuples
        formatted_rows = [{"artifact": row[0], "count": row[1].count} for row in anonymized_data]
        errors = client.insert_rows_json("shadowtag-omega-v4.b2b.hdi_dataset", formatted_rows)

        if errors:
            return {"status": "error", "message": str(errors)}
    except Exception as e:
        return {"status": "error", "message": f"BigQuery routing failed: {str(e)}"}

    return {"status": "success", "message": "B2B Refinery pipeline generated anonymized dataset."}
