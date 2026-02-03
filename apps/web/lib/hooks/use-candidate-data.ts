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
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      dedupingInterval: 60000, // 1 minute
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
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      dedupingInterval: 60000, // 1 minute
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
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      dedupingInterval: 60000,
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
  const { data, error, isLoading } = useSWR(
    token ? ['github-analysis', token] : null,
    async ([, t]) => {
      try {
        return await candidateApi.getGitHubAnalysis(t)
      } catch {
        return null
      }
    },
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      dedupingInterval: 300000, // 5 minutes - analysis doesn't change often
    }
  )

  return {
    githubAnalysis: data,
    isLoading,
    error,
  }
}

// Hook for fetching vertical profiles with caching
export function useVerticalProfiles(token: string | null) {
  const { data, error, isLoading, mutate } = useSWR(
    token ? ['vertical-profiles', token] : null,
    ([, t]) => candidateVerticalApi.getMyVerticals(t),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      dedupingInterval: 60000,
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
  const { data, error, isLoading } = useSWR(
    token ? ['matching-jobs', token] : null,
    ([, t]) => candidateVerticalApi.getMatchingJobs(t),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      dedupingInterval: 120000, // 2 minutes
    }
  )

  return {
    jobs: data?.jobs || [],
    isLoading,
    error,
  }
}

// Combined hook for all dashboard data
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
    mutateResume: resume.mutate,
    mutateGitHub: github.mutate,
    mutateProfiles: profiles.mutate,
  }
}
