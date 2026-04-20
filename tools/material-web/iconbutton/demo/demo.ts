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

const collection = new MaterialCollection<KnobTypesToKnobs<StoryKnobs>>('Icon Button', [
  new Knob('disabled', { ui: boolInput(), defaultValue: false }),
  new Knob('icon', { ui: textInput(), defaultValue: '' }),
  new Knob('selectedIcon', { ui: textInput(), defaultValue: '' }),
  new Knob('softDisabled', { ui: boolInput(), defaultValue: false }),
]);

collection.addStories(...materialInitsToStoryInits(stories));

setUpDemo(collection, { icons: 'material-symbols' });
