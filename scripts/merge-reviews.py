#!/usr/bin/env python3
"""Merge the fact-check verdicts into the on-disk card JSON.

The reviews were produced by the `factchecker` agent. They are recorded here so the review
queue is readable from the repo and from the POC server, not only inside the Artifact.
Each entry is a faithful condensation of that card's report: every blocking defect is kept,
fixes and gaps are trimmed to the ones that change what a reader should do.
"""
import json, pathlib, sys

CARDS = pathlib.Path(__file__).resolve().parent.parent / "cards"

R = {}

R["type-2-diabetes-mellitus"] = {
 "verdict": "BLOCK",
 "checked": "26 claims · 15 searches · all 7 cited FDA label PDFs downloaded and read directly",
 "blocking": [
  {"claim": "Metformin row links to its FDA label",
   "says": "That URL is the label for SEGLUROMET (ertugliflozin + metformin), a fixed-dose SGLT2i/metformin combination — not metformin monotherapy. A clinician clicking the row lands on a two-drug product whose separate SGLT2i risks (DKA, Fournier's gangrene) the row does not disclose."},
  {"claim": "Metformin boxed warning: renal impairment, sepsis, dehydration, alcohol, acute CHF",
   "says": "The label enumerates renal impairment, concomitant drugs, AGE 65 AND OVER, RADIOLOGICAL STUDIES WITH CONTRAST, surgery, hypoxic states, alcohol, hepatic impairment. Four label risk factors are omitted and three non-label terms substituted. The contrast hold is a routine decision this card would fail to prompt."},
  {"claim": "Not on this card: Ozempic CKD indication unverified, no primary source",
   "says": "The card's own cited Ozempic label carries that indication in INDICATIONS AND USAGE. It is FDA-approved and documented in the source already on the card. The hedge became its own misinformation."}],
 "fixes": [
  {"claim": "Sulfonylurea boxed-warning format unconfirmed",
   "change": "RESOLVED: the UGDP cardiovascular-mortality warning is NOT a boxed warning; it sits in the ordinary WARNINGS section. Confirmed on two current labels."},
  {"claim": "Canagliflozin warnings incomplete",
   "change": "Add necrotizing fasciitis of the perineum (Fournier's gangrene), labelled as serious and life-threatening."},
  {"claim": "Tirzepatide row lists HFpEF-with-obesity",
   "change": "That is a Zepbound indication, not Mounjaro's. Relabel the row or drop the clause."}],
 "verified": [
  "Canagliflozin genuinely has NO boxed warning — the amputation warning was removed in 2020 and is now W&P only",
  "Thyroid C-cell tumour boxed warnings accurate on dulaglutide, semaglutide and tirzepatide",
  "ADA Standards of Care 2026 is the current edition and the year on the card is right",
  "Every Mounjaro figure matches SURPASS-CVOT including HR 0.92 (95.3% CI 0.83-1.01)",
  "No cited URL is dead or fabricated"],
 "couldNotVerify": [
  "The card's headline claim — that ADA 2026 frames GLP-1/SGLT2i as disease-modifying from diagnosis — is corroborated at Tier 3 only; diabetesjournals.org returned 403.",
  "Every figure in the West Michigan treatment-gap study. DOI and title confirmed via Crossref; full text blocked."]}

R["atrial-fibrillation"] = {
 "verdict": "BLOCK",
 "checked": "22 claims · 15 searches (at ceiling) · only 6 of 11 drug rows opened — 3 of those 6 were defective",
 "blocking": [
  {"claim": "Dofetilide — no boxed warning in retrieved label text",
   "says": "Tikosyn HAS a boxed warning, and the 3-day in-facility initiation requirement IS its content. The card prints the warning's substance while denying the warning exists."},
  {"claim": "Sotalol — no boxed warning noted",
   "says": "Sotalol injection carries WARNING: LIFE THREATENING PROARRHYTHMIA. The boxed warning's headline hazard — QT-prolonging ventricular tachycardia — is absent from the card altogether."},
  {"claim": "Metoprolol tartrate — no boxed warning",
   "says": "It carries one: abrupt cessation can cause angina exacerbation and myocardial infarction; taper over 1-2 weeks. The cited URL also resolves to a 12.5 mg SPL under a brand not marketed at that strength, which happens to lack the box — the metformin failure mode again."}],
 "fixes": [
  {"claim": "Apixaban cited to a 2021 supplement",
   "change": "A newer 2025 supplement exists; the boxed warning is UNCHANGED. Only the citation is stale."},
  {"claim": "Amiodarone route PO/IV",
   "change": "The cited label is tablets, oral only. An oral-label boxed warning cannot substantiate an IV route."},
  {"claim": "Gaps section claims the guideline avoids sex-specific CHA2DS2-VASc cutoffs",
   "change": "Wrong — the guideline states the 2%/year threshold with the sex-specific scores as its equivalent."},
  {"claim": "Internal contradiction on ablation",
   "change": "The summary asserts first-line ablation as fact while the gaps section calls that Tier 4 only. One must change."}],
 "verified": [
  "Edoxaban's three-part boxed warning is exact, including the CrCl above 95 mL/min do-not-use clause",
  "Amiodarone's three-part warning is correct and both figures are label-verbatim",
  "Dronedarone's boxed warning and both contraindications are exact",
  "The 2023 ACC/AHA/ACCP/HRS guideline is current and not superseded"],
 "couldNotVerify": [
  "FIVE DRUG ROWS WERE NEVER OPENED — warfarin, dabigatran, rivaroxaban, diltiazem, digoxin. Given 3 of 6 opened rows were wrong, these must be treated as unverified. A second pass is required.",
  "REMS status for dofetilide and oral sotalol.",
  "None of the three news items were opened."]}

R["major-depressive-disorder"] = {
 "verdict": "BLOCK",
 "checked": "31 claims · 14 searches · all 9 cited URLs opened; all 9 resolve and are the correct drug",
 "blocking": [
  {"claim": "Esketamine boxed warning: sedation, dissociation, abuse/misuse, suicidal thoughts",
   "says": "The boxed warning is titled SEDATION; DISSOCIATION; RESPIRATORY DEPRESSION; ABUSE AND MISUSE; SUICIDAL THOUGHTS AND BEHAVIORS. Respiratory depression is omitted — and it is the specific reason pulse oximetry is required. The orchestrator's own review brief also listed only four components; the label governs."},
  {"claim": "2025-01-21 monotherapy approval cited to the S-021 approval letter",
   "says": "S-021 is a Changes Being Effected supplement whose entire content is a REMS form revision. The monotherapy indication was SUPPL-16, approved 2025-01-17. The claim is true; the citation does not support it."},
  {"claim": "2025-03-24 SPRAVATO REMS modified (most recent update)",
   "says": "The cited letter describes that date as the PRIOR modification. Six later ones exist; the most recent is 2026-06-24. The card is 15 months stale."},
  {"claim": "Auvelity approved for dementia agitation, dated 2025",
   "says": "The card's own cited FDA announcement dates it 2026-04-30. Correctly dated it becomes the newest item on the card."}],
 "fixes": [
  {"claim": "Duloxetine label is the 2010 version",
   "change": "16 years stale. The claim holds but re-cite to the current PI."},
  {"claim": "'previously required a concomitant oral antidepressant' is unqualified",
   "change": "Monotherapy applies to TRD only. The acute-suicidal-ideation indication still requires one."},
  {"claim": "'reaffirmed 2015' on the headline APA claim",
   "change": "Unsourced — the APA page states no reaffirmation date. Came from the orchestrator's brief. Drop it or source it."}],
 "verified": [
  "The class suicidality boxed warning is verbatim-confirmed on all 8 rows, checked against eight separate labels",
  "Aripiprazole's two-limb boxed warning is accurate and complete",
  "THE HEADLINE CLAIM IS CORRECT: psychiatry.org's current guideline index contains no MDD guideline; it appears only under Legacy Practice Guidelines",
  "VA/DoD 2022 is current with no interim addendum",
  "Zuranolone correctly kept off the table — it received a Complete Response Letter for the MDD indication"],
 "couldNotVerify": [
  "'reaffirmed 2015' and '3rd edition' — neither appears on the APA page cited."]}

R["measles"] = {
 "verdict": "BLOCK",
 "checked": "34 claims · 11 searches",
 "blocking": [
  {"claim": "GamaSTAN — no boxed warning noted",
   "says": "The label carries WARNING: THROMBOSIS, with risk factors including advanced age, immobilisation, hypercoagulable states, prior thrombosis, oestrogen use and central vascular catheters."},
  {"claim": "IGIV 100-400 mg/kg",
   "says": "The card's own cited CDC source says 400 mg/kg. There is no range and no 100 mg/kg figure. The low end of the card's range is a FOUR-FOLD UNDERDOSE. The source also sets a route split the card omits: IGIV above 30 kg, GamaSTAN below 30 kg and not indicated for adults."},
  {"claim": "Antiviral therapy — none exists; no pipeline agent to list",
   "says": "The core negative is confirmed — no FDA-approved antiviral. But the card's own source has a ribavirin section: in vitro activity, used off-label in severe or immunocompromised disease, oral commercially available, IV only via FDA EIND. The absolute framing could lead a clinician to believe nothing off-label exists."},
  {"claim": "ProQuad row lists no contraindications at all",
   "says": "The label contraindicates it in hypersensitivity, immunosuppression, moderate or severe febrile illness, active untreated tuberculosis and pregnancy. A live attenuated vaccine row omitting pregnancy and immunosuppression is harm-capable."},
  {"claim": "M-M-R II contraindications omit active untreated tuberculosis",
   "says": "The label lists five contraindications including active untreated TB. The card also narrows hypersensitivity to neomycin; the label says any component."},
  {"claim": "Vitamin A row omits the pregnancy warning",
   "says": "Immediately adjacent to the toxicity sentence the card did use: pregnant women should avoid high-dose vitamin A, which has been linked to severe birth defects. The card gives no teratogenicity warning on the only row where it matters."}],
 "fixes": [
  {"claim": "The MMRV scheduling refusal",
   "change": "No longer the right call. CDC's live schedule notes state the operative recommendation: for dose 1 at 12-47 months, administer MMR and varicella separately; MMRV may be used if caregivers prefer. Replace 'unsettled' with that quoted language and its as-of date."},
  {"claim": "ProQuad route SC",
   "change": "Label says intramuscular or subcutaneous."},
  {"claim": "GamaSTAN dosing",
   "change": "CDC supersedes the label operationally: 0.5 mL/kg regardless of immune status, max 15 mL."},
  {"claim": "Secondary attack rate '90% or more'",
   "change": "CDC says 'up to 9 out of 10' — an upper bound. The card inverts it into a floor."},
  {"claim": "Missing from the PEP prose",
   "change": "Patients who receive IG PEP and are eligible for MMR should wait at least 6 months before vaccination."}],
 "verified": [
  "No FDA-approved antiviral and supportive-care-only management — confirmed verbatim",
  "ProQuad and M-M-R II genuinely carry no boxed warning; full label text extracted",
  "GamaSTAN IM-only / do-not-administer-intravenously is stated unambiguously on the card",
  "Vitamin A dosing matches CDC exactly, as do the 2026 and 2025 case counts to the digit",
  "PEP windows, IG eligibility and the 3-4 week protection duration all confirmed"],
 "couldNotVerify": [
  "The immunocompromised isolation clause is clinically standard but its cited source does not contain it.",
  "'Worst year since the early 1990s' is not stated on the CDC page it is attached to."]}

R["community-acquired-pneumonia"] = {
 "verdict": "BLOCK",
 "checked": "31 claims · 13 searches · both fluoroquinolone label PDFs parsed directly",
 "blocking": [
  {"claim": "Ceftaroline (Teflaro) listed as an anti-MRSA cephalosporin",
   "says": "Its CABP indication covers Staphylococcus aureus METHICILLIN-SUSCEPTIBLE ISOLATES ONLY. Only the skin-infection indication includes MRSA. On a CAP card from which vancomycin and linezolid were cut, this is the only row a provider scanning for MRSA coverage can land on, and it is the wrong answer."},
  {"claim": "The rendered card silently omits vancomycin and linezolid",
   "says": "The renderer normalises cards against a fixed key whitelist. 'cutForSpace' is not in it and is dropped, and the three cut agents live only there. In the shipped card a provider sees eight agents, none covering MRSA, with no indication that vancomycin or linezolid exist. The 8-row cap was the wrong thing to protect: a formatting limit should never outrank coverage completeness."}],
 "fixes": [
  {"claim": "Gaps section says the fluoroquinolone wording was never directly parsed",
   "change": "DELETE — the gap is closed. Both PDFs retrieved and extracted; all four boxed-warning elements present and the card's wording is accurate. The declared weak point was clean."},
  {"claim": "Levofloxacin route PO/IV",
   "change": "The cited label is tablets for oral use and its Recent Major Changes record the injection form being removed. Cite an injection label alongside it."},
  {"claim": "'Treat the four 2025 changes as contested, not settled'",
   "change": "Overstates the dissent. It PRAISES the shortened durations and objects specifically to the virus-positive antibacterial recommendation and the guideline process."},
  {"claim": "Severe-CAP criterion counts given without the decision rule",
   "change": "Add the threshold: one major OR three or more of nine minor. Severity gates two of the four recommendations the card asserts, so without it a provider cannot apply the card's own guidance."}],
 "verified": [
  "The 2025 update exists, is ATS-only, and IDSA is not a co-sponsor — the guideline page states it was not approved by IDSA",
  "All four 2025 recommendations are correct in direction AND strength",
  "PSI preferred over CURB-65 — strong recommendation, moderate quality",
  "Fluoroquinolone boxed warnings complete and accurate on all four elements",
  "Boxed-warning status confirmed for all 8 table rows plus all 3 cut agents; none omitted",
  "Three of the four dissent authors sat on the 2025 ATS panel — a genuine insider dissent"],
 "couldNotVerify": [
  "Whether IDSA will publish its own CAP guideline — the thing to re-check next refresh, since it would turn this card's two-guideline structure into three."]}

R["hypertension"] = {
 "verdict": "BLOCK",
 "checked": "31 claims · 14 searches · 7 direct fetches with a browser user-agent",
 "blocking": [
  {"claim": "Baxdrostat approved 2026-05-18",
   "says": "Drugs@FDA gives NDA 219878 submission status date 2026-05-15. Drugs.com's approval history independently gives May 15. Nothing supports May 18. Wrong in all four places it appears."},
  {"claim": "Spironolactone row: boxed tumorigenicity, citing a 2014 label",
   "says": "Three problems from one root. The cited 2014 PDF says on its own face 'this label may not be the latest approved by FDA'. The current reference label (Rev 11/2025) has NO boxed warning at all — the PLR conversion removed it. And the row omits HYPERKALEMIA, which is both a contraindication and the lead Warning, on a row explicitly scoped to add-on use in resistant hypertension stacked on an ACEi or ARB. Marketed generics do still carry the old box, so the claim is stale and inconsistent rather than fabricated."}],
 "fixes": [
  {"claim": "Guideline dated 2025-05 online",
   "change": "Published online 2025-08-14. The 2025-05 appears to have been read off the DOI suffix, which is not a publication date."},
  {"claim": "Lisinopril boxed warning includes a 2nd/3rd trimester clause",
   "change": "Not in the box. The box says discontinue as soon as pregnancy is detected, full stop. As written the card narrows a boxed warning toward LESS caution in the first trimester."},
  {"claim": "Gaps note about an unreconciled 47.7% vs 49.1% prevalence denominator",
   "change": "DELETE. '49.1' appears zero times in the cited CDC brief. 47.7% is correct and correctly labelled — the note asserts a figure its own source does not contain."},
  {"claim": "Baxdrostat has no drug row because its boxed-warning status is unverified",
   "change": "Now determined: NO boxed warning, no contraindications, W&P hyperkalemia and hyponatremia. It earns a row."}],
 "verified": [
  "The 2025 AHA/ACC multisociety guideline exists and is current, and ALL SIX specifics check out: <130/80 target, three first-line classes, two agents at 140/90, PREVENT replacing the Pooled Cohort Equations, renal denervation as Class 2b, aldosteronism screening regardless of potassium",
  "Losartan's fetal-toxicity boxed warning is accurate and complete",
  "'No boxed warning' is correct for amlodipine, chlorthalidone and hydrochlorothiazide — verified absences, not parsing misses",
  "47.7% prevalence and 20.7% controlled to <130/80 are both exactly right",
  "All three BaxHTN figures confirmed off the label itself",
  "Beta-blocker omission judged SAFE as disclosed — they are not first-line in the 2025 guideline and the gaps note preserves their compelling indications"],
 "couldNotVerify": [
  "Nothing material. Two publisher bot-blocks were worked around via independent primary sources."]}

changed = 0
for slug, review in R.items():
    p = CARDS / (slug + ".json")
    if not p.exists():
        print("  missing:", p.name, file=sys.stderr); continue
    d = json.loads(p.read_text())
    d["review"] = review
    p.write_text(json.dumps(d, indent=2) + "\n")
    nb, nf = len(review["blocking"]), len(review["fixes"])
    print("  %-40s %s  %d blocking, %d fixes" % (slug, review["verdict"], nb, nf))
    changed += 1
print("merged %d reviews" % changed)
