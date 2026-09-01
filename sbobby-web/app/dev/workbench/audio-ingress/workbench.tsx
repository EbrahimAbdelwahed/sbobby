'use client';

import { useEffect, useRef, useState } from 'react';
import { AUDIO_CHUNK_BUDGET, AUDIO_RESOURCE_CAPS, isSupportedAudioFile, type AudioSourceDescriptor, type PreparedAudioChunk } from '@/src/client/audio/chunk-budget';
import { BrowserAudioPreparer } from '@/src/client/audio/preparer';
import type { WorkerTelemetry } from '@/src/client/audio/worker-protocol';

type Status = 'idle' | 'inspecting' | 'ready' | 'preparing' | 'complete' | 'failed' | 'aborted';
type ChunkRow = { sequence: number; startMs: number; endMs: number; sizeBytes: number };
type NormalizedSpan = { startMs: number; endMs: number; text: string };
type ProbeResult = { sequence: number; status: 'accepted' | 'rejected'; latencyMs: number; spans: NormalizedSpan[] };
type StorageAudit = { indexedDbRecords: number; cacheEntries: number; blobUrls: number };

function formatBytes(value: number): string {
  if (value < 1_000_000) return `${Math.round(value / 1_000)} KB`;
  return `${(value / 1_000_000).toFixed(2)} MB`;
}

function formatDuration(value: number): string {
  const totalSeconds = Math.round(value / 1000);
  return `${Math.floor(totalSeconds / 3600)}h ${String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, '0')}m`;
}

export default function AudioIngressWorkbench() {
  const [status, setStatus] = useState<Status>('idle');
  const [descriptor, setDescriptor] = useState<AudioSourceDescriptor | null>(null);
  const [chunks, setChunks] = useState<ChunkRow[]>([]);
  const [probeResults, setProbeResults] = useState<ProbeResult[]>([]);
  const [probeSecret, setProbeSecret] = useState('');
  const [liveProbe, setLiveProbe] = useState(false);
  const [audit, setAudit] = useState<StorageAudit>({ indexedDbRecords: 0, cacheEntries: 0, blobUrls: 0 });
  const [telemetry, setTelemetry] = useState<WorkerTelemetry | null>(null);
  const [error, setError] = useState<string | null>(null);
  const preparerRef = useRef<BrowserAudioPreparer | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => () => {
    abortRef.current?.abort();
    preparerRef.current?.terminate();
  }, []);

  const auditStorage = async () => {
    let indexedDbRecords = 0;
    let cacheEntries = 0;
    if ('indexedDB' in window && 'databases' in indexedDB) {
      const databases = await indexedDB.databases();
      for (const database of databases) {
        if (!database.name) continue;
        indexedDbRecords += await new Promise<number>((resolve) => {
          const request = indexedDB.open(database.name as string);
          request.onerror = () => resolve(0);
          request.onsuccess = () => {
            const db = request.result;
            const stores = Array.from(db.objectStoreNames);
            if (!stores.length) { db.close(); resolve(0); return; }
            const transaction = db.transaction(stores, 'readonly');
            let total = 0;
            let pending = stores.length;
            for (const storeName of stores) {
              const count = transaction.objectStore(storeName).count();
              count.onsuccess = () => { total += count.result; pending -= 1; if (pending === 0) { db.close(); resolve(total); } };
              count.onerror = () => { pending -= 1; if (pending === 0) { db.close(); resolve(total); } };
            }
          };
        });
      }
    }
    if ('caches' in window) {
      for (const cacheName of await caches.keys()) cacheEntries += (await (await caches.open(cacheName)).keys()).length;
    }
    setAudit({ indexedDbRecords, cacheEntries, blobUrls: 0 });
  };

  useEffect(() => {
    const auditTimer = window.setTimeout(() => { void auditStorage(); }, 0);
    return () => window.clearTimeout(auditTimer);
  }, []);

  const reset = (clearFileInput = true) => {
    abortRef.current?.abort();
    preparerRef.current?.terminate();
    preparerRef.current = null;
    if (clearFileInput) {
      const input = document.querySelector<HTMLInputElement>('#audio-file');
      if (input) input.value = '';
    }
    setStatus('idle');
    setDescriptor(null);
    setChunks([]);
    setProbeResults([]);
    setProbeSecret('');
    setTelemetry(null);
    setError(null);
    void auditStorage();
  };

  const sendProbeChunk = async (chunk: PreparedAudioChunk): Promise<ProbeResult> => {
    const startedAt = performance.now();
    const response = await fetch('/api/internal/spikes/transcription-chunk', {
      method: 'POST',
      headers: {
        'content-type': AUDIO_CHUNK_BUDGET.internalMediaType,
        'x-audio-probe': probeSecret,
        'x-audio-sequence': String(chunk.sequence),
        'x-audio-start-ms': String(chunk.startMs),
        'x-audio-end-ms': String(chunk.endMs),
        'x-audio-source-start-ms': String(chunk.sourceStartMs),
        'x-audio-source-end-ms': String(chunk.sourceEndMs),
        'x-audio-byte-length': String(chunk.bytes.byteLength)
      },
      body: chunk.bytes.slice().buffer as ArrayBuffer
    });
    const body = await response.text();
    if (new TextEncoder().encode(body).byteLength > AUDIO_CHUNK_BUDGET.maxResponseBytes) throw new Error('PROBE_RESPONSE_LIMIT');
    let payload: { spans?: unknown } = {};
    try { payload = JSON.parse(body) as { spans?: unknown }; } catch { /* stable public route errors are not JSON payloads */ }
    if (!response.ok) throw new Error(typeof (payload as { error?: unknown }).error === 'string' ? String((payload as { error: string }).error) : `PROBE_HTTP_${response.status}`);
    const spans = Array.isArray(payload.spans) ? payload.spans.flatMap((value): NormalizedSpan[] => {
      if (!value || typeof value !== 'object') return [];
      const span = value as { startMs?: unknown; endMs?: unknown; text?: unknown };
      return typeof span.startMs === 'number' && typeof span.endMs === 'number' && typeof span.text === 'string'
        ? [{ startMs: span.startMs, endMs: span.endMs, text: span.text.slice(0, 240) }]
        : [];
    }) : [];
    return { sequence: chunk.sequence, status: 'accepted', latencyMs: Math.round(performance.now() - startedAt), spans };
  };

  const inspect = async (file: File) => {
    reset(false);
    if (!isSupportedAudioFile(file) || file.size > AUDIO_RESOURCE_CAPS.maxSourceBytes) {
      setStatus('failed');
      setError('UNSUPPORTED_AUDIO_OR_SOURCE_SIZE_LIMIT');
      return;
    }
    const preparer = new BrowserAudioPreparer(setTelemetry);
    preparerRef.current = preparer;
    setStatus('inspecting');
    try {
      const result = await preparer.inspect(file);
      setDescriptor(result);
      setStatus('ready');
    } catch (cause) {
      setStatus('failed');
      setError(cause instanceof Error ? cause.message : 'INSPECT_FAILED');
      preparer.terminate();
    }
  };

  const prepare = async () => {
    const input = document.querySelector<HTMLInputElement>('#audio-file');
    const file = input?.files?.[0];
    if (!file || !preparerRef.current) return;
    const controller = new AbortController();
    abortRef.current = controller;
    setStatus('preparing');
    setChunks([]);
    setError(null);
    try {
      if (liveProbe && !probeSecret) throw new Error('PROBE_SECRET_REQUIRED');
      for await (const chunk of preparerRef.current.prepare(file, AUDIO_CHUNK_BUDGET, controller.signal)) {
        const row = { sequence: chunk.sequence, startMs: chunk.startMs, endMs: chunk.endMs, sizeBytes: chunk.bytes.byteLength };
        if (liveProbe) {
          try {
            const result = await sendProbeChunk(chunk);
            setProbeResults((previous) => [...previous, result]);
          } finally {
            chunk.bytes.fill(0);
          }
        } else {
          chunk.bytes.fill(0);
        }
        setChunks((previous) => [...previous, row]);
      }
      setStatus('complete');
    } catch (cause) {
      setStatus(controller.signal.aborted ? 'aborted' : 'failed');
      setError(cause instanceof Error ? cause.message : 'PREPARE_FAILED');
    } finally {
      abortRef.current = null;
      void auditStorage();
    }
  };

  const abort = () => abortRef.current?.abort();
  const percentage = descriptor ? Math.min(100, Math.round((chunks.length / Math.max(1, Math.ceil(descriptor.durationMs / AUDIO_CHUNK_BUDGET.chunkDurationMs))) * 100)) : 0;

  return (
    <main className="shell">
      <header className="topbar">
        <div><span className="eyebrow">S00 · FEASIBILITY</span><h1>Audio ingress lab</h1></div>
        <span className={`status status-${status}`}>{status.toUpperCase()}</span>
      </header>
      <section className="hero">
        <div>
          <p className="kicker">Browser-only preparation</p>
          <h2>Un file locale. Chunk grezzi. Nessuna persistenza.</h2>
          <p className="lede">Questa workbench misura la conversione M4A/MP3 in chunk MP3 indipendentemente decodificabili, prima di qualsiasi chiamata provider.</p>
        </div>
        <div className="hero-mark" aria-hidden="true">↘</div>
      </section>
      <div className="grid">
        <section className="panel import-panel" aria-labelledby="source-title">
          <div className="panel-heading"><span className="step">01</span><div><h3 id="source-title">Scegli una sorgente</h3><p>Il file resta nella memoria del browser.</p></div></div>
          <label className="dropzone" htmlFor="audio-file"><span className="drop-icon">↑</span><strong>Importa audio</strong><span>MP3 o M4A · massimo 250 MiB</span><input id="audio-file" type="file" accept=".mp3,.m4a,audio/mpeg,audio/mp4" onChange={(event) => { const file = event.target.files?.[0]; if (file) void inspect(file); }} /></label>
          {descriptor && <dl className="facts"><div><dt>Formato</dt><dd>{descriptor.nameHint.toUpperCase()}</dd></div><div><dt>Dimensione</dt><dd>{formatBytes(descriptor.sizeBytes)}</dd></div><div><dt>Durata</dt><dd>{formatDuration(descriptor.durationMs)}</dd></div><div><dt>Campioni stimati</dt><dd>{descriptor.decodedSamplesEstimate.toLocaleString('it-IT')}</dd></div></dl>}
          {error && <p className="error" role="alert">{error}</p>}
        </section>
        <section className="panel limits-panel" aria-labelledby="limits-title">
          <div className="panel-heading"><span className="step">02</span><div><h3 id="limits-title">Contratto misurabile</h3><p>Valori fissi della slice S00.</p></div></div>
          <dl className="limits"><div><dt>Output</dt><dd>MP3 mono · 16 kHz · 48 kbps</dd></div><div><dt>Chunk body</dt><dd>≤ {formatBytes(AUDIO_CHUNK_BUDGET.maxRequestBodyBytes)}</dd></div><div><dt>Finestra</dt><dd>{AUDIO_CHUNK_BUDGET.chunkDurationMs / 60_000} min + {AUDIO_CHUNK_BUDGET.overlapMs / 1000}s overlap</dd></div><div><dt>Risposta</dt><dd>≤ {formatBytes(AUDIO_CHUNK_BUDGET.maxResponseBytes)}</dd></div></dl>
          <div className="meter" aria-label={`${percentage}% chunk preparati`}><span style={{ width: `${percentage}%` }} /></div>
          <label className="probe-toggle"><input type="checkbox" checked={liveProbe} onChange={(event) => setLiveProbe(event.target.checked)} /> <span>Invia chunk al probe Groq live</span></label>
          {liveProbe && <label className="secret-field"><span>Chiave probe (solo memoria tab)</span><input type="password" value={probeSecret} autoComplete="off" onChange={(event) => setProbeSecret(event.target.value)} /></label>}
          <div className="actions">{status === 'ready' && <button className="primary" type="button" onClick={() => void prepare()}>Prepara chunk</button>}{status === 'preparing' && <button className="danger" type="button" onClick={abort}>Annulla e cancella memoria</button>}{(status === 'complete' || status === 'aborted' || status === 'failed') && <button className="secondary" type="button" onClick={() => reset()}>Nuova sorgente</button>}</div>
        </section>
        <section className="panel telemetry-panel" aria-labelledby="telemetry-title">
          <div className="panel-heading"><span className="step">03</span><div><h3 id="telemetry-title">Telemetria</h3><p>Solo contatori, mai audio o filename.</p></div></div>
          <dl className="telemetry"><div><dt>Chunk prodotti</dt><dd>{chunks.length}</dd></div><div><dt>Output totale</dt><dd>{formatBytes(chunks.reduce((total, chunk) => total + chunk.sizeBytes, 0))}</dd></div><div><dt>Heap stimato</dt><dd>{formatBytes(telemetry?.peakBytesEstimate ?? 0)}</dd></div><div><dt>Tempo worker</dt><dd>{Math.round(telemetry?.elapsedMs ?? 0)} ms</dd></div></dl>
          <div className="chunk-list" aria-live="polite">{chunks.length === 0 ? <p className="muted">I chunk appariranno qui non appena disponibili.</p> : chunks.map((chunk) => <div className="chunk-row" key={chunk.sequence}><span>#{String(chunk.sequence + 1).padStart(2, '0')}</span><span>{Math.round(chunk.startMs / 1000)}–{Math.round(chunk.endMs / 1000)}s</span><strong>{formatBytes(chunk.sizeBytes)}</strong></div>)}</div>
          {probeResults.length > 0 && <div className="probe-results">{probeResults.map((result) => <div key={`probe-${result.sequence}`}><div className="chunk-row"><span>Groq #{result.sequence + 1}</span><span>{result.spans.length} span · {result.latencyMs} ms</span><strong>{result.status}</strong></div>{result.spans.slice(0, 8).map((span) => <p className="probe-span" key={`${result.sequence}-${span.startMs}-${span.endMs}`}>{span.startMs}–{span.endMs} ms · {span.text}</p>)}</div>)}</div>}
        </section>
        <section className="panel audit-panel" aria-labelledby="audit-title">
          <div className="panel-heading"><span className="step">04</span><div><h3 id="audit-title">Storage audit</h3><p>Controllo negativo intenzionale.</p></div></div>
          <div className="audit-grid"><div><span className="audit-value">{audit.indexedDbRecords}</span><span>IndexedDB records</span></div><div><span className="audit-value">{audit.cacheEntries}</span><span>Cache entries</span></div><div><span className="audit-value">{audit.blobUrls}</span><span>Blob URLs created</span></div></div>
          <p className="audit-note">La preview Groq è disabilitata finché il deployment non espone il probe server-side protetto.</p>
        </section>
      </div>
    </main>
  );
}
