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

// Default Logo Component - Simple text mark
function Logo() {
  return (
    <Link href="/" className="font-semibold text-stone-900 text-lg tracking-tight hover:text-stone-600 transition-colors duration-300">
      Pathway
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
      className="md:hidden inline-flex items-center justify-center p-2 rounded-lg text-stone-500 hover:text-stone-900 hover:bg-stone-100 transition-colors duration-300"
      aria-expanded={isOpen}
    >
      <span className="sr-only">{isOpen ? 'Close menu' : 'Open menu'}</span>
      {isOpen ? (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6 18L18 6M6 6l12 12" />
        </svg>
      ) : (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 6h16M4 12h16M4 18h16" />
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
  // Note: These are for employer dashboard - route is /employer/dashboard
  const defaultNavItems: NavItem[] = variant === 'dashboard'
    ? [
        { label: 'Overview', href: '/employer/dashboard' },
        { label: 'Interviews', href: '/employer/dashboard?tab=interviews' },
        { label: 'Jobs', href: '/employer/dashboard?tab=jobs' },
        { label: 'Talent Pool', href: '/employer/dashboard?tab=talent' },
      ]
    : []

  const items = navItems ?? defaultNavItems

  // Default right content based on variant
  // Landing page is student-focused, so nav buttons go to student auth
  const defaultRightContent = variant === 'default' ? (
    <div className="flex items-center gap-2">
      <Link
        href="/candidate/login"
        className="text-sm text-stone-500 hover:text-stone-900 transition-colors duration-300 px-3 py-2"
      >
        Log in
      </Link>
      <Link
        href="/register"
        className="text-sm font-medium text-white bg-stone-900 hover:bg-stone-800 px-5 py-2 rounded-full transition-all duration-300 hover:scale-[1.02]"
      >
        Sign Up
      </Link>
    </div>
  ) : null

  const right = rightContent ?? defaultRightContent

  return (
    <nav
      className={cn(
        'fixed top-0 left-0 right-0 z-50 bg-stone-50/80 backdrop-blur-md border-b border-stone-100',
        className
      )}
    >
      <div className="max-w-5xl mx-auto px-4 sm:px-6">
        <div className="flex justify-between items-center h-14">
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
                      'px-3 py-2 text-sm rounded-lg transition-colors',
                      isActive
                        ? 'text-stone-900 font-medium'
                        : 'text-stone-500 hover:text-stone-900'
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
          <div className="md:hidden py-4 border-t border-stone-100 animate-fade-in">
            {items.length > 0 && (
              <div className="space-y-1 mb-4">
                {items.map((item) => {
                  const isActive = item.active ?? pathname === item.href
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={cn(
                        'block px-4 py-2 text-sm rounded-lg transition-colors',
                        isActive
                          ? 'text-stone-900 font-medium'
                          : 'text-stone-500 hover:text-stone-900'
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
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-stone-100 rounded-full">
              <div className="w-5 h-5 bg-teal-600 rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-xs">
                  {companyName.charAt(0)}
                </span>
              </div>
              <span className="text-sm text-stone-600">{companyName}</span>
            </div>
          )}
          {onLogout && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onLogout}
              className="text-stone-400 hover:text-stone-900"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </Button>
          )}
        </div>
      }
    />
  )
}

// Admin Navbar - No employer navigation, just logo + admin indicator + logout
interface AdminNavbarProps {
  onLogout?: () => void
}

export function AdminNavbar({ onLogout }: AdminNavbarProps) {
  return (
    <Navbar
      navItems={[]} // No navigation items for admin
      rightContent={
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-teal-50 rounded-full">
            <div className="w-5 h-5 bg-teal-600 rounded-full flex items-center justify-center">
              <span className="text-white font-medium text-xs">A</span>
            </div>
            <span className="text-sm text-teal-700 font-medium">Admin</span>
          </div>
          {onLogout && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onLogout}
              className="text-stone-400 hover:text-stone-900"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </Button>
          )}
        </div>
      }
    />
  )
}

export { Logo }
