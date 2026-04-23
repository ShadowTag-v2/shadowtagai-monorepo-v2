"""SEO Master API Router"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.seo import (
    BatchURLAnalysisRequest,
    BatchURLAnalysisResponse,
    CoreWebVitalCreate,
    CoreWebVitalResponse,
    MetaTagCreate,
    MetaTagHTMLResponse,
    MetaTagResponse,
    SchemaMarkupCreate,
    SchemaMarkupJSONLDResponse,
    SchemaMarkupResponse,
    SEOAnalysisCreate,
    SEOAnalysisResponse,
    SitemapCreate,
    SitemapResponse,
    SitemapXMLResponse,
)
from app.services.seo_service import SEOService

router = APIRouter(
    prefix="/api/v1/seo",
    tags=["SEO Master"],
)


# SEO Analysis Endpoints
@router.post("/analyze", response_model=SEOAnalysisResponse, status_code=status.HTTP_201_CREATED)
def analyze_url(url_data: SEOAnalysisCreate, db: Session = Depends(get_db)):
    """Analyze a URL for SEO optimization.

    Returns comprehensive SEO analysis including:
    - Page title and meta description
    - Heading structure (H1, H2)
    - Image optimization
    - Link analysis
    - SEO score
    - Issues and recommendations
    """
    try:
        analysis = SEOService.analyze_url(db, url_data.url)
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to analyze URL: {e!s}",
        ) from e


@router.get("/analyze/{analysis_id}", response_model=SEOAnalysisResponse)
def get_seo_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """Get SEO analysis by ID"""
    analysis = SEOService.get_seo_analysis_by_id(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SEO analysis not found")
    return analysis


@router.get("/analyze", response_model=list[SEOAnalysisResponse])
def list_seo_analyses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """List all SEO analyses with pagination"""
    return SEOService.list_seo_analyses(db, skip=skip, limit=limit)


@router.post("/analyze/batch", response_model=BatchURLAnalysisResponse)
def batch_analyze_urls(batch_request: BatchURLAnalysisRequest, db: Session = Depends(get_db)):
    """Analyze multiple URLs in batch.
    Maximum 100 URLs per request.
    """
    results = []
    errors = []
    successful = 0
    failed = 0

    for url in batch_request.urls:
        try:
            analysis = SEOService.analyze_url(db, url)
            results.append(analysis)
            successful += 1
        except Exception as e:
            errors.append({"url": url, "error": str(e)})
            failed += 1

    return BatchURLAnalysisResponse(
        total=len(batch_request.urls),
        successful=successful,
        failed=failed,
        results=results,
        errors=errors or None,
    )


# Meta Tags Endpoints
@router.post("/meta-tags", response_model=MetaTagResponse, status_code=status.HTTP_201_CREATED)
def create_meta_tags(meta_tag_data: MetaTagCreate, db: Session = Depends(get_db)):
    """Create or update meta tags for a URL.

    Includes:
    - Standard meta tags (title, description, keywords)
    - Open Graph tags for social media
    - Twitter Card tags
    - Canonical URL
    """
    try:
        meta_tag = SEOService.create_meta_tags(db, meta_tag_data)
        return meta_tag
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create meta tags: {e!s}",
        ) from e


@router.get("/meta-tags/{meta_tag_id}/html", response_model=MetaTagHTMLResponse)
def get_meta_tags_html(meta_tag_id: int, db: Session = Depends(get_db)):
    """Generate HTML meta tags ready to be inserted in <head> section."""
    from app.db.models.seo import MetaTag

    meta_tag = db.query(MetaTag).filter(MetaTag.id == meta_tag_id).first()
    if not meta_tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meta tags not found")

    html = SEOService.generate_meta_tags_html(meta_tag)
    return MetaTagHTMLResponse(html=html)


# Schema Markup Endpoints
@router.post("/schema", response_model=SchemaMarkupResponse, status_code=status.HTTP_201_CREATED)
def create_schema_markup(schema_data: SchemaMarkupCreate, db: Session = Depends(get_db)):
    """Create Schema.org structured data markup.

    Supports types like:
    - Article
    - Product
    - Organization
    - Person
    - Event
    - Review
    - And more...
    """
    try:
        schema_markup = SEOService.create_schema_markup(db, schema_data)
        return schema_markup
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create schema markup: {e!s}",
        ) from e


@router.get("/schema/{schema_id}/jsonld", response_model=SchemaMarkupJSONLDResponse)
def get_schema_jsonld(schema_id: int, db: Session = Depends(get_db)):
    """Generate JSON-LD script tag for schema markup.
    Ready to be inserted in <head> or <body> section.
    """
    from app.db.models.seo import SchemaMarkup

    schema_markup = db.query(SchemaMarkup).filter(SchemaMarkup.id == schema_id).first()
    if not schema_markup:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schema markup not found")

    json_ld = SEOService.generate_schema_jsonld(schema_markup)
    return SchemaMarkupJSONLDResponse(json_ld=json_ld)


# Sitemap Endpoints
@router.post("/sitemap", response_model=SitemapResponse, status_code=status.HTTP_201_CREATED)
def create_sitemap(sitemap_data: SitemapCreate, db: Session = Depends(get_db)):
    """Generate XML sitemap for a website.

    Include URLs with:
    - Location (required)
    - Last modification date
    - Change frequency
    - Priority (0.0 to 1.0)
    """
    try:
        sitemap = SEOService.create_sitemap(db, sitemap_data)
        return sitemap
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create sitemap: {e!s}",
        ) from e


@router.get("/sitemap/{sitemap_id}", response_model=SitemapResponse)
def get_sitemap(sitemap_id: int, db: Session = Depends(get_db)):
    """Get sitemap by ID"""
    sitemap = SEOService.get_sitemap_by_id(db, sitemap_id)
    if not sitemap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sitemap not found")
    return sitemap


@router.get("/sitemap/{sitemap_id}/xml", response_model=SitemapXMLResponse)
def get_sitemap_xml(sitemap_id: int, db: Session = Depends(get_db)):
    """Get sitemap XML content.
    Ready to be saved as sitemap.xml file.
    """
    sitemap = SEOService.get_sitemap_by_id(db, sitemap_id)
    if not sitemap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sitemap not found")

    return SitemapXMLResponse(xml=sitemap.xml_content, url=f"/api/v1/seo/sitemap/{sitemap_id}/xml")


@router.get("/sitemap", response_model=list[SitemapResponse])
def list_sitemaps(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """List all sitemaps with pagination"""
    return SEOService.list_sitemaps(db, skip=skip, limit=limit)


# Core Web Vitals Endpoints
@router.post(
    "/core-web-vitals",
    response_model=CoreWebVitalResponse,
    status_code=status.HTTP_201_CREATED,
)
def record_core_web_vitals(vitals_data: CoreWebVitalCreate, db: Session = Depends(get_db)):
    """Record Core Web Vitals metrics for a URL.

    Metrics include:
    - LCP (Largest Contentful Paint)
    - FID (First Input Delay)
    - CLS (Cumulative Layout Shift)
    - FCP (First Contentful Paint)
    - TTFB (Time to First Byte)
    - TTI (Time to Interactive)
    - TBT (Total Blocking Time)
    """
    try:
        vitals = SEOService.record_core_web_vitals(db, vitals_data)
        return vitals
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to record Core Web Vitals: {e!s}",
        ) from e


# Health Check
@router.get("/health")
def health_check():
    """SEO Master service health check"""
    return {"status": "healthy", "service": "SEO Master", "version": "1.0.0"}
