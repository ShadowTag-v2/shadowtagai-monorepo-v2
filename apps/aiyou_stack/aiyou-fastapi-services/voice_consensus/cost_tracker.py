"""
Cost Tracking and Analytics for Multi-LLM Consensus System

Tracks API costs, provides ROI analysis, and cost optimization recommendations.
"""

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

# Pricing per 1M tokens (input/output) as of Nov 2025
PRICING = {
    "claude-sonnet-4-20250514": {
        "input": 3.00,  # $3 per 1M input tokens
        "output": 15.00,  # $15 per 1M output tokens
    },
    "gemini-2.0-flash-exp": {
        "input": 0.075,  # $0.075 per 1M input tokens
        "output": 0.30,  # $0.30 per 1M output tokens
    },
    "grok-2-latest": {
        "input": 2.00,  # $2 per 1M input tokens
        "output": 10.00,  # $10 per 1M output tokens
    },
    "gpt-4-turbo-preview": {
        "input": 10.00,  # $10 per 1M input tokens
        "output": 30.00,  # $30 per 1M output tokens
    },
    "llama-3.1-sonar-large-128k-online": {  # Perplexity
        "input": 1.00,  # $1 per 1M input tokens
        "output": 1.00,  # $1 per 1M output tokens
    },
}


@dataclass
class QueryCost:
    """Cost breakdown for a single query"""

    query_id: int
    timestamp: str
    system_type: str  # 'atomic', 'simple', or 'single'

    # Token usage
    total_input_tokens: int
    total_output_tokens: int

    # Cost breakdown by model
    model_costs: dict[str, float]

    # Total cost
    total_cost: float

    # Metadata
    models_used: int
    api_calls_made: int
    peer_reviews: int
    threads: int

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "query_id": self.query_id,
            "timestamp": self.timestamp,
            "system_type": self.system_type,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "model_costs": self.model_costs,
            "total_cost": self.total_cost,
            "models_used": self.models_used,
            "api_calls_made": self.api_calls_made,
            "peer_reviews": self.peer_reviews,
            "threads": self.threads,
        }


class CostTracker:
    """
    Track and analyze costs for multi-LLM consensus queries.
    Integrates with transcript archive for historical cost analysis.
    """

    def __init__(self, db_path: str = "~/.consensus_archive.db"):
        """Initialize cost tracker using the same database as transcript archive"""
        self.db_path = Path(db_path).expanduser()
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

        self._initialize_cost_tables()

    def _initialize_cost_tables(self):
        """Create cost tracking tables"""
        cursor = self.conn.cursor()

        # Cost tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_costs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transcript_id INTEGER,
                timestamp TEXT NOT NULL,
                system_type TEXT NOT NULL,

                -- Token usage
                total_input_tokens INTEGER DEFAULT 0,
                total_output_tokens INTEGER DEFAULT 0,

                -- Cost details (JSON)
                model_costs_json TEXT,  -- {model_name: cost}
                total_cost REAL DEFAULT 0.0,

                -- Metadata
                models_used INTEGER DEFAULT 0,
                api_calls_made INTEGER DEFAULT 0,
                peer_reviews INTEGER DEFAULT 0,
                threads INTEGER DEFAULT 0,

                -- Foreign key
                FOREIGN KEY (transcript_id) REFERENCES transcripts(id),

                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Indexes
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_cost_transcript ON query_costs(transcript_id)"
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cost_timestamp ON query_costs(timestamp)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_cost_system_type ON query_costs(system_type)"
        )

        self.conn.commit()

    def calculate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a model based on token usage"""
        if model_name not in PRICING:
            # Unknown model, estimate conservatively
            return (input_tokens * 5.0 + output_tokens * 15.0) / 1_000_000

        pricing = PRICING[model_name]
        input_cost = (input_tokens * pricing["input"]) / 1_000_000
        output_cost = (output_tokens * pricing["output"]) / 1_000_000

        return input_cost + output_cost

    def track_query_cost(
        self,
        transcript_id: int,
        system_type: str,
        model_usage: dict[str, dict[str, int]],  # {model_name: {input: X, output: Y}}
        api_calls: int,
        peer_reviews: int = 0,
        threads: int = 0,
    ) -> QueryCost:
        """
        Track cost for a query.

        Args:
            transcript_id: ID from transcript archive
            system_type: 'atomic', 'simple', or 'single'
            model_usage: Token usage per model
            api_calls: Total API calls made
            peer_reviews: Number of peer reviews
            threads: Number of atomic threads (if applicable)

        Returns:
            QueryCost object
        """
        # Calculate costs per model
        model_costs = {}
        total_input = 0
        total_output = 0

        for model_name, tokens in model_usage.items():
            input_tokens = tokens.get("input", 0)
            output_tokens = tokens.get("output", 0)

            cost = self.calculate_cost(model_name, input_tokens, output_tokens)
            model_costs[model_name] = cost

            total_input += input_tokens
            total_output += output_tokens

        total_cost = sum(model_costs.values())

        # Store in database
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO query_costs (
                transcript_id, timestamp, system_type,
                total_input_tokens, total_output_tokens,
                model_costs_json, total_cost,
                models_used, api_calls_made, peer_reviews, threads
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                transcript_id,
                datetime.utcnow().isoformat(),
                system_type,
                total_input,
                total_output,
                json.dumps(model_costs),
                total_cost,
                len(model_usage),
                api_calls,
                peer_reviews,
                threads,
            ),
        )

        self.conn.commit()
        query_id = cursor.lastrowid

        return QueryCost(
            query_id=query_id,
            timestamp=datetime.utcnow().isoformat(),
            system_type=system_type,
            total_input_tokens=total_input,
            total_output_tokens=total_output,
            model_costs=model_costs,
            total_cost=total_cost,
            models_used=len(model_usage),
            api_calls_made=api_calls,
            peer_reviews=peer_reviews,
            threads=threads,
        )

    def get_cost_stats(self, days: int = 30, system_type: str | None = None) -> dict:
        """
        Get cost statistics for a period.

        Args:
            days: Number of days to analyze
            system_type: Filter by system type

        Returns:
            Dictionary with cost statistics
        """
        cursor = self.conn.cursor()

        # Date filter
        since_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

        # Build query
        where_clause = "WHERE timestamp >= ?"
        params = [since_date]

        if system_type:
            where_clause += " AND system_type = ?"
            params.append(system_type)

        # Get aggregate stats
        cursor.execute(
            f"""
            SELECT
                COUNT(*) as total_queries,
                SUM(total_cost) as total_cost,
                AVG(total_cost) as avg_cost_per_query,
                MIN(total_cost) as min_cost,
                MAX(total_cost) as max_cost,
                SUM(total_input_tokens) as total_input_tokens,
                SUM(total_output_tokens) as total_output_tokens,
                SUM(api_calls_made) as total_api_calls,
                AVG(api_calls_made) as avg_api_calls_per_query,
                SUM(peer_reviews) as total_peer_reviews,
                SUM(threads) as total_threads
            FROM query_costs
            {where_clause}
        """,
            params,
        )

        row = cursor.fetchone()

        # Costs by system type
        cursor.execute(
            """
            SELECT
                system_type,
                COUNT(*) as queries,
                SUM(total_cost) as cost,
                AVG(total_cost) as avg_cost
            FROM query_costs
            WHERE timestamp >= ?
            GROUP BY system_type
        """,
            [since_date],
        )

        by_system = {
            row["system_type"]: {
                "queries": row["queries"],
                "total_cost": row["cost"],
                "avg_cost": row["avg_cost"],
            }
            for row in cursor.fetchall()
        }

        # Cost by model
        cursor.execute(
            f"""
            SELECT model_costs_json
            FROM query_costs
            {where_clause}
        """,
            params,
        )

        model_totals = {}
        for row in cursor.fetchall():
            costs = json.loads(row["model_costs_json"])
            for model, cost in costs.items():
                model_totals[model] = model_totals.get(model, 0) + cost

        return {
            "period_days": days,
            "total_queries": row["total_queries"] or 0,
            "total_cost": row["total_cost"] or 0.0,
            "avg_cost_per_query": row["avg_cost_per_query"] or 0.0,
            "min_cost": row["min_cost"] or 0.0,
            "max_cost": row["max_cost"] or 0.0,
            "total_input_tokens": row["total_input_tokens"] or 0,
            "total_output_tokens": row["total_output_tokens"] or 0,
            "total_api_calls": row["total_api_calls"] or 0,
            "avg_api_calls_per_query": row["avg_api_calls_per_query"] or 0.0,
            "total_peer_reviews": row["total_peer_reviews"] or 0,
            "total_threads": row["total_threads"] or 0,
            "cost_by_system_type": by_system,
            "cost_by_model": model_totals,
        }

    def get_roi_analysis(self, days: int = 30) -> dict:
        """
        Calculate ROI of consensus vs single-model approach.

        Compares cost of consensus against estimated cost of:
        - Using only Claude
        - Human time savings
        - Error reduction value
        """
        stats = self.get_cost_stats(days)

        # Estimate single-Claude cost (2 calls per query avg)
        single_claude_cost_per_query = 0.05  # ~$0.05 for typical query
        single_claude_total = stats["total_queries"] * single_claude_cost_per_query

        # Consensus cost premium
        consensus_premium = stats["total_cost"] - single_claude_total
        consensus_premium_pct = (
            (consensus_premium / single_claude_total * 100) if single_claude_total > 0 else 0
        )

        # Estimated value (conservative estimates)
        # 1. Human time savings: 30 min per complex query @ $150/hr
        time_saved_value = stats["total_queries"] * 0.5 * 150  # 30min @ $150/hr = $75/query

        # 2. Error reduction: Assume consensus catches 80% of errors
        # Value of avoiding 1 production error: ~$500
        error_avoidance_value = (
            stats["total_queries"] * 0.1 * 0.8 * 500
        )  # 10% error rate, 80% caught, $500 per error

        # Total value delivered
        total_value = time_saved_value + error_avoidance_value

        # ROI calculation
        roi = (
            ((total_value - stats["total_cost"]) / stats["total_cost"] * 100)
            if stats["total_cost"] > 0
            else 0
        )

        return {
            "period_days": days,
            # Costs
            "consensus_total_cost": stats["total_cost"],
            "single_claude_estimated_cost": single_claude_total,
            "consensus_premium_dollars": consensus_premium,
            "consensus_premium_percent": consensus_premium_pct,
            # Value delivered
            "time_saved_hours": stats["total_queries"] * 0.5,
            "time_saved_value": time_saved_value,
            "error_avoidance_value": error_avoidance_value,
            "total_value_delivered": total_value,
            # ROI
            "roi_percent": roi,
            "net_value": total_value - stats["total_cost"],
            # Per-query breakdown
            "avg_consensus_cost_per_query": stats["avg_cost_per_query"],
            "avg_single_claude_cost_per_query": single_claude_cost_per_query,
            "avg_value_per_query": total_value / stats["total_queries"]
            if stats["total_queries"] > 0
            else 0,
            # Efficiency metrics
            "cost_per_api_call": stats["total_cost"] / stats["total_api_calls"]
            if stats["total_api_calls"] > 0
            else 0,
            "cost_per_peer_review": stats["total_cost"] / stats["total_peer_reviews"]
            if stats["total_peer_reviews"] > 0
            else 0,
        }

    def get_optimization_recommendations(self) -> list[dict]:
        """
        Provide cost optimization recommendations based on usage patterns.
        """
        stats = self.get_cost_stats(30)
        recommendations = []

        # Check if using expensive models unnecessarily
        if "cost_by_model" in stats:
            total_cost = stats["total_cost"]
            for model, cost in stats["cost_by_model"].items():
                model_pct = (cost / total_cost * 100) if total_cost > 0 else 0

                if model == "gpt-4-turbo-preview" and model_pct > 30:
                    recommendations.append(
                        {
                            "priority": "high",
                            "type": "model_substitution",
                            "title": "High GPT-4 usage detected",
                            "description": f"GPT-4 accounts for {model_pct:.1f}% of costs. Consider using Gemini or Grok for peer reviews.",
                            "potential_savings_percent": 15,
                        }
                    )

        # Check if consensus is overused
        if "cost_by_system_type" in stats:
            atomic_queries = stats["cost_by_system_type"].get("atomic", {}).get("queries", 0)
            total_queries = stats["total_queries"]

            if total_queries > 0:
                atomic_pct = atomic_queries / total_queries * 100

                if atomic_pct > 50:
                    recommendations.append(
                        {
                            "priority": "medium",
                            "type": "system_selection",
                            "title": "High atomic consensus usage",
                            "description": f"{atomic_pct:.1f}% of queries use full atomic consensus. Consider simple consensus for straightforward queries.",
                            "potential_savings_percent": 30,
                        }
                    )

        # Check API call efficiency
        if stats["avg_api_calls_per_query"] > 15:
            recommendations.append(
                {
                    "priority": "medium",
                    "type": "api_efficiency",
                    "title": "High API calls per query",
                    "description": f"Averaging {stats['avg_api_calls_per_query']:.1f} API calls per query. Consider reducing thread count or model count.",
                    "potential_savings_percent": 20,
                }
            )

        # Check if caching would help
        if stats["total_queries"] > 50:
            recommendations.append(
                {
                    "priority": "low",
                    "type": "caching",
                    "title": "Enable caching for common queries",
                    "description": "Consider implementing Redis caching for repeated queries.",
                    "potential_savings_percent": 10,
                }
            )

        return recommendations

    def export_cost_report(self, output_file: str, days: int = 30):
        """Export detailed cost report to JSON"""
        stats = self.get_cost_stats(days)
        roi = self.get_roi_analysis(days)
        recommendations = self.get_optimization_recommendations()

        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "period_days": days,
            "usage_statistics": stats,
            "roi_analysis": roi,
            "optimization_recommendations": recommendations,
            "pricing_reference": PRICING,
        }

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        return report

    def close(self):
        """Close database connection"""
        self.conn.close()


# === CLI ===


def main():
    """CLI for cost tracking and analysis"""
    import argparse

    parser = argparse.ArgumentParser(description="Consensus Cost Tracker")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Stats
    stats_parser = subparsers.add_parser("stats", help="Show cost statistics")
    stats_parser.add_argument("--days", type=int, default=30, help="Days to analyze")
    stats_parser.add_argument(
        "--type", choices=["atomic", "simple", "single"], help="Filter by system type"
    )

    # ROI
    roi_parser = subparsers.add_parser("roi", help="Show ROI analysis")
    roi_parser.add_argument("--days", type=int, default=30, help="Days to analyze")

    # Recommendations
    subparsers.add_parser("optimize", help="Get optimization recommendations")

    # Export
    export_parser = subparsers.add_parser("export", help="Export cost report")
    export_parser.add_argument("output", help="Output JSON file")
    export_parser.add_argument("--days", type=int, default=30, help="Days to analyze")

    args = parser.parse_args()

    tracker = CostTracker()

    if args.command == "stats":
        stats = tracker.get_cost_stats(days=args.days, system_type=args.type)

        print(f"\n{'=' * 80}")
        print(f"COST STATISTICS ({args.days} days)")
        print(f"{'=' * 80}\n")
        print(f"Total Queries: {stats['total_queries']}")
        print(f"Total Cost: ${stats['total_cost']:.2f}")
        print(f"Avg Cost/Query: ${stats['avg_cost_per_query']:.2f}")
        print(f"Min Cost: ${stats['min_cost']:.2f}")
        print(f"Max Cost: ${stats['max_cost']:.2f}")
        print(f"\nTotal API Calls: {stats['total_api_calls']}")
        print(f"Avg API Calls/Query: {stats['avg_api_calls_per_query']:.1f}")
        print(f"Total Peer Reviews: {stats['total_peer_reviews']}")
        print("\nCost by System Type:")
        for sys_type, data in stats["cost_by_system_type"].items():
            print(
                f"  {sys_type}: {data['queries']} queries, ${data['total_cost']:.2f} total, ${data['avg_cost']:.2f} avg"
            )
        print("\nCost by Model:")
        for model, cost in stats["cost_by_model"].items():
            print(f"  {model}: ${cost:.2f}")
        print()

    elif args.command == "roi":
        roi = tracker.get_roi_analysis(days=args.days)

        print(f"\n{'=' * 80}")
        print(f"ROI ANALYSIS ({args.days} days)")
        print(f"{'=' * 80}\n")
        print("COSTS:")
        print(f"  Consensus Total: ${roi['consensus_total_cost']:.2f}")
        print(f"  Single-Claude Estimated: ${roi['single_claude_estimated_cost']:.2f}")
        print(
            f"  Consensus Premium: ${roi['consensus_premium_dollars']:.2f} ({roi['consensus_premium_percent']:.1f}%)"
        )
        print("\nVALUE DELIVERED:")
        print(f"  Time Saved: {roi['time_saved_hours']:.1f} hours")
        print(f"  Time Savings Value: ${roi['time_saved_value']:.2f}")
        print(f"  Error Avoidance Value: ${roi['error_avoidance_value']:.2f}")
        print(f"  Total Value: ${roi['total_value_delivered']:.2f}")
        print("\nROI:")
        print(f"  ROI: {roi['roi_percent']:.1f}%")
        print(f"  Net Value: ${roi['net_value']:.2f}")
        print("\nPER-QUERY METRICS:")
        print(f"  Avg Consensus Cost: ${roi['avg_consensus_cost_per_query']:.2f}")
        print(f"  Avg Single-Claude Cost: ${roi['avg_single_claude_cost_per_query']:.2f}")
        print(f"  Avg Value Delivered: ${roi['avg_value_per_query']:.2f}")
        print()

    elif args.command == "optimize":
        recommendations = tracker.get_optimization_recommendations()

        print(f"\n{'=' * 80}")
        print("COST OPTIMIZATION RECOMMENDATIONS")
        print(f"{'=' * 80}\n")

        if not recommendations:
            print("No optimization recommendations at this time.\n")
        else:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. [{rec['priority'].upper()}] {rec['title']}")
                print(f"   {rec['description']}")
                print(f"   Potential Savings: ~{rec['potential_savings_percent']}%\n")

    elif args.command == "export":
        report = tracker.export_cost_report(args.output, args.days)
        print(f"\n✓ Cost report exported to {args.output}")
        print(f"  Period: {args.days} days")
        print(f"  Total Cost: ${report['usage_statistics']['total_cost']:.2f}")
        print(f"  ROI: {report['roi_analysis']['roi_percent']:.1f}%\n")

    else:
        parser.print_help()

    tracker.close()


if __name__ == "__main__":
    main()
