export type ArtifactId = string; // ULIDs
export type TagKey = string; // e.g. "origin/source", "pii", "topic"
export type TagValue = string | number | boolean | string[];

export type Tag = { key: TagKey; value: TagValue; confidence?: number };
export type TagSet = Record<TagKey, TagValue>;

export type Vector = Float32Array;
export type EmbeddingRef = { dim: number; provider: string; id: string };

export type Span = { start: number; end: number }; // byte offsets for text
export type ShadowRef = {
  artifactId: ArtifactId;
  spans?: Span[]; // optional precise anchors
  hash: string; // content hash for integrity
};

export type MetricCounter = (name: string, tags?: Record<string, string>) => void;
export type MetricTimer = <T>(name: string, f: () => Promise<T>) => Promise<T>;
