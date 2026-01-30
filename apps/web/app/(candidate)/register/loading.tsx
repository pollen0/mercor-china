'use client'

import { Skeleton } from '@/components/loading'

export default function RegisterLoading() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-brand-50 to-white flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-soft-lg p-8">
        {/* Header */}
        <div className="text-center mb-6">
          <Skeleton className="h-10 w-10 rounded-xl mx-auto mb-4" />
          <Skeleton className="h-6 w-48 mx-auto mb-2" />
          <Skeleton className="h-4 w-64 mx-auto" />
        </div>

        {/* WeChat button skeleton */}
        <Skeleton className="h-12 w-full rounded-xl mb-5" />

        {/* Divider */}
        <div className="flex items-center gap-4 my-5">
          <div className="flex-1 h-px bg-warm-200" />
          <Skeleton className="h-4 w-24" />
          <div className="flex-1 h-px bg-warm-200" />
        </div>

        {/* Form fields */}
        <div className="space-y-5">
          <div>
            <Skeleton className="h-4 w-20 mb-2" />
            <Skeleton className="h-12 w-full rounded-xl" />
          </div>
          <div>
            <Skeleton className="h-4 w-16 mb-2" />
            <Skeleton className="h-12 w-full rounded-xl" />
          </div>
          <div>
            <Skeleton className="h-4 w-24 mb-2" />
            <Skeleton className="h-12 w-full rounded-xl" />
          </div>
          <div>
            <Skeleton className="h-4 w-20 mb-2" />
            <Skeleton className="h-12 w-full rounded-xl" />
          </div>

          {/* Role buttons */}
          <div>
            <Skeleton className="h-4 w-32 mb-3" />
            <div className="flex flex-wrap gap-2">
              <Skeleton className="h-10 w-24 rounded-full" />
              <Skeleton className="h-10 w-28 rounded-full" />
              <Skeleton className="h-10 w-20 rounded-full" />
              <Skeleton className="h-10 w-32 rounded-full" />
            </div>
          </div>

          {/* Submit button */}
          <Skeleton className="h-12 w-full rounded-xl" />
        </div>
      </div>
    </main>
  )
}
