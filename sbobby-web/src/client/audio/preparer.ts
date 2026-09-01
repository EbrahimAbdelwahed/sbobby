import {
  AUDIO_CHUNK_BUDGET,
  type AudioChunkBudget,
  type AudioSourceDescriptor,
  type PreparedAudioChunk
} from './chunk-budget';
import type { WorkerRequest, WorkerResponse, WorkerTelemetry } from './worker-protocol';

export interface AudioPreparer {
  inspect(file: File): Promise<AudioSourceDescriptor>;
  prepare(file: File, budget: AudioChunkBudget, signal: AbortSignal): AsyncIterable<PreparedAudioChunk>;
  terminate(): void;
}

function requestId(): string {
  return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export class BrowserAudioPreparer implements AudioPreparer {
  private worker: Worker;
  private pending = new Map<string, { resolve: (value: AudioSourceDescriptor) => void; reject: (error: Error) => void }>();
  private telemetryListener?: (telemetry: WorkerTelemetry) => void;
  private workerFailure?: (error: Error) => void;

  constructor(onTelemetry?: (telemetry: WorkerTelemetry) => void) {
    this.worker = new Worker(new URL('./prepare.worker.ts', import.meta.url), { type: 'module' });
    this.telemetryListener = onTelemetry;
    this.worker.onmessage = (event: MessageEvent<WorkerResponse>) => {
      const response = event.data;
      this.telemetryListener?.(response.telemetry);
      if (response.type === 'descriptor') {
        this.pending.get(response.requestId)?.resolve(response.descriptor);
        this.pending.delete(response.requestId);
      } else if (response.type === 'error') {
        this.pending.get(response.requestId)?.reject(new Error(response.code));
        this.pending.delete(response.requestId);
      }
    };
    const failWorker = () => {
      const error = new Error('WORKER_FAILED');
      for (const entry of this.pending.values()) entry.reject(error);
      this.pending.clear();
      this.workerFailure?.(error);
    };
    this.worker.onerror = failWorker;
    this.worker.onmessageerror = failWorker;
  }

  inspect(file: File): Promise<AudioSourceDescriptor> {
    const id = requestId();
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.worker.postMessage({ type: 'inspect', requestId: id, file } satisfies WorkerRequest);
    });
  }

  async *prepare(file: File, budget: AudioChunkBudget = AUDIO_CHUNK_BUDGET, signal: AbortSignal): AsyncIterable<PreparedAudioChunk> {
    const id = requestId();
    const chunks: PreparedAudioChunk[] = [];
    let done = false;
    let failure: Error | undefined;
    let wake: (() => void) | undefined;
    const onAbort = () => {
      this.worker.postMessage({ type: 'abort', requestId: id } satisfies WorkerRequest);
      wake?.();
    };
    const failPrepare = (error: Error) => {
      done = true;
      failure = error;
      wake?.();
    };
    this.workerFailure = failPrepare;
    signal.addEventListener('abort', onAbort, { once: true });
    const previousHandler = this.worker.onmessage;
    this.worker.onmessage = (event: MessageEvent<WorkerResponse>) => {
      const response = event.data;
      this.telemetryListener?.(response.telemetry);
      if (response.requestId !== id) {
        previousHandler?.call(this.worker, event);
        return;
      }
      if (response.type === 'chunk') chunks.push({ ...response.chunk, bytes: new Uint8Array(response.chunk.bytes) });
      if (response.type === 'done' || response.type === 'error') {
        done = true;
        if (response.type === 'error') failure = new Error(response.code);
      }
      wake?.();
    };
    try {
      this.worker.postMessage({ type: 'prepare', requestId: id, file, budget } satisfies WorkerRequest);
      while (!done || chunks.length) {
        if (chunks.length) {
          yield chunks.shift() as PreparedAudioChunk;
        } else {
          if (signal.aborted) throw new DOMException('The operation was aborted.', 'AbortError');
          await new Promise<void>((resolve) => { wake = resolve; });
          wake = undefined;
        }
      }
      if (failure) throw failure;
    } finally {
      signal.removeEventListener('abort', onAbort);
      if (this.workerFailure === failPrepare) this.workerFailure = undefined;
      this.worker.onmessage = previousHandler;
      if (signal.aborted) this.worker.postMessage({ type: 'abort', requestId: id } satisfies WorkerRequest);
    }
  }

  terminate(): void {
    const error = new Error('WORKER_TERMINATED');
    for (const entry of this.pending.values()) entry.reject(error);
    this.pending.clear();
    this.workerFailure?.(error);
    this.workerFailure = undefined;
    this.worker.terminate();
  }
}
