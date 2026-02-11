'use client'

import { useEffect, useState } from 'react'
import { useParams, useSearchParams } from 'next/navigation'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { publicApi } from '@/lib/api'

const VERTICAL_NAMES: Record<string, string> = {
  software_engineering: 'Software Engineering',
  data: 'Data',
  product: 'Product',
  design: 'Design',
  finance: 'Finance',
}

export default function PublicCandidateProfilePage() {
  const params = useParams()
  const searchParams = useSearchParams()
  const candidateId = params.candidateId as string
  const token = searchParams.get('token')

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [profile, setProfile] = useState<any>(null)

  useEffect(() => {
    if (!token) {
      setError('Missing access token')
      setLoading(false)
      return
    }

    loadProfile()
  }, [candidateId, token])

  const loadProfile = async () => {
    try {
      const data = await publicApi.getCandidateProfile(candidateId, token!)
      setProfile(data)
    } catch (err: any) {
      console.error('Failed to load profile:', err)
      if (err.status === 403) {
        setError('This link has expired or the candidate has disabled sharing')
      } else if (err.status === 404) {
        setError('Candidate not found')
      } else {
        setError('Failed to load profile')
      }
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="animate-pulse text-stone-600">Loading profile...</div>
      </div>
    )
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center p-8">
        <Card className="max-w-md p-8 text-center">
          <div className="mb-4 flex justify-center">
            <svg className="w-12 h-12 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" /></svg>
          </div>
          <h2 className="text-2xl font-semibold text-stone-900 mb-2">Unable to Load Profile</h2>
          <p className="text-stone-600">{error}</p>
        </Card>
      </div>
    )
  }

  const majors = profile.majors && profile.majors.length > 0 ? profile.majors : (profile.major ? [profile.major] : [])

  return (
    <div className="min-h-screen bg-stone-50">
      {/* Header */}
      <header className="bg-white border-b border-stone-200">
        <div className="max-w-5xl mx-auto px-6 py-6">
          <div className="flex items-center gap-2 text-sm text-stone-500 mb-4">
            <span>Pathway</span>
            <span>•</span>
            <span>Candidate Profile</span>
          </div>
          <h1 className="text-3xl font-semibold text-stone-900">{profile.name}</h1>
          {profile.university && (
            <p className="text-stone-600 mt-2">
              {majors.join(' & ')} at {profile.university}
              {profile.graduationYear && ` • Class of ${profile.graduationYear}`}
            </p>
          )}
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-6 py-8 space-y-6">
        {/* Education Card */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Education</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-stone-500">University</p>
              <p className="font-medium">{profile.university || 'Not specified'}</p>
            </div>
            {majors.length > 0 && (
              <div>
                <p className="text-sm text-stone-500">Major{majors.length > 1 ? 's' : ''}</p>
                <p className="font-medium">{majors.join(', ')}</p>
              </div>
            )}
            {profile.minors && profile.minors.length > 0 && (
              <div>
                <p className="text-sm text-stone-500">Minor{profile.minors.length > 1 ? 's' : ''}</p>
                <p className="font-medium">{profile.minors.join(', ')}</p>
              </div>
            )}
            {profile.gpa && (
              <div>
                <p className="text-sm text-stone-500">GPA</p>
                <p className="font-medium">{profile.gpa.toFixed(2)} / 4.0</p>
              </div>
            )}
            {profile.graduationYear && (
              <div>
                <p className="text-sm text-stone-500">Graduation Year</p>
                <p className="font-medium">{profile.graduationYear}</p>
              </div>
            )}
          </div>
        </Card>

        {/* Interview Scores */}
        {profile.bestScores && Object.keys(profile.bestScores).length > 0 && (
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Interview Scores</h2>
            <div className="grid grid-cols-2 gap-4">
              {Object.entries(profile.bestScores).map(([vertical, score]: [string, any]) => (
                <div key={vertical} className="flex items-center justify-between p-4 bg-stone-50 rounded-lg">
                  <span className="font-medium">{VERTICAL_NAMES[vertical] || vertical}</span>
                  <div className="flex items-center gap-2">
                    <div className="text-2xl font-semibold text-teal-600">{score.toFixed(1)}</div>
                    <span className="text-sm text-stone-500">/ 10</span>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* GitHub */}
        {profile.githubUsername && (
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">GitHub Profile</h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-stone-500 mb-2">Username</p>
                <a
                  href={`https://github.com/${profile.githubUsername}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-teal-600 hover:underline font-medium"
                >
                  @{profile.githubUsername}
                </a>
              </div>

              {profile.githubData?.languages && Object.keys(profile.githubData.languages).length > 0 && (
                <div>
                  <p className="text-sm text-stone-500 mb-2">Top Languages</p>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(profile.githubData.languages)
                      .sort(([, a]: any, [, b]: any) => b - a)
                      .slice(0, 5)
                      .map(([lang]: any) => (
                        <Badge key={lang} variant="default">{lang}</Badge>
                      ))}
                  </div>
                </div>
              )}

              {profile.githubData?.repos && profile.githubData.repos.length > 0 && (
                <div>
                  <p className="text-sm text-stone-500 mb-2">Top Repositories</p>
                  <div className="space-y-2">
                    {profile.githubData.repos.slice(0, 3).map((repo: any) => (
                      <a
                        key={repo.name}
                        href={repo.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block p-3 bg-stone-50 rounded-lg hover:bg-stone-100 transition"
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-medium text-stone-900">{repo.name}</p>
                            {repo.description && (
                              <p className="text-sm text-stone-600 mt-1">{repo.description}</p>
                            )}
                          </div>
                          <div className="flex items-center gap-1 text-sm text-stone-500">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" /></svg>
                            {repo.stars || 0}
                          </div>
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </Card>
        )}

        {/* Bio */}
        {profile.bio && (
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">About</h2>
            <p className="text-stone-700 whitespace-pre-wrap">{profile.bio}</p>
          </Card>
        )}

        {/* Links */}
        {(profile.linkedinUrl || profile.portfolioUrl || profile.resumeUrl) && (
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Links</h2>
            <div className="space-y-3">
              {profile.linkedinUrl && (
                <a
                  href={profile.linkedinUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block p-3 bg-stone-50 rounded-lg hover:bg-stone-100 transition text-teal-600 hover:underline"
                >
                  LinkedIn Profile <svg className="inline w-3.5 h-3.5 ml-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" /></svg>
                </a>
              )}
              {profile.portfolioUrl && (
                <a
                  href={profile.portfolioUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block p-3 bg-stone-50 rounded-lg hover:bg-stone-100 transition text-teal-600 hover:underline"
                >
                  Portfolio <svg className="inline w-3.5 h-3.5 ml-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" /></svg>
                </a>
              )}
              {profile.resumeUrl && (
                <a
                  href={profile.resumeUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block p-3 bg-stone-50 rounded-lg hover:bg-stone-100 transition text-teal-600 hover:underline"
                >
                  View Resume <svg className="inline w-3.5 h-3.5 ml-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" /></svg>
                </a>
              )}
            </div>
          </Card>
        )}

        {/* Footer */}
        <div className="text-center py-8">
          <p className="text-sm text-stone-500">
            Powered by{' '}
            <a href="/" className="text-teal-600 hover:underline font-medium">
              Pathway
            </a>
          </p>
          <p className="text-xs text-stone-400 mt-2">
            This is a secure, time-limited link. Contact information is protected.
          </p>
        </div>
      </div>
    </div>
  )
}
