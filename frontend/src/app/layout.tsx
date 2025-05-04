// app/layout.tsx
'use client';

//import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Link from 'next/link';
import { CircuitBoard, Github, MessageSquare, Info } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ThemeProvider } from 'next-themes';
import { ThemeToggle } from '@/components/theme-toggle';
import { ErrorBoundary } from '@/components/error-boundary';

// Initialize the Inter font
const inter = Inter({ subsets: ['latin'] });

// Metadata for the application
// export const metadata: Metadata = {
//   title: 'Dynamic Workflow System',
//   description: 'An intelligent system that automatically selects and executes the optimal workflow pattern for each query using specialized AI agents.',
// };

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <div className="flex min-h-screen flex-col">
            <header className="sticky top-0 z-50 w-full border-b shadow-sm bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
              <div className="container flex h-14 items-center">
                <div className="mr-4 flex">
                  <Link href="/" className="mr-6 flex items-center space-x-2">
                    <CircuitBoard className="h-6 w-6" />
                    <span className="hidden font-bold sm:inline-block">
                      Dynamic Workflow
                    </span>
                  </Link>
                </div>
                <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
                  <div className="flex items-center gap-2">
                    <Button variant="ghost" size="icon">
                      <MessageSquare className="h-5 w-5" />
                    </Button>
                    <Button variant="ghost" size="icon">
                      <Github className="h-5 w-5" />
                    </Button>
                    <Link href="/about">
                      <Button variant="ghost" size="icon">
                        <Info className="h-5 w-5" />
                      </Button>
                    </Link>
                    <ThemeToggle />
                  </div>
                </div>
              </div>
            </header>
            <main className="flex-1">
              <ErrorBoundary>
                {children}
              </ErrorBoundary>
            </main>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}