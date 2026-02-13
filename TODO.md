# Pathway - Product Backlog & TODO

## High Priority

### Authentication & Security
- [x] **Forgot Password Flow** - Password reset via email
- [x] **Onboarding Email Sequence** - Welcome emails for new users
- [ ] **Email Verification Reminders** - Nudge unverified users

### Calendar & Scheduling
- [x] **Google Calendar Integration** - OAuth connection for candidates
- [x] **Google Meet Invites** - Auto-create meeting links for interviews
- [ ] **Interview Scheduling** - Let employers schedule calls with candidates (Frontend UI needed)

### Notifications
- [x] **Interview Completion Emails** - Notify candidates of results
- [ ] **Employer Match Alerts** - Email employers when good candidates match
- [x] **Weekly Digest** - Summary of activity for opted-in users
- [x] **Profile View Notifications** - Tell candidates when employers view them

---

## Medium Priority

### Live Coding / Product Building Interviews
> **Research completed - see details below**

- [ ] Embed CodeSandbox or StackBlitz for coding environment
- [ ] Create role-specific starter templates (React, Express, etc.)
- [ ] 30-45 min time-boxed building sessions
- [ ] AI review of code quality and patterns
- [ ] Session recording for employer playback
- [ ] Progressive difficulty (harder tasks as scores improve)

**Recommended Approach:** Start with CodeSandbox embeds, add AI code review

### Profile Enhancements
- [ ] **LinkedIn Import** - Pull profile data from LinkedIn
- [ ] **Portfolio Links** - Better showcase of projects
- [ ] **Video Introduction** - 60-second pitch video option

### Employer Features
- [ ] **Job URL Import** - Paste a job posting URL and auto-extract details using AI
- [ ] **Saved Searches** - Save talent pool filters
- [ ] **ATS Integration** - Export to Greenhouse, Lever, etc.

### Technical Debt
- [ ] **Split api.ts** - Break `lib/api.ts` (~4700 lines) into modules
- [ ] Apply grade inflation adjustment in transcript scoring
- [ ] Add CSRF state validation in GitHub OAuth callback
- [ ] Add GitHub API rate limiting
- [ ] Add error notifications for failed background tasks
- [ ] Migrate existing plaintext GitHub tokens to encrypted

---

## Low Priority / Future

### Analytics
- [ ] **Candidate Analytics** - Track profile views, match rates
- [ ] **Employer Analytics** - Hiring funnel metrics
- [ ] **Platform Analytics** - Overall usage dashboard

### Mobile
- [ ] **Mobile App** - React Native app for interviews on-the-go
- [ ] **Mobile-Optimized Recording** - Better video capture on phones

### AI Enhancements
- [ ] **AI Interview Coach** - Practice mode with real-time feedback
- [ ] **Resume Optimizer** - AI suggestions to improve resume
- [ ] **Question Bank Expansion** - More industry-specific questions

### Integrations
- [ ] **Slack Integration** - Notifications in Slack
- [ ] **Zapier Integration** - Connect to other tools
- [ ] **Calendar Sync** - Sync interviews to any calendar

---

## Future / Enterprise Features (Deferred)

> These features are premature for current stage. Revisit after GTM validation with 50+ companies.

### University Relations
- [ ] **University Relationship Management** - Track recruiting success by school
- [ ] **Campus Event Management** - Info sessions, career fairs

### Intern Program Management
- [ ] **Internship to FT Conversion Tracking** - Track return offers
- [ ] **Intern Class Planning** - Cohort sizes, start dates, team assignments

### Network Effects
- [ ] **Alumni Referral Network** - Connect hired candidates back to refer classmates

---

## Completed

### Core Platform
- [x] Monthly interview system with 30-day cooldown
- [x] 5-Dimension AI Scoring (Communication, Problem Solving, Technical, Growth Mindset, Culture Fit)
- [x] Progressive AI Question System (difficulty adjusts based on history)
- [x] Talent Pool with Filters (vertical, school, graduation year, score)
- [x] Candidate status management (New/Contacted/In Review/Shortlisted/Rejected/Hired)

### GitHub Integration
- [x] GitHub OAuth Integration
- [x] Code quality analysis (originality, activity, depth, collaboration)
- [x] GitHub analysis display (visual scores on dashboard)
- [x] Token Encryption for GitHub (Fernet)

### Growth Tracking
- [x] Resume versioning (versioned uploads with skill deltas)
- [x] GitHub analysis history (timestamped score snapshots)
- [x] Profile change logs (audit trail for GPA, major, education)
- [x] Growth Timeline UI (recruiter-only progressive disclosure component)

### Employer Features
- [x] Private candidate notes for employers
- [x] Scheduled interviews page with Google Meet
- [x] Self-scheduling links (employers create, candidates book)
- [x] Match alerts for high-scoring candidates
- [x] Organization teams with roles and invites

### Communication
- [x] Welcome/Onboarding Emails
- [x] Interview Reminder Emails
- [x] Profile View Notification Emails
- [x] Weekly Digest Emails
- [x] Forgot Password Flow

### Other
- [x] Resume Parsing & Analysis
- [x] Transcript Analysis & Verification
- [x] Profile Sharing Preferences
- [x] Public Candidate Profiles with shareable tokens
- [x] Profile Scoring Endpoint
- [x] Cohort Comparisons ("Top X% of [University] [Year]")
- [x] Candidate Watchlist
- [x] Preference Boost in Matching (+30 max)
- [x] Club/Activity Database (147 Berkeley clubs)
- [x] Google Calendar OAuth Service
- [x] Referral System (code generation, status tracking, stats)
- [x] Vibe Code Challenge Sessions
- [x] Marketing Referrer Tracking
- [x] ML Scoring Data Pipeline
- [x] Admin Panel with batch operations

### Job Seeding (14 VC Firms)
- [x] Y Combinator (x2 batches)
- [x] Andreessen Horowitz (a16z)
- [x] Sequoia Capital
- [x] Lightspeed Venture Partners
- [x] Khosla Ventures
- [x] New Enterprise Associates (NEA)
- [x] Accel
- [x] Bessemer Venture Partners
- [x] Dragoneer Investment Group
- [x] Legend Venture Capital
- [x] Tiger Global Management
- [x] Technology Crossover Ventures (TCV)

**DB Totals**: ~134 employers, ~180 intern job positions

---

*Last updated: 2026-02-13*
