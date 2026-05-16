// @flow

const Immutable = require("immutable");

const tasksPerStatusMap = new Map([].map((taskStatus) => [taskStatus, new Map()]));
for (const [taskStatus, tasksMap] of tasksPerStatusMap) {
  tasksPerStatusMap.set(taskStatus, Immutable.Map(tasksMap));
}
