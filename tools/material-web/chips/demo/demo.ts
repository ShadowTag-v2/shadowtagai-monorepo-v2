/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import './material-collection.js';
import './index.js';

import { boolInput, Knob, textInput } from './index.js';
import {
  type KnobTypesToKnobs,
  MaterialCollection,
  materialInitsToStoryInits,
  setUpDemo,
} from './material-collection.js';

import { type StoryKnobs, stories } from './stories.js';

const collection = new MaterialCollection<KnobTypesToKnobs<StoryKnobs>>('Chips', [
  new Knob('label', { defaultValue: '', ui: textInput() }),
  new Knob('elevated', { defaultValue: false, ui: boolInput() }),
  new Knob('disabled', { defaultValue: false, ui: boolInput() }),
  new Knob('scrolling', { defaultValue: false, ui: boolInput() }),
]);

collection.addStories(...materialInitsToStoryInits(stories));

setUpDemo(collection, { icons: 'material-symbols' });
