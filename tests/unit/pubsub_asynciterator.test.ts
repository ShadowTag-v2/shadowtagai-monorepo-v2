/**
 * VCR Test Cassette — PubSub AsyncIterator Pattern
 * Tests the GraphQL subscription AsyncIterator for deterministic event delivery.
 * V25 Pinnacle — Property-Based Testing
 */
import { describe, it, expect, beforeEach } from 'vitest';

/** Minimal PubSub implementation mirroring graphql_server.ts */
class TestPubSub {
  private subscribers = new Map<string, Array<(value: unknown) => void>>();

  publish(channel: string, payload: unknown): void {
    const subs = this.subscribers.get(channel) ?? [];
    for (const cb of subs) cb(payload);
  }

  asyncIterator<T>(channel: string): AsyncIterableIterator<T> {
    const queue: T[] = [];
    let resolve: ((value: IteratorResult<T>) => void) | null = null;

    const cb = (value: unknown) => {
      if (resolve) {
        const r = resolve;
        resolve = null;
        r({ value: value as T, done: false });
      } else {
        queue.push(value as T);
      }
    };

    if (!this.subscribers.has(channel)) {
      this.subscribers.set(channel, []);
    }
    this.subscribers.get(channel)!.push(cb);

    return {
      next(): Promise<IteratorResult<T>> {
        if (queue.length > 0) {
          return Promise.resolve({ value: queue.shift()!, done: false });
        }
        return new Promise<IteratorResult<T>>((r) => { resolve = r; });
      },
      return(): Promise<IteratorResult<T>> {
        const subs = new Map<string, Array<(value: unknown) => void>>();
        subs.delete(channel);
        return Promise.resolve({ value: undefined as T, done: true });
      },
      throw(err: unknown): Promise<IteratorResult<T>> {
        return Promise.reject(err);
      },
      [Symbol.asyncIterator]() { return this; },
    };
  }
}

describe('PubSub AsyncIterator — VCR Cassette', () => {
  let pubsub: TestPubSub;

  beforeEach(() => {
    pubsub = new TestPubSub();
  });

  it('delivers events to async iterator in order', async () => {
    const iter = pubsub.asyncIterator<{ type: string; data: string }>('events');

    // Publish 3 events
    pubsub.publish('events', { type: 'CDC_INSERT', data: 'row_1' });
    pubsub.publish('events', { type: 'CDC_UPDATE', data: 'row_2' });
    pubsub.publish('events', { type: 'CDC_DELETE', data: 'row_3' });

    const e1 = await iter.next();
    const e2 = await iter.next();
    const e3 = await iter.next();

    expect(e1.done).toBe(false);
    expect(e1.value.type).toBe('CDC_INSERT');
    expect(e2.value.type).toBe('CDC_UPDATE');
    expect(e3.value.data).toBe('row_3');
  });

  it('handles async publish after iterator is waiting', async () => {
    const iter = pubsub.asyncIterator<{ id: number }>('live');

    // Start waiting BEFORE publish
    const promise = iter.next();

    // Small delay then publish
    setTimeout(() => pubsub.publish('live', { id: 42 }), 10);

    const result = await promise;
    expect(result.done).toBe(false);
    expect(result.value.id).toBe(42);
  });

  it('supports multiple subscribers on same channel', async () => {
    const iter1 = pubsub.asyncIterator<string>('shared');
    const iter2 = pubsub.asyncIterator<string>('shared');

    pubsub.publish('shared', 'broadcast');

    const r1 = await iter1.next();
    const r2 = await iter2.next();

    expect(r1.value).toBe('broadcast');
    expect(r2.value).toBe('broadcast');
  });

  it('isolates channels from each other', async () => {
    const iterA = pubsub.asyncIterator<string>('channel_a');

    pubsub.publish('channel_b', 'wrong_channel');
    pubsub.publish('channel_a', 'correct');

    const result = await iterA.next();
    expect(result.value).toBe('correct');
  });

  it('return() signals done', async () => {
    const iter = pubsub.asyncIterator<string>('fin');
    const result = await iter.return!();
    expect(result.done).toBe(true);
  });

  it('handles site_id filtered subscriptions', async () => {
    const siteId = 'site_headfade';
    const iter = pubsub.asyncIterator<{ siteId: string; event: string }>(`events:${siteId}`);

    pubsub.publish(`events:${siteId}`, { siteId, event: 'page_view' });
    pubsub.publish('events:site_kovelai', { siteId: 'site_kovelai', event: 'signup' });

    const result = await iter.next();
    expect(result.value.siteId).toBe(siteId);
    expect(result.value.event).toBe('page_view');
  });
});
