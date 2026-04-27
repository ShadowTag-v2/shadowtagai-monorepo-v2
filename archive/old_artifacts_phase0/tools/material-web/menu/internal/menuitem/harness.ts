/**
 * @license
 * Copyright 2022 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import type { LitElement } from 'lit';

import { ListItemHarness } from '../../../list/internal/listitem/harness.js';
import type { MenuItem } from '../controllers/menuItemController.js';

/**
 * Test harness for menu item.
 */
export class MenuItemHarness extends ListItemHarness<MenuItem & LitElement> {}
