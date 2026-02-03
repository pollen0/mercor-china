# Matching Logic & Preferences

## Core Principle: Show to All, Prioritize by Preferences

**Students are shown to ALL employers.** Preferences simply help them rank higher for relevant companies.

---

## Student Preferences (Optional)

Students can optionally set preferences to be prioritized:

### Limits
- **Company Stages**: Max 2 selections (e.g., Seed + Series A)
- **Locations**: Max 4 selections (e.g., Remote, SF, NYC, Seattle)
- **Industries**: Max 3 selections (e.g., Fintech, AI, Climate)

### Why Limits?
Forces students to think: "What do I *really* want?" instead of clicking everything.

### UI Messaging
- "Your profile is shown to **ALL employers**"
- "Set preferences to be **prioritized** for companies you're most interested in"
- "Leave blank to be equally visible to everyone"

---

## How Matching Works

### Base Score (Interview + Skills + Experience)
Every candidate gets a base match score (0-100) based on:
- Interview scores in relevant vertical
- Skills match with job requirements
- Experience level
- GitHub profile quality

### Preference Boost
If candidate's preferences align with the job, add bonus points:
- ✓ Company stage matches: **+10 points**
- ✓ Location matches: **+10 points**
- ✓ Industry matches: **+10 points**
- **Max boost: +30 points**

### Example Scores

**Candidate A** (no preferences set):
- Base score: 75
- Preference boost: 0
- **Final: 75**

**Candidate B** (prefers Seed/Series A, SF, Fintech):
For a Seed-stage Fintech startup in SF:
- Base score: 75
- Preference boost: +10 (stage) +10 (location) +10 (industry) = +30
- **Final: 100** (capped at 100)

For a Series B Enterprise SaaS startup in Austin:
- Base score: 75
- Preference boost: 0 (no matches)
- **Final: 75**

**Result:** Candidate B ranks higher for the Fintech job but is still visible for the Enterprise SaaS job.

---

## Backend Implementation

### Current State
The preference boost logic is **implemented** in `app/services/matching.py`. The `calculate_preference_boost()` method calculates boost points based on candidate preferences matching job attributes (company_stage, location, industry).

### Implementation Details
In `app/services/matching.py`:

```python
def calculate_match_score(candidate, job):
    # Base score from interview + skills
    base_score = calculate_base_match(candidate, job)  # 0-100

    # Preference boost
    boost = 0
    if candidate.sharing_preferences:
        prefs = candidate.sharing_preferences

        # Company stage match
        if job.company_stage in prefs.get('company_stages', []):
            boost += 10

        # Location match
        if job.location in prefs.get('locations', []):
            boost += 10

        # Industry match
        if job.industry in prefs.get('industries', []):
            boost += 10

    # Apply boost (cap at 100)
    final_score = min(base_score + boost, 100)

    return final_score
```

### Sorting Talent Pool
When employers browse talent pool:
1. Filter by vertical/role (required)
2. Calculate match score for each candidate
3. Sort by score (highest first)
4. Show all candidates (no filtering by preferences)

---

## Key Benefits

### For Students
- ✅ Maximum visibility (shown to everyone)
- ✅ Control over prioritization (not gatekeeping)
- ✅ No risk of missing opportunities

### For Employers
- ✅ See all candidates (not limited by student preferences)
- ✅ Top matches ranked first (saves time)
- ✅ Can still discover "hidden gems" lower in the list

### For Pathway
- ✅ Avoids empty talent pools (no hard filtering)
- ✅ Better data on what preferences actually matter
- ✅ Can A/B test different boost amounts

---

## Future Enhancements

### Phase 2 (After GTM Validation)
- Add salary range preferences (boost if within range)
- Add company size preferences (10-50, 50-200, 200+)
- Add "must-have" vs "nice-to-have" preference types
- Track: Do employers actually hire preference-boosted candidates more?

### Phase 3 (ML-Powered)
- Learn from successful hires to auto-adjust boost amounts
- Predict student-company fit beyond stated preferences
- Personalized preference recommendations: "Students like you prefer..."

---

## Testing Preferences

### Manual Test Flow
1. **Student A**: Opts in, sets no preferences
2. **Student B**: Opts in, sets Seed + SF + Fintech
3. **Employer**: Creates Seed-stage Fintech job in SF
4. **Expected**: Student B ranks higher, but both are visible

### Validation Metrics
After launch, track:
- Do students with preferences get contacted more?
- Do preference-boosted matches convert to hires at higher rates?
- Are students setting diverse preferences or all choosing the same?

---

**Status**: ✅ Fully implemented. Preferences UI with limits + matching algorithm boost logic.
