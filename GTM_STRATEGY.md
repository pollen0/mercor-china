# Go-To-Market Strategy: Invite-Only Launch

## Approach 3: Invite-Only Beta (Recommended)

### Overview

Launch Pathway as an **exclusive beta** with curated students and hand-selected startups. Create FOMO through scarcity while manually ensuring high-quality matches and gathering feedback.

### Phase 1: Foundation (Weeks 1-2)

#### Build Core Features
- [ ] **Student Consent & Preferences System**
  - Opt-in checkbox during registration: "Allow Pathway to share my profile with vetted employers"
  - Settings page where students control:
    - Which companies can see their profile (by stage: Seed/Series A/Series B+)
    - Geographic preferences (Remote/SF/NYC/etc)
    - Industries (fintech, climate, AI, etc)
    - Email digest: "Your profile was shared with X companies this week"

- [ ] **Public Candidate Profiles**
  - `/talent/[candidateId]?token=xxx` route for shareable links
  - Beautiful one-page profile with:
    - Photo, name, university, major, graduation year
    - 5-dimension score breakdown (radar chart)
    - Best interview video highlights (30-60 sec clips)
    - GitHub stats (repos, languages, contributions)
    - Progress chart showing monthly improvement
    - Redacted contact info (employers must request intro)
  - Magic link authentication (no login required for employers to preview)
  - Expiring tokens (7-day validity)

#### Recruit Initial Cohort
- [ ] Target: 50-100 students (focus quality over quantity)
- [ ] Channels:
  - Campus clubs (CS/Engineering societies at Stanford, Berkeley, MIT)
  - LinkedIn outreach to student groups
  - Referrals from network (incentivize: "Refer a friend, both get early access")
  - Reddit (r/csMajors, r/cscareerquestions - "New interview platform, free AI feedback")
- [ ] Messaging: "Be part of exclusive beta. Interview monthly, get AI feedback, connect with top startups"
- [ ] Filter criteria:
  - Junior/Senior CS/Engineering students at target schools
  - Active GitHub profile (shows commitment)
  - 3.0+ GPA preferred

### Phase 2: Company Outreach (Weeks 3-4)

#### Identify Target Companies
- [ ] Criteria:
  - YC/TechStars companies (Seed to Series B)
  - Actively hiring (check LinkedIn "We're hiring" posts, company careers pages)
  - 10-200 employees (small enough to care, big enough to hire)
  - Engineering-heavy (need SWE/data roles for initial cohort)
- [ ] Build list of 50 companies:
  - 20 warm intros (from your 1-5 contacts)
  - 30 cold outreach (but well-researched)

#### Outreach Template

**Subject**: Private beta: Top [Stanford/MIT] CS students looking for Summer 2026 roles

**Body**:
```
Hi [Name],

I'm reaching out because [Company] is actively hiring [Software Engineers/Data Scientists], and I'd love to give you early access to Pathway's beta.

What we do differently:
- Students interview monthly → you see their growth trajectory (2-4 years), not just a snapshot
- AI-scored on 5 dimensions (Communication, Problem-Solving, Technical, Growth Mindset, Culture Fit)
- GitHub integration shows authenticity (we detect AI-assisted code)
- Pre-vetted: Only [Stanford/Berkeley/MIT] students with 3.0+ GPA

I've curated 5 students specifically for [Company]:
→ [Link to shareable batch: pathway.com/batch/abc123?token=xyz]

If any look promising, reply to this email and I'll make a warm intro.

This is invite-only right now—would you like access to the full talent pool (50+ students)?

Best,
[Your Name]
Pathway
```

#### Tracking
- [ ] Spreadsheet with columns:
  - Company Name, Contact Name, Email, Sent Date, Opened?, Clicked?, Replied?, Status
- [ ] Track metrics:
  - Open rate (target: 40%+)
  - Click rate on batch link (target: 20%+)
  - Reply rate (target: 10%+, 5 replies = success)
  - Intro requests (target: 3-5 companies)

### Phase 3: White-Glove Service (Weeks 5-8)

#### For Companies Who Respond
- [ ] Send personal invite code: "EARLY_ACCESS_[COMPANY]"
- [ ] Create their account + first job posting for them (reduce friction)
- [ ] Schedule 15-min onboarding call:
  - Show them how to use talent pool
  - Understand what they're looking for
  - Get feedback on scoring system
- [ ] Manually curate top 3-5 candidates for their specific role
- [ ] Make warm intros via email (CC both sides)
- [ ] Follow up weekly: "Any candidates you'd like to interview?"

#### For Students
- [ ] When a company views their profile, send notification:
  - "Good news! [Company Name] viewed your profile"
  - "They're hiring for [Role]. Want to learn more?"
- [ ] When intro is made:
  - "You've been matched with [Company]! Here's what to expect..."
  - Prep guide: company research, common interview questions
- [ ] After company interview:
  - Survey: "How was the experience? Would you recommend Pathway?"

### Phase 4: Scale (Weeks 9-12)

#### Expand Student Pipeline
- [ ] Target: 200-300 students
- [ ] Add more schools: CMU, UIUC, Georgia Tech, UT Austin
- [ ] Expand verticals: Data, Product (in addition to Engineering)
- [ ] Referral program: "Refer 3 friends, get premium features free"

#### Transition to Self-Service
- [ ] Companies who responded in Phase 3 → now browse talent pool independently
- [ ] Add payment tier:
  - Free: View 10 candidate profiles/month
  - Pro ($199/month): Unlimited views + AI matching + intro requests
- [ ] Reduce manual work:
  - Auto-send weekly digest: "Top 10 new candidates in Engineering"
  - Self-service intro requests (students must approve)

#### Measure Success
- [ ] KPIs:
  - 10+ companies actively using platform monthly
  - 100+ students interviewed at least once
  - 5+ successful intros leading to company interviews
  - 1-2 job offers (dream outcome)
- [ ] Gather testimonials from both sides
- [ ] Create case studies: "[Student] landed [Company] via Pathway"

---

## Why This Approach Works

✅ **Solves cold start** - Students come first (intrinsic value from AI feedback), companies come after seeing quality
✅ **Creates FOMO** - Invite-only = exclusivity, both sides feel special
✅ **Validates demand** - You'll know in 4 weeks if companies actually want this
✅ **Builds relationships** - Manual intros create trust, gather feedback, iterate product
✅ **Uses product as designed** - Companies eventually self-serve, you're not building a services business

---

## Key Assumptions to Validate

1. **Students will interview without guaranteed job outcomes** → Validated if 50+ students complete interviews
2. **Companies value growth trajectory over single snapshot** → Validated if companies request multiple students over time
3. **AI scoring is credible** → Validated if companies interview students based on scores
4. **GitHub integration matters** → Validated if companies mention GitHub in feedback
5. **Monthly cadence creates stickiness** → Validated if students return for 2nd+ interviews

---

## Next Steps

### Immediate (This Week)
1. ✅ Build student consent & preferences system
2. ✅ Build public candidate profile pages with magic links
3. ✅ Add admin endpoint for bulk link generation
4. Design outreach email templates + batch presentation page

### How to Generate Batch Links (Admin)

Use the admin API endpoint to generate shareable links for your curated candidates:

```bash
# Generate links for 5 candidates
curl -X POST http://localhost:8000/api/admin/generate-batch-links \
  -H "Content-Type: application/json" \
  -H "Authorization: your-admin-password" \
  -d '{
    "candidate_ids": ["c123", "c456", "c789"],
    "expires_in_days": 7
  }'

# Returns:
{
  "success": true,
  "count": 3,
  "expires_in_days": 7,
  "links": [
    {
      "candidate_id": "c123",
      "candidate_name": "Alice Smith",
      "token": "xyz123...",
      "share_url": "/talent/c123?token=xyz123...",
      "expires_at": "2026-02-08T..."
    },
    ...
  ]
}
```

Then copy the share URLs and include them in your outreach emails to companies.

### Week 2
4. Recruit first 20 students (test the interview flow)
5. Manually curate top 5 students for outreach
6. Reach out to 5 warm company contacts

### Week 3-4
7. Send outreach emails to 50 companies
8. Track opens, clicks, replies
9. Schedule onboarding calls with responders

### Week 5+
10. Make warm intros between students and companies
11. Gather feedback from both sides
12. Iterate based on learnings
13. Scale what works, kill what doesn't

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Students don't opt-in to sharing | Make value clear: "Companies who see your profile may reach out with opportunities" |
| Companies ignore emails | A/B test subject lines, send from warm contacts, offer exclusive beta access |
| Students ghost after company intro | Set expectations upfront, send prep materials, follow up |
| Low quality matches | Manually review before sending, gather feedback, refine AI matching |
| Legal/privacy concerns | Clear consent flow, let students control who sees what, compliance review |

---

## Success Metrics (12-Week Goals)

| Metric | Target |
|--------|--------|
| Students registered | 100+ |
| Students completed 1+ interview | 75+ |
| Companies signed up | 15+ |
| Companies actively using platform | 10+ |
| Warm intros made | 20+ |
| Company interviews scheduled | 10+ |
| Job offers extended | 2+ |
| NPS from students | 40+ |
| NPS from companies | 30+ |

---

**Status**: Not started
**Owner**: TBD
**Last Updated**: 2026-02-01
