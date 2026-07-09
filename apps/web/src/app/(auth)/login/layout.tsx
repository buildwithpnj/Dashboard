import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Login',
  description: 'Log in to your BuildWithPNJ account to access the developer workspace.',
  robots: {
    index: false,
    follow: false,
  },
};

export default function LoginLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
