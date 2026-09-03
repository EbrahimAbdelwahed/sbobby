import { redirect } from 'next/navigation';

export default async function SignInPage({ searchParams }: { searchParams: Promise<{ error?: string; next?: string }> }) {
  const params = await searchParams;
  return (
    <main className="auth-shell">
      <section className="auth-card">
        <span className="brand-mark">SB</span>
        <p className="eyebrow">BETA PRIVATA</p>
        <h1>Entra in Sbobby</h1>
        <p className="auth-copy">La sbobina parte dall’audio e arriva pronta da leggere, cercare e scaricare.</p>
        <form action={async (formData) => {
          'use server';
          const code = String(formData.get('code') ?? '');
          const next = String(formData.get('next') ?? '/app');
          if (!process.env.APP_ACCESS_CODE || code !== process.env.APP_ACCESS_CODE) redirect(`/sign-in?error=1&next=${encodeURIComponent(next)}`);
          const { cookies } = await import('next/headers');
          const store = await cookies();
          store.set('sbobby_session', process.env.APP_SESSION_TOKEN ?? '', { httpOnly: true, sameSite: 'lax', secure: process.env.NODE_ENV === 'production', maxAge: 60 * 60 * 24 * 30, path: '/' });
          redirect(next.startsWith('/app') ? next : '/app');
        }}>
          <input type="hidden" name="next" value={params.next ?? '/app'} />
          <label className="field"><span>Codice di accesso</span><input name="code" type="password" autoComplete="current-password" required autoFocus /></label>
          {params.error && <p className="form-error" role="alert">Codice non valido.</p>}
          <button className="primary wide" type="submit">Continua</button>
        </form>
        <p className="fine-print">Accesso riservato al gruppo studenti invitato.</p>
      </section>
    </main>
  );
}
