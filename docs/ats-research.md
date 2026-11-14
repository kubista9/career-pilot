# ATS research: what is known, what is myth, what a local check can do

All sources were read on 2026-11-14. Grades: **primary** (vendor or regulator documentation for the exact claim), **secondary** (practitioner, law-firm or press write-up, or an independent test), **marketing** (a vendor describing its own product or study). A claim marked "snippet only" was seen in a search result excerpt, because the page did not load or returned 403. A claim marked "from general knowledge, unverified" has no source here.

## Summary

1. Every ATS studied here parses an uploaded CV into text and a few fields. Text-based PDF and DOCX are accepted everywhere that publishes a list.
2. Parsing fails or degrades on scanned or image-only files, text the parser cannot select, tables, columns and unusual fonts. Vendors say so in their own help pages.
3. Vendors say AI match scores sort and flag candidates, and do not reject them. Auto-reject exists, but the employer builds it from knock-out questions.
4. The claim "75% of CVs are never seen by a human" has no traceable study. It is usually traced to a 2012 sales pitch.
5. Whether a recruiter reads every application depends on the employer. No source says they do.
6. Easy apply on LinkedIn and Indeed passes the CV file and screening answers to the employer. Indeed documents a cover letter as plain text. What survives in a given ATS is employer-specific.
7. Under the EU AI Act, hiring tools are high-risk. The date moved to 2 December 2027. GDPR Article 22 and Article 15(1)(h) already apply.
8. Online "ATS score" checkers measure keyword overlap and format heuristics. Jobscan and Enhancv say themselves that no real ATS gives that score.
9. A local check can test the file (text layer, reading order, fonts, size). It cannot test what a given ATS does with it.
10. Gaps: no source for icon fonts, file naming, date formats, applying early, or Teamtailor, iCIMS, Taleo and Affinda parser internals.

## What is established

- **File types.** Greenhouse accepts .doc, .docx, .pdf, .rtf and .txt, up to 100 MB [1]. Lever lists Word, PDF, RTF, WordPerfect, HTML and ODF as parseable [5, snippet only]. Recruitee accepts PDF, DOC, DOCX, ODT, RTF, TXT, and JPG or PNG images of a CV [11, snippet only]. Indeed delivers PDF, DOC, DOCX, RTF and TXT [15]. Textkernel handles more than 70 formats, and image or scanned CVs only through an optional OCR add-on [8]. Workday publishes no list in its admin guide [6].
- **Parse failure causes (vendors).** Greenhouse: not enough information, a non-standard file type, or characters the text parser does not recognise [2]. Recruitee: no email address, several documents in one file, text that cannot be selected, unusual fonts, an email address in the header or footer, scans, password protection, "highly visual" designs [10]. RChilli: the parser converts the CV to plain text first, and tables, columns and decoration scramble in that step; missing section headers can make content be overlooked [14, snippet only]. Workday: results vary with format and word order, and the guide advises resumes without images or image-based styles [6].
- **Fields extracted.** Teamtailor's basic parser fills name, email, phone and LinkedIn URL and attaches the CV [13, snippet only]. Workday fills profile fields but not hidden fields, Languages or Skills [6]. Greenhouse Talent Matching reads the parsed resume against weighted criteria such as skills, industry, years of experience and job titles [3].
- **The recruiter can usually still get the original.** Recruitee converts non-PDF files for preview and keeps the original downloadable [11, snippet only]. If a CV cannot be read at all, Recruitee still creates a profile and uses the file name as the candidate name [11, snippet only]. For Greenhouse, the failed-import article does not say whether the original stays available [2]. For Workday, Lever, Teamtailor: not found.
- **AI match is opt-in by the employer in the sources that document it.** Greenhouse: a Site Admin turns Talent Matching on, can turn AI off per job, and the feature "does not automatically advance or reject" [3]. Workday HiredScore grades candidates against job requirements and shows a "Fit & Gap" view [7, snippet only]; it is a separately licensed product (from general knowledge, unverified).
- **Auto-reject is built from knock-out questions by the employer.** Greenhouse states that auto-reject comes from employer-configured screening answers, not from its AI [4, snippet only]. Homerun: knock-outs are off by default, are Yes/No questions the employer adds, and a "No" moves the candidate to Disqualified [12]. Recruitee has knock-outs that disqualify and notify the candidate [11, snippet only].
- **The 75% claim has no study behind it** (see next section).
- **Canva: the Flatten PDF option removes accessibility tags and turns selectable text into pixels**, per two accessibility write-ups that cite Canva's own help [39, 40 snippet only]. Leave it off.

## What is disputed or a myth

- **"75% of CVs never reach a human."** The Interview Guys trace it to a 2012 sales pitch by Preptel, a CV-optimisation company, with no method, sample or survey [19, secondary, snippet only]. One snippet attributes the origin to Jobscan marketing instead, so the origin itself is disputed [18]. Enhancv's own post links a 2020 blog as its source and says the claim is repeated without data [18]. Reliability: none. Treat as a myth.
- **"92% of recruiters say the ATS does not auto-reject."** This comes from Enhancv: 25 US recruiters, interviewed September to October 2025, self-reported, small and not representative, run by a CV-builder company [18, marketing]. It supports "most recruiters say they do not use format-based auto-reject" and nothing stronger. In the same study 44% said their ATS has an AI or fit score, mostly used as a guide; the study names Bullhorn and BambooHR as the two systems with content-based auto-reject [18].
- **Filters can still exclude people.** A Harvard Business School and Accenture report (2021) says employers' screening software uses rules such as an employment gap to exclude candidates, based on a survey of about 8,700 hidden workers and 2,275 executives [secondary, via press coverage, snippet only; source 20]. This is about employer-set filters, not about parser failure.
- **"Recruiters search by keyword."** Several practitioner pages say so for Greenhouse. No Greenhouse primary page read here confirms recruiter keyword search. Unverified.
- **Greenhouse parse limit of 2.5 MB.** Repeated by third-party guides. Not on the Greenhouse pages read [1, 2]. Unverified.
- **PDF versus DOCX.** Practitioner pages split. Vendor pages only say both are accepted. No test evidence found. See the checklist.
- **Canva export settings.** Sources disagree about PDF Standard versus PDF Print. One accessibility guide recommends Standard with Flatten off [39]; a CV blog says Print is more text-friendly [42, weak]. Unresolved; test the file, do not trust the setting.
- **"Match Rate above 75% gets you through."** Jobscan sets its own 75% target [28]. Nothing links that number to a real ATS.
- **"Application received" and "Under review".** Only career blogs explain these labels [44, weak]. They agree "received" means logged, and that "under review" does not prove a human opened it. No vendor definition found.

## Per-system notes

| System | Parser | File types | Ranking or filter features | Source |
|---|---|---|---|---|
| Greenhouse | Not stated by Greenhouse. A third-party site says Sovren/Textkernel historically; unverified | .doc .docx .pdf .rtf .txt, 100 MB | Talent Matching (opt-in, five categories, no auto-reject); employer auto-reject rules from screening answers | [1] [2] [3] [4] |
| Lever | Not stated | Word, PDF, RTF, WordPerfect, HTML, ODF; images not parsed | Not researched | [5] snippet only |
| Workday Recruiting | Not stated in admin guide | No list published | Parsing populates profile; HiredScore grading is a separate product | [6] [7] |
| SmartRecruiters | Chose Textkernel (announcement, 2010 era) | Not found | "Winston"/SmartAssistant matching claimed by marketing; no primary page found | [9] snippet only |
| Recruitee | In-house or unstated; ML rules mentioned | PDF DOC DOCX ODT RTF TXT, JPG, PNG | Knock-out questions that disqualify | [10] [11] |
| Teamtailor | Not stated | docx pptx pdf pages txt rtf (from Co-pilot and API docs, not the basic parser page) | Co-pilot add-on screening | [13] snippet only |
| Homerun | Not researched | Not researched | Knock-outs off by default, then auto-disqualify | [12] |
| iCIMS, Taleo | Not found | Not found | Not found | none |
| Textkernel (vendor) | Is the parser | 70+ formats; OCR add-on for scans and images | n/a | [8] |
| RChilli (vendor) | Is the parser | Not read | n/a | [14] snippet only |
| Affinda, DaXtra, Sovren (as Textkernel), HireAbility | No documentation reached | n/a | n/a | none |

## Boards and easy apply

- **LinkedIn.** Easy Apply "hosts the application on LinkedIn and sends application data to your ATS" through Apply Connect, which is rolling out and replaced an older integration [17]. The candidate data LinkedIn lists as shared back to the ATS is: application viewed, resume downloaded, application rejected [17]. Applicant-facing "Viewed" means the poster opened the application including screening answers; "Resume downloaded" means the poster saved the attached CV; neither guarantees a reply [16]. Whether every employer has the integration on, and whether otherwise the application sits only in LinkedIn for the poster, is not settled by any LinkedIn page. One recruiter's post claims it sits in a LinkedIn "project" folder; that is anecdote.
- **Indeed.** Indeed posts each application to a URL set by the employer or ATS. The employer chooses whether the resume file is required, optional or hidden; formats are PDF, DOC, DOCX, RTF and TXT; the cover letter field is required, optional or hidden and is sent as plain text, so a file needs a screener question with an upload [15]. Screener answers are sent with the application [15]. Indeed Apply can also send a resume built on Indeed instead of a file [15].
- **What can be lost** (from the above, inferred): the cover letter's layout (Indeed sends plain text), any attachment the employer hid, and the file itself if the employer hid the resume field. Screening answers that the ATS does not map are lost: not documented, unverified.
- **Direct versus board.** No primary source compares outcomes. Practitioner pages claim direct applications do better; the figures (for example 1 to 3% versus 5 to 15%) come from vendor blogs. Unverified.

## Rules (GDPR, AI Act)

- **GDPR Article 22.** A person has the right not to be subject to a decision based solely on automated processing, including profiling, that has legal or similarly significant effects. Exceptions: necessary for a contract, authorised by law with safeguards, or explicit consent. Where an exception applies, the controller must give at least a right to human review, to state a view and to contest the decision. Special-category data is further restricted [21, secondary reproduction of the text; EUR-Lex not read].
- **GDPR Article 15(1)(h).** A candidate can ask whether such decision-making is used and, if so, for meaningful information about the logic involved and its likely consequences [22].
- **CJEU SCHUFA (C-634/21, 7 December 2023).** An automated score can itself count as a decision under Article 22(1) when a third party's decision draws strongly on it. Law-firm commentary notes this does not automatically catch every scoring system [23, secondary]. Whether it extends to a recruiter relying on an ATS match score is not established by anything read here.
- **AI Act.** Annex III point 4 makes AI used to recruit or select people (including advertising vacancies, filtering and screening applications, and evaluating candidates) high-risk [24, secondary reproduction]. Article 86 lets an affected person ask the deployer for a clear explanation of the AI system's role in a decision that significantly affects them, where Union or national law gives no equivalent right [25].
- **Dates.** The Digital Omnibus on AI was published in the Official Journal on 24 July 2026 and entered into force on 27 July 2026. It moves the stand-alone high-risk (Annex III) obligations from 2 August 2026 to 2 December 2027 [26, 27]. Source 27 was written before final adoption (15 May 2026, provisional agreement of 7 May); source 26 is the later one. The Official Journal text was not read. One snippet says systems already in use may have until December 2030; one source only, unverified.
- **What a candidate can do.** Ask the employer (as controller) whether automated decision-making or profiling was used, ask for the logic and consequences (Art. 15), ask for human review and contest a solely automated decision (Art. 22), and from the AI Act dates, ask for an explanation (Art. 86). Whether a given employer's ATS use counts as "solely automated" is a legal question this document does not answer.

## What online checkers measure

| Tool | What it says it measures | How | Source |
|---|---|---|---|
| Jobscan | Match Rate vs a pasted job description (hard skills, education, job title, soft skills, other keywords, in that priority); 30+ checks over readability, keywords, content, job match, formatting | Rule and keyword based; says it does not use AI for the scan; says the rate is "a visualization tool, not a score assigned by the employer's ATS" | [28] marketing, plus snippet on priority order |
| atsscorechecker.io | 35 rule-based checks: parse fidelity 35 points, findability 30, impact 25, language 10; "what the ATS read" view | Score is deterministic, no AI; separate AI report; says no mainstream ATS rejects on this score; stores uploaded files until deletion is requested | [29] marketing |
| Resume Worded | 30+ checks: impact, wording, formatting; separate job-relevance score | Method not described | [30] marketing |
| Enhancv | 27 checks in seven areas, including file name, parse coverage, tailoring | Says no tool can give a true ATS score | [32] marketing |
| Kickresume | 20+ checks, plus comparison with a database of "successful" CVs and an AI reviewer | Simulated scan; weights not shown | [31] marketing |
| OpenResume parser (open source, AGPL-3.0) | Whether a CV parses into name, email, sections | pdf.js text items, grouped into lines and sections by bold, uppercase and keyword heuristics, then scored attribute extractors; designed for single-column English CVs | [33] |

**Distance from a real ATS.** These tools check three things: whether text can be extracted, whether sections are detected, and how many job-description words appear. A real ATS parser is a trained or rule-based model run by a specific vendor, and none of its models is published. So the checker score is a proxy. Two vendors say this outright [28, 29, 32]. No independent test comparing a checker score with real ATS outcomes was found.

**Privacy note for the repo.** Hosted checkers upload the CV. The local command must not.

**PDF text extraction libraries** (metadata from PyPI and GitHub, 2026-11-14 [35]):

| Library | Licence | Maintenance | Reading-order notes |
|---|---|---|---|
| pypdf | BSD-3-Clause | Release 7.1.0 on 2026-11-13; repo pushed 2026-11-13 | Docs say PDFs have no semantic layer and tables are hard; whitespace is not guaranteed; layout mode follows the rendered layout; not OCR [34] |
| pdfminer.six | MIT | 20260107 release; repo pushed 2026-03-13 | Has layout analysis (from general knowledge, unverified); little reading-order data found |
| pdfplumber | MIT | 0.11.10 on 2026-06-15; repo pushed 2026-10-15 | One self-published benchmark scored it badly on reading order [38]; other pages disagree |
| PyMuPDF | AGPL-3.0 or commercial (Artifex) | 2.1 on 2026-11-02; repo pushed 2026-11-13 | Best on text extraction in a preprint comparing six rule-based tools, but the paper did not test multi-column order specifically [37]; block mode with sorting is the usual workaround [38] |
| poppler pdftotext | GPL-2.0 (COPYING in the repository) | Packaged as 26.01.0 in Debian experimental | Default mode outputs "reading order" and undoes columns; `-raw` keeps content-stream order and is not recommended; `-layout` keeps physical layout [36, snippet only] |

Practical reading: no library is proven to match an ATS. Extract with two (for example pypdf and pdftotext) and flag disagreement. PyMuPDF's AGPL licence matters if the repo is later packaged; pypdf, pdfminer.six and pdfplumber are permissive. Poppler is an external binary, not a Python dependency.

## Canva

- **Real text layer.** Canva's own accessibility help says flattening removes tags [40, snippet only]. A CommonLook knowledge-base article says direct Canva exports can have missing tags and a poor reading order; layers act as the reading order; Flatten merges everything into an image and turns text into pixels [39, secondary, dated only "27 Mar", year not shown]. So: a normal (unflattened) export keeps selectable text, and a flattened one does not.
- **Settings that matter.** Flatten PDF off. Reading order follows layer order, and Canva's help mentions a "match reading order to layers" option [39, 40]. One accessibility guide says manual reading-order adjustment is not supported [snippet only]; the sources conflict.
- **Canva Docs versus fixed-page designs.** Nothing reliable found for Canva Docs specifically.
- **Fonts.** No source explains how Canva embeds fonts. Recruitee names unusual fonts as a failure cause [10].
- **Observed, unverified.** The repo owner measured a small set locally on 14 November 2026, with no personal data involved. This is an observation on nine files, not a general fact. The set was nine one-page PDF exports from Canva fixed-page designs with a two-column layout.
  - Text layer: present in all nine, about 2,700 to 2,900 characters per page. Fonts were embedded. No private-use, replacement or ligature characters were found, and all date ranges were readable.
  - Reading order: five extractors were compared. pypdf and pdftotext agreed with PyMuPDF on word order. pdfminer.six differed by roughly 30 percent and pdfplumber by roughly 60 percent. pdfplumber put sidebar and main-column text on the same line in about a fifth of lines.
  - Links: none of the URLs was a clickable link annotation.
  - Hosted checker: one checker reported "no phone" for a CV whose phone number was written in national format without a country code. A local pattern found the number. The cause was not confirmed.
- **Verdict.** In that set, an unflattened fixed-page export kept its text. The open risk is reading order in multi-column designs, so extract the text of the real exported file and compare extractors. That is what `ats-check` is for. Canva Docs: nothing found.

## A clean CV template

Status: **established** = a vendor primary page says it; **likely** = several secondary sources agree or it follows from how text extraction works; **unverified** = no source here.

- [ ] Text-based PDF or DOCX, not a scan or an image. **Established** [2, 6, 10, 8].
- [ ] Every character selectable; the email and phone are real text. **Established** [10].
- [ ] No contact details only in a header or footer; repeat them in the body. **Established** for Recruitee [10]; **likely** elsewhere.
- [ ] One column, one reading direction. **Likely** [14, 33; extraction docs 34].
- [ ] No tables for layout, no text boxes, no sidebars. **Likely** [14, 34].
- [ ] No text inside images, no skill bars or rating graphics. **Established** for images [6, 10].
- [ ] Standard fonts (Arial, Times New Roman and similar), embedded. **Established** for "unusual fonts cause trouble" [10]; **unverified** for which fonts are safest.
- [ ] No icon fonts for phone, mail or LinkedIn; write the words. **Unverified** (no source found; follows from private-use code points having no text meaning).
- [ ] Ligatures: text extracts correctly in the finished file (check for "ﬁ", missing letters). **Likely** [43, bug reports]. Test, do not assume.
- [ ] Standard section headings: Experience, Education, Skills. **Likely** [14, 33].
- [ ] Dates in one consistent format with month and year, for example "Mar 2022 to Jun 2024". **Unverified** (practitioner advice only).
- [ ] The exact job title and tool names as in the listing, only where true. **Likely** that keyword search exists in some systems [3, 29]; **unverified** that it decides outcomes. Honesty is a rule of this repo regardless.
- [ ] Reasonable file size; stay well under 10 MB. **Established** that limits exist: 100 MB Greenhouse [1]; Lever 10 MB from a snippet only [5].
- [ ] No password, no encryption. **Established** [10].
- [ ] One CV per file, no merged documents. **Established** [10].
- [ ] A readable file name with no version numbers or internal notes, for example `Alex-Example-CV.pdf`. **Unverified** that file names matter; Enhancv lists file name as a check [32], which is marketing.
- [ ] Canva or similar design tools: export with Flatten off, then verify extraction. **Established** for Flatten [39, 40 snippet].
- [ ] Do not fake keywords in white text or hidden layers. **From general knowledge, unverified** as a parser effect; it breaks the repo's honesty rule.

## Checks a local `ats-check` command should run

Ordered by value. "Heuristic" means a rule of thumb, not something a vendor documents.

1. **File opens and is not encrypted.** Reason: password-protected files fail parsing [10]. Grade: established.
2. **Text layer exists.** Extract text with one library; fail if the characters per page are below a small threshold (heuristic threshold). Reason: scans and flattened PDFs produce no text [2, 10, 39]. Grade: established for the reason; threshold is a heuristic.
3. **Contact details are in the extracted text.** Find an email address and a phone number with a pattern. Reason: Recruitee fails on a missing email [10]; Teamtailor and Workday fill these fields [6, 13]. Grade: established for the reason; pattern is a heuristic.
4. **Contact details are not only in a header or footer.** Compare page header and footer bands (by position) with the body text. Reason: [10]. Grade: established for Recruitee, heuristic for the band positions.
5. **Reading order is sane.** Extract with two tools (for example pypdf and pdftotext) and compare the order of section headings and the first words of each block. Report disagreement. Reason: the libraries differ and none is proven to match an ATS [34, 36, 37, 38]. Grade: heuristic.
6. **Section headings are present and in the extracted text.** Look for Experience, Education, Skills (and local-language equivalents from a list). Reason: [14, 33]. Grade: likely; the list is a heuristic.
7. **Column and table signal.** Flag lines that look like two columns merged into one line (big internal gaps in layout mode), and rows of repeated spacing. Reason: [14, 34]. Grade: likely; detection is a heuristic.
8. **Odd characters.** Count private-use code points (U+E000 to U+F8FF), replacement characters (U+FFFD), U+0000, and unexpanded ligature characters (U+FB00 to U+FB06). Reason: broken ToUnicode maps and icon fonts [2, 43]. Grade: likely; follows from [2] and bug reports.
9. **Fonts.** List fonts and whether each is embedded; warn on non-embedded and on decorative fonts. Reason: [10]. Grade: established that unusual fonts cause trouble; "decorative" is a heuristic.
10. **Images.** Count images and the share of page area; warn when large. Reason: [6, 10]. Grade: established for the reason; thresholds heuristic.
11. **Flatten signal.** Flag a PDF with images on every page and no text. Covered by check 2; also report producer metadata (for example Canva) as information. Reason: [39]. Grade: likely.
12. **File size and page count.** Warn above 10 MB; warn above three pages (page count is a heuristic, for readability, not for parsing). Reason: size limits exist [1, 5]. Grade: size established; page count heuristic.
13. **Dates.** Find date-like strings and report mixed formats. Reason: practitioner advice only. Grade: unverified, heuristic.
14. **Keyword overlap with the listing (optional, advisory).** Show which listing terms are missing from the CV. Never edit the CV from this. Reason: some ATS offer keyword search or match [3, 7]. Grade: likely that it matters in some systems, unverified how much. The command must not give a score that suggests an ATS result.

## What a local check cannot tell

- What a specific employer's ATS and parser version do with the file. The parsers' models are not public (Textkernel's docs do not describe handling of headers, footers or text boxes [8]).
- Whether the employer uses auto-reject, knock-out questions or AI match, and with which settings.
- Whether a person reads the application.
- Whether LinkedIn or Indeed forwarded the file, the cover letter and the answers intact.
- Whether the content is good. A clean parse says nothing about the quality of the CV.
- A "score". There is no real ATS score; the local command should report pass, warn and fail per check, not a number.

## Sources

Format: number, URL, publisher, date read (all 2026-11-14), grade. "Snippet only" means the page itself did not load or was blocked (403) and the claim comes from a search excerpt. Publication dates are given only where a page showed one.

1. https://support.greenhouse.io/hc/en-us/articles/360052218132-Supported-file-types-for-resumes-and-cover-letters, Greenhouse, no date shown, primary.
2. https://support.greenhouse.io/hc/en-us/articles/200721684-Why-didn-t-the-candidate-s-resume-import-correctly, Greenhouse, no date shown, primary.
3. https://support.greenhouse.io/hc/en-us/articles/41396009937307-Talent-Matching, Greenhouse, no date shown, primary.
4. https://www.greenhouse.com/blog/evolving-legal-landscape-of-ai-in-the-hiring-process, Greenhouse blog, no date shown, primary (vendor statement). Snippet only.
5. https://help.lever.co/hc/en-us/articles/20087345054749 (and https://lever-old.zendesk.com/hc/en-us/articles/360056337151, 403), Lever, no date shown, primary. Snippet only; the page rendered empty.
6. https://doc.workday.com/admin-guide/en-us/human-capital-management/recruiting/candidates/set-up-prospects-and-candidates/hdc1552497830785.html, Workday, no date shown, primary.
7. https://doc.workday.com/admin-guide/en-us/workday-feature-descriptions/workday-hiredscore/hiredscore-ai-for-recruiting.html and https://doc.workday.com/hiredscore/en-us/workday-hiredscore/hiredscore-release-notes/2026/august/wednesday%2D%2D5th-august.html.html, Workday, August 2026 release note, primary. Snippet only.
8. https://developers.textkernel.com/TKPlatform/master/file-formats/, Textkernel, no date shown, primary.
9. https://www.onrec.com/news/news-archive/smartrecruiters-chooses-textkernel%E2%80%99s-resume-parsing-software, OnRec (press release reprint), about 2010, secondary. Snippet only.
10. https://support.recruitee.com/en/articles/4752121-why-was-my-candidate-s-cv-not-parsed-correctly, Recruitee, no date shown, primary.
11. https://support.recruitee.com/en/articles/1109254-upload-and-parse-cvs and https://support.recruitee.com/articles/6108676 (knock-out questions), Recruitee, no date shown, primary. Snippet only.
12. https://help.homerun.co/en/articles/10922292-automatically-disqualifying-candidates-with-knockout-questions, Homerun, no date shown, primary.
13. https://www.teamtailor.com/en/productnews/auto-add-candidate-information-with-resume-parser/ and https://support.teamtailor.com/en/articles/10209597-co-pilot-candidate-screening, Teamtailor, no date shown, primary. Snippet only.
14. https://help.rchilli.com/hc/en-us/articles/360011188234-Tips-to-Ensure-that-Our-Resume-Parser-Reads-Your-Resumes-with-Perfection, RChilli, no date shown, primary. 403; snippet only.
15. https://docs.indeed.com/indeed-apply/add-indeed-apply, Indeed, no date shown, primary.
16. https://www.linkedin.com/help/linkedin/answer/a508716, LinkedIn, no date shown, primary.
17. https://www.linkedin.com/help/linkedin/answer/a514094, LinkedIn, no date shown, primary.
18. https://enhancv.com/blog/does-ats-reject-resumes/, Enhancv, published 2025-11-03, marketing (vendor-run study, 25 recruiters).
19. https://blog.theinterviewguys.com/?p=1967, The Interview Guys, no date shown, secondary. Snippet only.
20. https://www.hrdive.com/news/report-applicant-tracking-systems-may-exclude-whole-segments-of-candidates/606614/ (coverage of the Harvard Business School and Accenture "Hidden Workers" report, 2021), HR Dive, secondary. Snippet only; the report itself was not opened.
21. https://gdpr-info.eu/art-22-gdpr/, gdpr-info.eu (unofficial reproduction of Regulation (EU) 2016/679), secondary.
22. https://gdpr-info.eu/art-15-gdpr/, same, secondary.
23. https://iapp.org/news/a/key-takeaways-from-the-cjeus-recent-automated-decision-making-rulings and https://twobirds.com/en/insights/2023/global/key-takeaways-from-the-schufa-case-of-the-cjeu, IAPP and Bird & Bird, December 2023 onward, secondary. Snippet only; the judgment text was not read.
24. https://artificialintelligenceact.eu/annex/3/, Future of Life Institute site (reproduction of Regulation (EU) 2024/1689), secondary.
25. https://artificialintelligenceact.eu/article/86/, same, secondary.
26. https://www.lewissilkin.com/insights/2026/07/27/the-digital-omnibus-on-ai-enters-into-force-today-102nedo, Lewis Silkin, 2026-07-27, secondary.
27. https://cms.law/en/gbr/publication/the-eu-s-digital-omnibus-on-ai-what-the-provisional-agreement-really-changes, CMS, 2026-05-15 (modified 2026-05-26), secondary.
28. https://www.jobscan.co/resume-score, Jobscan, no date shown, marketing.
29. https://atsscorechecker.io, atsscorechecker.io, no date shown, marketing.
30. https://resumeworded.com/, Resume Worded, no date shown, marketing.
31. https://www.kickresume.com/en/resume-checker/, Kickresume, no date shown, marketing.
32. https://enhancv.com/resources/resume-checker/, Enhancv, no date shown, marketing.
33. https://github.com/xitanggg/open-resume and https://www.open-resume.com/resume-parser, OpenResume authors, no date shown, primary for the tool itself.
34. https://pypdf.readthedocs.io/en/stable/user/extract-text.html, pypdf project, no date shown, primary.
35. https://pypi.org/pypi/pypdf/json, .../pdfminer.six/json, .../pdfplumber/json, .../PyMuPDF/json, and the GitHub API pages of py-pdf/pypdf, pdfminer/pdfminer.six, jsvine/pdfplumber, pymupdf/PyMuPDF, PyPI and GitHub, fetched 2026-11-14, primary.
36. https://manpages.debian.org/trixie/poppler-utils/pdftotext.1.en.html and https://gitlab.freedesktop.org/poppler/poppler/-/raw/master/COPYING, Debian and the poppler project, primary. The man page is snippet only; COPYING header read directly (GPL version 2).
37. https://arxiv.org/html/2410.09871v2, Adhikari and Agarwal, 2025, arXiv preprint (not shown as peer reviewed), secondary.
38. https://github.com/justin-aj/pdf-extraction-benchmark and similar blog benchmarks, individual authors, no dates checked, secondary (weak). Snippet only.
39. https://support.allyant.com/support/solutions/articles/156000382271-making-canva-pdfs-accessible, Allyant/CommonLook knowledge base, "Modified on 27 Mar", year not shown, secondary.
40. https://www.canva.com/help/pdf-accessibility-features/ and https://www.canva.com/help/download-flattened-pdf/, Canva, no date shown, primary. 403; snippet only.
41. https://www.glassdoor.com/research/interview-sources/ and https://lbsresearch.london.edu/id/eprint/3540/1/Campero_Kacperczyk_accepted.pdf, Glassdoor and London Business School, secondary. Snippet only. They concern referrals only; nothing was found on applying early.
42. https://blog.loopcv.pro/are-canva-resumes-ats-friendly/ and similar CV blogs, secondary (weak). Snippet only.
43. https://bugzilla.mozilla.org/show_bug.cgi?id=1810914 and https://bugs.freedesktop.org/show_bug.cgi?id=7002, Mozilla and freedesktop bug trackers, secondary. Snippet only.
44. https://www.loopcv.pro/guides/greenhouse-application-status/ and similar, career blogs, secondary (weak). Snippet only.
