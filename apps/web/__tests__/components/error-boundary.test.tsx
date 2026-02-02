/**
 * Tests for error boundary and error handling components.
 */
import { render, screen, fireEvent } from '@testing-library/react'
import { ErrorBoundary, ErrorDisplay, useErrorHandler } from '@/components/error-boundary'

// Simple component that always throws
const AlwaysThrows = () => {
  throw new Error('Test error')
}

// Component that throws conditionally
const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error')
  }
  return <div>No error</div>
}

// Suppress console.error for error boundary tests
const originalError = console.error
beforeAll(() => {
  console.error = jest.fn()
})
afterAll(() => {
  console.error = originalError
})

describe('ErrorBoundary', () => {
  it('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <div>Child content</div>
      </ErrorBoundary>
    )
    expect(screen.getByText('Child content')).toBeInTheDocument()
  })

  it('renders error UI when child throws', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )
    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
    expect(screen.getByText('Try Again')).toBeInTheDocument()
    expect(screen.getByText('Go Home')).toBeInTheDocument()
  })

  it('renders custom fallback when provided', () => {
    render(
      <ErrorBoundary fallback={<div>Custom error UI</div>}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )
    expect(screen.getByText('Custom error UI')).toBeInTheDocument()
  })

  it('Try Again button is clickable', () => {
    render(
      <ErrorBoundary>
        <AlwaysThrows />
      </ErrorBoundary>
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()

    const tryAgainButton = screen.getByText('Try Again')
    expect(tryAgainButton).toBeInTheDocument()

    // Clicking should not throw (it will re-render and error will reappear since child always throws)
    expect(() => fireEvent.click(tryAgainButton)).not.toThrow()
  })

  it('Go Home button navigates to home', () => {
    // Mock window.location.href
    const originalLocation = window.location
    delete (window as { location?: Location }).location
    window.location = { href: '' } as Location

    render(
      <ErrorBoundary>
        <AlwaysThrows />
      </ErrorBoundary>
    )

    const goHomeButton = screen.getByText('Go Home')
    fireEvent.click(goHomeButton)

    expect(window.location.href).toBe('/')

    // Restore
    window.location = originalLocation
  })
})

describe('ErrorDisplay', () => {
  it('renders error message from string', () => {
    render(<ErrorDisplay error="Something went wrong" />)
    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
  })

  it('renders error message from Error object', () => {
    render(<ErrorDisplay error={new Error('Error object message')} />)
    expect(screen.getByText('Error object message')).toBeInTheDocument()
  })

  it('shows retry button when onRetry provided', () => {
    const onRetry = jest.fn()
    render(<ErrorDisplay error="Error" onRetry={onRetry} />)

    const retryButton = screen.getByText('Try Again')
    expect(retryButton).toBeInTheDocument()

    fireEvent.click(retryButton)
    expect(onRetry).toHaveBeenCalledTimes(1)
  })

  it('shows dismiss button when onDismiss provided', () => {
    const onDismiss = jest.fn()
    render(<ErrorDisplay error="Error" onDismiss={onDismiss} />)

    const dismissButton = screen.getByText('Dismiss')
    expect(dismissButton).toBeInTheDocument()

    fireEvent.click(dismissButton)
    expect(onDismiss).toHaveBeenCalledTimes(1)
  })

  it('hides action buttons when no callbacks provided', () => {
    render(<ErrorDisplay error="Error" />)

    expect(screen.queryByText('Try Again')).not.toBeInTheDocument()
    expect(screen.queryByText('Dismiss')).not.toBeInTheDocument()
  })

  it('shows both buttons when both callbacks provided', () => {
    render(
      <ErrorDisplay
        error="Error"
        onRetry={() => {}}
        onDismiss={() => {}}
      />
    )

    expect(screen.getByText('Try Again')).toBeInTheDocument()
    expect(screen.getByText('Dismiss')).toBeInTheDocument()
  })
})

describe('useErrorHandler', () => {
  // Test component using the hook
  const TestComponent = () => {
    const { error, handleError, clearError } = useErrorHandler()

    return (
      <div>
        {error && <div data-testid="error">{error.message}</div>}
        <button onClick={() => handleError(new Error('Test error'))}>
          Trigger Error
        </button>
        <button onClick={clearError}>Clear Error</button>
      </div>
    )
  }

  it('initially has no error', () => {
    render(<TestComponent />)
    expect(screen.queryByTestId('error')).not.toBeInTheDocument()
  })

  it('sets error when handleError is called', () => {
    render(<TestComponent />)

    fireEvent.click(screen.getByText('Trigger Error'))

    expect(screen.getByTestId('error')).toHaveTextContent('Test error')
  })

  it('clears error when clearError is called', () => {
    render(<TestComponent />)

    fireEvent.click(screen.getByText('Trigger Error'))
    expect(screen.getByTestId('error')).toBeInTheDocument()

    fireEvent.click(screen.getByText('Clear Error'))
    expect(screen.queryByTestId('error')).not.toBeInTheDocument()
  })
})
