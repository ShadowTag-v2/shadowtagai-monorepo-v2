/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { AsyncLocalStorage } from "node:async_hooks";
import type express from "express";

export const requestStorage = new AsyncLocalStorage<{ req: express.Request }>();
