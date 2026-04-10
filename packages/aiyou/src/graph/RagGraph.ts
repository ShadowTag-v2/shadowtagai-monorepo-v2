import { ArtifactId, Vector, EmbeddingRef, TagSet } from "@shared/types";

export type NodeId = string;
export type Edge = { from: NodeId; to: NodeId; rel: "cites"|"derives"|"mentions"|"duplicates"; weight?: number };

export interface InsertDoc {
  artifactId: ArtifactId;
  text: string;
  tags?: TagSet;
  embed?: Vector | EmbeddingRef;
}

export interface RetrieveQuery {
  q: string;
  k?: number;
  filter?: TagSet;      // delegates to ShadowTag for fast filtering
}

export interface RetrieveHit {
  artifactId: ArtifactId;
  snippet: string;
  score: number;
  tags: TagSet;
}

export interface RagGraph {
  insert(doc: InsertDoc): Promise<void>;
  link(edges: Edge[]): Promise<void>;
  retrieve(query: RetrieveQuery): Promise<RetrieveHit[]>;
}
