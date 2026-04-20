/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

// Declarative shadow dom polyfill
import { hydrateShadowRoots } from '@webcomponents/template-shadowroot/template-shadowroot.js';

if (!Object.hasOwn(HTMLTemplateElement.prototype, 'shadowRoot')) {
  hydrateShadowRoots(document.body);
}
document.body.removeAttribute('dsd-pending');
