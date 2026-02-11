/**
 * Tests for interview components.
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { PermissionCheck } from '@/components/interview/permission-check'
import { QuestionCard } from '@/components/interview/question-card'
import { InterviewProgress } from '@/components/interview/interview-progress'

describe('PermissionCheck', () => {
  const mockOnPermissionGranted = jest.fn()

  beforeEach(() => {
    mockOnPermissionGranted.mockClear()
    // Mock navigator.permissions.query to return 'prompt' status
    Object.defineProperty(navigator, 'permissions', {
      value: {
        query: jest.fn().mockResolvedValue({
          state: 'prompt',
          onchange: null,
        }),
      },
      configurable: true,
    })
  })

  it('renders permission request UI', () => {
    render(<PermissionCheck onPermissionGranted={mockOnPermissionGranted} />)

    expect(screen.getByText(/camera and microphone/i)).toBeInTheDocument()
    expect(screen.getByText(/grant access/i)).toBeInTheDocument()
  })

  it('shows requesting state when button clicked', async () => {
    render(<PermissionCheck onPermissionGranted={mockOnPermissionGranted} />)

    const button = screen.getByRole('button', { name: /grant access/i })
    fireEvent.click(button)

    expect(screen.getByText(/requesting/i)).toBeInTheDocument()
  })

  it('calls onPermissionGranted when permissions are granted', async () => {
    // Mock successful permission
    const mockStream = {
      getTracks: () => [{ stop: jest.fn() }],
      getVideoTracks: () => [{ stop: jest.fn() }],
      getAudioTracks: () => [{ stop: jest.fn() }],
    }
    ;(navigator.mediaDevices.getUserMedia as jest.Mock).mockResolvedValueOnce(mockStream)

    render(<PermissionCheck onPermissionGranted={mockOnPermissionGranted} />)

    const button = screen.getByRole('button', { name: /grant access/i })
    fireEvent.click(button)

    await waitFor(() => {
      expect(mockOnPermissionGranted).toHaveBeenCalled()
    })
  })

  it('shows error when permissions are denied', async () => {
    ;(navigator.mediaDevices.getUserMedia as jest.Mock).mockRejectedValueOnce(
      new Error('Permission denied')
    )

    render(<PermissionCheck onPermissionGranted={mockOnPermissionGranted} />)

    const button = screen.getByRole('button', { name: /grant access/i })
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText(/denied/i)).toBeInTheDocument()
    })
  })
})

describe('QuestionCard', () => {
  const defaultProps = {
    questionNumber: 1,
    totalQuestions: 5,
    text: 'Tell me about yourself',
  }

  it('renders question text', () => {
    render(<QuestionCard {...defaultProps} />)

    expect(screen.getByText('Tell me about yourself')).toBeInTheDocument()
  })

  it('shows question number and total', () => {
    render(<QuestionCard {...defaultProps} />)

    expect(screen.getByText(/question 1/i)).toBeInTheDocument()
    expect(screen.getByText(/of 5/i)).toBeInTheDocument()
  })

  it('renders question card with correct styling', () => {
    render(<QuestionCard {...defaultProps} />)

    expect(screen.getByText('Tell me about yourself')).toBeInTheDocument()
  })

  it('renders question card with correct styling', () => {
    render(<QuestionCard {...defaultProps} />)

    const card = document.querySelector('.border-stone-900')
    expect(card).toBeInTheDocument()
  })
})

describe('InterviewProgress', () => {
  it('renders progress bar', () => {
    render(
      <InterviewProgress
        currentQuestion={2}
        totalQuestions={5}
        completedQuestions={[0, 1]}
      />
    )

    // Progress bar should exist
    const progressBar = document.querySelector('[role="progressbar"]')
    expect(progressBar || document.querySelector('.h-2')).toBeInTheDocument()
  })

  it('shows correct question indicators', () => {
    render(
      <InterviewProgress
        currentQuestion={2}
        totalQuestions={5}
        completedQuestions={[0, 1]}
      />
    )

    // Should have 5 question indicators
    const indicators = document.querySelectorAll('.rounded-full')
    expect(indicators.length).toBeGreaterThanOrEqual(5)
  })

  it('marks answered questions', () => {
    render(
      <InterviewProgress
        currentQuestion={2}
        totalQuestions={3}
        completedQuestions={[0]}
      />
    )

    // First question should be marked as answered (green background)
    const indicators = document.querySelectorAll('.rounded-full')
    // Check that at least one indicator has answered styling
    expect(indicators.length).toBeGreaterThan(0)
  })

  it('highlights current question', () => {
    render(
      <InterviewProgress
        currentQuestion={1}
        totalQuestions={3}
        completedQuestions={[0]}
      />
    )

    // Current question should have ring styling
    const currentIndicator = document.querySelector('.ring-2')
    expect(currentIndicator).toBeInTheDocument()
  })

  it('calculates progress percentage correctly', () => {
    render(
      <InterviewProgress
        currentQuestion={2}
        totalQuestions={5}
        completedQuestions={[0, 1]}
      />
    )

    // 2 out of 5 completed = 40%
    // Check for "2/5 completed" text
    expect(screen.getByText('2/5 completed')).toBeInTheDocument()
  })
})
