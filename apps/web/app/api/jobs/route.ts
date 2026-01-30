import { NextResponse } from 'next/server'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const isActive = searchParams.get('is_active') || 'true'

    const response = await fetch(`${API_URL}/api/employers/jobs?is_active=${isActive}`, {
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      // Return empty jobs list on error
      return NextResponse.json({ jobs: [], total: 0 })
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Jobs fetch error:', error)
    return NextResponse.json({ jobs: [], total: 0 })
  }
}
