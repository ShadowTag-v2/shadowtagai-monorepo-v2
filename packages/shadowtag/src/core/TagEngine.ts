import type { ArtifactId, ShadowRef, Tag, TagSet } from "@shared/types";

export interface TagWrite {
  artifactId: ArtifactId;
  tags: Tag[];
  shadow?: ShadowRef;
  ts?: number; // ms epoch
}

export interface TagQuery {
  anyOf?: TagSet; // OR
  allOf?: TagSet; // AND
  not?: TagSet; // NOT
  textContains?: string; // optional text anchor search
  limit?: number;
  cursor?: string;
}

export interface TagResult {
  artifactId: ArtifactId;
  tags: Tag[];
  shadow?: ShadowRef;
  score?: number;
}

export interface TagEngine {
  put(input: TagWrite): Promise<void>;
  bulkPut(batch: TagWrite[]): Promise<void>;
  get(artifactId: ArtifactId): Promise<TagResult | null>;
  query(q: TagQuery): Promise<{ items: TagResult[]; nextCursor?: string }>;
  delete(artifactId: ArtifactId): Promise<void>;
}
