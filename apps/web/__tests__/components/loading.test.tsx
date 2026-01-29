/**
 * Tests for loading and skeleton components.
 */
import { render, screen } from '@testing-library/react'
import {
  Spinner,
  PageLoading,
  Skeleton,
  SkeletonText,
  SkeletonCard,
  SkeletonTable,
  SkeletonDashboard,
  SkeletonInterview,
  LoadingButton,
} from '@/components/loading'

describe('Spinner', () => {
  it('renders with default size', () => {
    render(<Spinner />)
    const spinner = document.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
    expect(spinner).toHaveClass('h-8', 'w-8')
  })

  it('renders with small size', () => {
    render(<Spinner size="sm" />)
    const spinner = document.querySelector('.animate-spin')
    expect(spinner).toHaveClass('h-4', 'w-4')
  })

  it('renders with large size', () => {
    render(<Spinner size="lg" />)
    const spinner = document.querySelector('.animate-spin')
    expect(spinner).toHaveClass('h-12', 'w-12')
  })

  it('accepts custom className', () => {
    render(<Spinner className="custom-class" />)
    const spinner = document.querySelector('.animate-spin')
    expect(spinner).toHaveClass('custom-class')
  })
})

describe('PageLoading', () => {
  it('renders with default message', () => {
    render(<PageLoading />)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders with custom message', () => {
    render(<PageLoading message="Please wait..." />)
    expect(screen.getByText('Please wait...')).toBeInTheDocument()
  })

  it('contains a spinner', () => {
    render(<PageLoading />)
    const spinner = document.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
  })
})

describe('Skeleton', () => {
  it('renders with animate-pulse class', () => {
    render(<Skeleton className="h-4 w-full" />)
    const skeleton = document.querySelector('.animate-pulse')
    expect(skeleton).toBeInTheDocument()
  })

  it('accepts custom className', () => {
    render(<Skeleton className="h-10 w-20" />)
    const skeleton = document.querySelector('.animate-pulse')
    expect(skeleton).toHaveClass('h-10', 'w-20')
  })
})

describe('SkeletonText', () => {
  it('renders single line by default', () => {
    render(<SkeletonText />)
    const skeletons = document.querySelectorAll('.animate-pulse')
    expect(skeletons).toHaveLength(1)
  })

  it('renders multiple lines', () => {
    render(<SkeletonText lines={3} />)
    const skeletons = document.querySelectorAll('.animate-pulse')
    expect(skeletons).toHaveLength(3)
  })

  it('last line is shorter when multiple lines', () => {
    render(<SkeletonText lines={3} />)
    const skeletons = document.querySelectorAll('.animate-pulse')
    expect(skeletons[2]).toHaveClass('w-3/4')
  })
})

describe('SkeletonCard', () => {
  it('renders card structure', () => {
    render(<SkeletonCard />)
    const skeletons = document.querySelectorAll('.animate-pulse')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('has avatar placeholder', () => {
    render(<SkeletonCard />)
    const avatar = document.querySelector('.rounded-full.h-12.w-12')
    expect(avatar).toBeInTheDocument()
  })
})

describe('SkeletonTable', () => {
  it('renders header and default rows', () => {
    render(<SkeletonTable />)
    const rows = document.querySelectorAll('.border.rounded')
    expect(rows).toHaveLength(5) // default rows
  })

  it('renders custom number of rows', () => {
    render(<SkeletonTable rows={3} cols={2} />)
    const rows = document.querySelectorAll('.border.rounded')
    expect(rows).toHaveLength(3)
  })
})

describe('SkeletonDashboard', () => {
  it('renders stats cards', () => {
    render(<SkeletonDashboard />)
    const statsSection = document.querySelector('.grid-cols-1')
    expect(statsSection).toBeInTheDocument()
  })
})

describe('SkeletonInterview', () => {
  it('renders interview structure', () => {
    render(<SkeletonInterview />)
    const videoPlaceholder = document.querySelector('.aspect-video')
    expect(videoPlaceholder).toBeInTheDocument()
  })
})

describe('LoadingButton', () => {
  it('renders children when not loading', () => {
    render(<LoadingButton loading={false}>Click me</LoadingButton>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('renders loading text when loading', () => {
    render(<LoadingButton loading={true}>Click me</LoadingButton>)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders custom loading text', () => {
    render(
      <LoadingButton loading={true} loadingText="Saving...">
        Save
      </LoadingButton>
    )
    expect(screen.getByText('Saving...')).toBeInTheDocument()
  })

  it('is disabled when loading', () => {
    render(<LoadingButton loading={true}>Click me</LoadingButton>)
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('is disabled when disabled prop is true', () => {
    render(
      <LoadingButton loading={false} disabled>
        Click me
      </LoadingButton>
    )
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('shows spinner when loading', () => {
    render(<LoadingButton loading={true}>Click me</LoadingButton>)
    const spinner = document.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
  })
})
