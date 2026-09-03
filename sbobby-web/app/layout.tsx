import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Sbobby · Audio → Sbobina',
  description: 'Trasforma una lezione registrata in trascrizione, sbobina e materiale di studio.'
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="it"><body>{children}</body></html>;
}
