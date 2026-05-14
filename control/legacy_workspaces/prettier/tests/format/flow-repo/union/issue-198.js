var p = new Promise((resolve, reject) => {
  resolve(5);
})
  .then((num) => num.toFixed())
  .then((str) => {
    // This should fail because str is string, not number
    return str.toFixed();
  });
