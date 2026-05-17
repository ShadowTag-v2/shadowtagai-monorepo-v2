import sharp, { FormatEnum, type Sharp } from "sharp";
import type { ImageEncodingOptions, ImageEncodingResult } from "./types";

/**
 * Image Encoding Module
 * Provides comprehensive image encoding, format conversion, and manipulation
 */

export class ImageEncoder {
  /**
   * Convert image to a different format
   */
  static async convert(
    input: Buffer | string,
    options: ImageEncodingOptions = {},
  ): Promise<ImageEncodingResult> {
    const { format = "jpeg", quality = 80, width, height, fit = "cover" } = options;

    let pipeline: Sharp = sharp(input);

    // Resize if dimensions specified
    if (width || height) {
      pipeline = pipeline.resize(width, height, { fit });
    }

    // Convert to target format
    let outputBuffer: Buffer;
    switch (format) {
      case "jpeg":
        outputBuffer = await pipeline.jpeg({ quality }).toBuffer();
        break;
      case "png":
        outputBuffer = await pipeline.png({ quality }).toBuffer();
        break;
      case "webp":
        outputBuffer = await pipeline.webp({ quality }).toBuffer();
        break;
      case "avif":
        outputBuffer = await pipeline.avif({ quality }).toBuffer();
        break;
      case "gif":
        outputBuffer = await pipeline.gif().toBuffer();
        break;
      default:
        throw new Error(`Unsupported format: ${format}`);
    }

    // Get metadata
    const metadata = await sharp(outputBuffer).metadata();

    return {
      data: outputBuffer,
      format,
      width: metadata.width || 0,
      height: metadata.height || 0,
      size: outputBuffer.length,
    };
  }

  /**
   * Encode image to Base64 data URI
   */
  static async toBase64(
    input: Buffer | string,
    options: ImageEncodingOptions = {},
  ): Promise<string> {
    const result = await ImageEncoder.convert(input, options);
    const base64 = result.data.toString("base64");
    const mimeType = `image/${result.format}`;
    return `data:${mimeType};base64,${base64}`;
  }

  /**
   * Decode Base64 data URI to image buffer
   */
  static fromBase64(dataUri: string): Buffer {
    const matches = dataUri.match(/^data:image\/[a-z]+;base64,(.+)$/);
    if (!matches) {
      throw new Error("Invalid image data URI format");
    }
    return Buffer.from(matches[1], "base64");
  }

  /**
   * Optimize image (reduce file size while maintaining quality)
   */
  static async optimize(
    input: Buffer | string,
    targetFormat?: "jpeg" | "png" | "webp" | "avif",
  ): Promise<ImageEncodingResult> {
    const metadata = await sharp(input).metadata();
    const format = targetFormat || (metadata.format as any) || "jpeg";

    let pipeline = sharp(input);

    // Apply format-specific optimizations
    switch (format) {
      case "jpeg":
        pipeline = pipeline.jpeg({ quality: 85, progressive: true, mozjpeg: true });
        break;
      case "png":
        pipeline = pipeline.png({ compressionLevel: 9, progressive: true });
        break;
      case "webp":
        pipeline = pipeline.webp({ quality: 85, effort: 6 });
        break;
      case "avif":
        pipeline = pipeline.avif({ quality: 80, effort: 6 });
        break;
    }

    const outputBuffer = await pipeline.toBuffer();
    const outputMetadata = await sharp(outputBuffer).metadata();

    return {
      data: outputBuffer,
      format,
      width: outputMetadata.width || 0,
      height: outputMetadata.height || 0,
      size: outputBuffer.length,
    };
  }

  /**
   * Resize image
   */
  static async resize(
    input: Buffer | string,
    width?: number,
    height?: number,
    options: Partial<ImageEncodingOptions> = {},
  ): Promise<ImageEncodingResult> {
    return ImageEncoder.convert(input, { ...options, width, height });
  }

  /**
   * Create thumbnail
   */
  static async thumbnail(
    input: Buffer | string,
    size: number = 200,
    options: Partial<ImageEncodingOptions> = {},
  ): Promise<ImageEncodingResult> {
    return ImageEncoder.convert(input, {
      ...options,
      width: size,
      height: size,
      fit: "cover",
    });
  }

  /**
   * Convert to grayscale
   */
  static async grayscale(
    input: Buffer | string,
    options: Partial<ImageEncodingOptions> = {},
  ): Promise<ImageEncodingResult> {
    const pipeline = sharp(input).grayscale();
    const format = options.format || "jpeg";

    let outputBuffer: Buffer;
    switch (format) {
      case "jpeg":
        outputBuffer = await pipeline.jpeg({ quality: options.quality || 80 }).toBuffer();
        break;
      case "png":
        outputBuffer = await pipeline.png().toBuffer();
        break;
      case "webp":
        outputBuffer = await pipeline.webp({ quality: options.quality || 80 }).toBuffer();
        break;
      default:
        outputBuffer = await pipeline.toBuffer();
    }

    const metadata = await sharp(outputBuffer).metadata();

    return {
      data: outputBuffer,
      format,
      width: metadata.width || 0,
      height: metadata.height || 0,
      size: outputBuffer.length,
    };
  }

  /**
   * Rotate image
   */
  static async rotate(
    input: Buffer | string,
    angle: number,
    options: Partial<ImageEncodingOptions> = {},
  ): Promise<ImageEncodingResult> {
    const pipeline = sharp(input).rotate(angle);
    const format = options.format || "jpeg";

    let outputBuffer: Buffer;
    switch (format) {
      case "jpeg":
        outputBuffer = await pipeline.jpeg({ quality: options.quality || 80 }).toBuffer();
        break;
      case "png":
        outputBuffer = await pipeline.png().toBuffer();
        break;
      case "webp":
        outputBuffer = await pipeline.webp({ quality: options.quality || 80 }).toBuffer();
        break;
      default:
        outputBuffer = await pipeline.toBuffer();
    }

    const metadata = await sharp(outputBuffer).metadata();

    return {
      data: outputBuffer,
      format,
      width: metadata.width || 0,
      height: metadata.height || 0,
      size: outputBuffer.length,
    };
  }

  /**
   * Get image metadata
   */
  static async getMetadata(input: Buffer | string): Promise<sharp.Metadata> {
    return await sharp(input).metadata();
  }

  /**
   * Batch convert multiple images
   */
  static async batchConvert(
    inputs: (Buffer | string)[],
    options: ImageEncodingOptions = {},
  ): Promise<ImageEncodingResult[]> {
    return Promise.all(inputs.map((input) => ImageEncoder.convert(input, options)));
  }
}

// Convenience functions
export const convertImage = ImageEncoder.convert;
export const imageToBase64 = ImageEncoder.toBase64;
export const imageFromBase64 = ImageEncoder.fromBase64;
export const optimizeImage = ImageEncoder.optimize;
export const resizeImage = ImageEncoder.resize;
export const createThumbnail = ImageEncoder.thumbnail;
export const grayscaleImage = ImageEncoder.grayscale;
export const rotateImage = ImageEncoder.rotate;
export const getImageMetadata = ImageEncoder.getMetadata;
export const batchConvertImages = ImageEncoder.batchConvert;
