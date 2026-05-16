// @flow

const tests = [
  // getContext
  (el: HTMLCanvasElement) => {
    (el.getContext('2d'): ?CanvasRenderingContext2D);
  }
];
