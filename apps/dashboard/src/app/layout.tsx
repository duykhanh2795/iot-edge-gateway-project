import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'IoT Environment Monitor',
  description: 'Dashboard for ESP32 environmental telemetry and relay control.',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

