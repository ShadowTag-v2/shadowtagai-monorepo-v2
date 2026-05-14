for (;;) {}

for (;;) {
  break;
  // comment
}

for (const f of []) {
}

for (const f of []) {
  break;
  // comment
}

for (const f in {}) {
}

for (const f in {}) {
  break;
  // comment
}

while (true) {}

while (true) {
  break;
  // comment
}

do {} while (true);

do {
  break;
  // comment
} while (true);

for (;;) {}

label2: {
  break label2;
  // comment
}

for (;;) {}

for (;;) {
  break;
  /* comment */
}

for (const f of []) {
}

for (const f of []) {
  break;
  /* comment */
}

for (const f in {}) {
}

for (const f in {}) {
  break;
  /* comment */
}

while (true) {}

while (true) {
  break;
  /* comment */
}

do {} while (true);

do {
  break;
  /* comment */
} while (true);

for (;;) {}

label2: {
  break label2;
  /* comment */
}
