# Writing module — task data and sources

**60 tasks: 10 per CEFR level (A1–C2).** Every task carries **Leitpunkte** — the bullet
points that guide the student — because that scaffold is how the real exams work:
telc states its bullet points explicitly (4 Leitpunkte at B1), and Goethe's tasks
are defined by what the text must cover.

Each task shows: level · target length · which exam it comes from, plus the bullets.

The task list is built from the **writing sections of the real German proficiency
exams**, not invented. Research done 2026-10; re-check before treating any of it as permanent.

Providers: **Goethe-Institut** (`Schreiben`), **telc** (`Schriftlicher Ausdruck`),
**ÖSD** (`Schreiben`). telc and ÖSD are separate exams from Goethe, and their formats
genuinely differ — that is why several levels offer more than one task.

## Per-level structure

| Level | Goethe | telc | ÖSD |
|---|---|---|---|
| A1 | 2 tasks (form + ~30 w) | 2 tasks (form + ~30 w) | 2 tasks (form + ~30 w) |
| A2 | 2 tasks (SMS 20–30 w + E-Mail 30–40 w) | 2 tasks (form + ~40 w) | **1 task** (~50 w) |
| B1 | **3 tasks** (80 / 80 / 40) | **1 task** (semi-formal e-mail, 4 Leitpunkte) | **3 tasks** (80 / 80 / 40) |
| B2 | 2 tasks (150 + 100) | **1 of 2** (~150 w) | 2 tasks (120 + 120) |
| C1 | 2 tasks (230 + 120) | **1 of 2** (~350 w) | 2 tasks (formal reply + 250 w) |
| C2 | 2 tasks (reformulation + 350 w) | **1** (essay, no limit) | — |

**Leitpunkte** = the bullet points telc gives you and expects you to cover.

## Sources

**Goethe** — https://bfu.goethe.de/a1_sd1/schreiben.php ·
https://bfu.goethe.de/a2_mod_2MX5/schreiben.php · https://bfu.goethe.de/b1_mod/schreiben.php ·
https://bfu.goethe.de/b2_mod_2MX6/schreiben.php · https://bfu.goethe.de/c1mod/ ·
https://bfu.goethe.de/c2_mod/schreiben.php

**telc** — Deutsch_B2_Handbuch.pdf, Deutsch_B1_plus_Beruf_Handbuch.pdf, Deutsch_c1_beruf_Handbuch.pdf,
Deutsch_c1_hochschule_tipps_zur_pruefungsvorbereitung.pdf, Deutsch_c2_Handbuch.pdf, Deutsch_c2_tipps_zur_pruefungsvorbereitung.pdf
(all under `https://www.telc.net/fileadmin/user_upload/pdfs/Handbuch_und_Tipps_fuer_Pruefungsvorbereitung/`),
plus `https://www.telc.net/en/language-examinations/certificate-exams/german/…` exam pages.

**ÖSD** — https://osd.at/wp-content/uploads/2021/06/ZA1-Modellsatz_schriftliche-Pruefung-1.pdf ·
https://www.osd.at/wp-content/uploads/2018/10/zb2-j_modellsatz_schreiben.pdf ·
https://www.osd.at/wp-content/uploads/2026/08/ZC1-Modellsatz-Homepage-SA.pdf ·
https://www.osd.at/wp-content/uploads/2025/08/ZC1-PMB-AW_s_Ver.1.0_16_07_25_WEB.pdf

## Deliberate deviations

- **A1 "Formular ausfüllen" is adapted.** The real task is filling five blanks on a
  printed form; this app has one textarea, so the task asks for the five values as a
  short block of text. Same content, different input control.
- **C2 Goethe Aufgabe 1 (Überarbeitung eines Kurzreferats) is omitted.** It is a
  10-gap reformulation, not free composition, so it does not fit a "write a text" flow.
- **Ten tasks per level exceeds what any single exam asks for.** Each level offers
  one or two *documented* exam formats (marked with a provider label such as
  `Goethe B2, Teil 1` or `telc B2`), then fills the rest with **the same text sorts in
  new situations**, marked `Goethe A1 Register` / `Goethe B2 Register`. Those are
  practice variations built on a real register, not exam papers.
- **Situations and bullets are written fresh**, not lifted from Modellsatz PDFs.
- **Leitpunkte for the documented formats follow the published task content**
  (e.g. Goethe A1 Teil 2 genuinely asks for reason + cultural programme + hotel
  addresses). Bullet *wording* is ours.

## Known gaps

1. **telc B1 has no official word count.** telc's own test-format table gives the task
   type, 4 Leitpunkte and 30 minutes, but no length. The 80–100 shown for
   `b1-telc-leitpunkte` is inferred from model answers, not a telc specification.
2. **telc B2·C1 Beruf** — only the structure table (3 tasks / 60 min) was obtainable;
   task types and word counts are not documented. Not included.
3. **telc B2+ Beruf** — exam exists, no writing spec retrieved. Not included.
4. **telc C2 Beruf does not exist.** telc's C-level vocational exams are C1 Beruf and
   B2·C1 Beruf. telc C2 itself (integrative essay) is included.
5. **ÖSD C1 Aufgabe 1** — the model set gives no length for the formal reply e-mail.
   Shown as 250 words to match Aufgabe 2, which is documented.
6. Several telc mock-exam PDFs are scan-only with no text layer; figures were taken from
   the Handbücher instead.
7. Nothing here comes from third-party prep sites — only provider documents.