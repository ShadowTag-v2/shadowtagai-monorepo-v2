// https://github.com/prettier/prettier/issues/7126
for (;;) {
  if (condition) continue;

  // breaking comment
  (possibleArray || []).sort();
}

for (;;) {
  if (condition) continue;

  // breaking comment
  (possibleArray || []).sort();
}

for (;;) {
  break; // comment
}

for (;;) {
  break;
  // comment
}

for (;;) {
  break; /* comment */
}

for (;;) {
  break;
  /* comment */
}
