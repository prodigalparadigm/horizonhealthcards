# Fact-check report — Type 2 diabetes mellitus

**Verdict: BLOCK** · 2026-10-12 · 26 claims · 15 searches/fetches · all 7 cited FDA label PDFs downloaded and read directly

Blocking defects must be corrected and the card re-reviewed. A BLOCK verdict disables
the reviewer's clear button in the dashboard; this card cannot reach staff as written.

## Blocking defects

### 1. Metformin row → label link

That URL is the label for SEGLUROMET (ertugliflozin + metformin), NDA 209806, a fixed-dose SGLT2i/metformin combination — not metformin monotherapy. A clinician clicking this row lands on a two-drug product whose separate SGLT2i risks (DKA, Fournier's gangrene, genital mycotic infection) the row does not disclose. The row also says 2022; the document is revised 09/2021.

Source checked: <https://www.accessdata.fda.gov/drugsatfda_docs/label/2022/209806s008lbl.pdf>

### 2. Metformin boxed warning — "renal/hepatic impairment, sepsis, dehydration, excess alcohol, acute CHF"

The label enumerates: renal impairment, concomitant use of certain drugs, AGE >=65, RADIOLOGICAL STUDIES WITH CONTRAST, SURGERY AND OTHER PROCEDURES, hypoxic states, excessive alcohol intake, hepatic impairment. The card omits four label risk factors and substitutes three that are not label headings. It also drops "Prompt hemodialysis is recommended." The two most actionable omissions are age >=65 and iodinated contrast — the contrast hold is a routine decision this card would fail to prompt.

Source checked: <https://www.accessdata.fda.gov/drugsatfda_docs/label/2022/209806s008lbl.pdf>

### 3. Not on this card: "Reported Ozempic CKD indication (FLOW) — unverified, no retrievable primary source"

The card's OWN cited Ozempic label (rev. 10/2025) carries this in INDICATIONS AND USAGE: "to reduce the risk of sustained eGFR decline, end-stage kidney disease and cardiovascular death in adults with type 2 diabetes mellitus and chronic kidney disease." The indication is FDA-approved and documented in the primary source already on the card. As written, the card tells a provider an approved renal indication is dubious.

Source checked: <https://www.accessdata.fda.gov/drugsatfda_docs/label/2025/209637s035,209637s037lbl.pdf>

## Fixes required

- **Sulfonylurea row — "boxed-format not confirmed"** — RESOLVED: the UGDP cardiovascular-mortality warning is NOT a boxed warning; it sits under the ordinary WARNINGS section. Confirmed on two independent current labels. State it affirmatively and set boxed:false.
  Source: <https://www.accessdata.fda.gov/drugsatfda_docs/label/2008/017783s019lbl.pdf>
- **Canagliflozin warnings — "amputation, DKA, genital mycotic infection"** — Incomplete in a clinically consequential way. Add necrotizing fasciitis of the perineum (Fournier's gangrene, §5.6, "serious, life-threatening cases") at minimum; label W&P also include volume depletion/AKI, urosepsis and pyelonephritis, hypoglycemia, hypersensitivity, bone fracture.
  Source: <https://www.accessdata.fda.gov/drugsatfda_docs/label/2023/204042s040lbl.pdf>
- **Tirzepatide row — "1L (ASCVD, HFpEF+obesity)"** — HFpEF-with-obesity is an indication for Zepbound, not Mounjaro. Either relabel the row as tirzepatide across brands or drop the HFpEF clause.
- **Tirzepatide label currency** — Row cites the 05/2025 Mounjaro label, which predates the Aug 2026 MACE indication the card's own lead news item reports. Row and news contradict each other.
- **Pioglitazone — "contraindicated NYHA Class III/IV HF"** — Should read: INITIATION is contraindicated in established NYHA Class III/IV HF. The label separately states ACTOS is not recommended in symptomatic heart failure.
  Source: <https://www.accessdata.fda.gov/drugsatfda_docs/label/2017/021073s049lbl.pdf>
- **JSON/markdown disagreement** — The markdown's guideline note (do not combine DPP-4i with GLP-1 RA; on insulin, add a GLP-1 RA rather than intensifying insulin) has no counterpart anywhere in the JSON. The two forms must agree.
- **JSON — boxed-warning absence not encoded** — canagliflozin and sulfonylureas carry no `boxed` key at all while the other five carry boxed:true. Absent key is ambiguous between unknown and false. Set boxed:false explicitly on both — both are now confirmed absences.
- **Awiqli naming and stale gap entry** — Generic name is insulin icodec-abae, not insulin icodec. The "boxed-warning status not checked" gap entry is now resolvable: the Awiqli SPL has no boxed warning.
  Source: <https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=5162b93e-5775-4581-a5e9-e8783ae0acd7>
- **Glipizide source vintage** — Cited Glucotrol label is a 2008 non-PLR document. Accurate but old; substitute a current DailyMed SPL so the reviewer is not judging currency off a 2008 PDF.
- **Dulaglutide label currency** — Cited label is revised 09/2020. Boxed warning content is unchanged and correct, but update to the current Trulicity label.

## Verified

- Canagliflozin has NO boxed warning — read the full Highlights of the cited Invokana label (rev. 07/2023); amputation is W&P §5.2. The builder's most-feared failure mode is absent here
- Thyroid C-cell tumor boxed warning present and accurately stated on dulaglutide, semaglutide and tirzepatide labels, with MTC/MEN 2 contraindications
- Pioglitazone CONGESTIVE HEART FAILURE boxed warning present and class-wide
- Sulfonylureas carry no boxed warning — resolved affirmatively against two labels
- ADA Standards of Care 2026 is the current edition (released 2025-12-08), not superseded as of today; Section 9 reference correct
- Mounjaro MACE approval 2026-08-28 — every figure on the card matches SURPASS-CVOT including HR 0.92 (95.3% CI 0.83-1.01)
- Rybelsus CV indication 2025-10-17 and Awiqli approval 2026-03-26 both confirmed; card's dates and figures match
- J Diabetes Res citation resolves via Crossref exactly as printed
- No cited URL on the card is dead or fabricated — all 7 label PDFs resolve and were read
- Footer clinical-reference line present; no patient-directed or imperative language anywhere; no Tier 4 content presented as fact

## Could not verify

- The card's HEADLINE clinical claim — that ADA 2026 frames GLP-1 RA and SGLT2i as disease-modifying, considered from diagnosis — is corroborated at Tier 3 only. diabetesjournals.org and Wiley both returned 403. The risk-stratified half (ASCVD/HF/CKD regardless of A1C) is well corroborated; the "disease-modifying from diagnosis" half rests on one secondary source. Needs a primary citation or an explicit tier marker.
- Every figure in the West Michigan treatment-gap study — 5,783 patients, 60 clinics, 19.9%, and the subgroup rates. Wiley returned 403 on full text; DOI, title, journal and article number confirmed via Crossref but no number could be checked. Attribute as reported rather than stating flatly.
- Onswik: no claim about it reached the card, so nothing needed checking. The unconfirmed ~2026-09-23 date never made it onto the card, which is the correct outcome.
