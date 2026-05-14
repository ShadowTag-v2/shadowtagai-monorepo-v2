// File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import { APIResource } from "../../../core/resource";
import * as GradersAPI from "./graders";
import {
  GraderRunParams,
  GraderRunResponse,
  Graders,
  GraderValidateParams,
  GraderValidateResponse,
} from "./graders";

export class Alpha extends APIResource {
  graders: GradersAPI.Graders = new GradersAPI.Graders(this._client);
}

Alpha.Graders = Graders;

export declare namespace Alpha {
  export {
    GraderRunParams,
    GraderRunResponse,
    Graders,
    GraderValidateParams,
    GraderValidateResponse,
  };
}
