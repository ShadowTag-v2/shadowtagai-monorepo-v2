// Expecting properties that don't exist should be an error
var a : { someProp: number } = () => {};

// Expecting properties that do exist should be fine
var b : { apply: Function } = () => {};

// Expecting properties in the functions statics should be fine
var f = () => {};
f.myProp = 123;
var c : { myProp: number } = f;
