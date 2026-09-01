import type { AudioChunkBudget, AudioSourceDescriptor, PreparedAudioChunk } from './chunk-budget';

export type WorkerTelemetry = {
  phase: 'loading' | 'inspecting' | 'encoding' | 'complete' | 'aborted' | 'failed';
  sequence?: number;
  chunksProduced: number;
  inputBytes: number;
  outputBytes: number;
  elapsedMs: number;
  peakBytesEstimate: number;
  message?: string;
};

export type WorkerRequest =
  | { type: 'inspect'; requestId: string; file: File }
  | { type: 'prepare'; requestId: string; file: File; budget: AudioChunkBudget }
  | { type: 'abort'; requestId: string };

export type WorkerResponse =
  | { type: 'ready'; requestId: string; telemetry: WorkerTelemetry }
  | { type: 'descriptor'; requestId: string; descriptor: AudioSourceDescriptor; telemetry: WorkerTelemetry }
  | { type: 'chunk'; requestId: string; chunk: Omit<PreparedAudioChunk, 'bytes'> & { bytes: ArrayBuffer }; telemetry: WorkerTelemetry }
  | { type: 'done'; requestId: string; telemetry: WorkerTelemetry }
  | { type: 'error'; requestId: string; code: string; telemetry: WorkerTelemetry };
