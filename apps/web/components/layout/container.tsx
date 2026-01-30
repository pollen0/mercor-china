import * as React from 'react'
import { cn } from '@/lib/utils'

interface ContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  as?: React.ElementType
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
}

const containerSizes = {
  sm: 'max-w-3xl',
  md: 'max-w-5xl',
  lg: 'max-w-6xl',
  xl: 'max-w-7xl',
  full: 'max-w-full',
}

export function Container({
  as: Component = 'div',
  size = 'xl',
  className,
  children,
  ...props
}: ContainerProps) {
  return (
    <Component
      className={cn(
        'mx-auto px-4 sm:px-6 lg:px-8',
        containerSizes[size],
        className
      )}
      {...props}
    >
      {children}
    </Component>
  )
}

// Page wrapper with navbar offset
interface PageWrapperProps extends React.HTMLAttributes<HTMLDivElement> {
  navbarOffset?: boolean
}

export function PageWrapper({
  navbarOffset = true,
  className,
  children,
  ...props
}: PageWrapperProps) {
  return (
    <main
      className={cn(
        'min-h-screen bg-background',
        navbarOffset && 'pt-16',
        className
      )}
      {...props}
    >
      {children}
    </main>
  )
}

// Section component for consistent spacing
interface SectionProps extends React.HTMLAttributes<HTMLElement> {
  as?: React.ElementType
  size?: 'sm' | 'md' | 'lg'
}

const sectionSizes = {
  sm: 'py-10 md:py-12 lg:py-16',
  md: 'py-12 md:py-16 lg:py-20',
  lg: 'py-16 md:py-20 lg:py-24',
}

export function Section({
  as: Component = 'section',
  size = 'md',
  className,
  children,
  ...props
}: SectionProps) {
  return (
    <Component
      className={cn(sectionSizes[size], className)}
      {...props}
    >
      {children}
    </Component>
  )
}
