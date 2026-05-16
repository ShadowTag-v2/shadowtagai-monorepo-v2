if (1) {
  // 11
  doThing(foo);
}
if (1) {
} else {
  // 12
  doThing(foo);
}

if (2) {
  // 21
  doThing(foo);
}
if (2) {
}
// 22
else {
  doThing(foo);
}

if (3) {
  // 31
  doThing(foo);
}
if (3) {
} // 32
else {
  doThing(foo);
}

if (4) {
  /* 41 */ doThing(foo);
}
if (4) {
} /* 42 */ else {
  doThing(foo);
}
