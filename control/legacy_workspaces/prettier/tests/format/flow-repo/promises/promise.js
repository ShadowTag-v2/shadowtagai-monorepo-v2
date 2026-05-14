/**
 * @flow
 */

//////////////////////////////////////////////////
// == Promise constructor resolve() function == //
//////////////////////////////////////////////////

// Promise constructor resolve(T) -> then(T)
new Promise((resolve, reject) => {
  resolve(0);
}).then((num) => {
  var a: number = num;

  // TODO: The error message that results from this is almost useless
  var b: string = num; // Error: number ~> string
});

// Promise constructor with arrow function resolve(T) -> then(T)
new Promise((resolve, reject) => resolve(0)).then((num) => {
  var a: number = num;

  // TODO: The error message that results from this is almost useless
  var b: string = num; // Error: number ~> string
});

// Promise constructor resolve(Promise<T>) -> then(T)
new Promise((resolve, reject) => {
  resolve(
    new Promise((resolve, reject) => {
      resolve(0);
    }),
  );
}).then((num) => {
  var a: number = num;
  var b: string = num; // Error: number ~> string
});

// Promise constructor resolve(Promise<Promise<T>>) -> then(T)
new Promise((resolve, reject) => {
  resolve(
    new Promise((resolve, reject) => {
      resolve(
        new Promise((resolve, reject) => {
          resolve(0);
        }),
      );
    }),
  );
}).then((num) => {
  var a: number = num;
  var b: string = num; // Error: number ~> string
});

// Promise constructor resolve(T); resolve(U); -> then(T|U)
new Promise((resolve, reject) => {
  if (Math.random()) {
    resolve(42);
  } else {
    resolve("str");
  }
}).then((numOrStr) => {
  if (typeof numOrStr === "string") {
    var a: string = numOrStr;
  } else {
    var b: number = numOrStr;
  }
  var c: string = numOrStr; // Error: number|string -> string
});

/////////////////////////////////////////////////
// == Promise constructor reject() function == //
/////////////////////////////////////////////////

// TODO: Promise constructor reject(T) -> catch(T)
new Promise((resolve, reject) => {
  reject(0);
}).catch((num) => {
  var a: number = num;

  // TODO
  var b: string = num; // Error: number ~> string
});

// TODO: Promise constructor reject(Promise<T>) ~> catch(Promise<T>)
new Promise((resolve, reject) => {
  reject(
    new Promise((resolve, reject) => {
      reject(0);
    }),
  );
}).catch((num) => {
  var a: Promise<number> = num;

  // TODO
  var b: number = num; // Error: Promise<Number> ~> number
});

// TODO: Promise constructor reject(T); reject(U); -> then(T|U)
new Promise((resolve, reject) => {
  if (Math.random()) {
    reject(42);
  } else {
    reject("str");
  }
}).catch((numOrStr) => {
  if (typeof numOrStr === "string") {
    var a: string = numOrStr;
  } else {
    var b: number = numOrStr;
  }

  // TODO
  var c: string = numOrStr; // Error: number|string -> string
});

/////////////////////////////
// == Promise.resolve() == //
/////////////////////////////

// Promise.resolve(T) -> then(T)
Promise.resolve(0).then((num) => {
  var a: number = num;
  var b: string = num; // Error: number ~> string
});

// Promise.resolve(Promise<T>) -> then(T)
Promise.resolve(Promise.resolve(0)).then((num) => {
  var a: number = num;
  var b: string = num; // Error: number ~> string
});

// Promise.resolve(Promise<Promise<T>>) -> then(T)
Promise.resolve(Promise.resolve(Promise.resolve(0))).then((num) => {
  var a: number = num;
  var b: string = num; // Error: number ~> string
});

////////////////////////////
// == Promise.reject() == //
////////////////////////////

// TODO: Promise.reject(T) -> catch(T)
Promise.reject(0).catch((num) => {
  var a: number = num;

  // TODO
  var b: string = num; // Error: number ~> string
});

// TODO: Promise.reject(Promise<T>) -> catch(Promise<T>)
Promise.reject(Promise.resolve(0)).then((num) => {
  var a: Promise<number> = num;

  // TODO
  var b: number = num; // Error: Promise<number> ~> number
});

//////////////////////////////////
// == Promise.prototype.then == //
//////////////////////////////////

// resolvedPromise.then():T -> then(T)
Promise.resolve(0)
  .then((num) => "asdf")
  .then((str) => {
    var a: string = str;
    var b: number = str; // Error: string ~> number
  });

// resolvedPromise.then():Promise<T> -> then(T)
Promise.resolve(0)
  .then((num) => Promise.resolve("asdf"))
  .then((str) => {
    var a: string = str;
    var b: number = str; // Error: string ~> number
  });

// resolvedPromise.then():Promise<Promise<T>> -> then(T)
Promise.resolve(0)
  .then((num) => Promise.resolve(Promise.resolve("asdf")))
  .then((str) => {
    var a: string = str;
    var b: number = str; // Error: string ~> number
  });

// TODO: resolvedPromise.then(<throw(T)>) -> catch(T)
Promise.resolve(0)
  .then((num) => {
    throw "str";
  })
  .catch((str) => {
    var a: string = str;

    // TODO
    var b: number = str; // Error: string ~> number
  });

///////////////////////////////////
// == Promise.prototype.catch == //
///////////////////////////////////

// rejectedPromise.catch():U -> then(U)
Promise.reject(0)
  .catch((num) => "asdf")
  .then((str) => {
    var a: string = str;
    var b: number = str; // Error: string ~> number
  });

// rejectedPromise.catch():Promise<U> -> then(U)
Promise.reject(0)
  .catch((num) => Promise.resolve("asdf"))
  .then((str) => {
    var a: string = str;
    var b: number = str; // Error: string ~> number
  });

// rejectedPromise.catch():Promise<Promise<U>> -> then(U)
Promise.reject(0)
  .catch((num) => Promise.resolve(Promise.resolve("asdf")))
  .then((str) => {
    var a: string = str;
    var b: number = str; // Error: string ~> number
  });

// resolvedPromise<T> -> catch() -> then():?T
Promise.resolve(0)
  .catch((err) => {})
  .then((num) => {
    var a:
    ?number = num
    var b: string = num; // Error: string ~> number
  });
