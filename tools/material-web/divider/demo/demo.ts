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

const collection = new MaterialCollection<KnobTypesToKnobs<StoryKnobs>>('Divider', [
  new Knob('inset', { defaultValue: true, ui: boolInput() }),
  new Knob('inset (start)', { defaultValue: false, ui: boolInput() }),
  new Knob('inset (end)', { defaultValue: false, ui: boolInput() }),
]);

collection.addStories(...materialInitsToStoryInits(stories));

setUpDemo(collection);
