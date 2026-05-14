// https://github.com/prettier/prettier/issues/7126
for (;;) {
  if (condition) {
    continue;

    // breaking comment
    (possibleArray || []).sort();
  }
}

for (;;) {
  if (condition) {
    continue;

    // breaking comment
    (possibleArray || []).sort();
  }
}

for (;;) {
  if (condition) {
    // prettier-ignore
    continue;

    // breaking comment
    (possibleArray || []).sort();
  }
  if (condition) {
    // prettier-ignore
    break;
    // breaking comment
    (possibleArray || []).sort();
  }
}
