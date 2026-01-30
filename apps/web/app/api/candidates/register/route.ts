import { NextResponse } from 'next/server'
import { candidateRegistrationSchema } from '@/lib/validations/candidate'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function POST(request: Request) {
  try {
    const body = await request.json()

    const result = candidateRegistrationSchema.safeParse(body)

    if (!result.success) {
      return NextResponse.json(
        { error: 'Validation failed', details: result.error.errors },
        { status: 400 }
      )
    }

    const { name, email, phone, password, targetRoles } = result.data

    // Call the FastAPI backend instead of Prisma
    const response = await fetch(`${API_URL}/api/candidates/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name,
        email,
        phone,
        password,
        target_roles: targetRoles,
      }),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Registration failed' }))

      // Handle duplicate email
      if (response.status === 409 || (typeof error.detail === 'string' && error.detail.includes('already'))) {
        return NextResponse.json(
          { error: 'This email is already registered' },
          { status: 409 }
        )
      }

      // Handle Pydantic validation errors (array format)
      if (Array.isArray(error.detail)) {
        const messages = error.detail.map((e: { msg?: string; loc?: string[] }) => {
          const field = e.loc?.[1] || 'field'
          const msg = e.msg?.replace('Value error, ', '') || 'Invalid value'
          return `${field}: ${msg}`
        }).join('; ')
        return NextResponse.json(
          { error: messages },
          { status: 400 }
        )
      }

      return NextResponse.json(
        { error: typeof error.detail === 'string' ? error.detail : 'Registration failed' },
        { status: response.status }
      )
    }

    const data = await response.json()

    return NextResponse.json(
      {
        message: 'Registration successful',
        candidate: {
          id: data.candidate.id,
          name: data.candidate.name,
          email: data.candidate.email,
        },
        token: data.token,
      },
      { status: 201 }
    )
  } catch (error) {
    console.error('Registration error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
