'use client';

import { upload } from '@vercel/blob/client';
import { useEffect, useMemo, useRef, useState } from 'react';
import { downloadTextPdf } from '@/src/client/pdf';

type Stage = 'idle' | 'uploading' | 'queued' | 'processing' | 'ready' | 'failed';
type Output = { title?: string; transcript?: string; full_document?: string; study_document?: string; stages?: string[] };
type WorkerSection = { title?: string; text?: string };
type WorkerOutput = {
  title?: string;
  transcript?: { text?: string };
  full?: { sections?: WorkerSection[] };
  study?: { sections?: WorkerSection[] };
  stages?: Array<string | { name?: string }>;
};
type SavedProject = { id: string; title: string; createdAt: string; expiresAt: string; output: Output };

const stageLabel: Record<Stage, string> = { idle: 'Pronto', uploading: 'Caricamento audio', queued: 'In coda', processing: 'Elaborazione', ready: 'Completato', failed: 'Da riprovare' };

function renderSections(sections?: WorkerSection[]) {
  return sections?.map((section) => `${section.title ? `# ${section.title}\n\n` : ''}${section.text ?? ''}`.trim()).filter(Boolean).join('\n\n') ?? '';
}

function normalizeWorkerOutput(value: WorkerOutput): Output {
  return {
    title: value.title,
    transcript: value.transcript?.text ?? '',
    full_document: renderSections(value.full?.sections),
    study_document: renderSections(value.study?.sections),
    stages: value.stages?.map((stage) => typeof stage === 'string' ? stage : stage.name ?? '').filter(Boolean),
  };
}

export default function Workspace() {
  const [stage, setStage] = useState<Stage>('idle');
  const [progress, setProgress] = useState(0);
  const [title, setTitle] = useState('');
  const [output, setOutput] = useState<Output | null>(null);
  const [tab, setTab] = useState<'full' | 'study' | 'transcript'>('full');
  const [query, setQuery] = useState('');
  const [error, setError] = useState('');
  const [saved, setSaved] = useState<SavedProject[]>([]);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    const projects = JSON.parse(localStorage.getItem('sbobby-projects') ?? '[]') as SavedProject[];
    const now = Date.now();
    const current = projects.filter((item) => Date.parse(item.expiresAt) > now);
    // Hydrate browser-owned projects after the server render.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setSaved(current);
    localStorage.setItem('sbobby-projects', JSON.stringify(current));
    return () => { if (timer.current) clearInterval(timer.current); };
  }, []);

  const persist = (result: Output, resolvedTitle: string) => {
    const project: SavedProject = { id: crypto.randomUUID(), title: resolvedTitle, createdAt: new Date().toISOString(), expiresAt: new Date(Date.now() + 30 * 864e5).toISOString(), output: result };
    setSaved((previous) => {
      const next = [project, ...previous].slice(0, 20);
      localStorage.setItem('sbobby-projects', JSON.stringify(next));
      return next;
    });
  };

  const poll = (jobId: string, audioUrl: string, resolvedTitle: string) => {
    timer.current = setInterval(async () => {
      const response = await fetch(`/api/jobs/${encodeURIComponent(jobId)}`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ audioUrl }) });
      const job = await response.json() as { status?: string; output?: WorkerOutput; error?: string };
      if (job.status === 'IN_QUEUE') { setStage('queued'); setProgress(35); }
      if (job.status === 'IN_PROGRESS') { setStage('processing'); setProgress(65); }
      if (job.status === 'COMPLETED' && job.output) {
        if (timer.current) clearInterval(timer.current);
        const result = normalizeWorkerOutput(job.output);
        setOutput(result); setStage('ready'); setProgress(100); persist(result, resolvedTitle);
      }
      if (job.status === 'FAILED' || job.error) {
        if (timer.current) clearInterval(timer.current);
        setError('Il worker non ha completato la lezione. Riprova.'); setStage('failed');
      }
    }, 3000);
  };

  const start = async (file: File) => {
    setError(''); setOutput(null); setStage('uploading'); setProgress(5);
    const ext = file.name.toLowerCase().endsWith('.m4a') ? 'm4a' : 'mp3';
    const resolvedTitle = title.trim() || file.name.replace(/\.(m4a|mp3)$/i, '');
    try {
      const blob = await upload(`audio/${crypto.randomUUID()}.${ext}`, file, { access: 'public', handleUploadUrl: '/api/upload', multipart: file.size > 20 * 1024 * 1024 });
      setProgress(28); setStage('queued');
      const response = await fetch('/api/jobs/start', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ audioUrl: blob.url, title: resolvedTitle }) });
      const job = await response.json() as { id?: string; error?: string };
      if (!response.ok || !job.id) throw new Error(job.error ?? 'JOB_START_FAILED');
      poll(job.id, blob.url, resolvedTitle);
    } catch (cause) {
      setError(cause instanceof Error && cause.message === 'WORKER_NOT_CONFIGURED' ? 'Il worker Runpod non è ancora configurato.' : 'Avvio non riuscito. Riprova tra poco.');
      setStage('failed');
    }
  };

  const body = tab === 'transcript' ? output?.transcript : tab === 'study' ? output?.study_document : output?.full_document;
  const highlighted = useMemo(() => {
    if (!body || !query.trim()) return body;
    const index = body.toLocaleLowerCase('it').indexOf(query.toLocaleLowerCase('it'));
    if (index < 0) return body;
    return `${body.slice(0, index)}⟦${body.slice(index, index + query.length)}⟧${body.slice(index + query.length)}`;
  }, [body, query]);

  return (
    <main className="product-shell">
      <header className="product-header"><div className="brand"><span className="brand-mark">SB</span><div><strong>Sbobby</strong><span>Audio → Sbobina</span></div></div><span className={`run-state state-${stage}`}>{stageLabel[stage]}</span></header>
      <section className="product-hero"><div><p className="eyebrow">NUOVA LEZIONE</p><h1>Carica. Aspetta.<br />Studia.</h1><p>Trascrizione Groq, sbobina completa e versione studio. Il lavoro pesante gira sul worker, anche per lezioni lunghe.</p></div>
        <form className="upload-card" onSubmit={(event) => { event.preventDefault(); const file = (event.currentTarget.elements.namedItem('audio') as HTMLInputElement).files?.[0]; if (file) void start(file); }}>
          <label className="field"><span>Titolo lezione</span><input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Es. Anatomia · Lezione 04" /></label>
          <label className="upload-zone"><input name="audio" type="file" accept=".mp3,.m4a,audio/mpeg,audio/mp4" required /><span className="upload-glyph">＋</span><strong>Scegli MP3 o M4A</strong><small>Massimo 250 MB</small></label>
          <button className="primary wide" disabled={!['idle', 'ready', 'failed'].includes(stage)}>Genera sbobina</button>
          {stage !== 'idle' && <div className="run-progress" aria-live="polite"><div><span>{stageLabel[stage]}</span><strong>{progress}%</strong></div><progress max="100" value={progress} /></div>}
          {error && <p className="form-error" role="alert">{error}</p>}
        </form>
      </section>

      {output && <section className="document-area">
        <div className="document-toolbar"><nav aria-label="Documenti"><button onClick={() => setTab('full')} className={tab === 'full' ? 'active' : ''}>Sbobina</button><button onClick={() => setTab('study')} className={tab === 'study' ? 'active' : ''}>Studio</button><button onClick={() => setTab('transcript')} className={tab === 'transcript' ? 'active' : ''}>Trascrizione</button></nav><label className="search"><span>⌕</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Cerca nella lezione" /></label></div>
        <article className="document"><header><p>{title || output.title}</p><h2>{tab === 'full' ? 'Sbobina completa' : tab === 'study' ? 'Documento di studio' : 'Trascrizione letterale'}</h2><button className="secondary" onClick={() => void downloadTextPdf(title || output.title || 'lezione', tab, body ?? '')}>Scarica PDF</button></header><pre>{highlighted}</pre></article>
      </section>}

      {saved.length > 0 && <section className="library"><div><p className="eyebrow">NEL BROWSER</p><h2>Lezioni recenti</h2></div><div className="library-grid">{saved.map((project) => <button key={project.id} onClick={() => { setTitle(project.title); setOutput(project.output); setStage('ready'); setProgress(100); }}><strong>{project.title}</strong><span>{new Date(project.createdAt).toLocaleDateString('it-IT')} · scade tra 30 giorni</span></button>)}</div></section>}
    </main>
  );
}
