'use client'

import * as React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'

interface NavItem {
  label: string
  href: string
  active?: boolean
}

interface NavbarProps {
  variant?: 'default' | 'dashboard'
  logo?: React.ReactNode
  navItems?: NavItem[]
  rightContent?: React.ReactNode
  className?: string
}

// Default Logo Component
function Logo() {
  return (
    <Link href="/" className="flex items-center gap-2.5 group">
      <div className="w-9 h-9 bg-gradient-to-br from-brand-500 to-brand-600 rounded-xl flex items-center justify-center shadow-brand group-hover:shadow-brand-lg transition-shadow">
        <span className="text-white font-bold text-sm">智</span>
      </div>
      <span className="font-semibold text-warm-900 text-lg">ZhiMian 智面</span>
    </Link>
  )
}

// Mobile Menu Button
function MobileMenuButton({
  isOpen,
  onClick,
}: {
  isOpen: boolean
  onClick: () => void
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="md:hidden inline-flex items-center justify-center p-2 rounded-lg text-warm-600 hover:text-warm-900 hover:bg-warm-100 transition-colors"
      aria-expanded={isOpen}
    >
      <span className="sr-only">{isOpen ? 'Close menu' : 'Open menu'}</span>
      {isOpen ? (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      ) : (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      )}
    </button>
  )
}

export function Navbar({
  variant = 'default',
  logo,
  navItems,
  rightContent,
  className,
}: NavbarProps) {
  const pathname = usePathname()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false)

  // Default nav items based on variant
  const defaultNavItems: NavItem[] = variant === 'dashboard'
    ? [
        { label: 'Overview', href: '/dashboard' },
        { label: 'Interviews', href: '/dashboard/interviews' },
        { label: 'Jobs', href: '/dashboard/jobs' },
        { label: 'Talent Pool', href: '/dashboard/talent-pool' },
      ]
    : []

  const items = navItems ?? defaultNavItems

  // Default right content based on variant
  const defaultRightContent = variant === 'default' ? (
    <div className="flex items-center gap-3">
      <Link
        href="/candidate/login"
        className="text-sm font-medium text-warm-600 hover:text-warm-900 transition-colors px-3 py-2"
      >
        Candidate Login
      </Link>
      <Link
        href="/login"
        className="text-sm font-medium text-warm-600 hover:text-warm-900 transition-colors px-3 py-2"
      >
        Employer Login
      </Link>
    </div>
  ) : null

  const right = rightContent ?? defaultRightContent

  return (
    <nav
      className={cn(
        'fixed top-0 left-0 right-0 z-fixed bg-white/80 backdrop-blur-md border-b border-warm-100',
        className
      )}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          {logo ?? <Logo />}

          {/* Desktop Navigation */}
          {items.length > 0 && (
            <div className="hidden md:flex items-center gap-1">
              {items.map((item) => {
                const isActive = item.active ?? pathname === item.href
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      'px-3 py-2 text-sm font-medium rounded-lg transition-colors',
                      isActive
                        ? 'text-brand-600 bg-brand-50'
                        : 'text-warm-600 hover:text-warm-900 hover:bg-warm-100'
                    )}
                  >
                    {item.label}
                  </Link>
                )
              })}
            </div>
          )}

          {/* Right Content */}
          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-3">
              {right}
            </div>
            <MobileMenuButton
              isOpen={isMobileMenuOpen}
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            />
          </div>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-warm-100 animate-slide-down">
            {items.length > 0 && (
              <div className="space-y-1 mb-4">
                {items.map((item) => {
                  const isActive = item.active ?? pathname === item.href
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={cn(
                        'block px-4 py-2 text-sm font-medium rounded-lg transition-colors',
                        isActive
                          ? 'text-brand-600 bg-brand-50'
                          : 'text-warm-600 hover:text-warm-900 hover:bg-warm-100'
                      )}
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      {item.label}
                    </Link>
                  )
                })}
              </div>
            )}
            <div className="px-4">{right}</div>
          </div>
        )}
      </div>
    </nav>
  )
}

// Dashboard Navbar with user info
interface DashboardNavbarProps {
  companyName?: string
  onLogout?: () => void
}

export function DashboardNavbar({ companyName, onLogout }: DashboardNavbarProps) {
  return (
    <Navbar
      variant="dashboard"
      rightContent={
        <div className="flex items-center gap-3">
          {companyName && (
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-warm-100 rounded-lg">
              <div className="w-6 h-6 bg-gradient-to-br from-warm-600 to-warm-700 rounded-md flex items-center justify-center">
                <span className="text-white font-medium text-xs">
                  {companyName.charAt(0)}
                </span>
              </div>
              <span className="text-sm font-medium text-warm-700">{companyName}</span>
            </div>
          )}
          {onLogout && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onLogout}
              className="text-warm-500 hover:text-warm-700"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </Button>
          )}
        </div>
      }
    />
  )
}

export { Logo }
