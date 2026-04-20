/**
 * @license
 * Copyright 2026 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import '@material/web/labs/gb/components/radio/md-radio.js';

import { adoptStyles } from '@material/web/labs/gb/styles/adopt-styles.js';
import { styles as m3Styles } from '@material/web/labs/gb/styles/m3.css' with { type: 'css' }; // github-only
import { css, html } from 'lit';
import type { MaterialStoryInit } from './material-collection.js';
// import {styles as m3Styles} from '@material/web/labs/gb/styles/m3.cssresult.js'; // google3-only

/** Knob types for radio stories. */
export interface StoryKnobs {
  disabled: boolean;
}

adoptStyles(document, [
  m3Styles,
  css`
    :root {
      --md-icon-font: 'Material Symbols Outlined';
    }
  `,
]);

const playground: MaterialStoryInit<StoryKnobs> = {
  name: 'Playground',
  render(knobs) {
    return html`
      <md-radio name="group" ?disabled=${knobs.disabled}></md-radio>
      <md-radio name="group" ?disabled=${knobs.disabled}></md-radio>
      <md-radio name="group" ?disabled=${knobs.disabled}></md-radio>
    `;
  },
};

/** Radio stories. */
export const stories = [playground];
