/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import './material-collection.js';
import './index.js';

import { Knob, numberInput } from './index.js';
import {
  type KnobTypesToKnobs,
  MaterialCollection,
  materialInitsToStoryInits,
  setUpDemo,
} from './material-collection.js';

import { type StoryKnobs, stories } from './stories.js';

const collection = new MaterialCollection<KnobTypesToKnobs<StoryKnobs>>('Elevation', [
  new Knob('level', { defaultValue: 1, ui: numberInput() }),
]);

collection.addStories(...materialInitsToStoryInits(stories));

setUpDemo(collection);
