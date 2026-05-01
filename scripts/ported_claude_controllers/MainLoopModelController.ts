import { onGrowthBookRefresh } from '../../services/analytics/growthbook.js';
import {
  getDefaultMainLoopModelSetting,
  type ModelName,
  parseUserSpecifiedModel,
} from '../../utils/model/model.js';
import { getAppStateStore } from '../../state/AppState.js';

/**
 * Headless controller for the main loop model.
 * Replaces React `useMainLoopModel` hook.
 */
export class MainLoopModelController {
  private unsubscribeStore: (() => void) | null = null;
  private unsubscribeGrowthBook: (() => void) | null = null;
  private onModelChange: (model: ModelName) => void;
  private currentModel: ModelName | null = null;

  constructor(onModelChange: (model: ModelName) => void) {
    this.onModelChange = onModelChange;
  }

  start() {
    const store = getAppStateStore();

    const evaluateModel = () => {
      const state = store.getState();
      const model = parseUserSpecifiedModel(
        state.mainLoopModelForSession ?? state.mainLoopModel ?? getDefaultMainLoopModelSetting(),
      );

      if (this.currentModel !== model) {
        this.currentModel = model;
        this.onModelChange(model);
      }
    };

    // Assuming store is a standard redux-like store
    this.unsubscribeStore = store.subscribe(evaluateModel);

    // Register with GrowthBook and retain unsubscribe if provided
    const gbUnsubscribe = onGrowthBookRefresh(() => evaluateModel());
    this.unsubscribeGrowthBook = typeof gbUnsubscribe === 'function' ? gbUnsubscribe : () => {};

    evaluateModel();
  }

  stop() {
    if (this.unsubscribeStore) this.unsubscribeStore();
    if (this.unsubscribeGrowthBook) this.unsubscribeGrowthBook();
    this.unsubscribeStore = null;
    this.unsubscribeGrowthBook = null;
  }

  getCurrentModel(): ModelName | null {
    return this.currentModel;
  }
}
