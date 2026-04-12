import type { TextEncodingResult } from "./types";

/**
 * Text Encoding Module
 * Provides comprehensive text encoding/decoding functionality
 */

export class TextEncoder {
  /**
   * Encode text to Base64
   */
  static toBase64(text: string): TextEncodingResult {
    const buffer = Buffer.from(text, "utf-8");
    const encoded = buffer.toString("base64");

    return {
      encoded,
      originalLength: text.length,
      encodedLength: encoded.length,
      encoding: "base64",
    };
  }

  /**
   * Decode Base64 to text
   */
  static fromBase64(encoded: string): string {
    return Buffer.from(encoded, "base64").toString("utf-8");
  }

  /**
   * Encode text to Base64 URL-safe format
   */
  static toBase64Url(text: string): TextEncodingResult {
    const buffer = Buffer.from(text, "utf-8");
    const base64 = buffer.toString("base64");
    const encoded = base64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "");

    return {
      encoded,
      originalLength: text.length,
      encodedLength: encoded.length,
      encoding: "base64url",
    };
  }

  /**
   * Decode Base64 URL-safe format to text
   */
  static fromBase64Url(encoded: string): string {
    let base64 = encoded.replace(/-/g, "+").replace(/_/g, "/");

    // Add padding
    while (base64.length % 4) {
      base64 += "=";
    }

    return Buffer.from(base64, "base64").toString("utf-8");
  }

  /**
   * Encode text to hexadecimal
   */
  static toHex(text: string): TextEncodingResult {
    const buffer = Buffer.from(text, "utf-8");
    const encoded = buffer.toString("hex");

    return {
      encoded,
      originalLength: text.length,
      encodedLength: encoded.length,
      encoding: "hex",
    };
  }

  /**
   * Decode hexadecimal to text
   */
  static fromHex(encoded: string): string {
    return Buffer.from(encoded, "hex").toString("utf-8");
  }

  /**
   * URL encode text (percent encoding)
   */
  static urlEncode(text: string): TextEncodingResult {
    const encoded = encodeURIComponent(text);

    return {
      encoded,
      originalLength: text.length,
      encodedLength: encoded.length,
      encoding: "url",
    };
  }

  /**
   * URL decode text
   */
  static urlDecode(encoded: string): string {
    return decodeURIComponent(encoded);
  }

  /**
   * Encode text to binary string (0s and 1s)
   */
  static toBinary(text: string): TextEncodingResult {
    const buffer = Buffer.from(text, "utf-8");
    const encoded = Array.from(buffer)
      .map((byte) => byte.toString(2).padStart(8, "0"))
      .join("");

    return {
      encoded,
      originalLength: text.length,
      encodedLength: encoded.length,
      encoding: "binary",
    };
  }

  /**
   * Decode binary string to text
   */
  static fromBinary(encoded: string): string {
    const bytes = encoded.match(/.{8}/g) || [];
    const buffer = Buffer.from(bytes.map((byte) => parseInt(byte, 2)));
    return buffer.toString("utf-8");
  }

  /**
   * Encode text to ASCII values (comma-separated)
   */
  static toAscii(text: string): TextEncodingResult {
    const encoded = Array.from(text)
      .map((char) => char.charCodeAt(0))
      .join(",");

    return {
      encoded,
      originalLength: text.length,
      encodedLength: encoded.length,
      encoding: "ascii",
    };
  }

  /**
   * Decode ASCII values to text
   */
  static fromAscii(encoded: string): string {
    return encoded
      .split(",")
      .map((code) => String.fromCharCode(parseInt(code, 10)))
      .join("");
  }

  /**
   * Encode text to UTF-8 bytes (comma-separated)
   */
  static toUtf8Bytes(text: string): TextEncodingResult {
    const buffer = Buffer.from(text, "utf-8");
    const encoded = Array.from(buffer).join(",");

    return {
      encoded,
      originalLength: text.length,
      encodedLength: encoded.length,
      encoding: "utf8-bytes",
    };
  }

  /**
   * Decode UTF-8 bytes to text
   */
  static fromUtf8Bytes(encoded: string): string {
    const bytes = encoded.split(",").map((b) => parseInt(b, 10));
    return Buffer.from(bytes).toString("utf-8");
  }

  /**
   * HTML entity encode
   */
  static toHtmlEntities(text: string): TextEncodingResult {
    const encoded = text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");

    return {
      encoded,
      originalLength: text.length,
      encodedLength: encoded.length,
      encoding: "html-entities",
    };
  }

  /**
   * HTML entity decode
   */
  static fromHtmlEntities(encoded: string): string {
    return encoded
      .replace(/&amp;/g, "&")
      .replace(/&lt;/g, "<")
      .replace(/&gt;/g, ">")
      .replace(/&quot;/g, '"')
      .replace(/&#39;/g, "'");
  }

  /**
   * ROT13 encode/decode (cipher)
   */
  static rot13(text: string): TextEncodingResult {
    const encoded = text.replace(/[a-zA-Z]/g, (char) => {
      const start = char <= "Z" ? 65 : 97;
      return String.fromCharCode(((char.charCodeAt(0) - start + 13) % 26) + start);
    });

    return {
      encoded,
      originalLength: text.length,
      encodedLength: encoded.length,
      encoding: "rot13",
    };
  }

  /**
   * Encode to data URI
   */
  static toDataUri(text: string, mimeType: string = "text/plain"): string {
    const base64 = Buffer.from(text, "utf-8").toString("base64");
    return `data:${mimeType};base64,${base64}`;
  }

  /**
   * Decode from data URI
   */
  static fromDataUri(dataUri: string): { data: string; mimeType: string } {
    const matches = dataUri.match(/^data:([^;]+);base64,(.+)$/);
    if (!matches) {
      throw new Error("Invalid data URI format");
    }

    return {
      mimeType: matches[1],
      data: Buffer.from(matches[2], "base64").toString("utf-8"),
    };
  }
}

// Convenience functions for quick access
export const toBase64 = TextEncoder.toBase64;
export const fromBase64 = TextEncoder.fromBase64;
export const toBase64Url = TextEncoder.toBase64Url;
export const fromBase64Url = TextEncoder.fromBase64Url;
export const toHex = TextEncoder.toHex;
export const fromHex = TextEncoder.fromHex;
export const urlEncode = TextEncoder.urlEncode;
export const urlDecode = TextEncoder.urlDecode;
export const toBinary = TextEncoder.toBinary;
export const fromBinary = TextEncoder.fromBinary;
export const toAscii = TextEncoder.toAscii;
export const fromAscii = TextEncoder.fromAscii;
export const toUtf8Bytes = TextEncoder.toUtf8Bytes;
export const fromUtf8Bytes = TextEncoder.fromUtf8Bytes;
export const toHtmlEntities = TextEncoder.toHtmlEntities;
export const fromHtmlEntities = TextEncoder.fromHtmlEntities;
export const rot13 = TextEncoder.rot13;
export const toDataUri = TextEncoder.toDataUri;
export const fromDataUri = TextEncoder.fromDataUri;
