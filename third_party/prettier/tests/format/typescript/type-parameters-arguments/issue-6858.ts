testFunc<//#region
{
  testProp: number;
}>(parserFunc`//#endregion

Some multiline string
In here`);

testFunc(
  //#region
  {
    testProp: number,
  },
  //#endregion
);
