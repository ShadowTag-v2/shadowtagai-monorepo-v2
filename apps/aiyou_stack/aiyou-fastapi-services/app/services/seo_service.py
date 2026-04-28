# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""SEO Master Service - Business logic for SEO operations"""

import re
from datetime import datetime
from typing import Any
from xml.etree import ElementTree as ET

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.seo import (
    CoreWebVital,
    MetaTag,
    SchemaMarkup,
    SEOAnalysis,
    Sitemap,
    SitemapURL,
)
from app.schemas.seo import (
    CoreWebVitalCreate,
    MetaTagCreate,
    SchemaMarkupCreate,
    SitemapCreate,
    SitemapURLCreate,
)


class SEOService:
    """Service for SEO analysis and optimization"""

    @staticmethod
    def analyze_url(db: Session, url: str) -> SEOAnalysis:
        """Perform comprehensive SEO analysis on a URL"""
        try:
            # Fetch the page
            response = requests.get(
                url,
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0 (compatible; SEOMasterBot/1.0)"},
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract basic information
            title = soup.find("title")
            title_text = title.get_text().strip() if title else None

            meta_desc = soup.find("meta", attrs={"name": "description"})
            description = meta_desc.get("content", "").strip() if meta_desc else None

            # Extract keywords
            meta_keywords = soup.find("meta", attrs={"name": "keywords"})
            keywords = []
            if meta_keywords:
                keywords = [k.strip() for k in meta_keywords.get("content", "").split(",")]

            # Extract headings
            h1_tags = [h1.get_text().strip() for h1 in soup.find_all("h1")]
            h2_tags = [h2.get_text().strip() for h2 in soup.find_all("h2")]

            # Image analysis
            images = soup.find_all("img")
            image_count = len(images)
            images_with_alt = sum(1 for img in images if img.get("alt"))

            # Link analysis
            links = soup.find_all("a", href=True)
            internal_links = sum(
                1 for link in links if url in link["href"] or link["href"].startswith("/")
            )
            external_links = len(links) - internal_links

            # Word count
            text_content = soup.get_text()
            words = re.findall(r"\w+", text_content)
            word_count = len(words)

            # SSL check
            has_ssl = url.startswith("https://")

            # Calculate SEO score
            seo_score = SEOService._calculate_seo_score(
                {
                    "title": title_text,
                    "description": description,
                    "h1_count": len(h1_tags),
                    "images_with_alt_ratio": images_with_alt / image_count
                    if image_count > 0
                    else 0,
                    "has_ssl": has_ssl,
                    "word_count": word_count,
                },
            )

            # Generate issues and recommendations
            issues, recommendations = SEOService._generate_recommendations(
                {
                    "title": title_text,
                    "description": description,
                    "h1_tags": h1_tags,
                    "images_with_alt": images_with_alt,
                    "image_count": image_count,
                    "has_ssl": has_ssl,
                    "word_count": word_count,
                },
            )

            # Create analysis record
            analysis = SEOAnalysis(
                url=url,
                title=title_text,
                description=description,
                keywords=keywords,
                h1_tags=h1_tags,
                h2_tags=h2_tags[:10],  # Limit to first 10
                image_count=image_count,
                images_with_alt=images_with_alt,
                internal_links=internal_links,
                external_links=external_links,
                word_count=word_count,
                has_ssl=has_ssl,
                seo_score=seo_score,
                issues=issues,
                recommendations=recommendations,
                analyzed_at=datetime.utcnow(),
            )

            db.add(analysis)
            db.commit()
            db.refresh(analysis)

            return analysis

        except Exception as e:
            raise Exception(f"Failed to analyze URL: {e!s}") from e

    @staticmethod
    def _calculate_seo_score(data: dict[str, Any]) -> float:
        """Calculate overall SEO score (0-100)"""
        score = 0.0

        # Title (20 points)
        if data.get("title"):
            title_len = len(data["title"])
            if 30 <= title_len <= settings.SEO_MAX_TITLE_LENGTH:
                score += 20
            elif title_len > 0:
                score += 10

        # Description (20 points)
        if data.get("description"):
            desc_len = len(data["description"])
            if 120 <= desc_len <= settings.SEO_MAX_DESCRIPTION_LENGTH:
                score += 20
            elif desc_len > 0:
                score += 10

        # H1 tags (15 points)
        h1_count = data.get("h1_count", 0)
        if h1_count == 1:
            score += 15
        elif h1_count > 0:
            score += 8

        # Images with alt text (15 points)
        alt_ratio = data.get("images_with_alt_ratio", 0)
        score += alt_ratio * 15

        # SSL (10 points)
        if data.get("has_ssl"):
            score += 10

        # Word count (20 points)
        word_count = data.get("word_count", 0)
        if word_count >= 300:
            score += 20
        elif word_count >= 150:
            score += 10
        elif word_count > 0:
            score += 5

        return round(min(score, 100.0), 2)

    @staticmethod
    def _generate_recommendations(data: dict[str, Any]) -> tuple:
        """Generate SEO issues and recommendations"""
        issues = []
        recommendations = []

        # Title checks
        if not data.get("title"):
            issues.append("Missing page title")
            recommendations.append("Add a descriptive title tag (30-60 characters)")
        elif len(data["title"]) > settings.SEO_MAX_TITLE_LENGTH:
            issues.append("Title too long")
            recommendations.append(
                f"Shorten title to under {settings.SEO_MAX_TITLE_LENGTH} characters",
            )

        # Description checks
        if not data.get("description"):
            issues.append("Missing meta description")
            recommendations.append("Add a meta description (120-160 characters)")
        elif len(data["description"]) > settings.SEO_MAX_DESCRIPTION_LENGTH:
            issues.append("Meta description too long")
            recommendations.append(
                f"Shorten description to under {settings.SEO_MAX_DESCRIPTION_LENGTH} characters",
            )

        # H1 checks
        h1_count = len(data.get("h1_tags", []))
        if h1_count == 0:
            issues.append("No H1 tag found")
            recommendations.append("Add a single H1 tag to the page")
        elif h1_count > 1:
            issues.append("Multiple H1 tags found")
            recommendations.append("Use only one H1 tag per page")

        # Image alt text checks
        if data.get("image_count", 0) > 0:
            alt_ratio = data.get("images_with_alt", 0) / data["image_count"]
            if alt_ratio < 1.0:
                issues.append(
                    f"{data['image_count'] - data['images_with_alt']} images missing alt text",
                )
                recommendations.append("Add alt text to all images for accessibility and SEO")

        # SSL check
        if not data.get("has_ssl"):
            issues.append("Not using HTTPS")
            recommendations.append("Enable HTTPS/SSL for security and SEO benefits")

        # Content length check
        if data.get("word_count", 0) < 300:
            issues.append("Low content word count")
            recommendations.append("Add more quality content (aim for 300+ words)")

        return issues, recommendations

    @staticmethod
    def create_meta_tags(db: Session, meta_tag_data: MetaTagCreate) -> MetaTag:
        """Create or update meta tags for a URL"""
        # Check if meta tags already exist for this URL
        existing = db.query(MetaTag).filter(MetaTag.url == meta_tag_data.url).first()

        if existing:
            # Update existing
            for key, value in meta_tag_data.model_dump(exclude_unset=True).items():
                setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing
        # Create new
        meta_tag = MetaTag(**meta_tag_data.model_dump())
        db.add(meta_tag)
        db.commit()
        db.refresh(meta_tag)
        return meta_tag

    @staticmethod
    def generate_meta_tags_html(meta_tag: MetaTag) -> str:
        """Generate HTML meta tags"""
        html_parts = []

        # Basic meta tags
        if meta_tag.charset:
            html_parts.append(f'<meta charset="{meta_tag.charset}">')
        if meta_tag.viewport:
            html_parts.append(f'<meta name="viewport" content="{meta_tag.viewport}">')
        if meta_tag.title:
            html_parts.append(f"<title>{meta_tag.title}</title>")
        if meta_tag.description:
            html_parts.append(f'<meta name="description" content="{meta_tag.description}">')
        if meta_tag.keywords:
            html_parts.append(f'<meta name="keywords" content="{meta_tag.keywords}">')
        if meta_tag.author:
            html_parts.append(f'<meta name="author" content="{meta_tag.author}">')
        if meta_tag.robots:
            html_parts.append(f'<meta name="robots" content="{meta_tag.robots}">')
        if meta_tag.canonical_url:
            html_parts.append(f'<link rel="canonical" href="{meta_tag.canonical_url}">')
        if meta_tag.language:
            html_parts.append(f'<meta http-equiv="content-language" content="{meta_tag.language}">')

        # Open Graph tags
        if meta_tag.og_title:
            html_parts.append(f'<meta property="og:title" content="{meta_tag.og_title}">')
        if meta_tag.og_description:
            html_parts.append(
                f'<meta property="og:description" content="{meta_tag.og_description}">',
            )
        if meta_tag.og_type:
            html_parts.append(f'<meta property="og:type" content="{meta_tag.og_type}">')
        if meta_tag.og_url:
            html_parts.append(f'<meta property="og:url" content="{meta_tag.og_url}">')
        if meta_tag.og_image:
            html_parts.append(f'<meta property="og:image" content="{meta_tag.og_image}">')
        if meta_tag.og_site_name:
            html_parts.append(f'<meta property="og:site_name" content="{meta_tag.og_site_name}">')
        if meta_tag.og_locale:
            html_parts.append(f'<meta property="og:locale" content="{meta_tag.og_locale}">')

        # Twitter Card tags
        if meta_tag.twitter_card:
            html_parts.append(f'<meta name="twitter:card" content="{meta_tag.twitter_card}">')
        if meta_tag.twitter_site:
            html_parts.append(f'<meta name="twitter:site" content="{meta_tag.twitter_site}">')
        if meta_tag.twitter_creator:
            html_parts.append(f'<meta name="twitter:creator" content="{meta_tag.twitter_creator}">')
        if meta_tag.twitter_title:
            html_parts.append(f'<meta name="twitter:title" content="{meta_tag.twitter_title}">')
        if meta_tag.twitter_description:
            html_parts.append(
                f'<meta name="twitter:description" content="{meta_tag.twitter_description}">',
            )
        if meta_tag.twitter_image:
            html_parts.append(f'<meta name="twitter:image" content="{meta_tag.twitter_image}">')

        return "\n".join(html_parts)

    @staticmethod
    def create_schema_markup(db: Session, schema_data: SchemaMarkupCreate) -> SchemaMarkup:
        """Create schema.org markup"""
        schema_markup = SchemaMarkup(**schema_data.model_dump())
        db.add(schema_markup)
        db.commit()
        db.refresh(schema_markup)
        return schema_markup

    @staticmethod
    def generate_schema_jsonld(schema_markup: SchemaMarkup) -> str:
        """Generate JSON-LD script tag"""
        import json

        json_data = {
            "@context": "https://schema.org",
            "@type": schema_markup.schema_type,
            **schema_markup.schema_data,
        }

        json_str = json.dumps(json_data, indent=2)
        return f'<script type="application/ld+json">\n{json_str}\n</script>'

    @staticmethod
    def create_sitemap(db: Session, sitemap_data: SitemapCreate) -> Sitemap:
        """Create a new sitemap"""
        sitemap = Sitemap(
            name=sitemap_data.name,
            domain=sitemap_data.domain,
            url_count=len(sitemap_data.urls),
        )
        db.add(sitemap)
        db.flush()

        # Add URLs
        for url_data in sitemap_data.urls:
            sitemap_url = SitemapURL(sitemap_id=sitemap.id, **url_data.model_dump())
            db.add(sitemap_url)

        # Generate XML
        xml_content = SEOService._generate_sitemap_xml(sitemap_data.urls, sitemap_data.domain)
        sitemap.xml_content = xml_content
        sitemap.last_generated = datetime.utcnow()

        db.commit()
        db.refresh(sitemap)
        return sitemap

    @staticmethod
    def _generate_sitemap_xml(urls: list[SitemapURLCreate], domain: str) -> str:
        """Generate sitemap XML content"""
        urlset = ET.Element("urlset")
        urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

        for url_data in urls:
            url_elem = ET.SubElement(urlset, "url")

            loc = ET.SubElement(url_elem, "loc")
            loc.text = url_data.loc

            if url_data.lastmod:
                lastmod = ET.SubElement(url_elem, "lastmod")
                lastmod.text = url_data.lastmod.strftime("%Y-%m-%d")

            if url_data.changefreq:
                changefreq = ET.SubElement(url_elem, "changefreq")
                changefreq.text = url_data.changefreq.value

            if url_data.priority is not None:
                priority = ET.SubElement(url_elem, "priority")
                priority.text = str(url_data.priority)

        return ET.tostring(urlset, encoding="unicode", method="xml")

    @staticmethod
    def get_sitemap_by_id(db: Session, sitemap_id: int) -> Sitemap | None:
        """Get sitemap by ID"""
        return db.query(Sitemap).filter(Sitemap.id == sitemap_id).first()

    @staticmethod
    def list_sitemaps(db: Session, skip: int = 0, limit: int = 100) -> list[Sitemap]:
        """List all sitemaps"""
        return db.query(Sitemap).offset(skip).limit(limit).all()

    @staticmethod
    def record_core_web_vitals(db: Session, vitals_data: CoreWebVitalCreate) -> CoreWebVital:
        """Record Core Web Vitals metrics"""
        from app.core.config import settings

        # Calculate performance scores
        lcp_score = (
            "good" if vitals_data.lcp and vitals_data.lcp <= settings.LCP_GOOD_THRESHOLD else "poor"
        )
        fid_score = (
            "good" if vitals_data.fid and vitals_data.fid <= settings.FID_GOOD_THRESHOLD else "poor"
        )
        cls_score = (
            "good" if vitals_data.cls and vitals_data.cls <= settings.CLS_GOOD_THRESHOLD else "poor"
        )

        # Calculate overall performance score
        performance_score = 0.0
        if vitals_data.lcp:
            performance_score += 33.3 if lcp_score == "good" else 0
        if vitals_data.fid:
            performance_score += 33.3 if fid_score == "good" else 0
        if vitals_data.cls:
            performance_score += 33.4 if cls_score == "good" else 0

        vitals = CoreWebVital(
            **vitals_data.model_dump(),
            lcp_score=lcp_score,
            fid_score=fid_score,
            cls_score=cls_score,
            performance_score=round(performance_score, 2),
            measured_at=datetime.utcnow(),
        )

        db.add(vitals)
        db.commit()
        db.refresh(vitals)
        return vitals

    @staticmethod
    def get_seo_analysis_by_id(db: Session, analysis_id: int) -> SEOAnalysis | None:
        """Get SEO analysis by ID"""
        return db.query(SEOAnalysis).filter(SEOAnalysis.id == analysis_id).first()

    @staticmethod
    def list_seo_analyses(db: Session, skip: int = 0, limit: int = 100) -> list[SEOAnalysis]:
        """List all SEO analyses"""
        return (
            db.query(SEOAnalysis)
            .order_by(SEOAnalysis.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
