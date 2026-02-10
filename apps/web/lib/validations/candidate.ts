import { z } from 'zod'

// Top 100 CS schools — alphabetical by label
export const universityOptions = [
  { value: 'asu', label: 'Arizona State University' },
  { value: 'auburn', label: 'Auburn University' },
  { value: 'binghamton', label: 'Binghamton University (SUNY)' },
  { value: 'bu', label: 'Boston University' },
  { value: 'brandeis', label: 'Brandeis University' },
  { value: 'brown', label: 'Brown University' },
  { value: 'caltech', label: 'Caltech' },
  { value: 'cmu', label: 'Carnegie Mellon University' },
  { value: 'case_western', label: 'Case Western Reserve University' },
  { value: 'clemson', label: 'Clemson University' },
  { value: 'colorado_state', label: 'Colorado State University' },
  { value: 'columbia', label: 'Columbia University' },
  { value: 'cornell', label: 'Cornell University' },
  { value: 'dartmouth', label: 'Dartmouth College' },
  { value: 'drexel', label: 'Drexel University' },
  { value: 'duke', label: 'Duke University' },
  { value: 'gmu', label: 'George Mason University' },
  { value: 'gwu', label: 'George Washington University' },
  { value: 'georgia_tech', label: 'Georgia Tech' },
  { value: 'georgetown', label: 'Georgetown University' },
  { value: 'harvard', label: 'Harvard University' },
  { value: 'indiana', label: 'Indiana University Bloomington' },
  { value: 'iowa_state', label: 'Iowa State University' },
  { value: 'johns_hopkins', label: 'Johns Hopkins University' },
  { value: 'lehigh', label: 'Lehigh University' },
  { value: 'lsu', label: 'Louisiana State University' },
  { value: 'mit', label: 'MIT' },
  { value: 'michigan_state', label: 'Michigan State University' },
  { value: 'nc_state', label: 'NC State University' },
  { value: 'njit', label: 'New Jersey Institute of Technology' },
  { value: 'nyu', label: 'New York University' },
  { value: 'northeastern', label: 'Northeastern University' },
  { value: 'northwestern', label: 'Northwestern University' },
  { value: 'ohio_state', label: 'Ohio State University' },
  { value: 'oregon_state', label: 'Oregon State University' },
  { value: 'penn_state', label: 'Penn State University' },
  { value: 'princeton', label: 'Princeton University' },
  { value: 'purdue', label: 'Purdue University' },
  { value: 'rpi', label: 'Rensselaer Polytechnic Institute' },
  { value: 'rice', label: 'Rice University' },
  { value: 'rit', label: 'Rochester Institute of Technology' },
  { value: 'rutgers', label: 'Rutgers University' },
  { value: 'santa_clara', label: 'Santa Clara University' },
  { value: 'smu', label: 'Southern Methodist University' },
  { value: 'stanford', label: 'Stanford University' },
  { value: 'stevens', label: 'Stevens Institute of Technology' },
  { value: 'stony_brook', label: 'Stony Brook University' },
  { value: 'syracuse', label: 'Syracuse University' },
  { value: 'temple', label: 'Temple University' },
  { value: 'tamu', label: 'Texas A&M University' },
  { value: 'tufts', label: 'Tufts University' },
  { value: 'tulane', label: 'Tulane University' },
  { value: 'berkeley', label: 'UC Berkeley' },
  { value: 'uc_davis', label: 'UC Davis' },
  { value: 'uc_irvine', label: 'UC Irvine' },
  { value: 'ucr', label: 'UC Riverside' },
  { value: 'ucla', label: 'UCLA' },
  { value: 'uc_san_diego', label: 'UC San Diego' },
  { value: 'ucsb', label: 'UC Santa Barbara' },
  { value: 'ucsc', label: 'UC Santa Cruz' },
  { value: 'usc', label: 'USC' },
  { value: 'utd', label: 'UT Dallas' },
  { value: 'buffalo', label: 'University at Buffalo (SUNY)' },
  { value: 'alabama', label: 'University of Alabama' },
  { value: 'ucf', label: 'University of Central Florida' },
  { value: 'cu_boulder', label: 'University of Colorado Boulder' },
  { value: 'uconn', label: 'University of Connecticut' },
  { value: 'delaware', label: 'University of Delaware' },
  { value: 'uf', label: 'University of Florida' },
  { value: 'uiuc', label: 'University of Illinois Urbana-Champaign' },
  { value: 'uic', label: 'University of Illinois Chicago' },
  { value: 'iowa', label: 'University of Iowa' },
  { value: 'kansas', label: 'University of Kansas' },
  { value: 'uky', label: 'University of Kentucky' },
  { value: 'umass', label: 'University of Massachusetts Amherst' },
  { value: 'umd', label: 'University of Maryland' },
  { value: 'miami', label: 'University of Miami' },
  { value: 'umich', label: 'University of Michigan' },
  { value: 'umn', label: 'University of Minnesota' },
  { value: 'missouri', label: 'University of Missouri' },
  { value: 'nebraska', label: 'University of Nebraska-Lincoln' },
  { value: 'unc', label: 'University of North Carolina at Chapel Hill' },
  { value: 'notre_dame', label: 'University of Notre Dame' },
  { value: 'uoregon', label: 'University of Oregon' },
  { value: 'upenn', label: 'University of Pennsylvania' },
  { value: 'pitt', label: 'University of Pittsburgh' },
  { value: 'rochester', label: 'University of Rochester' },
  { value: 'usf', label: 'University of South Florida' },
  { value: 'tennessee', label: 'University of Tennessee' },
  { value: 'ut_austin', label: 'University of Texas at Austin' },
  { value: 'utah', label: 'University of Utah' },
  { value: 'uva', label: 'University of Virginia' },
  { value: 'uw', label: 'University of Washington' },
  { value: 'uwisc', label: 'University of Wisconsin-Madison' },
  { value: 'vanderbilt', label: 'Vanderbilt University' },
  { value: 'virginia_tech', label: 'Virginia Tech' },
  { value: 'washu', label: 'Washington University in St. Louis' },
  { value: 'wm', label: 'William & Mary' },
  { value: 'wpi', label: 'Worcester Polytechnic Institute' },
  { value: 'yale', label: 'Yale University' },
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
