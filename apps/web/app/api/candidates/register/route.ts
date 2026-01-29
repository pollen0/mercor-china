import { NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { candidateRegistrationSchema } from '@/lib/validations/candidate'

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

    const { name, email, phone, targetRoles } = result.data

    const existingCandidate = await prisma.candidate.findUnique({
      where: { email },
    })

    if (existingCandidate) {
      return NextResponse.json(
        { error: 'This email is already registered' },
        { status: 409 }
      )
    }

    const candidate = await prisma.candidate.create({
      data: {
        name,
        email,
        phone,
        targetRoles,
      },
    })

    return NextResponse.json(
      {
        message: 'Registration successful',
        candidate: {
          id: candidate.id,
          name: candidate.name,
          email: candidate.email,
        },
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
