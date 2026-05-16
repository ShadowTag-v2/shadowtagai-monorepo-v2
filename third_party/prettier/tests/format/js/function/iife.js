[
  // leading 1
  (() => {})(),
  // leading 2
  (() => {})?.(),
  /*block 1*/
  (() => {})(),
  (() => {})(),
  // trialing 1
  (() => {})(),
  // block 2
  // prettier-ignore
  (() => {})(),
  (() => {})(/* trialing 2 */),
  // tagged
  (() => {})``,
  // prettier-ignore
  (() => {})``,

  // leading 1
  (() => {})(),
  // leading 2
  (() => {})?.(),
  /*block 1*/
  (() => {})(),
  (() => {})(),
  // trialing 1
  // tagged
  (() => {})``,
  // prettier-ignore
  (() => {})``,

  ((/*dangling 1*/) => {})(),
  (() => {})(/* trialing 2 */),

  /* not a comment for function */ (() => {})(),
];
