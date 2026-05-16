function f1() {}

function f2() {
  "ngInject";
  Object.assign(this, { $log, $uibModal });
}

function f3() {
  "ngInject";

  Object.assign(this, { $log, $uibModal });
}

function f4() {
  "ngInject";

  Object.assign(this, { $log, $uibModal });
}
