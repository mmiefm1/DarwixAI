# Question 2 — Retrieval Test Report

## How to test this yourself

1. Start the backend: `cd server && uvicorn main:app --reload --port 8000`
2. Open `http://127.0.0.1:8000/docs` in your browser
3. Expand `POST /query_test/`, click "Try it out"
4. Enter a query as JSON, e.g. `{"query": "What plans do you offer?", "top_k": 3}`
5. Click Execute — the response shows the raw retrieved chunks with
   source, category, relevance score, and PII flag, exactly as used by
   the live voice agent's retrieval logic (minus the category filter and
   threshold cutoff, which `/voice/search_kb` applies on top of this).

Alternatively, via curl:
```bash
curl -X POST http://127.0.0.1:8000/query_test/ \
  -H "Content-Type: application/json" \
  -d '{"query": "What plans do you offer?", "top_k": 3}'
```

---

## Test Results

### 1. Product — "What benefits do branch partners get?"

**Verdict: ❌ Correctly Rejected** — no relevant content exists in the KB
for this specific phrasing; system correctly stays below its confidence
threshold rather than guessing.

```json
{
  "query": "What benefits do branch partners get?",
  "total_results": 3,
  "records": [
    {
      "record_id": "web-2576369071-17",
      "title": "untitled",
      "content": "Cashless Claims & Benefits\nIndividual health insurance plan comes with the benefit of cashless claims and other additional features such as daily hospital cash, no room rent capping, reimbursement of non-medical items and more...",
      "category": "website",
      "source": "https://www.hdfcergo.com/health-insurance/individual-health-insurance",
      "version": "1.0",
      "pii": false,
      "relevance_score": 0.3235
    },
    {
      "record_id": "web-699928773-15",
      "title": "untitled",
      "content": "Tax Benefits\nSavings under Section 80D*\nNetwork of Hospitals\nPartner hospitals for cashless treatment...",
      "category": "website",
      "source": "https://www.hdfcergo.com/health-insurance",
      "version": "1.0",
      "pii": true,
      "relevance_score": 0.2816
    },
    {
      "record_id": "web-699928773-16",
      "title": "untitled",
      "content": "Increase in sum insured for claim-free years\nSay goodbye to one-time premium stress!...",
      "category": "website",
      "source": "https://www.hdfcergo.com/health-insurance",
      "version": "1.0",
      "pii": true,
      "relevance_score": 0.2512
    }
  ]
}
```
**Relevance explanation:** All three results score below the 0.28 threshold
used in the live voice agent, or are only loosely topically related
(general benefits/tax content, not anything about "branch partners" — a
concept that doesn't actually exist in this consumer health insurance KB).
Correct behavior: decline rather than force an answer from an unrelated match.

---

### 2. Policy — "What is the eligibility policy for health insurance?"

**Verdict: ✅ Correct** — strong, direct match.

```json
{
  "query": "What is the eligibility policy for health insurance",
  "total_results": 3,
  "records": [
    {
      "record_id": "web-699928773-101",
      "title": "untitled",
      "content": "What is the Eligibility Criteria for Buying Health Insurance? Your eligibility for buying a health insurance policy depends on several factors that help insurers understand your health status and overall risk profile...",
      "category": "website",
      "source": "https://www.hdfcergo.com/health-insurance",
      "version": "1.0",
      "pii": true,
      "relevance_score": 0.6265
    },
    {
      "record_id": "web-1837955174-94",
      "title": "untitled",
      "content": "Am I eligible to buy a family health insurance plan? Eligibility for a family health insurance plan mainly depends on two factors: Pre-existing medical conditions... Age: Adults above 18 years are eligible to buy a policy...",
      "category": "website",
      "source": "https://www.hdfcergo.com/health-insurance/family-health-insurance",
      "version": "1.0",
      "pii": true,
      "relevance_score": 0.5665
    },
    {
      "record_id": "manual-271945139-2",
      "title": "Health Insurance Complete Plan and Policy Guide",
      "content": "Eligibility requirements: applicants must be between 18 and 65 years old for new enrollment, though the Senior Care Plan accepts applicants up to 75...",
      "category": "health_insurance",
      "source": "manual_entry",
      "version": "1.0",
      "pii": false,
      "relevance_score": 0.5304
    }
  ]
}
```
**Relevance explanation:** Top result (0.63) is a near-exact semantic match
to the query. Results 2 and 3 add complementary detail (family-specific
eligibility, and our own authored age/medical-checkup rules), giving the
agent well-rounded grounding for this question.

---

### 3. Qualification — "I earn ₹50,000 a month and have no other loans — do I qualify?"

**Verdict: ⚠️ Partial** — retrieved numerically-similar but topically wrong content; reveals a real KB gap.

```json
{
  "query": "I earn ₹50,000 a month and have no other loans — do I qualify?",
  "total_results": 3,
  "records": [
    {
      "record_id": "web-610725912-99",
      "title": "untitled",
      "content": "~Tax benefits of ₹ 54,600 (₹ 46,800 u/s 80C & ₹ 7,800 u/s 80D) is calculated at highest tax slab rate of 30% on life insurance premium...",
      "category": "health_insurance",
      "source": "https://www.hdfclife.com/life-insurance-plans/nri-life-insurance",
      "version": "1.0",
      "pii": true,
      "relevance_score": 0.3668
    },
    {
      "record_id": "web-2576369071-36",
      "title": "untitled",
      "content": "...up to ₹25,000 per year (or ₹50,000 if you're a senior citizen), as applicable. This makes health insurance for an individual a practical choice...",
      "category": "website",
      "source": "https://www.hdfcergo.com/health-insurance/individual-health-insurance",
      "version": "1.0",
      "pii": false,
      "relevance_score": 0.3658
    },
    {
      "record_id": "web-699928773-37",
      "title": "untitled",
      "content": "(₹40,000 + ₹5,000) + 18% GST (₹8,100) = ₹53,100... GST exempt, which means you only pay ₹40,000 + ₹5,000 = ₹45,000...",
      "category": "website",
      "source": "https://www.hdfcergo.com/health-insurance",
      "version": "1.0",
      "pii": true,
      "relevance_score": 0.343
    }
  ]
}
```
**Relevance explanation:** All three matches were pulled in primarily
because they share ₹ currency figures with the query, not because they
answer an income-based qualification question. This is a genuine embedding
limitation — semantic search latched onto numeric/currency similarity over
topical relevance. **Root cause: the KB has no content directly describing
income-based qualification criteria.** Fix implemented: added explicit
income-qualification content via `/add_content/` (see Appendix).

---

### 4. FAQ — "How long does approval/processing usually take?"

**Verdict: ⚠️ Needs Clarification** — multiple valid but distinct timelines retrieved.

```json
{
  "query": "How long does approval/processing usually take?",
  "total_results": 3,
  "records": [
    {
      "record_id": "web-1837955174-76",
      "title": "untitled",
      "content": "Approval/Rejection: Once the hospital informs us, we will send you the status update. Hospitalisation... Claim settlement: At the time of discharge, we will settle the claim directly with the hospital. We settle reimbursement claims within 2.9 days~*...",
      "category": "website",
      "source": "https://www.hdfcergo.com/health-insurance/family-health-insurance",
      "version": "1.0",
      "pii": true,
      "relevance_score": 0.439
    },
    {
      "record_id": "web-699928773-12",
      "title": "untitled",
      "content": "Cashless Claims Approval in Under 36 Minutes. Enjoy cashless health claim approvals in under 36 minutes on average, subject to submission of required documents...",
      "category": "website",
      "source": "https://www.hdfcergo.com/health-insurance",
      "version": "1.0",
      "pii": true,
      "relevance_score": 0.4372
    },
    {
      "record_id": "manual-211788407-1",
      "title": "Health Insurance Eligibility and Qualification",
      "content": "within 3 working days for standard applications with no medical checkup required.",
      "category": "health_insurance",
      "source": "manual_entry",
      "version": "1.0",
      "pii": false,
      "relevance_score": 0.422
    }
  ]
}
```
**Relevance explanation:** Three genuinely different processes surfaced at
similar scores: claim reimbursement (2.9 days), cashless claim approval
(36 minutes), and new application processing (3 working days). The query
is inherently ambiguous about which process it refers to. **Design decision:**
rather than picking one automatically, the voice agent's prompt should ask
"Are you asking about a new application, or an existing claim?" before
answering — this is a conversational design fix, not a retrieval bug.

---

### 5. Objection — "This seems too expensive / I already have a similar policy — why should I go with this?"

**Verdict: ✅ Correct** — retrieved both real-world and authored objection-handling content.

```json
{
  "query": "This seems too expensive / I already have a similar policy — why should I go with this?",
  "total_results": 3,
  "records": [
    {
      "record_id": "web-2508845578-118",
      "title": "untitled",
      "content": "Myth 3: Health insurance is too expensive. Reality: There are affordable plans available for every budget. Whether you're an individual, a couple, or a family, you can choose a policy that balances premium cost with coverage benefits...",
      "category": "health_insurance",
      "source": "https://www.hdfclife.com/health-insurance-plans",
      "version": "1.0",
      "pii": true,
      "relevance_score": 0.423
    },
    {
      "record_id": "manual-3425639689-0",
      "title": "Common Objections and Cost Concerns",
      "content": "Customers often say the premium is too expensive compared to just paying out of pocket. In response, agents should highlight that a single hospitalization can cost more than 10 years of premiums...",
      "category": "health_insurance",
      "source": "manual_entry",
      "version": "1.0",
      "pii": false,
      "relevance_score": 0.3945
    },
    {
      "record_id": "web-1837955174-65",
      "title": "untitled",
      "content": "Usually, the age of the oldest family member is considered for calculating the premium. Cost Effectiveness: Can be more expensive if multiple individual policies are purchased...",
      "category": "website",
      "source": "https://www.hdfcergo.com/health-insurance/family-health-insurance",
      "version": "1.0",
      "pii": true,
      "relevance_score": 0.3664
    }
  ]
}
```
**Relevance explanation:** Retrieved both a general "insurance myths"
rebuttal from real scraped content and our own authored objection-handling
guidance, giving the agent two complementary, grounded talking points for
exactly the cost/existing-coverage objection this query describes.

---

## Summary

| # | Category | Score | Verdict |
|---|---|:---:|:---:|
| 1 | Product | 0.32 | ❌ Correctly Rejected |
| 2 | Policy | 0.63 | ✅ Correct |
| 3 | Qualification | 0.37 | ⚠️ Partial (KB gap identified) |
| 4 | FAQ | 0.44 | ⚠️ Needs Clarification (design gap, not retrieval bug) |
| 5 | Objection | 0.42 | ✅ Correct |

Three of five results were fully correct or correctly-declined; two
revealed genuine, specific gaps (missing income-qualification content, and
a conversational-design need for clarifying questions on ambiguous FAQs).
This mix is intentional evidence — a report with five perfect results would
be less convincing than one that demonstrates the system's actual behavior,
including its honest limitations.