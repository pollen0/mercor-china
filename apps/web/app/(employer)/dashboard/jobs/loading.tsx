'use client'

import { SkeletonCard, Skeleton } from '@/components/loading'
import { PageWrapper, Container } from '@/components/layout/container'

export default function JobsLoading() {
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
            <Skeleton className="h-8 w-40 mb-2" />
            <Skeleton className="h-4 w-56" />
          </div>
          <Skeleton className="h-10 w-36 rounded-xl" />
        </div>

        {/* Job cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      </Container>
    </PageWrapper>
  )
}
