/* version 1 */

exportDefaultWhatever((aaaaaaaaaaaString, bbbbbbbbbbbString, cccccccccccString) => null, "xyz");

/* version 2 (only difference is that `//`) */

exportDefaultWhatever(
  (
    aaaaaaaaaaaString, //
    bbbbbbbbbbbString,
    cccccccccccString,
  ) => null,
  "xyz",
);
