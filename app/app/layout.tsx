import './globals.css';

export const metadata = {
  title: 'Kronos Predictor',
  description: 'AI-powered cryptocurrency price prediction',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}