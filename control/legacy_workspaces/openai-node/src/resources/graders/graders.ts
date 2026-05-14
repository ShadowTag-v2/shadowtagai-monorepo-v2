// File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import { APIResource } from "../../core/resource";
import * as GraderModelsAPI from "./grader-models";
import {
  GraderModels,
  LabelModelGrader,
  MultiGrader,
  PythonGrader,
  ScoreModelGrader,
  StringCheckGrader,
  TextSimilarityGrader,
} from "./grader-models";

export class Graders extends APIResource {
  graderModels: GraderModelsAPI.GraderModels = new GraderModelsAPI.GraderModels(this._client);
}

Graders.GraderModels = GraderModels;

export declare namespace Graders {
  export {
    GraderModels,
    LabelModelGrader,
    MultiGrader,
    PythonGrader,
    ScoreModelGrader,
    StringCheckGrader,
    TextSimilarityGrader,
  };
}
