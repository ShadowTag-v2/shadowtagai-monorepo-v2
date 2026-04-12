//! TinyUfo-based caching layer for HLS segments
//!
//! TinyUfo provides O(1) lookup with adaptive eviction,
//! better than LRU for streaming workloads.

use bytes::Bytes;
use std::sync::Arc;
use std::time::{Duration, Instant};
use tinyufo::TinyUfo;
use tracing::{debug, info};

use crate::{MediaEdgeError, Result};

/// Cached entry with TTL tracking
#[derive(Clone)]
pub struct CacheEntry {
    pub data: Bytes,
    pub content_type: String,
    pub inserted_at: Instant,
    pub size_bytes: usize,
}

/// TinyUfo-based media cache
pub struct MediaCache {
    cache: TinyUfo<String, CacheEntry>,
    ttl: Duration,
    max_size_bytes: usize,
    segment_ttl: Duration,
    playlist_ttl: Duration,
}

impl MediaCache {
    /// Create a new cache with specified capacity
    ///
    /// # Arguments
    /// * `capacity_mb` - Maximum cache size in megabytes
    /// * `ttl_seconds` - Default TTL for cached entries
    pub fn new(capacity_mb: usize, ttl_seconds: u64) -> Self {
        // Estimate ~100KB per HLS segment average
        let estimated_entries = (capacity_mb * 1024) / 100;
        let max_size_bytes = capacity_mb * 1024 * 1024;

        info!(
            capacity_mb = capacity_mb,
            estimated_entries = estimated_entries,
            "Initializing TinyUfo cache"
        );

        Self {
            cache: TinyUfo::new(estimated_entries, estimated_entries),
            ttl: Duration::from_secs(ttl_seconds),
            max_size_bytes,
            segment_ttl: Duration::from_secs(86400), // 24 hours for segments
            playlist_ttl: Duration::from_secs(3600), // 1 hour for playlists
        }
    }

    /// Get TTL based on content type
    fn get_ttl_for_path(&self, path: &str) -> Duration {
        if path.ends_with(".m3u8") {
            self.playlist_ttl
        } else if path.ends_with(".ts") || path.ends_with(".m4s") {
            self.segment_ttl
        } else {
            self.ttl
        }
    }

    /// Get an entry from cache
    ///
    /// Returns None if not found or expired
    pub fn get(&self, key: &str) -> Option<(Bytes, String)> {
        let ttl = self.get_ttl_for_path(key);

        self.cache.get(&key.to_string()).and_then(|entry| {
            if entry.inserted_at.elapsed() < ttl {
                debug!(key = key, "Cache HIT");
                Some((entry.data.clone(), entry.content_type.clone()))
            } else {
                debug!(key = key, "Cache EXPIRED");
                None
            }
        })
    }

    /// Insert an entry into the cache
    pub fn insert(&self, key: String, data: Bytes, content_type: String) {
        let size_bytes = data.len();

        let entry = CacheEntry {
            data,
            content_type,
            inserted_at: Instant::now(),
            size_bytes,
        };

        // Weight based on size (1 weight unit = ~10KB)
        let weight = std::cmp::max(1, size_bytes / 10240);

        debug!(
            key = key,
            size_bytes = size_bytes,
            weight = weight,
            "Cache INSERT"
        );

        self.cache.put(key, entry, weight);
    }

    /// Check if key exists (without checking expiration)
    pub fn contains(&self, key: &str) -> bool {
        self.cache.get(&key.to_string()).is_some()
    }

    /// Get cache statistics
    pub fn stats(&self) -> CacheStats {
        CacheStats {
            max_size_bytes: self.max_size_bytes,
            ttl_seconds: self.ttl.as_secs(),
            segment_ttl_seconds: self.segment_ttl.as_secs(),
            playlist_ttl_seconds: self.playlist_ttl.as_secs(),
        }
    }
}

/// Cache statistics for monitoring
#[derive(Debug, Clone)]
pub struct CacheStats {
    pub max_size_bytes: usize,
    pub ttl_seconds: u64,
    pub segment_ttl_seconds: u64,
    pub playlist_ttl_seconds: u64,
}

/// Thread-safe cache handle
pub type CacheHandle = Arc<MediaCache>;

/// Create a new cache handle
pub fn create_cache(capacity_mb: usize, ttl_seconds: u64) -> CacheHandle {
    Arc::new(MediaCache::new(capacity_mb, ttl_seconds))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cache_insert_get() {
        let cache = MediaCache::new(1, 3600);
        let data = Bytes::from("test data");

        cache.insert(
            "test.ts".to_string(),
            data.clone(),
            "video/mp2t".to_string(),
        );

        let result = cache.get("test.ts");
        assert!(result.is_some());

        let (cached_data, content_type) = result.unwrap();
        assert_eq!(cached_data, data);
        assert_eq!(content_type, "video/mp2t");
    }

    #[test]
    fn test_cache_miss() {
        let cache = MediaCache::new(1, 3600);
        let result = cache.get("nonexistent.ts");
        assert!(result.is_none());
    }
}
