import useSWR from 'swr'
import { candidateApi, candidateVerticalApi, type Candidate } from '@/lib/api'

// SWR fetcher that uses the token from the function argument
const createFetcher = <T>(fetchFn: (token: string) => Promise<T>) => {
  return async (key: string, token: string) => {
    if (!token) throw new Error('No token')
    return fetchFn(token)
  }
}

// Hook for fetching candidate profile with caching
export function useCandidateProfile(token: string | null) {
  const { data, error, isLoading, mutate } = useSWR(
    token ? ['candidate-profile', token] : null,
    ([, t]) => candidateApi.getMe(t),
    {
      revalidateOnFocus: true,  // Re-fetch when user returns to tab (profile may have been edited)
      revalidateOnReconnect: true,
      dedupingInterval: 5000, // 5 seconds - allow quick re-fetches after edits
    }
  )

  return {
    profile: data,
    isLoading,
    error,
    mutate,
  }
}

// Hook for fetching resume data with caching
export function useResumeData(token: string | null) {
  const { data, error, isLoading, mutate } = useSWR(
    token ? ['resume', token] : null,
    ([, t]) => candidateApi.getMyResume(t),
    {
      revalidateOnFocus: true,  // Re-fetch when user returns (may have uploaded new resume)
      revalidateOnReconnect: true,
      dedupingInterval: 5000, // 5 seconds
    }
  )

  return {
    resumeData: data,
    isLoading,
    error,
    mutate,
  }
}

// Hook for fetching GitHub data with caching
export function useGitHubData(token: string | null) {
  const { data, error, isLoading, mutate } = useSWR(
    token ? ['github', token] : null,
    async ([, t]) => {
      try {
        return await candidateApi.getGitHubInfo(t)
      } catch {
        return null
      }
    },
    {
      revalidateOnFocus: true,  // Re-fetch when user returns (may have connected/refreshed GitHub)
      revalidateOnReconnect: true,
      dedupingInterval: 10000, // 10 seconds
    }
  )

  return {
    githubData: data,
    isLoading,
    error,
    mutate,
  }
}

// Hook for fetching GitHub analysis with caching
export function useGitHubAnalysis(token: string | null) {
  const { data, error, isLoading, mutate } = useSWR(
    token ? ['github-analysis', token] : null,
    async ([, t]) => {
      try {
        return await candidateApi.getGitHubAnalysis(t)
      } catch {
        return null
      }
    },
    {
      revalidateOnFocus: false, // Analysis doesn't change on user action
      revalidateOnReconnect: false,
      dedupingInterval: 120000, // 2 minutes - analysis takes time to compute
    }
  )

  return {
    githubAnalysis: data,
    isLoading,
    error,
    mutate,
  }
}

// Hook for fetching vertical profiles with caching
export function useVerticalProfiles(token: string | null) {
  const { data, error, isLoading, mutate } = useSWR(
    token ? ['vertical-profiles', token] : null,
    ([, t]) => candidateVerticalApi.getMyVerticals(t),
    {
      revalidateOnFocus: true,  // Re-fetch after completing interview
      revalidateOnReconnect: true,
      dedupingInterval: 10000, // 10 seconds
    }
  )

  return {
    profiles: data?.profiles || [],
    isLoading,
    error,
    mutate,
  }
}

// Hook for fetching matching jobs with caching
export function useMatchingJobs(token: string | null) {
  const { data, error, isLoading, mutate } = useSWR(
    token ? ['matching-jobs', token] : null,
    ([, t]) => candidateVerticalApi.getMatchingJobs(t),
    {
      revalidateOnFocus: false, // Jobs don't change based on user action
      revalidateOnReconnect: true,
      dedupingInterval: 60000, // 1 minute - jobs update server-side
    }
  )

  return {
    jobs: data?.jobs || [],
    isLoading,
    error,
    mutate,
  }
}

// Hook for fetching skill gap analysis
export function useSkillGap(token: string | null) {
  const { data, error, isLoading, mutate } = useSWR(
    token ? ['skill-gap', token] : null,
    async ([, t]) => {
      try {
        // Pass empty options object for general skill gap (not job-specific)
        return await candidateApi.getMySkillGap({}, t)
      } catch {
        return null
      }
    },
    {
      revalidateOnFocus: false, // Analysis doesn't change on user action
      revalidateOnReconnect: false,
      dedupingInterval: 120000, // 2 minutes
    }
  )

  return {
    skillGap: data,
    isLoading,
    error,
    mutate,
  }
}

// Combined hook for all dashboard data
// Note: useSkillGap is exported separately and should be called directly
// by consumers to avoid TypeScript inference depth limits with the large candidateApi object
export function useDashboardData(token: string | null) {
  const candidateProfile = useCandidateProfile(token)
  const resume = useResumeData(token)
  const github = useGitHubData(token)
  const githubAnalysis = useGitHubAnalysis(token)
  const profiles = useVerticalProfiles(token)
  const jobs = useMatchingJobs(token)

  const isLoading = candidateProfile.isLoading || resume.isLoading || github.isLoading || profiles.isLoading || jobs.isLoading

  return {
    candidateProfile: candidateProfile.profile,
    emailVerified: candidateProfile.profile?.emailVerified ?? true, // Default to true to avoid showing banner on error
    resumeData: resume.resumeData,
    githubData: github.githubData,
    githubAnalysis: githubAnalysis.githubAnalysis,
    verticalProfiles: profiles.profiles,
    matchingJobs: jobs.jobs,
    isLoading,
    mutateCandidate: candidateProfile.mutate,
    mutateResume: resume.mutate,
    mutateGitHub: github.mutate,
    mutateProfiles: profiles.mutate,
  }
}
