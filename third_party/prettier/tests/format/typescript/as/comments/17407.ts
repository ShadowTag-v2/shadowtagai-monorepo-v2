function getClassNameFromPrototypeMethod(container) {
  return ((container.left as PropertyAccessExpression).expression as PropertyAccessExpression) // a
    .expression; // b // c // d
}
