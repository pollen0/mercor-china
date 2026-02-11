/**
 * Tests for dashboard components.
 */
import { render, screen, fireEvent } from '@testing-library/react'
import { ScoreCard } from '@/components/dashboard/score-card'
import { TranscriptViewer } from '@/components/dashboard/transcript-viewer'
import { CandidateCard } from '@/components/dashboard/candidate-card'

describe('ScoreCard', () => {
  it('renders score value', () => {
    render(<ScoreCard score={8.5} label="Overall Score" />)

    expect(screen.getByText('8.5')).toBeInTheDocument()
    expect(screen.getByText('Overall Score')).toBeInTheDocument()
  })

  it('displays score with one decimal place', () => {
    render(<ScoreCard score={8.56} label="Score" />)

    expect(screen.getByText('8.6')).toBeInTheDocument()
  })

  it('applies teal color for high scores (>= 70%)', () => {
    render(<ScoreCard score={7} label="Score" />) // 70% of maxScore 10

    const scoreElement = screen.getByText('7.0')
    expect(scoreElement).toHaveClass('text-teal-700')
  })

  it('applies amber color for medium scores (50-69%)', () => {
    render(<ScoreCard score={5.5} label="Score" />) // 55% of maxScore 10

    const scoreElement = screen.getByText('5.5')
    expect(scoreElement).toHaveClass('text-amber-700')
  })

  it('applies red color for low scores (< 50%)', () => {
    render(<ScoreCard score={3.5} label="Score" />) // 35% of maxScore 10

    const scoreElement = screen.getByText('3.5')
    expect(scoreElement).toHaveClass('text-red-700')
  })

  it('uses custom maxScore for percentage calculation', () => {
    render(<ScoreCard score={85} label="Score" maxScore={100} />)

    // 85/100 = 85% which is >= 70, so should be teal
    const scoreElement = screen.getByText('85.0')
    expect(scoreElement).toHaveClass('text-teal-700')
  })

  it('renders without label', () => {
    render(<ScoreCard score={7.5} />)

    expect(screen.getByText('7.5')).toBeInTheDocument()
  })

  it('renders with different sizes', () => {
    const { rerender } = render(<ScoreCard score={7.5} size="sm" />)
    expect(document.querySelector('.w-16')).toBeInTheDocument()

    rerender(<ScoreCard score={7.5} size="lg" />)
    expect(document.querySelector('.w-32')).toBeInTheDocument()
  })
})

describe('TranscriptViewer', () => {
  const sampleTranscript = 'This is a sample transcript of the interview response. It contains multiple sentences to test the viewer component.'

  it('renders transcript text', () => {
    render(<TranscriptViewer transcript={sampleTranscript} />)

    expect(screen.getByText(/This is a sample transcript/)).toBeInTheDocument()
  })

  it('shows expand/collapse button', () => {
    render(<TranscriptViewer transcript={sampleTranscript} />)

    // Should show expand button initially
    expect(screen.getByText('Expand')).toBeInTheDocument()
  })

  it('toggles between expand and collapse', () => {
    render(<TranscriptViewer transcript={sampleTranscript} />)

    const expandButton = screen.getByText('Expand')
    fireEvent.click(expandButton)

    // Should now show collapse button
    expect(screen.getByText('Collapse')).toBeInTheDocument()
  })

  it('shows "Show more" for long transcripts when collapsed', () => {
    const longTranscript = 'Lorem ipsum dolor sit amet. '.repeat(50) // > 500 chars
    render(<TranscriptViewer transcript={longTranscript} />)

    expect(screen.getByText('Show more...')).toBeInTheDocument()
  })

  it('shows copy button', () => {
    render(<TranscriptViewer transcript={sampleTranscript} />)

    expect(screen.getByText('Copy')).toBeInTheDocument()
  })

  it('shows placeholder when transcript is empty', () => {
    render(<TranscriptViewer transcript="" />)

    expect(screen.getByText('No transcript available')).toBeInTheDocument()
  })

  it('shows placeholder when transcript is falsy', () => {
    render(<TranscriptViewer transcript={null as unknown as string} />)

    expect(screen.getByText('No transcript available')).toBeInTheDocument()
  })

  it('renders transcript header label', () => {
    render(<TranscriptViewer transcript={sampleTranscript} />)

    expect(screen.getByText('Transcript')).toBeInTheDocument()
  })
})

describe('CandidateCard', () => {
  const defaultProps = {
    name: 'John Doe',
    email: 'john@example.com',
    score: 8.5,
    status: 'SHORTLISTED' as const,
  }

  it('renders candidate name', () => {
    render(<CandidateCard {...defaultProps} />)

    expect(screen.getByText('John Doe')).toBeInTheDocument()
  })

  it('renders candidate email', () => {
    render(<CandidateCard {...defaultProps} />)

    expect(screen.getByText('john@example.com')).toBeInTheDocument()
  })

  it('renders score card', () => {
    render(<CandidateCard {...defaultProps} />)

    expect(screen.getByText('8.5')).toBeInTheDocument()
  })

  it('renders shortlisted status badge', () => {
    render(<CandidateCard {...defaultProps} status="SHORTLISTED" />)

    expect(screen.getByText('Shortlisted')).toBeInTheDocument()
  })

  it('renders pending status correctly', () => {
    render(<CandidateCard {...defaultProps} status="PENDING" />)

    expect(screen.getByText('Pending')).toBeInTheDocument()
  })

  it('renders rejected status correctly', () => {
    render(<CandidateCard {...defaultProps} status="REJECTED" />)

    expect(screen.getByText('Rejected')).toBeInTheDocument()
  })

  it('renders hired status correctly', () => {
    render(<CandidateCard {...defaultProps} status="HIRED" />)

    expect(screen.getByText('Hired')).toBeInTheDocument()
  })

  it('does not show score card when score is undefined', () => {
    render(<CandidateCard name="John" email="john@test.com" score={undefined} />)

    // ScoreCard should not be rendered
    expect(screen.queryByText(/\d+\.\d+/)).not.toBeInTheDocument()
  })

  it('renders target roles when provided', () => {
    render(
      <CandidateCard
        {...defaultProps}
        targetRoles={['Software Engineer', 'Backend Developer']}
      />
    )

    expect(screen.getByText('Software Engineer')).toBeInTheDocument()
    expect(screen.getByText('Backend Developer')).toBeInTheDocument()
  })

  it('limits displayed roles to 3 with overflow indicator', () => {
    render(
      <CandidateCard
        {...defaultProps}
        targetRoles={['Role 1', 'Role 2', 'Role 3', 'Role 4', 'Role 5']}
      />
    )

    expect(screen.getByText('Role 1')).toBeInTheDocument()
    expect(screen.getByText('Role 2')).toBeInTheDocument()
    expect(screen.getByText('Role 3')).toBeInTheDocument()
    expect(screen.getByText('+2 more')).toBeInTheDocument()
  })

  it('calls onClick when card is clicked', () => {
    const onClick = jest.fn()
    render(<CandidateCard {...defaultProps} onClick={onClick} />)

    const card = screen.getByText('John Doe').closest('div[class*="bg-white"]')
    if (card) fireEvent.click(card)

    expect(onClick).toHaveBeenCalled()
  })

  it('renders avatar with first letter of name', () => {
    render(<CandidateCard {...defaultProps} />)

    expect(screen.getByText('J')).toBeInTheDocument()
  })

  it('is clickable when onClick is provided', () => {
    const { container } = render(
      <CandidateCard {...defaultProps} onClick={() => {}} />
    )

    expect(container.firstChild).toHaveClass('cursor-pointer')
  })
})
