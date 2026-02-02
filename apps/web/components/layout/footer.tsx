import * as React from 'react'
import Link from 'next/link'
import { cn } from '@/lib/utils'

interface FooterProps extends React.HTMLAttributes<HTMLElement> {
  variant?: 'minimal' | 'default'
}

export function Footer({ variant = 'minimal', className, ...props }: FooterProps) {
  if (variant === 'minimal') {
    return (
      <footer
        className={cn('py-16 border-t border-stone-100 bg-white', className)}
        {...props}
      >
        <div className="max-w-5xl mx-auto px-6">
          <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
            <span className="font-medium text-stone-900">Pathway</span>
            <div className="flex items-center gap-8 text-sm text-stone-400">
              <Link href="/privacy" className="hover:text-stone-600 transition-colors duration-300">
                Privacy
              </Link>
              <Link href="/employer/login" className="hover:text-stone-600 transition-colors duration-300">
                Employers
              </Link>
              <span>&copy; {new Date().getFullYear()}</span>
            </div>
          </div>
        </div>
      </footer>
    )
  }

  return (
    <footer
      className={cn('py-20 bg-stone-50/50 border-t border-stone-100', className)}
      {...props}
    >
      <div className="max-w-5xl mx-auto px-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-12">
          {/* Brand */}
          <div className="col-span-2 md:col-span-1">
            <span className="font-semibold text-stone-900 text-lg">Pathway</span>
            <p className="mt-4 text-sm text-stone-500 leading-relaxed">
              The career platform for college students. Show your growth, land your first job.
            </p>
          </div>

          {/* For Students */}
          <div>
            <h4 className="font-medium text-stone-900 mb-4 text-sm">For Students</h4>
            <ul className="space-y-3 text-sm">
              <li>
                <Link href="/register" className="text-stone-500 hover:text-stone-900 transition-colors duration-300">
                  Create Account
                </Link>
              </li>
              <li>
                <Link href="/login" className="text-stone-500 hover:text-stone-900 transition-colors duration-300">
                  Sign In
                </Link>
              </li>
            </ul>
          </div>

          {/* For Employers */}
          <div>
            <h4 className="font-medium text-stone-900 mb-4 text-sm">For Employers</h4>
            <ul className="space-y-3 text-sm">
              <li>
                <Link href="/employer/login" className="text-stone-500 hover:text-stone-900 transition-colors duration-300">
                  Employer Portal
                </Link>
              </li>
              <li>
                <Link href="/dashboard?tab=talent" className="text-stone-500 hover:text-stone-900 transition-colors duration-300">
                  Browse Talent
                </Link>
              </li>
            </ul>
          </div>

          {/* Verticals */}
          <div>
            <h4 className="font-medium text-stone-900 mb-4 text-sm">Verticals</h4>
            <ul className="space-y-3 text-sm text-stone-500">
              <li>Engineering</li>
              <li>Data</li>
              <li>Business</li>
              <li>Design</li>
            </ul>
          </div>
        </div>

        <div className="mt-16 pt-8 border-t border-stone-200 flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="text-sm text-stone-400">
            &copy; {new Date().getFullYear()} Pathway
          </div>
          <div className="flex items-center gap-6 text-sm">
            <Link href="/privacy" className="text-stone-400 hover:text-stone-600 transition-colors duration-300">
              Privacy Policy
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}
