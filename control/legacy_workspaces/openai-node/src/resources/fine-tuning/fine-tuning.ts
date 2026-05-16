// File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import { APIResource } from "../../core/resource";
import * as AlphaAPI from "./alpha/alpha";
import { Alpha } from "./alpha/alpha";
import * as CheckpointsAPI from "./checkpoints/checkpoints";
import { Checkpoints } from "./checkpoints/checkpoints";
import * as JobsAPI from "./jobs/jobs";
import {
  FineTuningJob,
  FineTuningJobEvent,
  FineTuningJobEventsPage,
  FineTuningJobIntegration,
  FineTuningJobsPage,
  FineTuningJobWandbIntegration,
  FineTuningJobWandbIntegrationObject,
  JobCreateParams,
  JobListEventsParams,
  JobListParams,
  Jobs,
} from "./jobs/jobs";
import * as MethodsAPI from "./methods";
import {
  DpoHyperparameters,
  DpoMethod,
  Methods,
  ReinforcementHyperparameters,
  ReinforcementMethod,
  SupervisedHyperparameters,
  SupervisedMethod,
} from "./methods";

export class FineTuning extends APIResource {
  methods: MethodsAPI.Methods = new MethodsAPI.Methods(this._client);
  jobs: JobsAPI.Jobs = new JobsAPI.Jobs(this._client);
  checkpoints: CheckpointsAPI.Checkpoints = new CheckpointsAPI.Checkpoints(this._client);
  alpha: AlphaAPI.Alpha = new AlphaAPI.Alpha(this._client);
}

FineTuning.Methods = Methods;
FineTuning.Jobs = Jobs;
FineTuning.Checkpoints = Checkpoints;
FineTuning.Alpha = Alpha;

export declare namespace FineTuning {
  export {
    Alpha,
    Checkpoints,
    DpoHyperparameters,
    DpoMethod,
    FineTuningJob,
    FineTuningJobEvent,
    FineTuningJobEventsPage,
    FineTuningJobIntegration,
    FineTuningJobsPage,
    FineTuningJobWandbIntegration,
    FineTuningJobWandbIntegrationObject,
    JobCreateParams,
    JobListEventsParams,
    JobListParams,
    Jobs,
    Methods,
    ReinforcementHyperparameters,
    ReinforcementMethod,
    SupervisedHyperparameters,
    SupervisedMethod,
  };
}
