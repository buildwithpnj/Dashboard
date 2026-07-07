import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import localFont from 'next/font/local';
import './globals.css';
import { Providers } from './providers';

const geistSans = Geist({
  subsets: ['latin'],
  variable: '--font-geist',
});

const geistMono = Geist_Mono({
  subsets: ['latin'],
  variable: '--font-geist-mono',
});

const pixelOperator = localFont({
  src: '../../public/fonts/PixelOperator-Bold.ttf',
  variable: '--font-pixel',
  weight: '700',
  style: 'normal',
});

export const metadata: Metadata = {
  title: {
    default: 'BuildWithPNJ | AI Engineering Lab & Products',
    template: '%s | BuildWithPNJ',
  },
  description:
    'Architecting autonomous AI products, context-aware systems, and production-ready agentic workflows. Discover verified system designs and active product blueprints.',
  metadataBase: new URL('https://buildwithpnj.com'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    title: 'BuildWithPNJ | AI Engineering Lab & Products',
    description: 'Architecting autonomous AI products, context-aware systems, and production-ready agentic workflows.',
    url: 'https://buildwithpnj.com',
    siteName: 'BuildWithPNJ',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'BuildWithPNJ | AI Engineering Lab & Products',
    description: 'Architecting autonomous AI products, context-aware systems, and production-ready agentic workflows.',
    creator: '@buildwithpnj',
  },
  robots: {
    index: true,
    follow: true,
  },
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} ${pixelOperator.variable}`}
      suppressHydrationWarning
    >
      <body className="min-h-screen bg-background text-foreground antialiased font-sans">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
