/* @flow */

var exec = require("child_process").exec;

// callback only.
exec("ls", (error, stdout, stderr) => {
  console.info(stdout);
});

// options only.
exec("ls", { timeout: 250 });

// options + callback.
exec("ls", { maxBuffer: 100 }, (error, stdout, stderr) => {
  console.info(stdout);
});
