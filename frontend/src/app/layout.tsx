import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'WolfAlert - AI Intelligence Dashboard',
  description: 'AI-powered intelligence dashboard for utility and technology professionals',
  keywords: ['AI', 'intelligence', 'dashboard', 'utilities', 'technology', 'alerts'],
  authors: [{ name: 'WolfAlert Team' }],
  viewport: 'width=device-width, initial-scale=1',
  robots: 'index, follow',
  openGraph: {
    title: 'WolfAlert - AI Intelligence Dashboard',
    description: 'See only the AI developments that impact your business - with clear reasoning why they matter to you specifically.',
    url: 'https://wolfalert.app',
    siteName: 'WolfAlert',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'WolfAlert - AI Intelligence Dashboard',
    description: 'AI-powered intelligence dashboard for utility and technology professionals',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-gradient-to-br from-wolf-bg via-slate-900 to-wolf-primary min-h-screen text-white antialiased`}>
        {/* Animated Background */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-wolf-accent rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse" style={{animationDelay: '1s'}}></div>
        </div>
        
        {/* Main Content */}
        <div className="relative z-10">
          {children}
        </div>
      </body>
    </html>
  )
}