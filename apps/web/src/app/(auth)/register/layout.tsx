import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Register',
  description: 'Create a BuildWithPNJ account to access the developer workspace.',
  robots: {
    index: false,
    follow: false,
  },
};

export default function RegisterLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
