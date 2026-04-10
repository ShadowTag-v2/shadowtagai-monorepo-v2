from pydantic import BaseModel


class RateCard(BaseModel):
    """
    Pnkln Monetization Model (v1 - Dec 2025)
    """

    currency: str = "USD"

    # 1. Backhaul Savings Share (The "Toll")
    # We charge $0.05 per GB saved from going to cloud.
    # Cost to send to AWS: ~$0.09/GB. Savings: $0.04/GB net for client.
    data_egress_saved_price_per_gb: float = 0.05

    # 2. Premium Inference (The "Service")
    # Low-latency (<20ms) inference command premium.
    inference_unit_price: float = 0.002

    # 3. SLA Guarantees
    latency_sla_ms: int = 50
    sla_violation_penalty_pct: float = 0.10  # 10% refund if >50ms

    def to_stripe_metadata(self) -> dict:
        """Convert rate card to Stripe-compatible metadata."""
        return {
            "currency": self.currency,
            "egress_price_per_gb_cents": int(self.data_egress_saved_price_per_gb * 100),
            "inference_price_per_unit_cents": int(self.inference_unit_price * 100 * 1000),
            "latency_sla_ms": str(self.latency_sla_ms),
            "sla_penalty_pct": str(self.sla_violation_penalty_pct),
        }


class RevenueEvent(BaseModel):
    client_id: str
    node_id: str
    gb_processed_at_edge: float
    inference_count: int

    def calculate_bill(self, card: RateCard) -> float:
        savings_fee = self.gb_processed_at_edge * card.data_egress_saved_price_per_gb
        compute_fee = self.inference_count * card.inference_unit_price
        return savings_fee + compute_fee

    def submit_to_billing(self) -> str:
        """
        Submit this revenue event to the billing service.

        Returns:
            Invoice ID from the billing service
        """
        from src.pnkln.services.billing_service import BillingService

        service = BillingService()
        return service.create_invoice(self.client_id, self)

    def to_bigquery_row(self) -> dict:
        """Convert to BigQuery-compatible row format."""
        from datetime import datetime

        card = RateCard()
        return {
            "event_timestamp": datetime.utcnow().isoformat(),
            "client_id": self.client_id,
            "node_id": self.node_id,
            "gb_processed_at_edge": self.gb_processed_at_edge,
            "inference_count": self.inference_count,
            "revenue_generated_usd": self.calculate_bill(card),
        }
