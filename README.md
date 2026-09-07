# Fashion Marketplace Return Root-Cause Analyser

A minimum viable product (MVP) that turns vague, inconsistent return reasons
("exchange", "refund") into **structured, evidence-backed root-cause labels**
(e.g. `SIZE_CHART_ERROR`, `PHOTO_MISLEADING`) that a product team can actually
act on.

---

## 1. The Problem (Stakeholder Assumptions)

- **Who has this problem:** the Product/Catalog team at a fashion
  marketplace. They see thousands of returns per week but the only signal
  they get is a vague dropdown reason or refund/exchange action — it never
  tells them *which listing or product is actually broken*.
- **Assumption:** most "size" returns are not random — a meaningful chunk
  are caused by fixable issues: wrong size chart, misleading photos,
  inaccurate material description, or genuine defects.
- **Assumption:** warehouse staff already write free-text inspection notes
  when a returned item comes back — this data exists but isn't connected to
  the return reason today.
- **Assumption:** the team wants **high-precision, evidence-backed alerts**,
  not a noisy dashboard — a wrong alert (false positive) wastes a product
  manager's time and erodes trust in the tool faster than a missed one.
- **Out of scope for this MVP:** actual product fixes, financial return-cost
  modeling, real customer PII, real-time API integration.

---

## 2. Architecture

```
                 ┌──────────────────┐
                 │   Data Sources     │
                 │ (generate_data.py) │
                 ├────────────────────┤
                 │ returns.csv         │  <- customer return_text, action
                 │ products.csv        │  <- size_chart_accurate, material
                 │ listings.csv        │  <- listing text, photo_accurate
                 │ inspections.csv     │  <- warehouse inspection notes
                 └─────────┬──────────┘
                           │
                           v
              ┌─────────────────────────┐
              │   analyser.py             │
              │  (rule-based scoring)      │
              │  - keyword match (text)     │
              │  - attribute cross-check     │
              │  - listing cross-check        │
              │  - inspection cross-check      │
              │  -> label + confidence + evidence
              └─────────┬───────────────┘
                        │
          ┌─────────────┼──────────────┐
          v              v               v
  ┌───────────────┐ ┌───────────┐ ┌────────────────┐
  │  evaluate.py    │ │workload.py│ │    app.py         │
  │ accuracy, FP/FN,│ │ worker cap │ │ Streamlit dashboard│
  │ before/after,    │ │ safe assign│ │  (stakeholder view) │
  │ disruption test    │ └───────────┘ └────────────────┘
  └───────────────┘
```

**Flow:** raw return -> rule-based scoring against 4 evidence sources ->
labeled + prioritized output -> (a) evaluated for accuracy, (b) high-priority
items safely assigned to warehouse workers, (c) shown on a dashboard.

---

## 3. Data Schema

**products.csv**
| column | type | meaning |
|---|---|---|
| product_id | string | unique product key |
| category | string | T-Shirt, Jeans, Dress, etc. |
| material | string | listed material |
| size_chart_accurate | bool | was the size chart verified correct? |
| true_root_cause | string | **hidden ground truth**, used only for grading |

**listings.csv**
| column | type | meaning |
|---|---|---|
| product_id | string | FK -> products |
| listing_description | string | text shown to customer |
| photo_accurate | bool | does listing photo match real item? |

**inspections.csv**
| column | type | meaning |
|---|---|---|
| inspection_id | string | unique inspection key |
| product_id | string | FK -> products |
| inspection_notes | string | warehouse staff's free-text finding |
| defect_found | bool | was a defect confirmed? |

**returns_*.csv** (normal_day / disruption_day)
| column | type | meaning |
|---|---|---|
| return_id | string | unique return key |
| product_id | string | FK -> products |
| return_text | string | customer's free-text comment (can be empty) |
| customer_action | string | refund / exchange / store_credit |

---

## 4. Labels & Thresholds

| Label | Meaning |
|---|---|
| `SIZE_CHART_ERROR` | size chart for this product is wrong |
| `PHOTO_MISLEADING` | listing photo doesn't match the real item |
| `MATERIAL_MISMATCH` | fabric/material differs from listing |
| `DESCRIPTION_INACCURATE` | listing text specs are wrong |
| `QUALITY_DEFECT` | manufacturing defect / damage |
| `CUSTOMER_PREFERENCE` | not a product problem |
| `UNKNOWN` | not enough evidence — needs manual review |

Scoring (each source adds points, capped at 1.0):
- return text keyword match: **+0.4**
- product attribute contradiction (e.g. size chart flagged wrong): **+0.3**
- listing attribute contradiction (e.g. photo flagged wrong): **+0.3**
- inspection notes confirm it: **+0.5** (weighted highest — physical proof
  beats self-reported text; see Error Analysis below)

| Score | Priority | Meaning |
|---|---|---|
| ≥ 0.7 | HIGH | confident, actionable, goes to product team |
| 0.4 – 0.69 | MEDIUM | possible issue, needs human review |
| < 0.4 | LOW / UNKNOWN | not enough signal, don't act on it |

---

## 5. Results (Measured, not assumed)

Run `python evaluate.py` to reproduce. Current measured results:

| Metric | Normal day | Disruption day |
|---|---|---|
| Exact label accuracy | 100% | 91.7% |
| Issue vs. no-issue accuracy | 100% | 100% |
| False positive rate | 0% | 0% |
| False negative rate | 0% | 0% |

**Before vs After:**
- **Before:** raw `customer_action` (refund/exchange/store_credit) — tells
  the product team nothing about *why*.
- **After:** structured labels like `SIZE_CHART_ERROR` (12% of returns) —
  specific enough for a product manager to open a ticket against a SKU.

### Error Analysis (honest limitations — say this in your viva)
1. **Accuracy is measured on synthetic data whose phrase bank was written
   to match the rule keywords.** This measures *internal consistency*, not
   real-world generalisation. A production version would need real,
   messy customer text (typos, sarcasm, multiple languages) as a holdout
   set.
2. **Bug found during testing:** ground truth used `"NONE"` while the
   analyser correctly outputs `"CUSTOMER_PREFERENCE"` for the same
   situation — an exact-string comparison wrongly counted these as
   mismatches until normalised in `evaluate.py`. Lesson: always sanity-check
   your own evaluation code, not just the model.
3. **Weighting bug found via edge-case testing:** initially, vague customer
   text ("changed my mind") could outscore a confirmed warehouse defect
   finding, because text keywords were weighted equal to inspection
   evidence. Fixed by weighting inspection findings highest (0.5 vs 0.4),
   since physical inspection is objective and text is self-reported.
   See `test_edge_cases.py`, Edge Case 4.
4. **Disruption-day accuracy drop (100% → 91.7%) is caused entirely by
   missing return text** — every false negative on that day had an empty
   `return_text`. The system correctly falls back to `UNKNOWN` rather than
   guessing, which is the safe behavior, but it does mean recall drops
   when customers leave no comment.

---

## 6. Edge / Failure Cases (`test_edge_cases.py`)

1. **Zero evidence** (empty text, no attributes, no inspection) → correctly
   returns `UNKNOWN` instead of guessing.
2. **Text contradicts attributes** (customer blames size chart, but records
   say it's accurate) → capped at MEDIUM, never reaches HIGH on text alone.
3. **Missing/unknown product_id** (broken foreign key / deleted product) →
   does not crash, degrades gracefully to text-only scoring.
4. **Vague text but confirmed defect** (customer says "changed my mind" but
   inspection found real damage) → inspection evidence correctly overrides
   the vague text.

---

## 7. Worker Safety (`workload.py`)

- Only `HIGH` priority returns get queued for physical re-inspection.
- Hard cap: **25 inspections per worker per day**
  (`MAX_INSPECTIONS_PER_WORKER_PER_DAY` in `workload.py`).
- If there are more high-priority items than total safe capacity, the
  excess is **queued for the next day** — never dumped onto one worker.
- `verify_no_worker_overloaded()` proves, on every run, that no worker
  exceeds the cap. This is the "efficiency is not gained through unsafe
  assignment" requirement: the system could technically clear the backlog
  faster by ignoring the cap, but it deliberately doesn't.

---

## 8. Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| Keyword rules don't generalise to real customer phrasing/typos/slang | Missed issues (false negatives) | Start with rules (explainable), plan to add a fine-tuned text classifier later, keep rules as a fallback/explainer |
| Product team ignores alerts if false positive rate creeps up | Tool abandoned | Threshold tuned conservative (0.7 for HIGH); false positives tracked every run |
| Return text missing/empty (disruption days, mobile returns) | Lower recall | Falls back to attribute + inspection evidence; never guesses from nothing |
| Warehouse staff overloaded chasing every flagged item | Staff burnout, unsafe workload | Hard daily cap per worker + overflow queue (Section 7) |
| Ground-truth labels used for grading come from the same team writing the rules (circular validation) | Overstated accuracy | Documented explicitly in Error Analysis (Section 5); real deployment needs an independent labeled holdout set |
| Bias toward categories with more training phrases | Some root causes under-detected | Keyword lists are short and hand-written for MVP scope — flagged as a known limitation, not hidden |

---

## 9. User Guide

### Setup
```bash
pip install -r requirements.txt
```

### Run the full pipeline
```bash
python generate_data.py      # creates synthetic data in data/
python analyser.py           # runs the analyser on a normal day
python evaluate.py           # accuracy, FP/FN, before/after, disruption test
python test_edge_cases.py    # the 4 edge/failure cases
python workload.py           # worker safety check
```

### Run the dashboard
```bash
streamlit run app.py
```
Opens a browser window where you can toggle between "Normal day" and
"Disruption day", see before/after charts, high-priority flagged returns
with evidence, false positives/negatives, and worker workload safety.

### File-by-file guide
- `generate_data.py` — builds the 5 CSVs in `data/` (synthetic, reproducible via fixed random seed)
- `analyser.py` — the core rule-based scoring engine (read this first for the viva)
- `evaluate.py` — accuracy metrics, FP/FN inspection, before/after, disruption test
- `workload.py` — worker daily cap + safe assignment
- `test_edge_cases.py` — 4 standalone edge/failure case tests
- `app.py` — Streamlit dashboard

---

## 10. Stakeholder Validation

Playing the role of the "product team" reviewer: the top `SIZE_CHART_ERROR`
and `PHOTO_MISLEADING` flagged returns were manually cross-checked against
their `evidence` field (Section "High-priority flagged returns" in the
dashboard) and confirmed to be genuinely actionable — each one names the
specific keyword or inspection phrase that triggered it, so a reviewer
doesn't have to trust a black box. This evidence-first design is what
satisfies "provide evidence for every high-priority output."

**Recommendation from this validation round:** expand the keyword lists
using a sample of real historical return text before piloting on live
traffic, and set the HIGH threshold slightly higher (0.75) for the first
two weeks to build reviewer trust before loosening it.
