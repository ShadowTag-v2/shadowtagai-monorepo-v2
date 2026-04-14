"""Pydantic schemas for SEO Master service
"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


# Enums
class ChangeFrequency(StrEnum):
    ALWAYS = "always"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    NEVER = "never"


class DeviceType(StrEnum):
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"


class SearchEngine(StrEnum):
    GOOGLE = "google"
    BING = "bing"
    YAHOO = "yahoo"
    DUCKDUCKGO = "duckduckgo"


class PerformanceScore(StrEnum):
    GOOD = "good"
    NEEDS_IMPROVEMENT = "needs-improvement"
    POOR = "poor"


# Base Schemas
class SEOAnalysisBase(BaseModel):
    url: str = Field(..., description="URL to analyze")


class SEOAnalysisCreate(SEOAnalysisBase):
    pass


class SEOAnalysisResponse(SEOAnalysisBase):
    id: int
    title: str | None = None
    description: str | None = None
    keywords: list[str] | None = None
    h1_tags: list[str] | None = None
    h2_tags: list[str] | None = None
    image_count: int = 0
    images_with_alt: int = 0
    internal_links: int = 0
    external_links: int = 0
    word_count: int = 0
    has_ssl: bool = False
    mobile_friendly: bool = False
    page_speed_score: float | None = None
    seo_score: float | None = None
    issues: list[str] | None = None
    recommendations: list[str] | None = None
    analyzed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Meta Tags Schemas
class MetaTagBase(BaseModel):
    url: str
    title: str | None = None
    description: str | None = None
    keywords: str | None = None
    author: str | None = None
    robots: str | None = "index, follow"
    viewport: str | None = "width=device-width, initial-scale=1"
    charset: str | None = "UTF-8"


class MetaTagCreate(MetaTagBase):
    # Open Graph
    og_title: str | None = None
    og_description: str | None = None
    og_type: str | None = "website"
    og_url: str | None = None
    og_image: str | None = None
    og_site_name: str | None = None
    og_locale: str | None = "en_US"

    # Twitter Card
    twitter_card: str | None = "summary_large_image"
    twitter_site: str | None = None
    twitter_creator: str | None = None
    twitter_title: str | None = None
    twitter_description: str | None = None
    twitter_image: str | None = None

    # Additional
    canonical_url: str | None = None
    language: str | None = "en"


class MetaTagResponse(MetaTagBase):
    id: int
    og_title: str | None = None
    og_description: str | None = None
    og_type: str | None = None
    og_url: str | None = None
    og_image: str | None = None
    og_site_name: str | None = None
    og_locale: str | None = None
    twitter_card: str | None = None
    twitter_site: str | None = None
    twitter_creator: str | None = None
    twitter_title: str | None = None
    twitter_description: str | None = None
    twitter_image: str | None = None
    canonical_url: str | None = None
    language: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MetaTagHTMLResponse(BaseModel):
    html: str = Field(..., description="HTML meta tags ready to be inserted in <head>")


# Schema Markup Schemas
class SchemaMarkupBase(BaseModel):
    url: str
    schema_type: str = Field(
        ..., description="Schema.org type (e.g., Article, Product, Organization)",
    )
    schema_data: dict[str, Any] = Field(..., description="Schema markup data")


class SchemaMarkupCreate(SchemaMarkupBase):
    pass


class SchemaMarkupResponse(SchemaMarkupBase):
    id: int
    is_valid: bool = True
    validation_errors: list[str] | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SchemaMarkupJSONLDResponse(BaseModel):
    json_ld: str = Field(..., description="JSON-LD script tag ready to be inserted in <head>")


# Sitemap Schemas
class SitemapURLCreate(BaseModel):
    loc: str = Field(..., description="URL location")
    lastmod: datetime | None = None
    changefreq: ChangeFrequency | None = ChangeFrequency.WEEKLY
    priority: float | None = Field(0.5, ge=0.0, le=1.0)


class SitemapURLResponse(SitemapURLCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SitemapCreate(BaseModel):
    name: str = Field(..., description="Sitemap name")
    domain: str = Field(..., description="Domain for the sitemap")
    urls: list[SitemapURLCreate] = Field(..., description="List of URLs to include")


class SitemapResponse(BaseModel):
    id: int
    name: str
    domain: str
    sitemap_type: str
    url_count: int
    last_generated: datetime | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SitemapXMLResponse(BaseModel):
    xml: str = Field(..., description="XML sitemap content")
    url: str | None = Field(None, description="URL where sitemap is available")


# Core Web Vitals Schemas
class CoreWebVitalBase(BaseModel):
    url: str
    device_type: DeviceType = DeviceType.DESKTOP


class CoreWebVitalCreate(CoreWebVitalBase):
    lcp: float | None = None
    fid: float | None = None
    cls: float | None = None
    fcp: float | None = None
    ttfb: float | None = None
    tti: float | None = None
    tbt: float | None = None


class CoreWebVitalResponse(CoreWebVitalBase):
    id: int
    lcp: float | None = None
    fid: float | None = None
    cls: float | None = None
    fcp: float | None = None
    ttfb: float | None = None
    tti: float | None = None
    tbt: float | None = None
    performance_score: float | None = None
    lcp_score: PerformanceScore | None = None
    fid_score: PerformanceScore | None = None
    cls_score: PerformanceScore | None = None
    measured_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Search Ranking Schemas
class SearchRankingBase(BaseModel):
    url: str
    keyword: str
    search_engine: SearchEngine = SearchEngine.GOOGLE
    country: str = "US"
    language: str = "en"
    device_type: DeviceType = DeviceType.DESKTOP


class SearchRankingCreate(SearchRankingBase):
    pass


class SearchRankingResponse(SearchRankingBase):
    id: int
    position: int | None = None
    page: int = 1
    checked_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Utility Schemas
class SEORecommendation(BaseModel):
    category: str
    severity: str  # low, medium, high
    issue: str
    recommendation: str


class SEOScoreBreakdown(BaseModel):
    total_score: float
    meta_tags_score: float
    content_score: float
    technical_score: float
    performance_score: float
    mobile_score: float


# Batch Operations
class BatchURLAnalysisRequest(BaseModel):
    urls: list[str] = Field(..., max_items=100, description="List of URLs to analyze")


class BatchURLAnalysisResponse(BaseModel):
    total: int
    successful: int
    failed: int
    results: list[SEOAnalysisResponse]
    errors: list[dict[str, str]] | None = None
