// File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import { APIResource } from "../../core/resource";
import * as SpeechAPI from "./speech";
import { Speech, SpeechCreateParams, SpeechModel } from "./speech";
import * as TranscriptionsAPI from "./transcriptions";
import {
  Transcription,
  TranscriptionCreateParams,
  TranscriptionCreateParamsNonStreaming,
  TranscriptionCreateParamsStreaming,
  TranscriptionCreateResponse,
  TranscriptionDiarized,
  TranscriptionDiarizedSegment,
  TranscriptionInclude,
  TranscriptionSegment,
  TranscriptionStreamEvent,
  Transcriptions,
  TranscriptionTextDeltaEvent,
  TranscriptionTextDoneEvent,
  TranscriptionTextSegmentEvent,
  TranscriptionVerbose,
  TranscriptionWord,
} from "./transcriptions";
import * as TranslationsAPI from "./translations";
import {
  Translation,
  TranslationCreateParams,
  TranslationCreateResponse,
  Translations,
  TranslationVerbose,
} from "./translations";

export class Audio extends APIResource {
  transcriptions: TranscriptionsAPI.Transcriptions = new TranscriptionsAPI.Transcriptions(
    this._client,
  );
  translations: TranslationsAPI.Translations = new TranslationsAPI.Translations(this._client);
  speech: SpeechAPI.Speech = new SpeechAPI.Speech(this._client);
}

export type AudioModel =
  | "whisper-1"
  | "gpt-4o-transcribe"
  | "gpt-4o-mini-transcribe"
  | "gpt-4o-transcribe-diarize";

/**
 * The format of the output, in one of these options: `json`, `text`, `srt`,
 * `verbose_json`, `vtt`, or `diarized_json`. For `gpt-4o-transcribe` and
 * `gpt-4o-mini-transcribe`, the only supported format is `json`. For
 * `gpt-4o-transcribe-diarize`, the supported formats are `json`, `text`, and
 * `diarized_json`, with `diarized_json` required to receive speaker annotations.
 */
export type AudioResponseFormat =
  | "json"
  | "text"
  | "srt"
  | "verbose_json"
  | "vtt"
  | "diarized_json";

Audio.Transcriptions = Transcriptions;
Audio.Translations = Translations;
Audio.Speech = Speech;

export declare namespace Audio {
  export {
    type AudioModel,
    type AudioResponseFormat,
    Speech,
    SpeechCreateParams,
    SpeechModel,
    Transcription,
    TranscriptionCreateParams,
    TranscriptionCreateParamsNonStreaming,
    TranscriptionCreateParamsStreaming,
    TranscriptionCreateResponse,
    TranscriptionDiarized,
    TranscriptionDiarizedSegment,
    TranscriptionInclude,
    TranscriptionSegment,
    TranscriptionStreamEvent,
    Transcriptions,
    TranscriptionTextDeltaEvent,
    TranscriptionTextDoneEvent,
    TranscriptionTextSegmentEvent,
    TranscriptionVerbose,
    TranscriptionWord,
    Translation,
    TranslationCreateParams,
    TranslationCreateResponse,
    Translations,
    TranslationVerbose,
  };
}
