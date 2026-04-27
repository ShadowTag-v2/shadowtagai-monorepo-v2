/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import './material-collection.js';
import './index.js';

import { boolInput, Knob } from './index.js';
import {
  type KnobTypesToKnobs,
  MaterialCollection,
  materialInitsToStoryInits,
  setUpDemo,
} from './material-collection.js';

import { type StoryKnobs, stories } from './stories.js';

const collection = new MaterialCollection<KnobTypesToKnobs<StoryKnobs>>('Checkbox', [
  new Knob('checked', { defaultValue: false, ui: boolInput() }),
  new Knob('indeterminate', { defaultValue: false, ui: boolInput() }),
  new Knob('disabled', { defaultValue: false, ui: boolInput() }),
]);

collection.addStories(...materialInitsToStoryInits(stories));

setUpDemo(collection);
