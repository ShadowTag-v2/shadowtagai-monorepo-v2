// https://babeljs.io/docs/babel-plugin-proposal-pipeline-operator
// https://github.com/tc39/proposal-pipeline-operator/

const result = exclaim(capitalize(doubleSay("hello")));
result; //=> "Hello, hello!"

const result = "hello"
  |> doubleSay
  |> capitalize
  |> exclaim;

result; //=> "Hello, hello!"
