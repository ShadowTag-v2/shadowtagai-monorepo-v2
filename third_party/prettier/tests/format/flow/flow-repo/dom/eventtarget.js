// @flow

let listener: EventListener = function (event: Event) :void {};

const tests = [
  // attachEvent
  () => {
    const target = new EventTarget();
    (target.attachEvent('foo', listener)
    : void) // invalid, may be undefined
    (target.attachEvent && target.attachEvent('foo', listener)
    : void) // valid
  },

  // detachEvent
  () => {
    const target = new EventTarget();
    (target.detachEvent('foo', listener)
    : void) // invalid, may be undefined
    (target.detachEvent && target.detachEvent('foo', listener)
    : void) // valid
  },

  () => {
    window.onmessage = (event: MessageEvent) => {
      (event.target: window);
    };
  },
];
