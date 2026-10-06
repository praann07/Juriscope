# Juriscope evaluation results

Run on 2026-10-07 against the live `legal-rag` index.

## Summary

- **Correct document cited:** 10/10 (100%)
- **Expected facts in the answer:** 9/10 (90%)
- **Refused out-of-scope questions:** 2/2
- **Questions that hit a service error even after retries:** 0

Scoring is keyword-based: a fact question passes when the expected document is cited and every expected keyword appears in the answer.

## Fact questions

| Question | Expected source | Source cited | Facts present | Notes |
|---|---|---|---|---|
| Who were the parties in State of Uttar Pradesh v. Anurudh? | SCOLR_Judgement_State-of-Uttar-Pradesh-v-Anurudh.pdf | yes | yes |  |
| Which judges decided State of Uttar Pradesh v. Anurudh? | SCOLR_Judgement_State-of-Uttar-Pradesh-v-Anurudh.pdf | yes | yes |  |
| When was the State of Uttar Pradesh v. Anurudh judgment delivered? | SCOLR_Judgement_State-of-Uttar-Pradesh-v-Anurudh.pdf | yes | yes |  |
| What is the neutral citation of State of Uttar Pradesh v. Anurudh? | SCOLR_Judgement_State-of-Uttar-Pradesh-v-Anurudh.pdf | yes | yes |  |
| What was the special leave petition number in State of Uttar Pradesh v. Anurudh? | SCOLR_Judgement_State-of-Uttar-Pradesh-v-Anurudh.pdf | yes | yes |  |
| What was the outcome of the appeal in State of Uttar Pradesh v. Anurudh? | SCOLR_Judgement_State-of-Uttar-Pradesh-v-Anurudh.pdf | yes | yes |  |
| What happened to the High Court's directions in State of Uttar Pradesh v. Anurudh? | SCOLR_Judgement_State-of-Uttar-Pradesh-v-Anurudh.pdf | yes | no | missing: set aside / answer began: Based on the provided context from the Supreme Court judgment in **State of Uttar Pradesh v. Anurudh** (2026 INSC 47), the following occurred regarding the High |
| Will the effect of the judgment in State of Uttar Pradesh v. Anurudh be prospective? | SCOLR_Judgement_State-of-Uttar-Pradesh-v-Anurudh.pdf | yes | yes |  |
| Can a court conduct a mini trial at the bail stage? | SCOLR_Judgement_State-of-Uttar-Pradesh-v-Anurudh.pdf | yes | yes |  |
| What did the Supreme Court decide about bail in State of Uttar Pradesh v. Anurudh? | SCOLR_Judgement_State-of-Uttar-Pradesh-v-Anurudh.pdf | yes | yes |  |

## Out-of-scope questions

| Question | Refused | Notes |
|---|---|---|
| What is the capital of France? | yes |  |
| What is the current price of Bitcoin? | yes |  |

## Limits of this evaluation

- 10 hand-written fact questions and 2 out-of-scope questions, all about one judgment. A score on this set does not prove accuracy in general.
- Keyword matching checks that expected facts appear, not that the answer is well written or complete.
- The language model runs on an account with a low per-minute output limit, so the script waits between questions and retries on errors.
