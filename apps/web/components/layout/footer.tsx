import * as React from 'react'
import Link from 'next/link'
import { cn } from '@/lib/utils'
import { Container } from './container'

interface FooterProps extends React.HTMLAttributes<HTMLElement> {
  variant?: 'minimal' | 'default'
}

export function Footer({ variant = 'minimal', className, ...props }: FooterProps) {
  if (variant === 'minimal') {
    return (
      <footer
        className={cn('py-8 border-t border-warm-100', className)}
        {...props}
      >
        <Container>
          <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 bg-gradient-to-br from-brand-500 to-brand-600 rounded-md flex items-center justify-center">
                <span className="text-white font-bold text-xs">智</span>
              </div>
              <span className="font-medium text-warm-900">ZhiMian 智面</span>
            </div>
            <div className="flex items-center gap-4 text-sm text-warm-500">
              <Link href="/privacy" className="hover:text-warm-700 transition-colors">
                Privacy / 隐私
              </Link>
              <span>&copy; {new Date().getFullYear()} ZhiMian</span>
            </div>
          </div>
        </Container>
      </footer>
    )
  }

  return (
    <footer
      className={cn('py-12 bg-warm-50 border-t border-warm-100', className)}
      {...props}
    >
      <Container>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-2 md:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-brand-500 to-brand-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">智</span>
              </div>
              <span className="font-semibold text-warm-900">ZhiMian 智面</span>
            </div>
            <p className="text-sm text-warm-600 leading-relaxed">
              AI-powered recruiting platform for China&apos;s fastest-growing industries.
            </p>
          </div>

          {/* For Candidates */}
          <div>
            <h4 className="font-semibold text-warm-900 mb-4">For Candidates</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/candidate/register" className="text-warm-600 hover:text-brand-600 transition-colors">
                  Start Interview
                </Link>
              </li>
              <li>
                <Link href="/candidate/login" className="text-warm-600 hover:text-brand-600 transition-colors">
                  Sign In
                </Link>
              </li>
            </ul>
          </div>

          {/* For Employers */}
          <div>
            <h4 className="font-semibold text-warm-900 mb-4">For Employers</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/login" className="text-warm-600 hover:text-brand-600 transition-colors">
                  Employer Portal
                </Link>
              </li>
              <li>
                <Link href="/dashboard/jobs" className="text-warm-600 hover:text-brand-600 transition-colors">
                  Post a Job
                </Link>
              </li>
            </ul>
          </div>

          {/* Industries */}
          <div>
            <h4 className="font-semibold text-warm-900 mb-4">Industries</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <span className="text-warm-600">New Energy / EV</span>
              </li>
              <li>
                <span className="text-warm-600">Sales / BD</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-warm-200 flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="text-sm text-warm-500">
            &copy; {new Date().getFullYear()} ZhiMian. All rights reserved.
          </div>
          <div className="flex items-center gap-6 text-sm">
            <Link href="/privacy" className="text-warm-500 hover:text-warm-700 transition-colors">
              Privacy Policy / 隐私政策
            </Link>
          </div>
        </div>
      </Container>
    </footer>
  )
}
