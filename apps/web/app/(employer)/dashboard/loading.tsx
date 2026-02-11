'use client'

import { SkeletonDashboard } from '@/components/loading'
import { PageWrapper, Container } from '@/components/layout/container'

export default function DashboardLoading() {
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
        {/* Welcome section skeleton */}
        <div className="mb-10">
          <div className="h-8 w-64 bg-stone-200 rounded-lg animate-pulse mb-2" />
          <div className="h-4 w-48 bg-stone-100 rounded animate-pulse" />
        </div>

        <SkeletonDashboard />
      </Container>
    </PageWrapper>
  )
}
