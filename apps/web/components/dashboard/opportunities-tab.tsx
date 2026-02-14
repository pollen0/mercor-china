'use client'

import { useOpportunities } from '@/lib/hooks/use-candidate-data'
import { Card, CardContent } from '@/components/ui/card'
import type { OpportunityJob } from '@/lib/api'

const VERTICAL_LABELS: Record<string, string> = {
  software_engineering: 'Software Engineering',
  data: 'Data',
  product: 'Product',
  design: 'Design',
  finance: 'Finance',
}

function CompanyInitials({ name }: { name: string }) {
  const initials = name
    .split(/\s+/)
    .slice(0, 2)
    .map(w => w[0])
    .join('')
    .toUpperCase()

  return (
    <div className="w-8 h-8 rounded-full bg-stone-100 flex items-center justify-center text-xs font-medium text-stone-600 shrink-0">
      {initials}
    </div>
  )
}

function JobCard({ job }: { job: OpportunityJob }) {
  return (
    <Card className="hover:shadow-sm transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          {job.companyLogo ? (
            <img
              src={job.companyLogo}
              alt={job.companyName}
              className="w-8 h-8 rounded-full object-cover shrink-0"
            />
          ) : (
            <CompanyInitials name={job.companyName} />
          )}
          <div className="min-w-0 flex-1">
            <p className="font-medium text-stone-900 text-sm truncate">{job.jobTitle}</p>
            <p className="text-sm text-stone-500 truncate">{job.companyName}</p>
            {job.location && (
              <p className="text-xs text-stone-400 mt-0.5">{job.location}</p>
            )}
            <div className="flex flex-wrap items-center gap-1.5 mt-2">
              <span className="bg-stone-100 text-stone-600 text-xs px-2 py-0.5 rounded">
                {VERTICAL_LABELS[job.vertical] || job.vertical}
              </span>
              {job.roleType && (
                <span className="bg-stone-100 text-stone-600 text-xs px-2 py-0.5 rounded">
                  {job.roleType.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                </span>
              )}
              {!job.eligible && job.reason && (
                <span className="bg-amber-50 text-amber-600 text-xs px-2 py-0.5 rounded">
                  {job.reason}
                </span>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-12 bg-stone-100 rounded-lg" />
      <div className="space-y-3">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="h-24 bg-stone-50 rounded-lg border border-stone-100" />
        ))}
      </div>
    </div>
  )
}

export default function OpportunitiesTab({ token }: { token: string }) {
  const { opportunities, isLoading, error } = useOpportunities(token)

  if (isLoading) {
    return <LoadingSkeleton />
  }

  if (error) {
    return (
      <Card>
        <CardContent className="py-8 text-center">
          <p className="text-stone-400">Failed to load opportunities</p>
        </CardContent>
      </Card>
    )
  }

  if (!opportunities) {
    return null
  }

  const { eligibleJobs, notEligibleJobs, totalEligible, total } = opportunities

  return (
    <div className="space-y-8">
      {/* Summary */}
      <div className="bg-stone-50 border border-stone-100 rounded-lg px-5 py-4">
        <p className="text-sm text-stone-600">
          You&apos;re eligible for{' '}
          <span className="font-semibold text-teal-700">{totalEligible}</span>
          {' '}of {total} opportunities
        </p>
        <p className="text-xs text-stone-400 mt-1">
          Companies below can discover your profile automatically — no need to apply.
        </p>
      </div>

      {/* Eligible Jobs */}
      <div>
        <h3 className="text-sm font-medium text-stone-900 mb-3">
          Eligible ({eligibleJobs.length})
        </h3>
        {eligibleJobs.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center">
              <p className="text-stone-400 text-sm">Complete an interview to start qualifying for roles</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid sm:grid-cols-2 gap-3">
            {eligibleJobs.map(job => (
              <JobCard key={job.jobId} job={job} />
            ))}
          </div>
        )}
      </div>

      {/* Not Yet Eligible */}
      {notEligibleJobs.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-stone-500 mb-3">
            Not Yet Eligible ({notEligibleJobs.length})
          </h3>
          <div className="grid sm:grid-cols-2 gap-3">
            {notEligibleJobs.map(job => (
              <JobCard key={job.jobId} job={job} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
