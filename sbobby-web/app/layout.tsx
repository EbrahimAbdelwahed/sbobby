import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Audio → Sbobina | Ingress probe',
  description: 'Browser-only audio ingress feasibility workbench.'
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="it"><body>{children}</body></html>;
}
