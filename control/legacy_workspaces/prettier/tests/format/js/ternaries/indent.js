aaaaaaaaaaaaaaa
  ? bbbbbbbbbbbbbbbbbb
  : ccccccccccccccc
    ? ddddddddddddddd
    : eeeeeeeeeeeeeee
      ? fffffffffffffff
      : gggggggggggggggg;

aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
  ? aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    ? aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
      ? aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
      : aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    : aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
  : aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa;

a
  ? {
      a: 0,
    }
  : {
      a: {
        a: 0,
      }
        ? {
            a: 0,
          }
        : {
            y: {
              a: 0,
            }
              ? {
                  a: 0,
                }
              : {
                  a: 0,
                },
          },
    };

a
  ? {
      a: () =>
        a
          ? {
              a: [
                a
                  ? {
                      a: 0,
                      b: [a ? [0, 1] : []],
                    }
                  : [
                      [
                        0,
                        {
                          a: 0,
                        },
                        a ? 0 : 1,
                      ],
                      () =>
                        a
                          ? {
                              a: 0,
                            }
                          : [
                              {
                                a: 0,
                              },
                              {},
                            ],
                    ],
              ],
            }
          : [
              a
                ? () => {
                    a
                      ? a(
                          a
                            ? {
                                a: a({
                                  a: 0,
                                }),
                              }
                            : [
                                0,
                                a(),
                                a(
                                  a(),
                                  {
                                    a: 0,
                                  },
                                  a
                                    ? a()
                                    : a({
                                        a: 0,
                                      }),
                                ),
                                a()
                                  ? {
                                      a: a(),
                                      b: [],
                                    }
                                  : {},
                              ],
                        )
                      : a(
                          a()
                            ? {
                                a: 0,
                              }
                            : ((a) =>
                                a()
                                  ? [
                                      {
                                        a: 0,
                                        b: a(),
                                      },
                                    ]
                                  : a([
                                      a
                                        ? {
                                            a: 0,
                                          }
                                        : {},
                                      {
                                        a: 0,
                                      },
                                    ]))(a ? (a) => () => 0 : (a) => () => 1),
                        );
                  }
                : () => {},
            ],
    }
  : a;
