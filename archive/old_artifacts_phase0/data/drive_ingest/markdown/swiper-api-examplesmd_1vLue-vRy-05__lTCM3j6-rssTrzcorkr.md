# Swiper API - Usage Examples

## Quick Start

```bash
# Start the Swiper API server
cd /home/user/ShadowTag-v2-fastapi-services
python src/api/swiper.py

# Server runs on http://localhost:8000
# API docs: http://localhost:8000/docs
```

---

## Example 1: Create a Premium Beacon Video

### Request: Create Superman Movie (Part 1)

```bash
curl -X POST "http://localhost:8000/videos" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Superman: The Adventure Begins - Part 1",
    "description": "Watch Part 1 on your way to Walmart. Buy the doll to unlock Part 2!",
    "format": "long_form",
    "base_duration_seconds": 5400,
    "min_duration_seconds": 1800,
    "max_duration_seconds": 7200,
    "gcs_bucket": "swiper-videos",
    "gcs_path": "premium-beacons/superman-part1.mp4",
    "cdn_url": "https://cdn.swiper.com/superman-part1/manifest.m3u8",
    "thumbnail_url": "https://cdn.swiper.com/thumbnails/superman.jpg",
    "is_shoppable": true,
    "is_premium_beacon": true,
    "beacon_type": "drive_to_store",
    "retailer_id": "walmart-123",
    "available_runtimes": ["auto_adaptive", "full_feature"]
  }'
```

### Response

```json
{
  "id": "video-uuid-123",
  "title": "Superman: The Adventure Begins - Part 1",
  "format": "long_form",
  "base_duration_seconds": 5400,
  "cdn_url": "https://cdn.swiper.com/superman-part1/manifest.m3u8",
  "is_premium_beacon": true,
  "products_count": 0,
  "total_views": 0,
  "created_at": "2025-01-15T10:30:00Z"
}
```

---

## Example 2: Add Shoppable Product

### Request: Create Superman Action Figure

```bash
curl -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Superman Action Figure - Collectible Edition",
    "description": "Official DC Comics figure. As seen in the movie!",
    "category": "toys",
    "price": 29.99,
    "currency": "USD",
    "retailer_id": "walmart-123",
    "buy_url": "https://walmart.com/products/superman-figure",
    "image_url": "https://cdn.swiper.com/products/superman.jpg",
    "in_stock": true
  }'
```

### Response

```json
{
  "id": "product-uuid-456",
  "name": "Superman Action Figure - Collectible Edition",
  "category": "toys",
  "price": 29.99,
  "in_stock": true,
  "total_clicks": 0,
  "total_purchases": 0
}
```

---

## Example 3: Add Product Overlay to Video

### Request: Make Superman appear at 75 minutes

```bash
curl -X POST "http://localhost:8000/products/overlays" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "video-uuid-123",
    "product_id": "product-uuid-456",
    "start_time_seconds": 4500,
    "end_time_seconds": 5400,
    "position_x": 80,
    "position_y": 80,
    "width": 15,
    "height": 15,
    "cta_text": "Get your Superman!",
    "is_clickable": true
  }'
```

### Response

```json
{
  "id": "overlay-uuid-789",
  "video_id": "video-uuid-123",
  "product_id": "product-uuid-456",
  "start_time_seconds": 4500,
  "end_time_seconds": 5400,
  "cta_text": "Get your Superman!",
  "clicks": 0
}
```

---

## Example 4: Add Persuasion Layer (Kids → Parents)

### Request: Add parent-targeted talking point

```bash
curl -X POST "http://localhost:8000/persuasion-points" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "video-uuid-123",
    "target_audience": "parent",
    "message": "This Superman figure is made from safe, durable materials that last for years!",
    "context": "Target parents concerned about toy safety",
    "narrative_integration": "Character dialogue emphasizes durability",
    "start_time_seconds": 2700,
    "end_time_seconds": 2715,
    "delivery_method": "dialogue",
    "emphasis_level": "subtle"
  }'
```

### Response

```json
{
  "id": "persuasion-uuid-101",
  "video_id": "video-uuid-123",
  "target_audience": "parent",
  "message": "This Superman figure is made from safe, durable materials that last for years!",
  "delivery_method": "dialogue",
  "impressions": 0
}
```

---

## Example 5: Adaptive Playback (Core Feature!)

### Request: User driving to Walmart, 45 minutes away

```bash
curl -X POST "http://localhost:8000/videos/play" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "video-uuid-123",
    "user_id": "user-sarah-123",
    "runtime_mode": "auto_adaptive",
    "device_type": "mobile",
    "location_lat": 37.7749,
    "location_lon": -122.4194,
    "eta_minutes": 45,
    "household_type": "family_with_kids",
    "interests": ["toys", "family"],
    "scroll_speed": "medium",
    "hover_time_seconds": 8
  }'
```

### Response

```json
{
  "video_id": "video-uuid-123",
  "playback_url": "https://cdn.swiper.com/superman-part1/manifest.m3u8",
  "runtime_seconds": 2700,
  "selected_runtime_mode": "auto_adaptive",

  "narrative_arc": {
    "arc_id": "family_fun",
    "scenes": ["intro", "product_demo", "family_interaction", "cta"],
    "emphasis": "safety_and_fun"
  },

  "products": [
    {
      "product_id": "product-uuid-456",
      "name": "Superman Action Figure",
      "price": 29.99,
      "buy_url": "https://walmart.com/products/superman-figure",
      "start_time": 4500,
      "end_time": 5400,
      "position": {"x": 80, "y": 80, "width": 15, "height": 15},
      "cta_text": "Get your Superman!"
    }
  ],

  "persuasion_points": [
    {
      "message": "This Superman figure is made from safe, durable materials...",
      "delivery_method": "dialogue",
      "start_time": 2700,
      "end_time": 2715,
      "emphasis": "subtle"
    },
    {
      "message": "Educational play that inspires heroism and builds imagination",
      "delivery_method": "voiceover",
      "start_time": 4200,
      "end_time": 4210,
      "emphasis": "moderate"
    }
  ],

  "is_beacon_session": true,
  "unlock_condition": "You're 523m from the store. Watch Part 1 on your way. Buy the product to unlock Part 2!",
  "session_id": "session-uuid-999",
  "personalization_stage": "bandits"
}
```

**What Happened:**
1. ✅ Movie runtime adjusted from 90min → 45min (matches ETA)
2. ✅ AI selected "family_fun" narrative arc (household type = family_with_kids)
3. ✅ Loaded parent-targeted persuasion points (kids will repeat these to mom)
4. ✅ Detected user near Walmart store (geofence active)
5. ✅ Set unlock condition: buy product to get Part 2

---

## Example 6: Log User Interaction

### Request: User clicks on Superman product at 75 minutes

```bash
curl -X POST "http://localhost:8000/interactions" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-sarah-123",
    "video_id": "video-uuid-123",
    "interaction_type": "click_product",
    "video_time_seconds": 4500,
    "runtime_mode": "auto_adaptive",
    "product_id": "product-uuid-456",
    "device_type": "mobile",
    "location_lat": 37.7749,
    "location_lon": -122.4194,
    "metadata": {
      "came_from_beacon": true,
      "eta_minutes_remaining": 2
    }
  }'
```

### Response

```json
{
  "interaction_id": "interaction-uuid-555",
  "status": "logged"
}
```

---

## Example 7: Log Purchase (Conversion!)

### Request: User bought the Superman figure at Walmart

```bash
curl -X POST "http://localhost:8000/interactions" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-sarah-123",
    "video_id": "video-uuid-123",
    "interaction_type": "purchase",
    "product_id": "product-uuid-456",
    "purchase_amount": 29.99,
    "device_type": "mobile",
    "location_lat": 37.7750,
    "location_lon": -122.4195,
    "metadata": {
      "store_id": "walmart-sf-001",
      "receipt_id": "receipt-123456",
      "unlock_part_2": true
    }
  }'
```

### Response

```json
{
  "interaction_id": "interaction-uuid-777",
  "status": "logged"
}
```

**Result:**
- Video conversion count incremented
- Product purchase count incremented
- User unlocks Part 2 for the ride home
- Analytics updated with $29.99 revenue

---

## Example 8: Get Video Analytics

### Request: Check Superman video performance

```bash
curl -X GET "http://localhost:8000/analytics/videos/video-uuid-123"
```

### Response

```json
{
  "video_id": "video-uuid-123",
  "total_views": 1247,
  "unique_viewers": 983,
  "avg_watch_time_seconds": 2580,
  "completion_rate": 0.78,
  "total_conversions": 412,
  "total_revenue": 12354.88,
  "conversion_rate": 33.04,

  "runtime_mode_distribution": {
    "auto_adaptive": 892,
    "full_feature": 355
  },

  "top_products": [
    {
      "product_id": "product-uuid-456",
      "name": "Superman Action Figure",
      "clicks": 687,
      "price": 29.99
    }
  ],

  "persuasion_lift_by_target": {
    "parent": 2.3,
    "spouse_partner": 0.0,
    "manager": 0.0
  },

  "drive_to_store_rate": 0.76,
  "post_purchase_unlock_rate": 0.41
}
```

**Insights:**
- ✅ **33% conversion rate** (vs. industry standard ~2-3%)
- ✅ **76% arrival rate** (most viewers actually drove to store)
- ✅ **41% unlock rate** (bought product to get Part 2)
- ✅ **2.3× persuasion lift** for parent-targeted talking points

---

## Example 9: Platform Dashboard

### Request: Get overall Swiper metrics

```bash
curl -X GET "http://localhost:8000/analytics/dashboard"
```

### Response

```json
{
  "platform": "Swiper Adaptive Shoppable Video",
  "timestamp": "2025-01-15T14:30:00Z",

  "overview": {
    "total_videos": 127,
    "total_products": 456,
    "total_views": 47839,
    "total_conversions": 12456,
    "total_revenue_usd": 387456.78,
    "avg_conversion_rate_pct": 26.04
  },

  "premium_beacons": {
    "total_beacon_videos": 23,
    "total_beacon_sessions": 8934,
    "avg_beacon_session_length_min": 42
  },

  "format_distribution": {
    "short_form": 45,
    "medium_form": 58,
    "long_form": 19,
    "adaptive": 5
  },

  "personalization": {
    "rules_stage_videos": 89,
    "bandits_stage_videos": 32,
    "generative_stage_videos": 6
  },

  "top_categories": [
    {"category": "toys", "products": 123},
    {"category": "electronics", "products": 87},
    {"category": "home_goods", "products": 65}
  ]
}
```

---

## Example 10: Retailer Performance

### Request: Check Walmart's ROI

```bash
curl -X GET "http://localhost:8000/retailers/walmart-123/performance"
```

### Response

```json
{
  "retailer_id": "walmart-123",
  "name": "Walmart",
  "videos_sponsored": 12,
  "total_views": 15678,
  "total_conversions": 4234,
  "total_revenue_usd": 126789.45,
  "conversion_rate_pct": 27.00,
  "revenue_share_pct": 15.0,
  "retailer_payout_usd": 19018.42
}
```

**Walmart's Return:**
- Invested: $50,000/month ad spend
- Generated: $126,789 in sales
- **ROI: 2.5× return**
- Plus: 15,678 store visits driven by Premium Beacons

---

## Python SDK Example

```python
import requests

class SwiperClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def create_premium_beacon(
        self,
        title: str,
        retailer_id: str,
        base_duration_min: int = 90,
        geofence_meters: int = 5000
    ):
        """Create a Premium Beacon video"""
        response = requests.post(
            f"{self.base_url}/videos",
            json={
                "title": title,
                "format": "long_form",
                "base_duration_seconds": base_duration_min * 60,
                "min_duration_seconds": base_duration_min * 60 * 0.3,
                "max_duration_seconds": base_duration_min * 60 * 1.3,
                "is_premium_beacon": True,
                "beacon_type": "drive_to_store",
                "location_radius_meters": geofence_meters,
                "retailer_id": retailer_id,
                # ... other required fields
            }
        )
        return response.json()

    def play_adaptive_video(
        self,
        video_id: str,
        user_lat: float,
        user_lon: float,
        eta_minutes: int,
        household_type: str = "family_with_kids"
    ):
        """Get adaptive playback configuration"""
        response = requests.post(
            f"{self.base_url}/videos/play",
            json={
                "video_id": video_id,
                "runtime_mode": "auto_adaptive",
                "location_lat": user_lat,
                "location_lon": user_lon,
                "eta_minutes": eta_minutes,
                "household_type": household_type
            }
        )
        return response.json()

# Usage
client = SwiperClient()

# Create video
video = client.create_premium_beacon(
    title="Batman Adventure",
    retailer_id="walmart-123",
    base_duration_min=90
)

# Get adaptive playback
playback = client.play_adaptive_video(
    video_id=video["id"],
    user_lat=37.7749,
    user_lon=-122.4194,
    eta_minutes=45,
    household_type="family_with_kids"
)

print(f"Runtime adjusted to: {playback['runtime_seconds'] / 60} minutes")
print(f"Narrative arc: {playback['narrative_arc']['arc_id']}")
print(f"Persuasion points: {len(playback['persuasion_points'])}")
```

---

## JavaScript/React Example

```javascript
// Swiper React Integration

import React, { useState, useEffect } from 'react';

const SwiperPlayer = ({ videoId, userId, userLocation, etaMinutes }) => {
  const [playback, setPlayback] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get adaptive playback configuration
    fetch('http://localhost:8000/videos/play', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        video_id: videoId,
        user_id: userId,
        runtime_mode: 'auto_adaptive',
        location_lat: userLocation.lat,
        location_lon: userLocation.lon,
        eta_minutes: etaMinutes,
        device_type: 'mobile'
      })
    })
      .then(res => res.json())
      .then(data => {
        setPlayback(data);
        setLoading(false);
      });
  }, [videoId, userId, userLocation, etaMinutes]);

  const handleProductClick = (product) => {
    // Log interaction
    fetch('http://localhost:8000/interactions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        video_id: videoId,
        interaction_type: 'click_product',
        product_id: product.product_id
      })
    });

    // Redirect to buy URL
    window.open(product.buy_url, '_blank');
  };

  if (loading) return <div>Loading adaptive content...</div>;

  return (
    <div className="swiper-player">
      <video
        src={playback.playback_url}
        autoPlay
        controls
        style={{ width: '100%' }}
      />

      {/* Shoppable Product Overlays */}
      {playback.products.map(product => (
        <div
          key={product.product_id}
          className="product-overlay"
          style={{
            position: 'absolute',
            left: `${product.position.x}%`,
            top: `${product.position.y}%`,
            width: `${product.position.width}%`,
            height: `${product.position.height}%`
          }}
          onClick={() => handleProductClick(product)}
        >
          <button>{product.cta_text}</button>
          <span>${product.price}</span>
        </div>
      ))}

      {/* Premium Beacon Unlock Message */}
      {playback.is_beacon_session && (
        <div className="unlock-banner">
          {playback.unlock_condition}
        </div>
      )}

      {/* Metadata */}
      <div className="video-info">
        <p>Runtime: {Math.floor(playback.runtime_seconds / 60)} minutes</p>
        <p>Personalized for you using {playback.personalization_stage}</p>
      </div>
    </div>
  );
};

export default SwiperPlayer;
```

---

## Testing with cURL

### Complete workflow test

```bash
# 1. Create retailer
RETAILER=$(curl -s -X POST "http://localhost:8000/retailers" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Retailer"}' | jq -r '.id')

# 2. Create video
VIDEO=$(curl -s -X POST "http://localhost:8000/videos" \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Test Video\", \"format\": \"long_form\", \"base_duration_seconds\": 3600, \"gcs_bucket\": \"test\", \"gcs_path\": \"test\", \"cdn_url\": \"https://test.com\", \"is_premium_beacon\": true, \"retailer_id\": \"$RETAILER\"}" \
  | jq -r '.id')

# 3. Create product
PRODUCT=$(curl -s -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Test Product\", \"category\": \"toys\", \"price\": 19.99, \"retailer_id\": \"$RETAILER\", \"buy_url\": \"https://test.com\"}" \
  | jq -r '.id')

# 4. Add product overlay
curl -s -X POST "http://localhost:8000/products/overlays" \
  -H "Content-Type: application/json" \
  -d "{\"video_id\": \"$VIDEO\", \"product_id\": \"$PRODUCT\", \"start_time_seconds\": 100, \"end_time_seconds\": 200, \"position_x\": 50, \"position_y\": 50}" \
  | jq

# 5. Get adaptive playback
curl -s -X POST "http://localhost:8000/videos/play" \
  -H "Content-Type: application/json" \
  -d "{\"video_id\": \"$VIDEO\", \"runtime_mode\": \"auto_adaptive\", \"eta_minutes\": 30}" \
  | jq

# 6. Check analytics
curl -s -X GET "http://localhost:8000/analytics/videos/$VIDEO" | jq
```

---

## 🎉 Ready to Build!

These examples cover all major Swiper features:

1. ✅ **Premium Beacons** - Time-collapsing location-based movies
2. ✅ **Shoppable Overlays** - In-video product clicks
3. ✅ **Persuasion Layer** - Household-targeted talking points
4. ✅ **Adaptive Playback** - AI-personalized runtime & narrative
5. ✅ **Analytics** - Comprehensive performance metrics

**Next Steps:**
- Try the API locally: `python src/api/swiper.py`
- Visit docs: http://localhost:8000/docs
- Build your first Premium Beacon!

**Questions?** Check the [main documentation](swiper-platform.md) or open an issue.
