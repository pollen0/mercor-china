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
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-pulse text-gray-600">Loading profile...</div>
      </div>
    )
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-8">
        <Card className="max-w-md p-8 text-center">
          <div className="text-red-600 text-5xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Unable to Load Profile</h2>
          <p className="text-gray-600">{error}</p>
        </Card>
      </div>
    )
  }

  const majors = profile.majors && profile.majors.length > 0 ? profile.majors : (profile.major ? [profile.major] : [])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-6 py-6">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
            <span>Pathway</span>
            <span>•</span>
            <span>Candidate Profile</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">{profile.name}</h1>
          {profile.university && (
            <p className="text-gray-600 mt-2">
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
              <p className="text-sm text-gray-500">University</p>
              <p className="font-medium">{profile.university || 'Not specified'}</p>
            </div>
            {majors.length > 0 && (
              <div>
                <p className="text-sm text-gray-500">Major{majors.length > 1 ? 's' : ''}</p>
                <p className="font-medium">{majors.join(', ')}</p>
              </div>
            )}
            {profile.minors && profile.minors.length > 0 && (
              <div>
                <p className="text-sm text-gray-500">Minor{profile.minors.length > 1 ? 's' : ''}</p>
                <p className="font-medium">{profile.minors.join(', ')}</p>
              </div>
            )}
            {profile.gpa && (
              <div>
                <p className="text-sm text-gray-500">GPA</p>
                <p className="font-medium">{profile.gpa.toFixed(2)} / 4.0</p>
              </div>
            )}
            {profile.graduationYear && (
              <div>
                <p className="text-sm text-gray-500">Graduation Year</p>
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
                <div key={vertical} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <span className="font-medium">{VERTICAL_NAMES[vertical] || vertical}</span>
                  <div className="flex items-center gap-2">
                    <div className="text-2xl font-bold text-indigo-600">{score.toFixed(1)}</div>
                    <span className="text-sm text-gray-500">/ 10</span>
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
                <p className="text-sm text-gray-500 mb-2">Username</p>
                <a
                  href={`https://github.com/${profile.githubUsername}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-indigo-600 hover:underline font-medium"
                >
                  @{profile.githubUsername}
                </a>
              </div>

              {profile.githubData?.languages && Object.keys(profile.githubData.languages).length > 0 && (
                <div>
                  <p className="text-sm text-gray-500 mb-2">Top Languages</p>
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
                  <p className="text-sm text-gray-500 mb-2">Top Repositories</p>
                  <div className="space-y-2">
                    {profile.githubData.repos.slice(0, 3).map((repo: any) => (
                      <a
                        key={repo.name}
                        href={repo.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-medium text-gray-900">{repo.name}</p>
                            {repo.description && (
                              <p className="text-sm text-gray-600 mt-1">{repo.description}</p>
                            )}
                          </div>
                          <div className="text-sm text-gray-500">
                            ⭐ {repo.stars || 0}
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
            <p className="text-gray-700 whitespace-pre-wrap">{profile.bio}</p>
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
                  className="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition text-indigo-600 hover:underline"
                >
                  LinkedIn Profile →
                </a>
              )}
              {profile.portfolioUrl && (
                <a
                  href={profile.portfolioUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition text-indigo-600 hover:underline"
                >
                  Portfolio →
                </a>
              )}
              {profile.resumeUrl && (
                <a
                  href={profile.resumeUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition text-indigo-600 hover:underline"
                >
                  View Resume →
                </a>
              )}
            </div>
          </Card>
        )}

        {/* Footer */}
        <div className="text-center py-8">
          <p className="text-sm text-gray-500">
            Powered by{' '}
            <a href="/" className="text-indigo-600 hover:underline font-medium">
              Pathway
            </a>
          </p>
          <p className="text-xs text-gray-400 mt-2">
            This is a secure, time-limited link. Contact information is protected.
          </p>
        </div>
      </div>
    </div>
  )
}
