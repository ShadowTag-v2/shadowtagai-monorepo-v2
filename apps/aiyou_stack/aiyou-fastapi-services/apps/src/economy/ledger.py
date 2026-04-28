# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""THE BOOKS
Sovereign Financial Ledger
Exports transactions to Quicken (QIF) and Universal CSV.
"""

from datetime import datetime

from src.economy.mall import Transaction


class LedgerBook:
    """Manages the Sovereign Chart of Accounts and exports."""

    # Chart of Accounts Mapping
    ACCOUNTS = {
        "ASSET_STRIPE": "Bank:Stripe Clearing",
        "ASSET_CRYPTO": "Bank:Crypto Wallet",
        "INC_SOVEREIGN": "Inc:Sovereign Tier",
        "INC_MALL_FEES": "Inc:Mall Fees",
        "INC_SUBS": "Inc:Subscriptions",
        "EXP_PAYOUTS": "Exp:Vendor Payouts",
        "EXP_COMPUTE": "Exp:Compute",
    }

    def format_qif_date(self, timestamp: float) -> str:
        """Converts timestamp to QIF date format (D/M/YYYY)."""
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%d/%m/%Y")

    def export_qif(self, transactions: list[Transaction]) -> str:
        """Generates a QIF file content string from a list of transactions.
        Simple implementation focusing on the Mall Fee collection (Income) for the platform.
        """
        qif_content = "!Type:Bank\n"

        for txn in transactions:
            # We record the MALL FEE as Income for the Platform
            # Date
            qif_content += f"D{self.format_qif_date(txn.timestamp)}\n"
            # Amount (The Fee we kept)
            qif_content += f"T{txn.mall_fee:.2f}\n"
            # Payee (The Buyer)
            qif_content += f"PPurchase by {txn.buyer_id}\n"
            # Memo (Product Details)
            qif_content += f"MProduct: {txn.product_id} (Vendor Payout: ${txn.vendor_payout:.2f})\n"
            # Category (Income Account)
            qif_content += f"L{self.ACCOUNTS['INC_MALL_FEES']}\n"
            # End of Record
            qif_content += "^\n"

        return qif_content

    def export_csv(self, transactions: list[Transaction]) -> str:
        """Generates a CSV string."""
        csv_content = "Date,Description,Amount,Category,Memo\n"

        for txn in transactions:
            date_str = datetime.fromtimestamp(txn.timestamp).strftime("%Y-%m-%d")
            # Mall Fee Income
            csv_content += f"{date_str},Purchase by {txn.buyer_id},{txn.mall_fee:.2f},{self.ACCOUNTS['INC_MALL_FEES']},Product: {txn.product_id}\n"

        return csv_content
