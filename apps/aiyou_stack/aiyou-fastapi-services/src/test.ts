/**
 * Test suite for all encoding modules
 */

import { DataSerializer } from './data-serialization';
import { EncodingService } from './index';
import { TextEncoder } from './text-encoding';

// Simple test runner
function test(name: string, fn: () => void | Promise<void>) {
  return async () => {
    try {
      await fn();
      console.log(`✓ ${name}`);
      return true;
    } catch (error) {
      console.error(`✗ ${name}`);
      console.error(`  Error: ${error}`);
      return false;
    }
  };
}

function assert(condition: boolean, message: string = 'Assertion failed') {
  if (!condition) {
    throw new Error(message);
  }
}

function assertEquals(actual: unknown, expected: unknown, message?: string) {
  if (JSON.stringify(actual) !== JSON.stringify(expected)) {
    throw new Error(
      message || `Expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`,
    );
  }
}

// Test Text Encoding
const textEncodingTests = [
  test('Base64 encoding/decoding', () => {
    const input = 'Hello, World!';
    const result = TextEncoder.toBase64(input);
    assert(result.encoded === 'SGVsbG8sIFdvcmxkIQ==', 'Base64 encoding failed');
    const decoded = TextEncoder.fromBase64(result.encoded);
    assertEquals(decoded, input, 'Base64 decoding failed');
  }),

  test('Base64 URL-safe encoding/decoding', () => {
    const input = 'Hello, World! + / =';
    const result = TextEncoder.toBase64Url(input);
    assert(!result.encoded.includes('+'), 'URL-safe should not contain +');
    assert(!result.encoded.includes('/'), 'URL-safe should not contain /');
    const decoded = TextEncoder.fromBase64Url(result.encoded);
    assertEquals(decoded, input, 'Base64 URL decoding failed');
  }),

  test('Hex encoding/decoding', () => {
    const input = 'Hello';
    const result = TextEncoder.toHex(input);
    assert(result.encoded === '48656c6c6f', 'Hex encoding failed');
    const decoded = TextEncoder.fromHex(result.encoded);
    assertEquals(decoded, input, 'Hex decoding failed');
  }),

  test('URL encoding/decoding', () => {
    const input = 'Hello World! @#$%';
    const result = TextEncoder.urlEncode(input);
    assert(result.encoded.includes('%20') || result.encoded.includes('+'), 'URL encoding failed');
    const decoded = TextEncoder.urlDecode(result.encoded);
    assertEquals(decoded, input, 'URL decoding failed');
  }),

  test('Binary encoding/decoding', () => {
    const input = 'Hi';
    const result = TextEncoder.toBinary(input);
    assert(result.encoded.includes('0') && result.encoded.includes('1'), 'Binary encoding failed');
    const decoded = TextEncoder.fromBinary(result.encoded);
    assertEquals(decoded, input, 'Binary decoding failed');
  }),

  test('ASCII encoding/decoding', () => {
    const input = 'ABC';
    const result = TextEncoder.toAscii(input);
    assert(result.encoded === '65,66,67', 'ASCII encoding failed');
    const decoded = TextEncoder.fromAscii(result.encoded);
    assertEquals(decoded, input, 'ASCII decoding failed');
  }),

  test('HTML entities encoding/decoding', () => {
    const input = '<div>Hello & "World"</div>';
    const result = TextEncoder.toHtmlEntities(input);
    assert(result.encoded.includes('&lt;'), 'HTML entities encoding failed');
    assert(result.encoded.includes('&amp;'), 'HTML entities encoding failed');
    const decoded = TextEncoder.fromHtmlEntities(result.encoded);
    assertEquals(decoded, input, 'HTML entities decoding failed');
  }),

  test('ROT13 encoding', () => {
    const input = 'Hello';
    const result = TextEncoder.rot13(input);
    assert(result.encoded === 'Uryyb', 'ROT13 encoding failed');
    // ROT13 is symmetric
    const decoded = TextEncoder.rot13(result.encoded);
    assertEquals(decoded.encoded, input, 'ROT13 decoding failed');
  }),

  test('Data URI encoding/decoding', () => {
    const input = 'Hello, World!';
    const dataUri = TextEncoder.toDataUri(input, 'text/plain');
    assert(dataUri.startsWith('data:text/plain;base64,'), 'Data URI encoding failed');
    const decoded = TextEncoder.fromDataUri(dataUri);
    assertEquals(decoded.data, input, 'Data URI decoding failed');
    assertEquals(decoded.mimeType, 'text/plain', 'Data URI mime type failed');
  }),
];

// Test Data Serialization
const dataSerializationTests = [
  test('JSON serialization/deserialization', () => {
    const input = { name: 'John', age: 30, tags: ['a', 'b'] };
    const result = DataSerializer.toJson(input);
    assert(typeof result.data === 'string', 'JSON serialization failed');
    const decoded = DataSerializer.fromJson(result.data as string);
    assertEquals(decoded, input, 'JSON deserialization failed');
  }),

  test('JSON pretty print', () => {
    const input = { name: 'John' };
    const result = DataSerializer.toJson(input, { pretty: true });
    assert(result.data.includes('\n'), 'Pretty JSON should contain newlines');
  }),

  test('Query string serialization/deserialization', () => {
    const input = { name: 'John Doe', age: '30', tags: ['a', 'b'] };
    const result = DataSerializer.toQueryString(input);
    assert(result.data.includes('name=John'), 'Query string serialization failed');
    const decoded = DataSerializer.fromQueryString(result.data as string);
    assert(decoded.name === 'John Doe', 'Query string deserialization failed');
  }),

  test('CSV serialization/deserialization', () => {
    const input = [
      { name: 'John', age: 30 },
      { name: 'Jane', age: 25 },
    ];
    const result = DataSerializer.toCsv(input);
    assert(result.data.includes('name,age'), 'CSV should have headers');
    assert(result.data.includes('John'), 'CSV should have data');
    const decoded = DataSerializer.fromCsv(result.data as string);
    assertEquals(decoded.length, 2, 'CSV deserialization failed');
    assertEquals(decoded[0].name, 'John', 'CSV data mismatch');
  }),

  test('CSV with special characters', () => {
    const input = [{ name: 'John, Jr.', note: 'He said "hello"' }];
    const result = DataSerializer.toCsv(input);
    assert(result.data.includes('"'), 'CSV should escape special characters');
    const decoded = DataSerializer.fromCsv(result.data as string);
    assertEquals(decoded[0].name, 'John, Jr.', 'CSV special character handling failed');
  }),

  test('XML serialization', () => {
    const input = { person: { name: 'John', age: 30 } };
    const result = DataSerializer.toXml(input, 'root');
    assert(result.data.includes('<?xml'), 'XML should have declaration');
    assert(result.data.includes('<person>'), 'XML should have elements');
    assert(result.data.includes('<name>John</name>'), 'XML should have data');
  }),

  test('Binary serialization', () => {
    const input = 'Hello, World!';
    const result = DataSerializer.toBinary(input);
    assert(Buffer.isBuffer(result.data), 'Binary should return Buffer');
    const decoded = DataSerializer.fromBinary(result.data as Buffer);
    assertEquals(decoded, input, 'Binary deserialization failed');
  }),

  test('Object cloning', () => {
    const input = { name: 'John', nested: { value: 42 } };
    const cloned = DataSerializer.clone(input);
    assertEquals(cloned, input, 'Clone should be equal');
    cloned.nested.value = 100;
    assert(input.nested.value === 42, 'Clone should be deep copy');
  }),

  test('Object equality', () => {
    const obj1 = { name: 'John', age: 30 };
    const obj2 = { name: 'John', age: 30 };
    const obj3 = { name: 'Jane', age: 30 };
    assert(DataSerializer.equals(obj1, obj2), 'Equal objects should return true');
    assert(!DataSerializer.equals(obj1, obj3), 'Different objects should return false');
  }),
];

// Test Encoding Service
const encodingServiceTests = [
  test('EncodingService.toBase64', () => {
    const result = EncodingService.toBase64('Hello');
    assert(result === 'SGVsbG8=', 'Quick Base64 encoding failed');
  }),

  test('EncodingService.fromBase64', () => {
    const result = EncodingService.fromBase64('SGVsbG8=');
    assertEquals(result, 'Hello', 'Quick Base64 decoding failed');
  }),

  test('EncodingService.urlEncode', () => {
    const result = EncodingService.urlEncode('Hello World');
    assert(result.includes('Hello'), 'Quick URL encoding failed');
  }),

  test('EncodingService.toJson', () => {
    const result = EncodingService.toJson({ name: 'John' });
    assert(result.includes('John'), 'Quick JSON encoding failed');
  }),

  test('EncodingService.getEncoders', () => {
    const encoders = EncodingService.getEncoders();
    assert(encoders.text.includes('base64'), 'Should list base64 encoder');
    assert(encoders.image.includes('jpeg'), 'Should list jpeg encoder');
    assert(encoders.data.includes('json'), 'Should list json encoder');
  }),

  test('EncodingService.getVersion', () => {
    const version = EncodingService.getVersion();
    assert(version === '1.0.0', 'Version should be 1.0.0');
  }),
];

// Run all tests
async function runTests() {
  console.log('\n🧪 Running Encoding Service Tests\n');

  let passed = 0;
  let failed = 0;

  console.log('📝 Text Encoding Tests');
  for (const testFn of textEncodingTests) {
    const result = await testFn();
    result ? passed++ : failed++;
  }

  console.log('\n📦 Data Serialization Tests');
  for (const testFn of dataSerializationTests) {
    const result = await testFn();
    result ? passed++ : failed++;
  }

  console.log('\n🔧 Encoding Service Tests');
  for (const testFn of encodingServiceTests) {
    const result = await testFn();
    result ? passed++ : failed++;
  }

  console.log('\n' + '='.repeat(50));
  console.log(`\n📊 Test Results: ${passed} passed, ${failed} failed`);

  if (failed === 0) {
    console.log('🎉 All tests passed!\n');
  } else {
    console.log('❌ Some tests failed\n');
    process.exit(1);
  }
}

// Run tests if this file is executed directly
if (require.main === module) {
  runTests().catch((error) => {
    console.error('Test runner error:', error);
    process.exit(1);
  });
}

export { runTests };
