/**
 * Tests for Footer component.
 */
import { render, screen } from '@testing-library/react'
import { Footer } from '@/components/layout/footer'

// Mock next/link
jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  )
})

describe('Footer', () => {
  describe('minimal variant', () => {
    it('renders Pathway branding', () => {
      render(<Footer variant="minimal" />)

      expect(screen.getByText('Pathway')).toBeInTheDocument()
    })

    it('shows copyright year', () => {
      render(<Footer variant="minimal" />)

      const currentYear = new Date().getFullYear().toString()
      expect(screen.getByText(new RegExp(currentYear))).toBeInTheDocument()
    })

    it('links to privacy policy', () => {
      render(<Footer variant="minimal" />)

      const privacyLink = screen.getByRole('link', { name: /privacy/i })
      expect(privacyLink).toHaveAttribute('href', '/privacy')
    })

    it('renders with custom className', () => {
      const { container } = render(<Footer variant="minimal" className="custom-class" />)

      expect(container.firstChild).toHaveClass('custom-class')
    })
  })

  describe('default variant', () => {
    it('renders all sections', () => {
      render(<Footer variant="default" />)

      expect(screen.getByText('For Students')).toBeInTheDocument()
      expect(screen.getByText('For Employers')).toBeInTheDocument()
      expect(screen.getByText('Verticals')).toBeInTheDocument()
    })

    it('shows student links', () => {
      render(<Footer variant="default" />)

      expect(screen.getByRole('link', { name: /create account/i })).toHaveAttribute('href', '/register')
      expect(screen.getByRole('link', { name: /sign in/i })).toHaveAttribute('href', '/candidate/login')
    })

    it('shows employer links', () => {
      render(<Footer variant="default" />)

      expect(screen.getByRole('link', { name: /employer portal/i })).toHaveAttribute('href', '/employer/login')
    })

    it('shows verticals', () => {
      render(<Footer variant="default" />)

      expect(screen.getByText('Engineering')).toBeInTheDocument()
      expect(screen.getByText('Data')).toBeInTheDocument()
      expect(screen.getByText('Business')).toBeInTheDocument()
      expect(screen.getByText('Design')).toBeInTheDocument()
    })

    it('shows company tagline', () => {
      render(<Footer variant="default" />)

      expect(screen.getByText(/career platform for college students/i)).toBeInTheDocument()
    })

    it('links to privacy policy', () => {
      render(<Footer variant="default" />)

      const privacyLinks = screen.getAllByRole('link', { name: /privacy/i })
      expect(privacyLinks.length).toBeGreaterThan(0)
    })
  })

  it('defaults to minimal variant', () => {
    render(<Footer />)

    // Minimal variant should not have "For Students" section
    expect(screen.queryByText('For Students')).not.toBeInTheDocument()
    expect(screen.getByText('Pathway')).toBeInTheDocument()
  })
})
