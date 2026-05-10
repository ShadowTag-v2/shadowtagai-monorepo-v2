"""SEO Master Database Models"""

from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class SEOAnalysis(Base):
    """SEO Analysis for a specific URL"""

    __tablename__ = "seo_analyses"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), nullable=False, index=True)
    title = Column(String(255))
    description = Column(Text)
    keywords = Column(JSON)  # List of keywords
    h1_tags = Column(JSON)  # List of H1 tags
    h2_tags = Column(JSON)  # List of H2 tags
    image_count = Column(Integer, default=0)
    images_with_alt = Column(Integer, default=0)
    internal_links = Column(Integer, default=0)
    external_links = Column(Integer, default=0)
    word_count = Column(Integer, default=0)
    has_ssl = Column(Boolean, default=False)
    mobile_friendly = Column(Boolean, default=False)
    page_speed_score = Column(Float)
    seo_score = Column(Float)  # Overall SEO score 0-100
    issues = Column(JSON)  # List of SEO issues found
    recommendations = Column(JSON)  # List of recommendations
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    meta_tags = relationship("MetaTag", back_populates="seo_analysis", cascade="all, delete-orphan")
    schema_markups = relationship(
        "SchemaMarkup",
        back_populates="seo_analysis",
        cascade="all, delete-orphan",
    )
    core_web_vitals = relationship(
        "CoreWebVital",
        back_populates="seo_analysis",
        cascade="all, delete-orphan",
    )


class MetaTag(Base):
    """Meta tags for SEO"""

    __tablename__ = "meta_tags"

    id = Column(Integer, primary_key=True, index=True)
    seo_analysis_id = Column(Integer, ForeignKey("seo_analyses.id"), nullable=True)
    url = Column(String(2048), index=True)

    # Standard meta tags
    title = Column(String(255))
    description = Column(Text)
    keywords = Column(Text)
    author = Column(String(255))
    robots = Column(String(100))
    viewport = Column(String(255))
    charset = Column(String(50))

    # Open Graph tags
    og_title = Column(String(255))
    og_description = Column(Text)
    og_type = Column(String(100))
    og_url = Column(String(2048))
    og_image = Column(String(2048))
    og_site_name = Column(String(255))
    og_locale = Column(String(50))

    # Twitter Card tags
    twitter_card = Column(String(100))
    twitter_site = Column(String(255))
    twitter_creator = Column(String(255))
    twitter_title = Column(String(255))
    twitter_description = Column(Text)
    twitter_image = Column(String(2048))

    # Additional metadata
    canonical_url = Column(String(2048))
    language = Column(String(10))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    seo_analysis = relationship("SEOAnalysis", back_populates="meta_tags")


class SchemaMarkup(Base):
    """Schema.org markup (JSON-LD)"""

    __tablename__ = "schema_markups"

    id = Column(Integer, primary_key=True, index=True)
    seo_analysis_id = Column(Integer, ForeignKey("seo_analyses.id"), nullable=True)
    url = Column(String(2048), index=True)
    schema_type = Column(String(100), nullable=False)  # Article, Product, Organization, etc.
    schema_data = Column(JSON, nullable=False)  # The actual schema markup as JSON
    is_valid = Column(Boolean, default=True)
    validation_errors = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    seo_analysis = relationship("SEOAnalysis", back_populates="schema_markups")


class Sitemap(Base):
    """XML Sitemap management"""

    __tablename__ = "sitemaps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=False, index=True)
    sitemap_type = Column(String(50), default="urlset")  # urlset, sitemapindex
    xml_content = Column(Text)
    url_count = Column(Integer, default=0)
    last_generated = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    urls = relationship("SitemapURL", back_populates="sitemap", cascade="all, delete-orphan")


class SitemapURL(Base):
    """Individual URLs in a sitemap"""

    __tablename__ = "sitemap_urls"

    id = Column(Integer, primary_key=True, index=True)
    sitemap_id = Column(Integer, ForeignKey("sitemaps.id"), nullable=False)
    loc = Column(String(2048), nullable=False)  # URL location
    lastmod = Column(DateTime)  # Last modification date
    changefreq = Column(String(20))  # always, hourly, daily, weekly, monthly, yearly, never
    priority = Column(Float, default=0.5)  # 0.0 to 1.0
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sitemap = relationship("Sitemap", back_populates="urls")


class CoreWebVital(Base):
    """Core Web Vitals metrics"""

    __tablename__ = "core_web_vitals"

    id = Column(Integer, primary_key=True, index=True)
    seo_analysis_id = Column(Integer, ForeignKey("seo_analyses.id"), nullable=True)
    url = Column(String(2048), nullable=False, index=True)

    # Core Web Vitals metrics
    lcp = Column(Float)  # Largest Contentful Paint (seconds)
    fid = Column(Float)  # First Input Delay (milliseconds)
    cls = Column(Float)  # Cumulative Layout Shift

    # Additional performance metrics
    fcp = Column(Float)  # First Contentful Paint (seconds)
    ttfb = Column(Float)  # Time to First Byte (milliseconds)
    tti = Column(Float)  # Time to Interactive (seconds)
    tbt = Column(Float)  # Total Blocking Time (milliseconds)

    # Performance scores
    performance_score = Column(Float)  # 0-100
    lcp_score = Column(String(20))  # good, needs-improvement, poor
    fid_score = Column(String(20))
    cls_score = Column(String(20))

    device_type = Column(String(20), default="desktop")  # desktop, mobile, tablet
    measured_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    seo_analysis = relationship("SEOAnalysis", back_populates="core_web_vitals")


class SearchRanking(Base):
    """Search engine ranking tracking"""

    __tablename__ = "search_rankings"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), nullable=False, index=True)
    keyword = Column(String(255), nullable=False, index=True)
    search_engine = Column(String(50), default="google")  # google, bing, yahoo, etc.
    position = Column(Integer)  # Ranking position
    page = Column(Integer, default=1)  # Which page of results
    country = Column(String(10), default="US")
    language = Column(String(10), default="en")
    device_type = Column(String(20), default="desktop")
    checked_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
