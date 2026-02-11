/**
 * Tests for Navbar component.
 */
import { render, screen, fireEvent } from '@testing-library/react'
import { Navbar, Logo, DashboardNavbar } from '@/components/layout/navbar'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(() => '/'),
}))

// Mock next/link
jest.mock('next/link', () => {
  return ({ children, href, className }: { children: React.ReactNode; href: string; className?: string }) => (
    <a href={href} className={className}>{children}</a>
  )
})

describe('Logo', () => {
  it('renders Pathway branding', () => {
    render(<Logo />)

    expect(screen.getByText('Pathway')).toBeInTheDocument()
  })

  it('links to home page', () => {
    render(<Logo />)

    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', '/')
  })

  it('renders as a link with Pathway text', () => {
    render(<Logo />)

    // Logo should be a link with Pathway text
    const link = screen.getByText('Pathway')
    expect(link).toHaveAttribute('href', '/')
  })
})

describe('Navbar', () => {
  it('renders default variant with login links', () => {
    render(<Navbar />)

    expect(screen.getByText('Log in')).toBeInTheDocument()
    expect(screen.getByText('Sign Up')).toBeInTheDocument()
  })

  it('renders Pathway logo by default', () => {
    render(<Navbar />)

    expect(screen.getByText('Pathway')).toBeInTheDocument()
  })

  it('renders custom logo when provided', () => {
    render(<Navbar logo={<div data-testid="custom-logo">Custom</div>} />)

    expect(screen.getByTestId('custom-logo')).toBeInTheDocument()
  })

  it('renders navigation items', () => {
    const navItems = [
      { label: 'Home', href: '/' },
      { label: 'About', href: '/about' },
    ]

    render(<Navbar navItems={navItems} />)

    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('About')).toBeInTheDocument()
  })

  it('renders custom right content', () => {
    render(<Navbar rightContent={<button>Custom Button</button>} />)

    expect(screen.getByText('Custom Button')).toBeInTheDocument()
  })

  it('toggles mobile menu', () => {
    render(<Navbar />)

    // Find mobile menu button
    const mobileMenuButton = screen.getByRole('button', { name: /open menu/i })

    // Login should be visible on desktop
    expect(screen.getByText('Log in')).toBeInTheDocument()

    // Click to open mobile menu
    fireEvent.click(mobileMenuButton)

    // Button should now say close menu
    expect(screen.getByRole('button', { name: /close menu/i })).toBeInTheDocument()
  })

  it('renders dashboard variant with navigation items', () => {
    render(<Navbar variant="dashboard" />)

    expect(screen.getByText('Overview')).toBeInTheDocument()
    expect(screen.getByText('Interviews')).toBeInTheDocument()
    expect(screen.getByText('Jobs')).toBeInTheDocument()
    expect(screen.getByText('Talent Pool')).toBeInTheDocument()
  })

  it('applies active state to current path', () => {
    const { usePathname } = require('next/navigation')
    usePathname.mockReturnValue('/dashboard')

    render(<Navbar variant="dashboard" />)

    // Overview link should have active styling when on /dashboard
    const overviewLink = screen.getByText('Overview').closest('a')
    expect(overviewLink).toHaveClass('text-stone-900')
    expect(overviewLink).toHaveClass('font-medium')
  })
})

describe('DashboardNavbar', () => {
  it('renders company name when provided', () => {
    render(<DashboardNavbar companyName="Acme Inc" />)

    expect(screen.getByText('Acme Inc')).toBeInTheDocument()
    expect(screen.getByText('A')).toBeInTheDocument() // Initial
  })

  it('renders logout button when onLogout provided', () => {
    const mockLogout = jest.fn()
    render(<DashboardNavbar onLogout={mockLogout} />)

    const logoutButton = document.querySelector('button')
    expect(logoutButton).toBeInTheDocument()

    fireEvent.click(logoutButton!)
    expect(mockLogout).toHaveBeenCalled()
  })

  it('does not render logout button when onLogout not provided', () => {
    render(<DashboardNavbar />)

    // Should not have the logout icon button
    const buttons = screen.queryAllByRole('button')
    // Only mobile menu button should exist
    expect(buttons.length).toBeLessThanOrEqual(1)
  })
})
