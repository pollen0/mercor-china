import { z } from 'zod'

// Top 20 CS schools + UCSB — alphabetical by label
export const universityOptions = [
  { value: 'caltech', label: 'Caltech' },
  { value: 'cmu', label: 'Carnegie Mellon University' },
  { value: 'columbia', label: 'Columbia University' },
  { value: 'cornell', label: 'Cornell University' },
  { value: 'georgia_tech', label: 'Georgia Tech' },
  { value: 'harvard', label: 'Harvard University' },
  { value: 'mit', label: 'MIT' },
  { value: 'princeton', label: 'Princeton University' },
  { value: 'purdue', label: 'Purdue University' },
  { value: 'stanford', label: 'Stanford University' },
  { value: 'uc_berkeley', label: 'UC Berkeley' },
  { value: 'ucla', label: 'UCLA' },
  { value: 'uc_san_diego', label: 'UC San Diego' },
  { value: 'ucsb', label: 'UC Santa Barbara' },
  { value: 'ucsc', label: 'UC Santa Cruz' },
  { value: 'uiuc', label: 'University of Illinois Urbana-Champaign' },
  { value: 'umich', label: 'University of Michigan' },
  { value: 'umd', label: 'University of Maryland' },
  { value: 'upenn', label: 'University of Pennsylvania' },
  { value: 'ut_austin', label: 'University of Texas at Austin' },
  { value: 'uw', label: 'University of Washington' },
  { value: 'uwisc', label: 'University of Wisconsin-Madison' },
] as const

export const graduationYearOptions = [
  { value: 2025, label: '2025' },
  { value: 2026, label: '2026' },
  { value: 2027, label: '2027' },
  { value: 2028, label: '2028' },
  { value: 2029, label: '2029' },
] as const

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
    .min(7, 'Please enter a valid phone number')
    .max(20, 'Phone number is too long'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[0-9]/, 'Password must contain at least one number')
    .regex(/[a-zA-Z]/, 'Password must contain at least one letter'),
  university: z
    .string()
    .min(1, 'Please select your university'),
  graduationYear: z
    .number()
    .min(2024, 'Invalid graduation year')
    .max(2030, 'Invalid graduation year')
    .optional(),
  major: z
    .string()
    .max(100, 'Major name is too long')
    .optional(),
  targetRoles: z
    .array(z.string())
    .optional()
    .default([]),
  referralCode: z
    .string()
    .optional(),
})

export type CandidateRegistrationInput = z.infer<typeof candidateRegistrationSchema>

export const candidateLoginSchema = z.object({
  email: z
    .string()
    .email('Please enter a valid email address'),
  password: z
    .string()
    .min(1, 'Password is required'),
})

export type CandidateLoginInput = z.infer<typeof candidateLoginSchema>

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

export const majorOptions = [
  { value: 'Computer Science', label: 'Computer Science' },
  { value: 'Computer Engineering', label: 'Computer Engineering' },
  { value: 'Electrical Engineering', label: 'Electrical Engineering' },
  { value: 'Software Engineering', label: 'Software Engineering' },
  { value: 'Data Science', label: 'Data Science' },
  { value: 'Statistics', label: 'Statistics' },
  { value: 'Mathematics', label: 'Mathematics' },
  { value: 'Applied Math', label: 'Applied Math' },
  { value: 'Physics', label: 'Physics' },
  { value: 'Information Science', label: 'Information Science' },
  { value: 'Economics', label: 'Economics' },
  { value: 'Business', label: 'Business' },
  { value: 'Finance', label: 'Finance' },
  { value: 'Cognitive Science', label: 'Cognitive Science' },
  { value: 'Mechanical Engineering', label: 'Mechanical Engineering' },
  { value: 'Bioengineering', label: 'Bioengineering' },
  { value: 'Design', label: 'Design' },
  { value: 'Other', label: 'Other' },
]
