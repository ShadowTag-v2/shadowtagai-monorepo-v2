import type { SerializationOptions, SerializationResult } from './types';

/**
 * Data Serialization Module
 * Provides comprehensive data serialization and deserialization functionality
 */

export class DataSerializer {
  /**
   * Serialize to JSON
   */
  static toJson<T = any>(data: T, options: SerializationOptions = {}): SerializationResult {
    const { pretty = false } = options;
    const jsonString = pretty ? JSON.stringify(data, null, 2) : JSON.stringify(data);

    return {
      data: jsonString,
      format: 'json',
      size: Buffer.byteLength(jsonString, 'utf-8'),
    };
  }

  /**
   * Deserialize from JSON
   */
  static fromJson<T = any>(jsonString: string): T {
    return JSON.parse(jsonString);
  }

  /**
   * Serialize to JSON Buffer
   */
  static toJsonBuffer<T = any>(data: T, options: SerializationOptions = {}): SerializationResult {
    const { pretty = false } = options;
    const jsonString = pretty ? JSON.stringify(data, null, 2) : JSON.stringify(data);
    const buffer = Buffer.from(jsonString, 'utf-8');

    return {
      data: buffer,
      format: 'json',
      size: buffer.length,
    };
  }

  /**
   * Deserialize from JSON Buffer
   */
  static fromJsonBuffer<T = any>(buffer: Buffer): T {
    return JSON.parse(buffer.toString('utf-8'));
  }

  /**
   * Serialize to Binary (using Node.js Buffer)
   */
  static toBinary(data: unknown): SerializationResult {
    let buffer: Buffer;

    if (Buffer.isBuffer(data)) {
      buffer = data;
    } else if (typeof data === 'string') {
      buffer = Buffer.from(data, 'utf-8');
    } else if (ArrayBuffer.isView(data)) {
      buffer = Buffer.from(data.buffer, data.byteOffset, data.byteLength);
    } else {
      // For objects, serialize to JSON first, then to buffer
      const jsonString = JSON.stringify(data);
      buffer = Buffer.from(jsonString, 'utf-8');
    }

    return {
      data: buffer,
      format: 'binary',
      size: buffer.length,
    };
  }

  /**
   * Deserialize from Binary
   */
  static fromBinary<T = any>(buffer: Buffer, parseJson: boolean = false): T | string {
    const str = buffer.toString('utf-8');
    return parseJson ? JSON.parse(str) : (str as any);
  }

  /**
   * Serialize to CBOR-like format (custom binary encoding)
   */
  static toCBOR(data: unknown): SerializationResult {
    // Simple CBOR-like implementation for basic types
    const buffer = DataSerializer.encodeCBOR(data);

    return {
      data: buffer,
      format: 'cbor',
      size: buffer.length,
    };
  }

  private static encodeCBOR(data: unknown): Buffer {
    const buffers: Buffer[] = [];

    const encode = (value: unknown) => {
      if (value === null) {
        buffers.push(Buffer.from([0xf6])); // null
      } else if (value === undefined) {
        buffers.push(Buffer.from([0xf7])); // undefined
      } else if (typeof value === 'boolean') {
        buffers.push(Buffer.from([value ? 0xf5 : 0xf4])); // true/false
      } else if (typeof value === 'number') {
        if (Number.isInteger(value) && value >= 0 && value < 24) {
          buffers.push(Buffer.from([value]));
        } else {
          const buf = Buffer.allocUnsafe(9);
          buf.writeUInt8(0x1b, 0);
          buf.writeDoubleBE(value, 1);
          buffers.push(buf);
        }
      } else if (typeof value === 'string') {
        const strBuf = Buffer.from(value, 'utf-8');
        const lenBuf = Buffer.allocUnsafe(5);
        lenBuf.writeUInt8(0x78, 0);
        lenBuf.writeUInt32BE(strBuf.length, 1);
        buffers.push(lenBuf, strBuf);
      } else if (Array.isArray(value)) {
        const lenBuf = Buffer.allocUnsafe(5);
        lenBuf.writeUInt8(0x98, 0);
        lenBuf.writeUInt32BE(value.length, 1);
        buffers.push(lenBuf);
        value.forEach(encode);
      } else if (typeof value === 'object') {
        const keys = Object.keys(value);
        const lenBuf = Buffer.allocUnsafe(5);
        lenBuf.writeUInt8(0xb8, 0);
        lenBuf.writeUInt32BE(keys.length, 1);
        buffers.push(lenBuf);
        keys.forEach((key) => {
          encode(key);
          encode(value[key]);
        });
      }
    };

    encode(data);
    return Buffer.concat(buffers);
  }

  /**
   * Serialize to URL Query String
   */
  static toQueryString(data: Record<string, any>): SerializationResult {
    const params = new URLSearchParams();

    Object.entries(data).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        if (Array.isArray(value)) {
          value.forEach((v) => params.append(key, String(v)));
        } else if (typeof value === 'object') {
          params.append(key, JSON.stringify(value));
        } else {
          params.append(key, String(value));
        }
      }
    });

    const queryString = params.toString();

    return {
      data: queryString,
      format: 'query-string',
      size: Buffer.byteLength(queryString, 'utf-8'),
    };
  }

  /**
   * Deserialize from URL Query String
   */
  static fromQueryString(queryString: string): Record<string, any> {
    const params = new URLSearchParams(queryString);
    const result: Record<string, any> = {};

    params.forEach((value, key) => {
      if (result[key]) {
        // Handle multiple values
        if (Array.isArray(result[key])) {
          result[key].push(value);
        } else {
          result[key] = [result[key], value];
        }
      } else {
        // Try to parse as JSON if it looks like an object
        if (value.startsWith('{') || value.startsWith('[')) {
          try {
            result[key] = JSON.parse(value);
          } catch {
            result[key] = value;
          }
        } else {
          result[key] = value;
        }
      }
    });

    return result;
  }

  /**
   * Serialize to Form Data
   */
  static toFormData(data: Record<string, any>): SerializationResult {
    const formData: string[] = [];

    Object.entries(data).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        const encodedKey = encodeURIComponent(key);
        if (Array.isArray(value)) {
          value.forEach((v) => {
            formData.push(`${encodedKey}=${encodeURIComponent(String(v))}`);
          });
        } else if (typeof value === 'object') {
          formData.push(`${encodedKey}=${encodeURIComponent(JSON.stringify(value))}`);
        } else {
          formData.push(`${encodedKey}=${encodeURIComponent(String(value))}`);
        }
      }
    });

    const formString = formData.join('&');

    return {
      data: formString,
      format: 'form-data',
      size: Buffer.byteLength(formString, 'utf-8'),
    };
  }

  /**
   * Deserialize from Form Data
   */
  static fromFormData(formString: string): Record<string, any> {
    return DataSerializer.fromQueryString(formString);
  }

  /**
   * Serialize to CSV
   */
  static toCsv(data: Array<Record<string, any>>, headers?: string[]): SerializationResult {
    if (!data || data.length === 0) {
      return {
        data: '',
        format: 'csv',
        size: 0,
      };
    }

    const csvHeaders = headers || Object.keys(data[0]);
    const csvRows: string[] = [];

    // Add header row
    csvRows.push(csvHeaders.map((h) => DataSerializer.escapeCsvValue(h)).join(','));

    // Add data rows
    data.forEach((row) => {
      const values = csvHeaders.map((header) => {
        const value = row[header];
        return DataSerializer.escapeCsvValue(value);
      });
      csvRows.push(values.join(','));
    });

    const csvString = csvRows.join('\n');

    return {
      data: csvString,
      format: 'csv',
      size: Buffer.byteLength(csvString, 'utf-8'),
    };
  }

  private static escapeCsvValue(value: unknown): string {
    if (value === null || value === undefined) {
      return '';
    }

    const str = String(value);

    // If the value contains comma, quote, or newline, wrap in quotes and escape quotes
    if (str.includes(',') || str.includes('"') || str.includes('\n')) {
      return `"${str.replace(/"/g, '""')}"`;
    }

    return str;
  }

  /**
   * Deserialize from CSV
   */
  static fromCsv(csvString: string): Array<Record<string, any>> {
    const lines = csvString.split('\n').filter((line) => line.trim());
    if (lines.length === 0) {
      return [];
    }

    const headers = DataSerializer.parseCsvLine(lines[0]);
    const result: Array<Record<string, any>> = [];

    for (let i = 1; i < lines.length; i++) {
      const values = DataSerializer.parseCsvLine(lines[i]);
      const row: Record<string, any> = {};

      headers.forEach((header, index) => {
        row[header] = values[index] || '';
      });

      result.push(row);
    }

    return result;
  }

  private static parseCsvLine(line: string): string[] {
    const result: string[] = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      const nextChar = line[i + 1];

      if (char === '"') {
        if (inQuotes && nextChar === '"') {
          current += '"';
          i++; // Skip next quote
        } else {
          inQuotes = !inQuotes;
        }
      } else if (char === ',' && !inQuotes) {
        result.push(current);
        current = '';
      } else {
        current += char;
      }
    }

    result.push(current);
    return result;
  }

  /**
   * Serialize to XML (simple implementation)
   */
  static toXml(data: unknown, rootElement: string = 'root'): SerializationResult {
    const xmlString = DataSerializer.objectToXml(data, rootElement);

    return {
      data: xmlString,
      format: 'xml',
      size: Buffer.byteLength(xmlString, 'utf-8'),
    };
  }

  private static objectToXml(obj: unknown, rootName: string): string {
    const encode = (val: unknown, name: string): string => {
      if (val === null || val === undefined) {
        return `<${name} />`;
      } else if (Array.isArray(val)) {
        return val.map((item) => encode(item, 'item')).join('');
      } else if (typeof val === 'object') {
        const inner = Object.entries(val)
          .map(([k, v]) => encode(v, k))
          .join('');
        return `<${name}>${inner}</${name}>`;
      } else {
        const escaped = String(val)
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;')
          .replace(/'/g, '&apos;');
        return `<${name}>${escaped}</${name}>`;
      }
    };

    return `<?xml version="1.0" encoding="UTF-8"?>${encode(obj, rootName)}`;
  }

  /**
   * Clone object (deep copy)
   */
  static clone<T>(data: T): T {
    return JSON.parse(JSON.stringify(data));
  }

  /**
   * Compare two objects for equality
   */
  static equals(a: unknown, b: unknown): boolean {
    return JSON.stringify(a) === JSON.stringify(b);
  }
}

// Convenience functions
export const toJson = DataSerializer.toJson;
export const fromJson = DataSerializer.fromJson;
export const toJsonBuffer = DataSerializer.toJsonBuffer;
export const fromJsonBuffer = DataSerializer.fromJsonBuffer;
// Note: toBinary and fromBinary are not exported to avoid naming conflicts with text-encoding module
// Use DataSerializer.toBinary and DataSerializer.fromBinary instead
export const toCBOR = DataSerializer.toCBOR;
export const toQueryString = DataSerializer.toQueryString;
export const fromQueryString = DataSerializer.fromQueryString;
export const toFormData = DataSerializer.toFormData;
export const fromFormData = DataSerializer.fromFormData;
export const toCsv = DataSerializer.toCsv;
export const fromCsv = DataSerializer.fromCsv;
export const toXml = DataSerializer.toXml;
export const cloneData = DataSerializer.clone;
export const dataEquals = DataSerializer.equals;
