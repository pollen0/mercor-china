import { z } from 'zod'

export const candidateRegistrationSchema = z.object({
  name: z
    .string()
    .min(2, 'Name must be at least 2 characters')
    .max(50, 'Name cannot exceed 50 characters'),
  email: z
    .string()
    .email('Please enter a valid email address'),
  phone: z
    .string()
    .min(10, 'Please enter a valid phone number')
    .max(20, 'Phone number is too long'),
  targetRoles: z
    .array(z.string())
    .optional()
    .default([]),
})

export type CandidateRegistrationInput = z.infer<typeof candidateRegistrationSchema>

export const targetRoleOptions = [
  { value: 'frontend', label: 'Frontend Developer' },
  { value: 'backend', label: 'Backend Developer' },
  { value: 'fullstack', label: 'Full Stack Developer' },
  { value: 'mobile', label: 'Mobile Developer' },
  { value: 'data', label: 'Data Engineer' },
  { value: 'ai', label: 'AI/Machine Learning' },
  { value: 'devops', label: 'DevOps Engineer' },
  { value: 'product', label: 'Product Manager' },
  { value: 'design', label: 'UI/UX Designer' },
  { value: 'qa', label: 'QA Engineer' },
]
