"""Database models package
"""

from app.db.models.seo import (
    CoreWebVital,
    MetaTag,
    SchemaMarkup,
    SearchRanking,
    SEOAnalysis,
    Sitemap,
    SitemapURL,
)

__all__ = [
    "CoreWebVital",
    "MetaTag",
    "SEOAnalysis",
    "SchemaMarkup",
    "SearchRanking",
    "Sitemap",
    "SitemapURL",
]
