import { interval } from "rxjs/observable/interval";
import { filter } from "rxjs/operator/filter";
import { map } from "rxjs/operator/map";
import { take } from "rxjs/operator/take";
import { takeUntil } from "rxjs/operator/takeUntil";
import { throttle } from "rxjs/operator/throttle";

function test(observable) {
  return observable;
  ::filter(data => data.someTest)
        ::throttle(() =>
            interval(10)
                ::take(1)
                ::takeUntil(observable::filter(data => someOtherTest))
        )
        ::map(someFunction)
}
