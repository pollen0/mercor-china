'use client'

import { SkeletonTable, Skeleton } from '@/components/loading'
import { PageWrapper, Container } from '@/components/layout/container'

export default function InterviewsLoading() {
  return (
    <PageWrapper>
      {/* Navbar skeleton */}
      <div className="fixed top-0 left-0 right-0 h-16 bg-white/80 backdrop-blur-md border-b border-stone-100 z-50">
        <Container className="h-full flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-stone-200 rounded-lg animate-pulse" />
            <div className="w-24 h-4 bg-stone-200 rounded animate-pulse" />
          </div>
          <div className="w-32 h-8 bg-stone-200 rounded-lg animate-pulse" />
        </Container>
      </div>

      <Container className="py-8 pt-24">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <Skeleton className="h-8 w-48 mb-2" />
            <Skeleton className="h-4 w-64" />
          </div>
          <Skeleton className="h-10 w-32 rounded-xl" />
        </div>

        {/* Filters */}
        <div className="flex gap-4 mb-6">
          <Skeleton className="h-10 w-32 rounded-xl" />
          <Skeleton className="h-10 w-32 rounded-xl" />
          <Skeleton className="h-10 w-48 rounded-xl" />
        </div>

        {/* Table */}
        <div className="bg-white rounded-2xl shadow-soft p-6">
          <SkeletonTable rows={8} cols={5} />
        </div>
      </Container>
    </PageWrapper>
  )
}
