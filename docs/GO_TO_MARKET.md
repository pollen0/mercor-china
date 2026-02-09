# Pathway — Go-to-Market Strategy

## Executive Summary

Pathway is a career platform for US college students. Students interview monthly to show growth over time, connect their GitHub, upload transcripts, and submit AI coding sessions. Employers get rich, multi-dimensional profiles with AI scoring, code authenticity analysis, and growth trajectory data.

**Business model**: Supply-first marketplace. Build student supply, then sell access to employers.

**Revenue**: Free during beta. Future: per-seat employer subscription ($500-2k/mo) or per-hire fee ($2-5k).

---

## Phase 1: Build Student Supply (Weeks 1-6)

### Goal: 200+ active student profiles with completed interviews

**Why students first**: An employer landing on an empty talent pool will never come back. We need critical mass before any employer outreach.

### Strategy: Campus-First at UC Berkeley

Berkeley is our strongest position (147 clubs with prestige data, course difficulty database, existing club relationships).

**Week 1-2: Seed users**
- Partner with 3-5 CS/engineering clubs (Codeology, CS KickStart, CSUA, SWE)
- Offer: "Get discovered by employers hiring Berkeley students. Free. Takes 15 minutes."
- Ask club leaders to send one Slack/Discord message to their members
- Target: 50 signups, 30 completed profiles

**Week 3-4: Campus push**
- Run a "Profile Building Night" event (2 hours, pizza, help students set up)
- Partner with Berkeley Career Center for co-promotion
- Post in CS 61A/61B/70/170 Piazza/Ed boards: "Looking for internships? Build your profile."
- Launch student referral: "Invite 3 friends, get priority employer matching"
- Target: 100 additional signups

**Week 5-6: Content + virality**
- Students who complete profiles get a shareable "Pathway Profile Card" (like a LinkedIn badge)
- Encourage sharing: "I just completed my Pathway Engineering profile — see my growth trajectory"
- Email students who signed up but didn't finish: "Complete your profile — employers are watching"
- Target: 200+ completed profiles with at least one interview

### Key Metrics
| Metric | Target |
|--------|--------|
| Signups | 300+ |
| Completed profiles (resume + interview) | 200+ |
| GitHub connected | 150+ |
| Average interviews per student | 1.3+ |
| Transcript uploaded | 100+ |

---

## Phase 2: Validate with Employers (Weeks 4-8, overlapping)

### Goal: 5-10 employer accounts actively browsing the talent pool

### Strategy: Warm Intros Before Cold Email

**Do NOT cold email yet.** Cold email to an unknown platform with no social proof = spam. Instead:

**Week 4-5: Warm outreach (10-15 targets)**
- Ask Berkeley CS professors who have industry contacts
- Ask club alumni now working at target companies
- Leverage any VC/advisor connections
- Target: startups (Series A-C) hiring entry-level engineers in SF Bay Area
- Pitch: "We have 200 pre-vetted Berkeley CS students with video interviews, GitHub analysis, and growth data. Want to browse them for free?"

**Week 5-6: Demo calls**
- Walk employers through 3-5 curated profiles matching their open roles
- Use the shareable profile link feature (ProfileToken) to send previews before they sign up
- Let them watch 30-second interview clips, see GitHub originality scores
- Ask for feedback: "What would make this more useful?"

**Week 7-8: Iterate based on feedback**
- Fix whatever employers ask for (sorting, filtering, export, integrations)
- Get 2-3 employers to make actual hires or start conversations with candidates
- Ask for testimonials

### Employer Target Profile
| Attribute | Ideal |
|-----------|-------|
| Stage | Seed to Series C |
| Location | SF Bay Area (for Berkeley students) |
| Hiring | Entry-level SWE, data, PM |
| Team size | 10-200 |
| Pain point | Too many applications, can't differentiate candidates |

### Companies to target first
- YC companies hiring new grads (check Work at a Startup)
- Bay Area startups posting on Handshake/LinkedIn for Berkeley
- Companies that sponsor Berkeley hackathons or career fairs
- Alumni-founded companies (Berkeley alumni network)

---

## Phase 3: Cold Email Campaign (Weeks 8-12)

### Prerequisites before cold email
- [ ] 200+ student profiles with completed interviews
- [ ] 3+ employer testimonials or case studies
- [ ] Employer landing page live (done)
- [ ] Shareable demo profile links working
- [ ] At least 1 confirmed hire through the platform

### Cold Email Strategy

**Who to email**: Engineering Managers and VPs of Engineering at companies actively hiring entry-level. NOT recruiters (they're flooded). Target the hiring manager who feels the pain.

**How to find them**:
- LinkedIn Sales Navigator: filter by title (Engineering Manager, VP Engineering), company size (50-500), hiring (has open junior roles)
- AngelList/Wellfound: startups with open roles tagged "new grad" or "entry level"
- Work at a Startup (YC): companies actively posting

**Subject line options**:
- "5 Berkeley CS students who match your [Role] opening"
- "Your [Company] SWE role — pre-vetted candidates with video interviews"
- "Hiring entry-level engineers? We have 200 pre-screened Berkeley students"

**Email template (cold)**:

```
Hi [First Name],

I saw [Company] is hiring a [Role]. We have 200+ Berkeley CS students
who've completed AI-assessed video interviews on our platform.

I pulled 3 candidates who match your requirements:
- [Name]: 8.2/10 interview score, 92% organic GitHub code, React + Python
- [Name]: 7.8/10 interview score, improving month-over-month, strong system design
- [Name]: 7.5/10 interview score, 12 original repos, leadership in [Club]

You can watch their interview clips and see growth trajectories here: [link]

Want me to share their full profiles? It's free during our beta.

[Your name]
Pathway — pathway.careers
```

**Key principle**: Lead with VALUE (specific candidates), not with a pitch about the platform.

**Follow-up cadence**:
- Day 0: Initial email with candidate previews
- Day 3: "Sharing one more candidate who matches — [Name] just scored 8.5"
- Day 7: "Quick question — is [Role] still open? Happy to send more matches"
- Day 14: Final: "Will close the loop — let me know if timing is better next quarter"

### Volume targets
| Week | Emails sent | Expected replies | Expected signups |
|------|-------------|------------------|------------------|
| 8 | 50 | 5-8 | 3-5 |
| 9 | 75 | 8-12 | 5-8 |
| 10 | 100 | 10-15 | 7-10 |
| 11-12 | 100 | 10-15 | 7-10 |

---

## Phase 4: Scale (Weeks 12+)

### Expand student supply
- Launch at UIUC (club data already seeded)
- Add Stanford, MIT, Carnegie Mellon (top CS programs)
- "Apply to 10+ companies with one Pathway profile" positioning
- Integrate with university career centers as an official tool

### Expand employer demand
- Offer "Redirect your applicants through Pathway" once trust is established
- Build ATS integrations (Greenhouse, Lever) — push candidate data into their workflow
- Create employer dashboard analytics (pipeline metrics, response rates)
- Team accounts (EmployerTeamMember model already exists, wire it up)

### Product expansion
- Custom evaluation criteria per employer
- Candidate comparison views (side-by-side)
- Scheduled live interviews through the platform
- Employer branding pages (company profiles visible to students)

---

## Metrics That Matter

### North Star: Employer-to-Candidate Conversations Started

This is the moment of value creation — an employer saw enough signal to reach out.

### Leading Indicators
| Metric | What it tells us |
|--------|-----------------|
| Student signup → profile completion rate | Is onboarding smooth? |
| Monthly interview retake rate | Are students engaged? |
| Employer time-on-platform per session | Is the talent pool useful? |
| Profiles viewed per employer session | Are they finding relevant candidates? |
| Contact rate (contacts / profiles viewed) | Is the data convincing enough? |

### Lagging Indicators
| Metric | What it tells us |
|--------|-----------------|
| Hires made through platform | Core value delivered |
| Employer retention (month-over-month) | Sustained value |
| Student NPS | Product-market fit (student side) |
| Revenue per employer | Business viability |

---

## Risks and Mitigations

### 1. "Why would students interview if employers aren't there yet?"
**Mitigation**: Position as career development, not just job matching. "Build your professional profile, practice interviewing, track your growth." The platform is useful to students even without employers.

### 2. "Why would employers use an unproven platform?"
**Mitigation**: Lead with curated candidate previews via shareable links. Don't ask them to "use a platform" — show them specific people who match their roles. Free during beta lowers the bar.

### 3. "AI scoring isn't validated"
**Mitigation**: Before any employer outreach, have 5-10 real recruiters review profiles and compare their assessments to AI scores. Build a validation dataset. Share calibration data with employers: "Our AI scoring correlates X% with recruiter assessments."

### 4. "Students will game the system"
**Mitigation**: Monthly retakes with progressive questions (already built). AI-generated questions avoid repetition. GitHub originality analysis catches fake projects. Transcript verification catches grade fraud. Vibe code analysis detects AI-dependent builders.

### 5. "Privacy / FERPA concerns"
**Mitigation**: Add explicit consent flow (opted_in_to_sharing field exists). Students must opt in before their profile is visible to employers. Transcript data requires separate consent. Add a privacy policy page.

---

## Budget (Bootstrap)

| Item | Cost/month |
|------|------------|
| Claude API (scoring, parsing, enrichment) | $200-500 |
| OpenAI Whisper (transcription) | $50-100 |
| Cloudflare R2 (video storage) | $20-50 |
| Resend (emails) | $20 |
| Domain + hosting | $20 |
| **Total** | **$310-690/mo** |

Campus events and club partnerships are free — just requires time.

---

## Timeline Summary

| Week | Focus | Milestone |
|------|-------|-----------|
| 1-2 | Club partnerships, seed users | 50 signups |
| 3-4 | Campus push, events | 200 signups |
| 4-5 | Warm employer intros | 5 employer demos |
| 5-6 | Demo calls, iterate | 3 active employers |
| 7-8 | First conversations/hires | 1 confirmed hire |
| 8-12 | Cold email campaign | 20+ employer accounts |
| 12+ | Expand to more schools | Scale |
