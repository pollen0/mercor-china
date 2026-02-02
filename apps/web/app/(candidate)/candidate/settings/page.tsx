'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { candidateApi } from '@/lib/api'

const COMPANY_STAGES = [
  { value: 'seed', label: 'Seed Stage' },
  { value: 'series_a', label: 'Series A' },
  { value: 'series_b', label: 'Series B' },
  { value: 'series_c_plus', label: 'Series C+' },
]

const LOCATIONS = [
  { value: 'remote', label: 'Remote' },
  { value: 'sf', label: 'San Francisco' },
  { value: 'nyc', label: 'New York City' },
  { value: 'seattle', label: 'Seattle' },
  { value: 'austin', label: 'Austin' },
  { value: 'boston', label: 'Boston' },
  { value: 'la', label: 'Los Angeles' },
  { value: 'chicago', label: 'Chicago' },
]

const INDUSTRIES = [
  { value: 'fintech', label: 'Fintech' },
  { value: 'climate', label: 'Climate Tech' },
  { value: 'ai', label: 'AI/ML' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'enterprise', label: 'Enterprise SaaS' },
  { value: 'consumer', label: 'Consumer Tech' },
  { value: 'crypto', label: 'Web3/Crypto' },
  { value: 'edtech', label: 'Education' },
]

export default function SettingsPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const [optedIn, setOptedIn] = useState(false)
  const [companyStages, setCompanyStages] = useState<string[]>([])
  const [locations, setLocations] = useState<string[]>([])
  const [industries, setIndustries] = useState<string[]>([])
  const [emailDigest, setEmailDigest] = useState(true)

  useEffect(() => {
    loadPreferences()
  }, [])

  const loadPreferences = async () => {
    try {
      const token = localStorage.getItem('candidate_token')
      if (!token) {
        router.push('/login')
        return
      }

      const data = await candidateApi.getSharingPreferences(token)
      setOptedIn(data.optedInToSharing)
      if (data.preferences) {
        setCompanyStages(data.preferences.companyStages)
        setLocations(data.preferences.locations)
        setIndustries(data.preferences.industries)
        setEmailDigest(data.preferences.emailDigest)
      }
    } catch (error) {
      console.error('Failed to load preferences:', error)
      setMessage({ type: 'error', text: 'Failed to load preferences' })
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setMessage(null)

    try {
      const token = localStorage.getItem('candidate_token')
      if (!token) {
        router.push('/login')
        return
      }

      await candidateApi.updateSharingPreferences(
        {
          optedInToSharing: optedIn,
          companyStages,
          locations,
          industries,
          emailDigest,
        },
        token
      )

      setMessage({ type: 'success', text: 'Preferences saved successfully!' })
    } catch (error: any) {
      console.error('Failed to save preferences:', error)
      setMessage({ type: 'error', text: error.message || 'Failed to save preferences' })
    } finally {
      setSaving(false)
    }
  }

  const toggleArrayValue = (
    array: string[],
    value: string,
    setter: (arr: string[]) => void,
    maxLimit?: number
  ) => {
    if (array.includes(value)) {
      setter(array.filter(v => v !== value))
    } else {
      // Check limit before adding
      if (maxLimit && array.length >= maxLimit) {
        return // Don't add if limit reached
      }
      setter([...array, value])
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-stone-50 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-stone-200 rounded w-1/4 mb-4"></div>
            <div className="h-64 bg-stone-200 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-stone-50 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.back()}
            className="text-stone-500 hover:text-stone-900 mb-4 flex items-center gap-2 transition-colors"
          >
            ← Back
          </button>
          <h1 className="text-3xl font-bold text-stone-900">Privacy & Sharing Settings</h1>
          <p className="text-stone-500 mt-2">
            Control how your profile is shared with employers
          </p>
        </div>

        {/* Message */}
        {message && (
          <div
            className={`mb-6 p-4 rounded-xl ${
              message.type === 'success'
                ? 'bg-teal-50 text-teal-800 border border-teal-200'
                : 'bg-red-50 text-red-700 border border-red-100'
            }`}
          >
            {message.text}
          </div>
        )}

        {/* Main Settings Card */}
        <Card className="p-6 mb-6 shadow-soft-sm">
          {/* Opt-in Toggle */}
          <div className="mb-8 pb-8 border-b border-stone-100">
            <div className="flex items-start gap-4">
              <input
                type="checkbox"
                id="opted-in"
                checked={optedIn}
                onChange={(e) => setOptedIn(e.target.checked)}
                className="mt-1 h-5 w-5 text-teal-600 focus:ring-teal-500 border-stone-300 rounded accent-teal-600"
              />
              <div className="flex-1">
                <Label htmlFor="opted-in" className="text-lg font-semibold cursor-pointer text-stone-900">
                  Allow employers to view my profile
                </Label>
                <p className="text-sm text-stone-500 mt-1">
                  When enabled, your profile is shown to <span className="font-semibold text-stone-700">ALL employers</span> on Pathway.
                  Set preferences below to be <span className="font-semibold text-stone-700">prioritized</span> for companies you're most interested in.
                </p>
              </div>
            </div>
          </div>

          {/* Preferences (only show if opted in) */}
          {optedIn && (
            <>
              {/* Company Stages */}
              <div className="mb-8">
                <div className="flex items-center justify-between mb-3">
                  <Label className="text-base font-semibold text-stone-900">
                    Company Stages
                  </Label>
                  <span className="text-sm text-stone-400">
                    {companyStages.length} / 2 selected
                  </span>
                </div>
                <p className="text-sm text-stone-500 mb-4">
                  Select up to 2 stages to be prioritized for those companies (optional)
                </p>
                <div className="grid grid-cols-2 gap-3">
                  {COMPANY_STAGES.map((stage) => {
                    const isSelected = companyStages.includes(stage.value)
                    const isDisabled = !isSelected && companyStages.length >= 2
                    return (
                      <label
                        key={stage.value}
                        className={`flex items-center gap-3 p-3 border rounded-xl transition-all duration-200 ${
                          isDisabled
                            ? 'opacity-50 cursor-not-allowed bg-stone-50 border-stone-100'
                            : isSelected
                            ? 'border-teal-200 bg-teal-50/50 cursor-pointer'
                            : 'border-stone-200 cursor-pointer hover:bg-stone-50 hover:border-stone-300'
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={isSelected}
                          disabled={isDisabled}
                          onChange={() => toggleArrayValue(companyStages, stage.value, setCompanyStages, 2)}
                          className="h-4 w-4 text-teal-600 focus:ring-teal-500 border-stone-300 rounded accent-teal-600 disabled:opacity-50"
                        />
                        <span className="text-sm text-stone-700">{stage.label}</span>
                      </label>
                    )
                  })}
                </div>
              </div>

              {/* Locations */}
              <div className="mb-8">
                <div className="flex items-center justify-between mb-3">
                  <Label className="text-base font-semibold text-stone-900">
                    Preferred Locations
                  </Label>
                  <span className="text-sm text-stone-400">
                    {locations.length} / 4 selected
                  </span>
                </div>
                <p className="text-sm text-stone-500 mb-4">
                  Select up to 4 locations to be prioritized for those areas (optional)
                </p>
                <div className="grid grid-cols-2 gap-3">
                  {LOCATIONS.map((location) => {
                    const isSelected = locations.includes(location.value)
                    const isDisabled = !isSelected && locations.length >= 4
                    return (
                      <label
                        key={location.value}
                        className={`flex items-center gap-3 p-3 border rounded-xl transition-all duration-200 ${
                          isDisabled
                            ? 'opacity-50 cursor-not-allowed bg-stone-50 border-stone-100'
                            : isSelected
                            ? 'border-teal-200 bg-teal-50/50 cursor-pointer'
                            : 'border-stone-200 cursor-pointer hover:bg-stone-50 hover:border-stone-300'
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={isSelected}
                          disabled={isDisabled}
                          onChange={() => toggleArrayValue(locations, location.value, setLocations, 4)}
                          className="h-4 w-4 text-teal-600 focus:ring-teal-500 border-stone-300 rounded accent-teal-600 disabled:opacity-50"
                        />
                        <span className="text-sm text-stone-700">{location.label}</span>
                      </label>
                    )
                  })}
                </div>
              </div>

              {/* Industries */}
              <div className="mb-8">
                <div className="flex items-center justify-between mb-3">
                  <Label className="text-base font-semibold text-stone-900">
                    Industries of Interest
                  </Label>
                  <span className="text-sm text-stone-400">
                    {industries.length} / 3 selected
                  </span>
                </div>
                <p className="text-sm text-stone-500 mb-4">
                  Select up to 3 industries to be prioritized for those companies (optional)
                </p>
                <div className="grid grid-cols-2 gap-3">
                  {INDUSTRIES.map((industry) => {
                    const isSelected = industries.includes(industry.value)
                    const isDisabled = !isSelected && industries.length >= 3
                    return (
                      <label
                        key={industry.value}
                        className={`flex items-center gap-3 p-3 border rounded-xl transition-all duration-200 ${
                          isDisabled
                            ? 'opacity-50 cursor-not-allowed bg-stone-50 border-stone-100'
                            : isSelected
                            ? 'border-teal-200 bg-teal-50/50 cursor-pointer'
                            : 'border-stone-200 cursor-pointer hover:bg-stone-50 hover:border-stone-300'
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={isSelected}
                          disabled={isDisabled}
                          onChange={() => toggleArrayValue(industries, industry.value, setIndustries, 3)}
                          className="h-4 w-4 text-teal-600 focus:ring-teal-500 border-stone-300 rounded accent-teal-600 disabled:opacity-50"
                        />
                        <span className="text-sm text-stone-700">{industry.label}</span>
                      </label>
                    )
                  })}
                </div>
              </div>

              {/* Email Digest */}
              <div className="mb-8">
                <div className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg">
                  <input
                    type="checkbox"
                    id="email-digest"
                    checked={emailDigest}
                    onChange={(e) => setEmailDigest(e.target.checked)}
                    className="mt-1 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <div className="flex-1">
                    <Label htmlFor="email-digest" className="font-medium cursor-pointer">
                      Email Digest Notifications
                    </Label>
                    <p className="text-sm text-gray-600 mt-1">
                      Receive weekly updates when companies view your profile
                    </p>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* Save Button */}
          <div className="flex justify-end gap-4 pt-6 border-t">
            <Button
              variant="outline"
              onClick={() => router.back()}
              disabled={saving}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              disabled={saving}
              className="bg-indigo-600 hover:bg-indigo-700 text-white"
            >
              {saving ? 'Saving...' : 'Save Preferences'}
            </Button>
          </div>
        </Card>

        {/* Info Card */}
        {!optedIn ? (
          <Card className="p-6 bg-blue-50 border-blue-200">
            <h3 className="font-semibold text-blue-900 mb-2">
              Why opt in to profile sharing?
            </h3>
            <ul className="text-sm text-blue-800 space-y-2">
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-0.5">✓</span>
                <span>Get matched with relevant job opportunities automatically</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-0.5">✓</span>
                <span>Companies can reach out to you directly based on your skills and growth</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-0.5">✓</span>
                <span>Your profile is shown to ALL employers - preferences just help you rank higher</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-0.5">✓</span>
                <span>Your contact information stays private until you approve</span>
              </li>
            </ul>
          </Card>
        ) : (
          <Card className="p-6 bg-indigo-50 border-indigo-200">
            <h3 className="font-semibold text-indigo-900 mb-2">
              How preferences work
            </h3>
            <ul className="text-sm text-indigo-800 space-y-2">
              <li className="flex items-start gap-2">
                <span className="text-indigo-600 mt-0.5">•</span>
                <span><strong>Shown to everyone:</strong> Your profile is visible to all employers on Pathway</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-indigo-600 mt-0.5">•</span>
                <span><strong>Prioritized for preferences:</strong> You rank higher for companies matching your preferences</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-indigo-600 mt-0.5">•</span>
                <span><strong>Optional:</strong> Leave preferences blank to be equally visible to all companies</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-indigo-600 mt-0.5">•</span>
                <span><strong>Limits exist:</strong> Max selections help you focus on what matters most</span>
              </li>
            </ul>
          </Card>
        )}
      </div>
    </div>
  )
}
