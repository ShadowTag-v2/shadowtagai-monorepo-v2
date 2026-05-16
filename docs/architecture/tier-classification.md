# Tier Classification Model

## Overview

The Tier Classification system categorizes ingested intelligence into three priority levels (Tier 1, 2, 3) based on authority, relevance, timeliness, and engagement. This enables efficient resource allocation and ensures high-value intelligence receives priority processing.

## Tier Definitions

### Tier 1: Priority Intelligence

**Characteristics**:
- High-authority sources (verified news outlets, official channels)
- Time-critical information (breaking news, urgent alerts)
- High relevance to objectives (direct topic match)
- Strong engagement signals (viral, trending)

**Examples**:
- Breaking news from AP, Reuters, BBC
- Official government announcements
- Verified expert analysis
- Trending social media threads (>1000 engagements)

**Target Distribution**: 10-20% of total items

**Processing Priority**: Immediate

### Tier 2: Standard Intelligence

**Characteristics**:
- Moderate-authority sources (reputable blogs, established channels)
- Standard timeliness (published within 72 hours)
- Moderate relevance (related topics, secondary sources)
- Moderate engagement (100-1000 engagements)

**Examples**:
- Industry blog posts
- Secondary news coverage
- Expert commentary
- Niche social media discussions

**Target Distribution**: 30-40% of total items

**Processing Priority**: Standard queue (within 24 hours)

### Tier 3: Background Intelligence

**Characteristics**:
- Lower-authority sources (personal blogs, unverified accounts)
- Low timeliness (>72 hours old)
- Tangential relevance (loosely related)
- Low engagement (<100 engagements)

**Examples**:
- Opinion pieces
- Older archival content
- Loosely related topics
- Low-engagement posts

**Target Distribution**: 40-60% of total items

**Processing Priority**: Backlog (process as resources allow)

## Classification Algorithm

### Ensemble Approach

The classification uses a **hybrid rules + ML** ensemble:

1. **Rule-Based Classifier** (40% weight): Deterministic rules for clear cases
2. **ML Classifier** (60% weight): Gradient boosting model for nuanced cases
3. **Ensemble**: Weighted voting with confidence thresholding

### Rule-Based Classifier

**Decision Tree**:

```python
def rule_based_tier(item: IngestedItem) -> int:
    """Deterministic tier assignment based on rules."""

    # Tier 1 Rules (high priority)
    if (item.source_authority >= 90 and
        item.age_hours <= 6 and
        item.relevance_score >= 80):
        return 1

    if item.engagement_score >= 1000 and item.age_hours <= 12:
        return 1

    if item.source_type == "official_government" and item.age_hours <= 24:
        return 1

    # Tier 3 Rules (low priority)
    if (item.source_authority < 40 or
        item.relevance_score < 30 or
        item.age_hours > 168):  # 7 days
        return 3

    if item.engagement_score < 10 and item.source_authority < 60:
        return 3

    # Default to Tier 2 (standard)
    return 2
```

### ML Classifier (Gradient Boosting)

**Features** (20 total):

| Feature | Type | Description |
|---------|------|-------------|
| `source_authority` | Float (0-100) | Reputation score of source |
| `age_hours` | Float | Hours since publication |
| `relevance_score` | Float (0-100) | Topic match strength |
| `engagement_score` | Int | Social signals (likes, shares, comments) |
| `source_type` | Categorical | news, social, blog, official, etc. |
| `content_length` | Int | Character count |
| `has_media` | Boolean | Images, videos present |
| `sentiment_score` | Float (-1 to 1) | Emotional tone |
| `entity_count` | Int | Named entities (people, orgs, places) |
| `keyword_density` | Float (0-1) | Target keyword ratio |
| `link_count` | Int | Outbound links |
| `author_followers` | Int | Social media following |
| `domain_rank` | Int | Alexa/Similar ranking |
| `is_verified` | Boolean | Verified account/source |
| `topic_tags` | List[str] | Assigned topic categories |
| `language` | Str | Content language (ISO 639-1) |
| `geo_location` | Str | Geographic origin |
| `publication_frequency` | Float | Source posting rate |
| `historical_tier_avg` | Float (1-3) | Source's avg past tier |
| `completeness_score` | Float (0-1) | Required fields present |

**Model Architecture**:
```python
from sklearn.ensemble import GradientBoostingClassifier

model = GradientBoostingClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=5,
    min_samples_split=20,
    subsample=0.8,
    random_state=42
)

# Training data: historical items with manual tier labels
X_train = feature_matrix  # (n_samples, 20 features)
y_train = tier_labels     # (n_samples,) values in {1, 2, 3}

model.fit(X_train, y_train)
```

**Performance**:
- **Accuracy**: 85% on validation set
- **Precision**: 82% (Tier 1), 87% (Tier 2), 84% (Tier 3)
- **Recall**: 79% (Tier 1), 88% (Tier 2), 86% (Tier 3)
- **F1-Score**: 0.80 (Tier 1), 0.87 (Tier 2), 0.85 (Tier 3)

### Ensemble Logic

```python
def ensemble_tier(item: IngestedItem) -> tuple[int, float]:
    """Combine rule-based and ML predictions."""

    # Get both predictions
    rule_tier = rule_based_tier(item)
    ml_tier, ml_confidence = ml_classifier.predict_proba(item)

    # Weighted voting
    if ml_confidence > 0.9:
        # High ML confidence: trust ML (60% weight dominates)
        final_tier = ml_tier
        confidence = ml_confidence
    elif rule_tier == ml_tier:
        # Agreement: high confidence
        final_tier = rule_tier
        confidence = 0.95
    else:
        # Disagreement: weighted vote
        if ml_confidence > 0.7:
            final_tier = ml_tier
            confidence = 0.7
        else:
            final_tier = rule_tier
            confidence = 0.6

    return final_tier, confidence
```

## Feature Engineering

### Source Authority Scoring

**Components**:
- **Domain Reputation**: Alexa rank, domain age, SSL cert
- **Historical Quality**: Past tier distribution from this source
- **Verification Status**: Official verification badges
- **Backlink Profile**: Authoritative sites linking to source
- **Editorial Standards**: Fact-checking, corrections policy

**Calculation**:
```python
def calculate_source_authority(source: Source) -> float:
    """Compute 0-100 authority score."""

    scores = {
        'domain_rank': min(100, 100 - (source.alexa_rank / 10000)),
        'domain_age_years': min(20, source.domain_age_years) * 5,
        'is_verified': 20 if source.is_verified else 0,
        'historical_tier_1_pct': source.tier_1_percentage,
        'has_editorial_standards': 10 if source.has_fact_checking else 0,
    }

    # Weighted average
    weights = {'domain_rank': 0.3, 'domain_age_years': 0.2,
               'is_verified': 0.25, 'historical_tier_1_pct': 0.15,
               'has_editorial_standards': 0.1}

    authority = sum(scores[k] * weights[k] for k in scores)
    return min(100, max(0, authority))
```

### Relevance Scoring

**Methods**:
1. **Keyword Matching**: TF-IDF weighted keyword presence
2. **Topic Modeling**: LDA topic alignment
3. **Semantic Similarity**: Embeddings (sentence-transformers)

**Implementation**:
```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_relevance(item_text: str, objective_text: str) -> float:
    """Compute 0-100 relevance score."""

    # Generate embeddings
    item_emb = embedding_model.encode([item_text])
    obj_emb = embedding_model.encode([objective_text])

    # Cosine similarity
    similarity = cosine_similarity(item_emb, obj_emb)[0][0]

    # Scale to 0-100
    relevance = similarity * 100

    return relevance
```

### Engagement Scoring

**Social Media Signals**:
```python
def calculate_engagement(item: IngestedItem) -> int:
    """Aggregate engagement metrics."""

    engagement = 0

    if item.source_type == "twitter":
        engagement = (
            item.likes * 1 +
            item.retweets * 3 +
            item.replies * 2 +
            item.quote_tweets * 4
        )
    elif item.source_type == "youtube":
        engagement = (
            item.views * 0.01 +
            item.likes * 2 +
            item.comments * 5
        )
    elif item.source_type == "news":
        engagement = (
            item.shares * 3 +
            item.comments * 2
        )

    return int(engagement)
```

## Configuration

### Tier Classification Config

**File**: `/config/tier-classification.yaml`

```yaml
tier_classification:
  ensemble:
    rule_weight: 0.4
    ml_weight: 0.6
    high_confidence_threshold: 0.9
    low_confidence_threshold: 0.6

  tier_1:
    min_authority: 90
    max_age_hours: 6
    min_relevance: 80
    min_engagement: 1000
    target_percentage: 15

  tier_2:
    min_authority: 60
    max_age_hours: 72
    min_relevance: 50
    min_engagement: 100
    target_percentage: 35

  tier_3:
    max_authority: 40
    max_relevance: 30
    min_age_hours: 168
    max_engagement: 10
    target_percentage: 50

  sources:
    verified_authorities:
      - "apnews.com"
      - "reuters.com"
      - "bbc.com"
      - "nytimes.com"
      - "wsj.com"

    official_government:
      - "*.gov"
      - "*.mil"
      - "europa.eu"

    auto_tier_3:
      - "personal-blog.example"
      - "low-quality.example"

  ml_model:
    model_path: "/models/tier_classifier_v1.pkl"
    feature_version: "v1"
    retrain_frequency_days: 30
    min_training_samples: 1000

  quality_gates:
    min_tier_1_daily: 50
    max_tier_1_daily: 500
    min_tier_2_daily: 300
    max_tier_3_percentage: 70
```

## Training & Updating

### Training Data Collection

**Sources**:
- Historical items with manual labels (gold standard)
- User feedback (promote/demote tier)
- Downstream quality signals (briefing inclusion, user engagement)

**Labeling Process**:
```python
def collect_training_sample(item: IngestedItem, label: int, source: str):
    """Save labeled example for retraining."""

    sample = {
        'item_id': item.id,
        'features': extract_features(item),
        'label': label,
        'source': source,  # 'manual', 'feedback', 'implicit'
        'timestamp': datetime.utcnow(),
        'labeler': 'user_id or system'
    }

    training_db.insert(sample)
```

### Retraining Schedule

**Frequency**: Monthly (or 1000 new samples)

**Process**:
1. Extract new training samples from DB
2. Combine with existing training set (max 10K samples)
3. Split into train (80%) / validation (20%)
4. Train new model
5. Evaluate performance (accuracy ≥85%)
6. A/B test new model (10% traffic) for 1 week
7. Full rollout if metrics improved
8. Version and archive old model

### Model Versioning

**Naming**: `tier_classifier_vX_YYYYMMDD.pkl`

**Metadata**:
```json
{
  "version": "v2",
  "trained_date": "2025-11-07",
  "training_samples": 5000,
  "validation_accuracy": 0.87,
  "feature_version": "v1",
  "hyperparameters": {
    "n_estimators": 200,
    "learning_rate": 0.05,
    "max_depth": 5
  }
}
```

## Monitoring & Evaluation

### Key Metrics

**Distribution Metrics**:
- Tier 1/2/3 percentage daily
- Trend over time (weekly, monthly)
- Per-source tier distribution

**Quality Metrics**:
- Tier accuracy (manual review sample)
- Tier stability (re-classification rate)
- User feedback ratio (promote/demote)

**Performance Metrics**:
- Classification latency (target: <50ms)
- Model confidence distribution
- Feature importance drift

### Dashboards

**Tier Distribution Over Time**:
```
Tier 1: ████░░░░░░░░░░░░░░░░░░ 15%
Tier 2: ████████████░░░░░░░░░░ 35%
Tier 3: ██████████████████████ 50%
```

**Source Quality**:
| Source | Tier 1 % | Tier 2 % | Tier 3 % | Avg Authority |
|--------|----------|----------|----------|---------------|
| apnews.com | 80% | 18% | 2% | 95 |
| bbc.com | 75% | 20% | 5% | 93 |
| twitter.com | 10% | 35% | 55% | 62 |
| personal-blog.example | 1% | 15% | 84% | 38 |

### Alerts

**Immediate**:
- Tier 1 percentage <5% or >30% (distribution skew)
- Model confidence <60% for >20% of items
- Classification latency >100ms

**Warning**:
- Tier distribution outside target ranges for 3+ days
- Source tier shift (e.g., normally 80% Tier 1 drops to 50%)
- Feature drift detected (distribution change)

## Future Enhancements

1. **Deep Learning**: BERT-based classifier for semantic understanding
2. **Multi-Label**: Assign multiple tiers with confidence scores
3. **Dynamic Tiers**: Adjust tier thresholds based on volume
4. **Personalization**: User-specific tier preferences
5. **Explainability**: SHAP values for tier decisions
6. **Real-time Updates**: Stream-based re-classification
7. **Active Learning**: Auto-label uncertain items with human review

## References

- [Gemini Ingestion Layer Architecture](./gemini-ingestion-layer.md)
- [Source Authority Database](../../data/source_authority.json)
- [ML Model Artifacts](../../models/)
- [Training Data Schema](../../schemas/training_sample.json)

## Version History

- **v1.0** (2025-11-07): Initial tier classification model
- Ensemble: Rules (40%) + ML (60%)
- Target accuracy: ≥85%
- Features: 20 signals
