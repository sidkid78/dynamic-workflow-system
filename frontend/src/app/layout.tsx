// app/layout.tsx
'use client';

//import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Link from 'next/link';
import { CircuitBoard, Github, MessageSquare, Info, Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';

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
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen flex flex-col">
          {/* Header */}
          <header className="border-b bg-white sticky top-0 z-10">
            <div className="container mx-auto px-4 py-4">
              <div className="flex justify-between items-center">
                <Link href="/" className="flex items-center gap-2">
                  <CircuitBoard className="h-6 w-6 text-blue-600" />
                  <span className="font-bold text-lg">Dynamic Workflows</span>
                </Link>
                
                <nav className="hidden md:flex items-center gap-6">
                  <Link 
                    href="/chat" 
                    className="text-gray-600 hover:text-blue-600 transition-colors flex items-center gap-1"
                  >
                    <MessageSquare className="h-4 w-4" />
                    <span>Chat</span>
                  </Link>
                  <Link 
                    href="/about" 
                    className="text-gray-600 hover:text-blue-600 transition-colors flex items-center gap-1"
                  >
                    <Info className="h-4 w-4" />
                    <span>About</span>
                  </Link>
                  <a 
                    href="https://github.com/sidkid78/dynamic-workflow-system" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-gray-600 hover:text-blue-600 transition-colors flex items-center gap-1"
                  >
                    <Github className="h-4 w-4" />
                    <span>GitHub</span>
                  </a>
                  <Link href="/chat">
                    <Button size="sm" className="ml-4">Try it now</Button>
                  </Link>
                </nav>
                
                <div className="md:hidden">
                  <button 
                    type="button"
                    className="text-gray-600 hover:text-blue-600 transition-colors"
                    aria-label="Toggle menu"
                    onClick={() => {
                      const mobileMenu = document.getElementById('mobile-menu');
                      if (mobileMenu) {
                        mobileMenu.classList.toggle('hidden');
                      }
                    }}
                  >
                    <Menu className="h-6 w-6" />
                  </button>
                </div>
              </div>
            </div>
            
            {/* Mobile menu */}
            <div id="mobile-menu" className="md:hidden hidden">
              <div className="px-4 py-3 border-t space-y-1">
                <Link 
                  href="/chat" 
                  className="block py-2 px-3 rounded-md hover:bg-gray-100 text-gray-700"
                >
                  Chat
                </Link>
                <Link 
                  href="/about" 
                  className="block py-2 px-3 rounded-md hover:bg-gray-100 text-gray-700"
                >
                  About
                </Link>
                <a 
                  href="https://github.com/sidkid78/dynamic-workflow-system" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="block py-2 px-3 rounded-md hover:bg-gray-100 text-gray-700"
                >
                  GitHub
                </a>
                <Link href="/chat">
                  <Button className="w-full mt-2">Try it now</Button>
                </Link>
              </div>
            </div>
          </header>

          {/* Main content */}
          <main className="flex-grow">
            {children}
          </main>

          {/* Footer */}
          <footer className="bg-gray-900 text-white py-12">
            <div className="container mx-auto px-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div>
                  <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                    <CircuitBoard className="h-5 w-5" />
                    Dynamic Workflows
                  </h3>
                  <p className="text-gray-400 mb-4">
                    An intelligent system that dynamically selects optimal workflow patterns for processing user queries.
                  </p>
                  <div className="flex gap-4">
                    <a 
                      href="https://github.com/sidkid78/dynamic-workflow-system" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-gray-400 hover:text-white transition-colors"
                      aria-label="GitHub"
                    >
                      <Github className="h-5 w-5" />
                    </a>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-bold mb-4">Navigation</h3>
                  <ul className="space-y-2">
                    <li>
                      <Link href="/" className="text-gray-400 hover:text-white transition-colors">
                        Home
                      </Link>
                    </li>
                    <li>
                      <Link href="/chat" className="text-gray-400 hover:text-white transition-colors">
                        Chat
                      </Link>
                    </li>
                    <li>
                      <Link href="/about" className="text-gray-400 hover:text-white transition-colors">
                        About
                      </Link>
                    </li>
                  </ul>
                </div>
                
                <div>
                  <h3 className="text-lg font-bold mb-4">Resources</h3>
                  <ul className="space-y-2">
                    <li>
                      <a 
                        href="https://github.com/sidkid78/dynamic-workflow-system/blob/main/README.md" 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-gray-400 hover:text-white transition-colors"
                      >
                        Documentation
                      </a>
                    </li>
                    <li>
                      <a 
                        href="https://github.com/sidkid78/dynamic-workflow-system/issues" 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-gray-400 hover:text-white transition-colors"
                      >
                        Report Issues
                      </a>
                    </li>
                    <li>
                      <a 
                        href="https://github.com/sidkid78/dynamic-workflow-system/blob/main/CONTRIBUTING.md" 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-gray-400 hover:text-white transition-colors"
                      >
                        Contribute
                      </a>
                    </li>
                  </ul>
                </div>
              </div>
              
              <div className="mt-8 pt-8 border-t border-gray-800 text-center text-gray-400 text-sm">
                <p>© {new Date().getFullYear()} Dynamic Workflow System. All rights reserved.</p>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}