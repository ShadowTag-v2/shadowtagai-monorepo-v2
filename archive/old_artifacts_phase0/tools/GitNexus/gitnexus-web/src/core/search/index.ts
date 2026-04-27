/**
 * Search Module
 *
 * Exports BM25 indexing and hybrid search functionality.
 */

export {
  type BM25SearchResult,
  buildBM25Index,
  clearBM25Index,
  getBM25Stats,
  isBM25Ready,
  searchBM25,
} from './bm25-index';

export {
  formatHybridResults,
  type HybridSearchResult,
  isHybridSearchReady,
  mergeWithRRF,
} from './hybrid-search';
