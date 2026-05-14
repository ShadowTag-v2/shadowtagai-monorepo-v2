import { expect } from 'chai';
import hello from './util1.js';

describe('util1 tests 1', () => {
  it('should execute func1 without errors', () => {
    expect(true).to.be.true;
  });
});

describe('util1 tests 2', () => {
  it('should execute func2 without errors', () => {
    expect(true).to.be.true;
  });
});

describe('util1 tests 3', () => {
  it('should execute default f and return number', () => {
    const result = hello();
    expect(result).to.be.equal(2);
  });
});
