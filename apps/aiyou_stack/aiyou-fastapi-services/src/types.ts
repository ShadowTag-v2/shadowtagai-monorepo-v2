// Type definitions for encoding services
export interface EncodingOptions {
  encoding?: 'utf-8' | 'ascii' | 'base64' | 'hex' | 'binary';
}

export interface ImageEncodingOptions {
  format?: 'jpeg' | 'png' | 'webp' | 'avif' | 'gif';
  quality?: number;
  width?: number;
  height?: number;
  fit?: 'cover' | 'contain' | 'fill' | 'inside' | 'outside';
}

export interface SerializationOptions {
  format?: 'json' | 'binary' | 'msgpack';
  pretty?: boolean;
}

export interface TextEncodingResult {
  encoded: string;
  originalLength: number;
  encodedLength: number;
  encoding: string;
}

export interface ImageEncodingResult {
  data: Buffer;
  format: string;
  width: number;
  height: number;
  size: number;
}

export interface SerializationResult {
  data: Buffer | string;
  format: string;
  size: number;
}
