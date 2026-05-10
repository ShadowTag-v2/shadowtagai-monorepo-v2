import { expect } from 'chai';
import { add } from './util2.js';

describe('add tests', () => {
  it('should execute sum on add', () => {
    const result = add(1, 1);
    expect(result).to.be.equal(2);
  });
});
