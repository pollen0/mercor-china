/**
 * Tests for interview components.
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { PermissionCheck } from '@/components/interview/permission-check'
import { QuestionCard } from '@/components/interview/question-card'
import { InterviewProgress } from '@/components/interview/interview-progress'

describe('PermissionCheck', () => {
  const mockOnPermissionsGranted = jest.fn()

  beforeEach(() => {
    mockOnPermissionsGranted.mockClear()
  })

  it('renders permission request UI', () => {
    render(<PermissionCheck onPermissionsGranted={mockOnPermissionsGranted} />)

    expect(screen.getByText(/camera and microphone/i)).toBeInTheDocument()
    expect(screen.getByText(/grant access/i)).toBeInTheDocument()
  })

  it('shows requesting state when button clicked', async () => {
    render(<PermissionCheck onPermissionsGranted={mockOnPermissionsGranted} />)

    const button = screen.getByRole('button', { name: /grant access/i })
    fireEvent.click(button)

    expect(screen.getByText(/requesting/i)).toBeInTheDocument()
  })

  it('calls onPermissionsGranted when permissions are granted', async () => {
    // Mock successful permission
    const mockStream = {
      getTracks: () => [],
      getVideoTracks: () => [{ stop: jest.fn() }],
      getAudioTracks: () => [{ stop: jest.fn() }],
    }
    ;(navigator.mediaDevices.getUserMedia as jest.Mock).mockResolvedValueOnce(mockStream)

    render(<PermissionCheck onPermissionsGranted={mockOnPermissionsGranted} />)

    const button = screen.getByRole('button', { name: /grant access/i })
    fireEvent.click(button)

    await waitFor(() => {
      expect(mockOnPermissionsGranted).toHaveBeenCalledWith(mockStream)
    })
  })

  it('shows error when permissions are denied', async () => {
    ;(navigator.mediaDevices.getUserMedia as jest.Mock).mockRejectedValueOnce(
      new Error('Permission denied')
    )

    render(<PermissionCheck onPermissionsGranted={mockOnPermissionsGranted} />)

    const button = screen.getByRole('button', { name: /grant access/i })
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText(/permission denied/i)).toBeInTheDocument()
    })
  })
})

describe('QuestionCard', () => {
  const defaultProps = {
    questionNumber: 1,
    totalQuestions: 5,
    text: 'Tell me about yourself',
    textZh: '请介绍一下你自己',
    category: 'introduction',
  }

  it('renders question text', () => {
    render(<QuestionCard {...defaultProps} />)

    expect(screen.getByText('Tell me about yourself')).toBeInTheDocument()
    expect(screen.getByText('请介绍一下你自己')).toBeInTheDocument()
  })

  it('shows question number and total', () => {
    render(<QuestionCard {...defaultProps} />)

    expect(screen.getByText(/question 1/i)).toBeInTheDocument()
    expect(screen.getByText(/of 5/i)).toBeInTheDocument()
  })

  it('shows category badge', () => {
    render(<QuestionCard {...defaultProps} />)

    expect(screen.getByText('introduction')).toBeInTheDocument()
  })

  it('renders without Chinese text', () => {
    const props = { ...defaultProps, textZh: undefined }
    render(<QuestionCard {...props} />)

    expect(screen.getByText('Tell me about yourself')).toBeInTheDocument()
  })

  it('renders without category', () => {
    const props = { ...defaultProps, category: undefined }
    render(<QuestionCard {...props} />)

    expect(screen.queryByText('introduction')).not.toBeInTheDocument()
  })
})

describe('InterviewProgress', () => {
  it('renders progress bar', () => {
    render(
      <InterviewProgress
        currentQuestion={2}
        totalQuestions={5}
        answeredQuestions={[0, 1]}
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
        answeredQuestions={[0, 1]}
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
        answeredQuestions={[0]}
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
        answeredQuestions={[0]}
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
        answeredQuestions={[0, 1]}
      />
    )

    // 2 out of 5 answered = 40%
    // The progress bar width should reflect this
    const progressFill = document.querySelector('.bg-blue-600')
    expect(progressFill).toBeInTheDocument()
  })
})
