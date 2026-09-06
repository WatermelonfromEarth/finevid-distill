# FinQA failure analysis

## Scope and method

This analysis reviews 80 genuine test-set `CompleteRecall@5` failures: 20 each for Frozen BGE, Hard-label BGE, Distilled BGE, and the Qwen teacher. A failure means at least one annotated gold candidate is absent from the first five ranked candidates. The sampler prioritizes hard-label-versus-distilled contrast cases and then uses a deterministic seed-42 ordering. The reviewed sample is therefore diagnostic, not a prevalence estimate.

Each case was checked against the question, mapped gold candidates, top-five ranking, peer-model rankings, original `gold_inds`, program, and executable answer. Every row has exactly one primary category and a concrete explanation in `outputs/error_analysis.csv`.

The review packet contains 1,147 test questions and exactly reproduces all four full-set `CompleteRecall@5` failure counts. The cached CPU rankings differ from the locked Tesla T4 results only for Frozen BGE NDCG@10 (+0.0000371) and three hard-label aggregate metrics (largest absolute difference +0.0004359 MRR); failure membership and counts are unchanged.

Provenance:

- Review archive SHA-256: `62ccadd74399bdbdfb3ba7fbec7cf6e3fb8a6ed50cc8b6597226f1fe53dc83da`
- Review JSON SHA-256: `8d522976f18cd0ff6e6b140dc5086e0bb51faeaf4d19d5bb081660f58cfbe8e7`
- Source bundle SHA-256: `1a14aa47469cb2affb2ef11c0e9e7e0335efe2629f29edb8449a1c10ea7d454f`

## Full-test failure counts

| Model | Failures | Failure rate | CompleteRecall@5 |
| --- | ---: | ---: | ---: |
| Frozen BGE | 328 | 28.60% | 0.7140 |
| Hard-label BGE | 151 | 13.16% | 0.8684 |
| Distilled BGE | 304 | 26.50% | 0.7350 |
| Qwen teacher | 323 | 28.16% | 0.7184 |

Hard-label BGE has 153 fewer failures than Distilled BGE. Distillation removes 24 failures relative to Frozen BGE and 19 relative to the Qwen teacher, but does not approach ordinary supervised fine-tuning.

## Reviewed failure categories

| Primary category | Frozen BGE | Hard-label BGE | Distilled BGE | Qwen teacher | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Ambiguous annotation | 10 | 12 | 11 | 13 | 46 |
| Incomplete multi-fact retrieval | 5 | 2 | 0 | 5 | 12 |
| Wrong financial metric | 3 | 3 | 1 | 0 | 7 |
| Teacher error | 0 | 0 | 6 | 0 | 6 |
| Missed table evidence | 1 | 0 | 2 | 1 | 4 |
| Wrong year | 0 | 3 | 0 | 0 | 3 |
| Missed prose evidence | 1 | 0 | 0 | 0 | 1 |
| Excessive lexical matching | 0 | 0 | 0 | 1 | 1 |
| Truncation problem | 0 | 0 | 0 | 0 | 0 |
| **Total** | **20** | **20** | **20** | **20** | **80** |

The high ambiguous-annotation count is substantive. Several `gold_inds` sets contain an irrelevant prose sentence, require both table and prose candidates that state the same number, or disagree with the question and program. Examples include a pension question paired with a CDO sentence, EPS questions paired with property-sale prose, and duplicate candidate text assigned different IDs. Strict candidate-ID `CompleteRecall@5` treats these as model failures even when the necessary numeric evidence is retrieved.

## Effects of distillation

### 1. Distillation improves the frozen encoder, but only modestly

Distilled BGE raises MRR from 0.7871 to 0.8469 and NDCG@10 from 0.7893 to 0.8285 relative to Frozen BGE. Its `CompleteRecall@5` increases by 2.09 percentage points, reducing full-test failures from 328 to 304. Teacher supervision therefore transfers useful ranking information to the frozen student.

### 2. Hard labels are much more effective than teacher scores here

Hard-label BGE reaches 0.9342 MRR and 0.9162 NDCG@10, versus 0.8469 and 0.8285 for Distilled BGE. It reduces `CompleteRecall@5` failures from 304 to 151. The distilled model has just over twice as many full-test failures as the hard-label model. This is the clearest weakness introduced by the selected distillation objective.

### 3. The distilled student inherits identifiable teacher preferences

Six of the 20 sampled distilled failures were classified as teacher errors. In each case, hard-label BGE retrieved every required fact while the teacher and distilled student missed the same table value or report-level total. These include money-pool receivables, capital-expenditure totals, contractual-obligation totals, securitization assets, GCLA totals, and the 2012 gross-liability balance. This pattern is consistent with the KL term transferring a weaker teacher ordering over near-relevant candidates.

### 4. Totals and denominator rows remain a recurring weakness

Across genuine, non-ambiguous errors, models often retrieve the numerator or named line item but leave a generic `total`, beginning-balance, or comparison-year row below rank five. Distilled examples include the current portion of lease obligations and the total employee row. Several teacher-error cases repeat the same total-row omission. Report-level candidates make these generic labels difficult because their relevance depends on combining the question with another candidate.

### 5. No truncation failure was found in the reviewed sample

None of the 80 cases showed evidence that the required candidate was lost because of question or candidate truncation. The observed errors are better explained by evidence composition, table-row selection, teacher preference, or annotation quality.

## Interpretation

The experimental answer remains **no**: on the fixed FinQA report-level candidate sets, teacher-score distillation does not improve BGE-small beyond ordinary hard-label fine-tuning. Distillation beats the frozen student and slightly exceeds the teacher itself—its teacher-quality-retained ratio is 1.033—but it is substantially worse than the hard-label model on every ranking metric.

The absolute `CompleteRecall@5` values should be interpreted with care because the metric requires every annotated candidate ID, including redundant or irrelevant annotations. This caveat affects all models and does not reverse the large hard-label-versus-distilled gap. Future work should add an evidence-equivalence audit or deduplicate semantically identical gold candidates before using complete recall as a primary endpoint.
