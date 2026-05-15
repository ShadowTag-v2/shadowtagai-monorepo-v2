/**
 * AI You - Comprehensive Encoding Services
 *
 * A complete encoding library for Node.js/TypeScript with support for:
 * - Text encoding (Base64, URL, Hex, Binary, ASCII, HTML entities, ROT13, Data URIs)
 * - Image encoding (JPEG, PNG, WebP, AVIF, GIF conversion and manipulation)
 * - Data serialization (JSON, Binary, CBOR, Query Strings, Form Data, CSV, XML)
 *
 * @packageDocumentation
 */

// Export data serialization
export * from './data-serialization';
// Export image encoding
export * from './image-encoding';
// Export text encoding
export * from './text-encoding';
// Export all types
export * from './types';

import { DataSerializer } from './data-serialization';
import { ImageEncoder } from './image-encoding';
// Import classes for unified API
import { TextEncoder } from './text-encoding';

/**
 * Unified Encoding Service
 * Provides a single entry point for all encoding operations
 */
export class EncodingService {
  /**
   * Text encoding utilities
   */
  static readonly text = TextEncoder;

  /**
   * Image encoding utilities
   */
  static readonly image = ImageEncoder;

  /**
   * Data serialization utilities
   */
  static readonly data = DataSerializer;

  /**
   * Quick encode to Base64
   */
  static toBase64(input: string | Buffer): string {
    if (typeof input === 'string') {
      return TextEncoder.toBase64(input).encoded;
    }
    return input.toString('base64');
  }

  /**
   * Quick decode from Base64
   */
  static fromBase64(encoded: string, asBuffer: boolean = false): string | Buffer {
    if (asBuffer) {
      return Buffer.from(encoded, 'base64');
    }
    return TextEncoder.fromBase64(encoded);
  }

  /**
   * Quick URL encode
   */
  static urlEncode(text: string): string {
    return TextEncoder.urlEncode(text).encoded;
  }

  /**
   * Quick URL decode
   */
  static urlDecode(encoded: string): string {
    return TextEncoder.urlDecode(encoded);
  }

  /**
   * Quick JSON stringify
   */
  static toJson(data: unknown, pretty: boolean = false): string {
    return DataSerializer.toJson(data, { pretty }).data as string;
  }

  /**
   * Quick JSON parse
   */
  static fromJson<T = any>(json: string): T {
    return DataSerializer.fromJson<T>(json);
  }

  /**
   * Get version info
   */
  static getVersion(): string {
    return '1.0.0';
  }

  /**
   * Get available encoders
   */
  static getEncoders(): {
    text: string[];
    image: string[];
    data: string[];
  } {
    return {
      text: [
        'base64',
        'base64url',
        'hex',
        'binary',
        'ascii',
        'utf8-bytes',
        'url',
        'html-entities',
        'rot13',
        'data-uri',
      ],
      image: ['jpeg', 'png', 'webp', 'avif', 'gif'],
      data: ['json', 'binary', 'cbor', 'query-string', 'form-data', 'csv', 'xml'],
    };
  }
}

/**
 * Default export for convenience
 */
export default EncodingService;

/**
 * Version of the encoding service
 */
export const VERSION = '1.0.0';

/**
 * Quick access to commonly used functions
 */
export const encode = {
  text: {
    toBase64: TextEncoder.toBase64,
    toHex: TextEncoder.toHex,
    toUrl: TextEncoder.urlEncode,
    toBinary: TextEncoder.toBinary,
  },
  data: {
    toJson: DataSerializer.toJson,
    toCsv: DataSerializer.toCsv,
    toXml: DataSerializer.toXml,
  },
  image: {
    convert: ImageEncoder.convert,
    optimize: ImageEncoder.optimize,
    resize: ImageEncoder.resize,
  },
};

export const decode = {
  text: {
    fromBase64: TextEncoder.fromBase64,
    fromHex: TextEncoder.fromHex,
    fromUrl: TextEncoder.urlDecode,
    fromBinary: TextEncoder.fromBinary,
  },
  data: {
    fromJson: DataSerializer.fromJson,
    fromCsv: DataSerializer.fromCsv,
  },
  image: {
    fromBase64: ImageEncoder.fromBase64,
  },
};
