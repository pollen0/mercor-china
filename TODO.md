# Pathway - Product Backlog & TODO

## High Priority

### Authentication & Security
- [x] **Forgot Password Flow** - Password reset via email (Backend done - needs frontend)
- [x] **Onboarding Email Sequence** - Welcome emails for new users (Backend done)
- [ ] **Email Verification Reminders** - Nudge unverified users

### Calendar & Scheduling
- [x] **Google Calendar Integration** - OAuth connection for candidates (Backend done - needs Google Console setup)
- [x] **Google Meet Invites** - Auto-create meeting links for interviews (Backend done)
- [ ] **Interview Scheduling** - Let employers schedule calls with candidates (Frontend UI needed)

### Notifications
- [x] **Interview Completion Emails** - Notify candidates of results (Backend done)
- [ ] **Employer Match Alerts** - Email employers when good candidates match
- [x] **Weekly Digest** - Summary of activity for opted-in users (Backend done)
- [x] **Profile View Notifications** - Tell candidates when employers view them (Backend done)

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

**Implementation Options:**
1. **Option A:** Embed existing platform (StackBlitz/CodeSandbox)
2. **Option B:** WebContainers API integration (runs Node.js in browser)
3. **Option C:** Replit/CodeSandbox API (spin up sandboxes per interview)

**Recommended Approach:** Start with CodeSandbox embeds, add AI code review

**Research Sources:**
- [CoderPad](https://coderpad.io/) - Live coding interview platform
- [CodeSignal](https://codesignal.com/integrated-development-environment/) - IDE for real dev simulation
- [WebContainers](https://webcontainers.io/ai) - In-browser code execution
- [Mercor Interview Prep](https://talent.docs.mercor.com/how-to/prepare-for-ai-interview)

### Profile Enhancements
- [ ] **LinkedIn Import** - Pull profile data from LinkedIn
- [ ] **Portfolio Links** - Better showcase of projects
- [ ] **Video Introduction** - 60-second pitch video option

### Employer Features
- [ ] **Saved Searches** - Save talent pool filters
- [ ] **Candidate Notes** - Private notes on candidates
- [ ] **Team Collaboration** - Multiple users per employer account
- [ ] **ATS Integration** - Export to Greenhouse, Lever, etc.

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

## Completed
- [x] Progressive AI Question System
- [x] GitHub OAuth Integration
- [x] Resume Parsing & Analysis
- [x] Transcript Analysis
- [x] Club/Activity Database (147 Berkeley clubs)
- [x] 5-Dimension AI Scoring
- [x] Talent Pool with Filters
- [x] Profile Sharing Preferences
- [x] Token Encryption for GitHub
- [x] Profile Scoring Endpoint
- [x] Forgot Password Flow (Backend API)
- [x] Welcome/Onboarding Emails (Backend API)
- [x] Google Calendar OAuth Service
- [x] Google Meet Integration (Backend API)
- [x] Interview Reminder Emails
- [x] Profile View Notification Emails
- [x] Weekly Digest Emails

---

## Technical Debt
- [ ] Apply grade inflation adjustment in transcript scoring
- [ ] Add CSRF state validation in GitHub OAuth callback
- [ ] Add GitHub API rate limiting
- [ ] Add error notifications for failed background tasks
- [ ] Migrate existing plaintext GitHub tokens to encrypted

---

*Last updated: 2026-02-01*
