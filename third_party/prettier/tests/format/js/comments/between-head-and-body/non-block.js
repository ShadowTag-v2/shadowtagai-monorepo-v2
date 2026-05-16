do
  // 11
  foo();
while (1);
for (a in b) // 12
  foo();
for (a of b) // 13
  foo();
for (;;)
  // 14
  foo();
if (a)
  // 15
  foo();
// 152
else foo();
while (a)
  // 16
  foo();
with(a) // 17
foo();

do
  // 21
  foo();
while (1);
// 22
for (a in b) foo();
// 23
for (a of b) foo();
for (;;)
  // 24
  foo();
if (a)
  // 25
  foo();
// 252
else foo();
while (a)
  // 26
  foo();
with(a)
// 27
foo();

do /* 31 */ foo();
while (1);
for (a in b /* 32 */) foo();
for (a of b /* 33 */) foo();
for (;;)
  // 34 */
  foo();
if (a) /* 35 */ foo();
/* 352 */ else foo();
while (a) /* 36 */ foo();
with(a) /* 37 */
foo();

do /* 41 */ foo();
while (1);
for (a in b /* 42 */) foo();
for (a of b /* 43 */) foo();
for (;;)
  // 34 */
  foo();
if (a) /* 45 */ foo();
/* 452 */ else foo();
while (a) /* 46 */ foo();
with(a) /* 47 */
foo();

do
  /*
51 */
  foo();
while (1);
for (a in b /*
52 */)
  foo();
for (a of b /*
53 */)
  foo();
for (;;)
  // 34 */
  foo();
if (a)
  /*
55 */
  foo();
/*
552 */ else foo();
while (a)
  /*
56 */
  foo();
with(a) /*
57 */
foo();
