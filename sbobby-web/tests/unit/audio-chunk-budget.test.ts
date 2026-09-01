import { describe, expect, it } from 'vitest';
import { AUDIO_CHUNK_BUDGET, AUDIO_RESOURCE_CAPS, assertRequestBodySize, chunkTimeRange, isSupportedAudioFile, validatePreparedChunk, validateSourceBounds } from '@/src/client/audio/chunk-budget';

describe('audio ingress budget', () => {
  it('accepts exactly the request cap and rejects one byte above it', () => {
    expect(() => assertRequestBodySize(AUDIO_CHUNK_BUDGET.maxRequestBodyBytes - 1)).not.toThrow();
    expect(() => assertRequestBodySize(AUDIO_CHUNK_BUDGET.maxRequestBodyBytes)).not.toThrow();
    expect(() => assertRequestBodySize(AUDIO_CHUNK_BUDGET.maxRequestBodyBytes + 1)).toThrow('REQUEST_BODY_LIMIT');
  });

  it('uses positive duration for live smoke while keeping 90 minutes as the fixture gate', () => {
    expect(AUDIO_RESOURCE_CAPS.requiredFixtureDurationMs).toBe(90 * 60 * 1000);
    expect(() => validateSourceBounds(1, 1)).not.toThrow();
    expect(() => validateSourceBounds(1, AUDIO_RESOURCE_CAPS.targetDurationMs + 1)).toThrow('SOURCE_DURATION_TARGET');
  });

  it('has gap-free canonical coverage and explicit bounded overlap', () => {
    const durationMs = 16 * 60 * 1000 + 1234;
    const ranges = Array.from({ length: Math.ceil(durationMs / AUDIO_CHUNK_BUDGET.chunkDurationMs) }, (_, sequence) => chunkTimeRange(durationMs, sequence));
    expect(ranges[0].startMs).toBe(0);
    expect(ranges.at(-1)?.endMs).toBe(durationMs);
    ranges.forEach((range, index) => {
      expect(range.sourceStartMs).toBeLessThanOrEqual(range.startMs);
      expect(range.sourceEndMs).toBeGreaterThanOrEqual(range.endMs);
      if (index) expect(range.startMs).toBe(ranges[index - 1].endMs);
      expect(range.startMs - range.sourceStartMs).toBeLessThanOrEqual(AUDIO_CHUNK_BUDGET.overlapMs);
      expect(range.sourceEndMs - range.endMs).toBeLessThanOrEqual(AUDIO_CHUNK_BUDGET.overlapMs);
    });
  });

  it('validates prepared media and common input extensions', () => {
    expect(isSupportedAudioFile({ name: 'lecture.MP3', type: 'audio/mpeg', size: 3 })).toBe(true);
    expect(isSupportedAudioFile({ name: 'lecture.m4a', type: 'audio/mp4', size: 3 })).toBe(true);
    expect(isSupportedAudioFile({ name: 'lecture.wav', type: 'audio/wav', size: 3 })).toBe(false);
    expect(() => validatePreparedChunk({ bytes: new Uint8Array(3_500_001), startMs: 0, endMs: 10, sourceStartMs: 0, sourceEndMs: 10, mediaType: 'audio/mpeg' })).toThrow('CHUNK_SIZE_LIMIT');
  });
});
