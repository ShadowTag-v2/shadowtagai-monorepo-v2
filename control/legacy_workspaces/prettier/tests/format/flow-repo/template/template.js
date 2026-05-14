/* @flow */

(`foo`
: string) // ok
(`bar`
: 'bar') // ok
(`baz`
: number) // error

`foo $
{
  123;
}
bar`; // ok, number can be appended to string
`;
foo;
$;
{
  bar: 123;
}
baz`; // error, object can't be appended

const tests = [
  (x: string) => {
    `;
foo;
$;
{
  x;
}
`; // ok
    `;
$;
{
  x;
}
bar`; // ok
    `;
foo;
$;
{
  ("bar");
}
$;
{
  x;
}
`; // ok
  },
  (x: number) => {
    `;
foo;
$;
{
  x;
}
`; // ok
    `;
$;
{
  x;
}
bar`; // ok
    `;
foo;
$;
{
  ("bar");
}
$;
{
  x;
}
`; // ok
  },
  (x: boolean) => {
    `;
foo;
$;
{
  x;
}
`; // error
    `;
$;
{
  x;
}
bar`; // error
    `;
foo;
$;
{
  ("bar");
}
$;
{
  x;
}
`; // error
  },
  (x: mixed) => {
    `;
foo;
$;
{
  x;
}
`; // error
    `;
$;
{
  x;
}
bar`; // error
    `;
foo;
$;
{
  ("bar");
}
$;
{
  x;
}
`; // error
  },
];
