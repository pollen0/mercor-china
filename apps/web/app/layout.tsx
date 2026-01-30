import type { Metadata, Viewport } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'ZhiMian 智面 - AI-Powered Recruiting Platform',
  description: 'AI-powered recruiting platform with video interviews, AI scoring, and employer dashboard. Built for New Energy/EV and Sales verticals in China.',
  keywords: ['AI interview', 'recruiting', 'hiring', 'China', 'New Energy', 'EV', 'Sales', '智能面试', '招聘'],
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#FAFAFA' },
    { media: '(prefers-color-scheme: dark)', color: '#0F0F0F' },
  ],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans antialiased">
        {children}
      </body>
    </html>
  )
}
