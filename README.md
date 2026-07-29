<p align="center">
  <img src="assets/portrait.svg" alt="ASCII portrait" width="460" />
</p>

<p align="center">
  <img src="assets/heading-about.svg" alt="about" width="600" />
</p>

> A GitHub profile that generates itself — the portrait above and the<br />
> graphics below are drawn by this repository's own code, on a schedule,<br />
> with zero third-party requests.

Every pixel on this page is produced inside this repo by a scheduled<br />
GitHub Action. The portrait is a photo run through a background cutout,<br />
a contrast curve, and a 13-character brightness ramp, then typed onto<br />
the page with SMIL animation. The graphics below are pulled fresh from<br />
the GitHub GraphQL API every night and redrawn as plain SVG — no<br />
`github-readme-stats`, no widget service that can rate-limit or go dark.

<p align="center">
  <img src="assets/heading-live-stats.svg" alt="live stats" width="600" />
</p>

<p align="center">
  <img src="assets/stats.svg" alt="contribution total and weekly sparkline" width="460" /><br />
  <img src="assets/streak.svg" alt="current and longest contribution streaks" width="460" /><br />
  <img src="assets/langs.svg" alt="top languages by bytes and by repo" width="460" /><br />
  <img src="assets/year.svg" alt="the last year, one character per day" width="700" />
</p>

<p align="center">
  <img src="assets/heading-how-this-works.svg" alt="how this works" width="600" />
</p>

Stack: <samp>Python · Pillow · OpenCV · rembg · GitHub GraphQL API · SMIL · GitHub Actions</samp>

**The portrait** (`scripts/generate_portrait.py`) cuts the subject from<br />
its background with `rembg`, smooths skin while keeping edges with a<br />
bilateral filter, evens out lighting with CLAHE, then applies a<br />
`(v/255)^1.7` darkening curve so shadow detail — glasses, brows, lips —<br />
survives the trip through a 13-character ramp. Each row types onto the<br />
page inside an animated `clipPath`, staggered top to bottom, `fill="freeze"`<br />
so it prints once and stops.

**The stats** (`scripts/generate_stats.py`) query `contributionsCollection`<br />
over a window pinned to whole UTC days — otherwise two runs minutes apart<br />
bucket days into different weeks and the sparkline appears to change every<br />
night for no reason — and `repositories(privacy: PUBLIC)` so language<br />
percentages don't depend on whether a personal token or the workflow's<br />
token ran the query. The generator has no dependencies beyond the Python<br />
standard library, so there's nothing in the data path for CI to break.

The nightly workflow (`.github/workflows/refresh.yml`) runs on a cron,<br />
regenerates the four stat SVGs, and commits only if something changed.<br />
It deliberately has no `push` trigger, since it commits — a `push`<br />
trigger would re-run the job on its own commit.

Everything renders through GitHub's own markdown sanitiser, which strips<br />
`<style>` blocks, `class`/`style` attributes, and raw inline `<svg>`.<br />
So headings above are images with an embedded `@font-face`, and the<br />
stat graphics are separate SVG documents loaded through `<img>` — the<br />
one place a data-URI font is still allowed to render.

<details>
<summary>font notes</summary>

The portrait's character grid assumes a monospace advance width of<br />
exactly 0.600 em. JetBrains Mono ships at 600/1000 units — matching<br />
exactly — so no per-font geometry correction is needed. Each SVG embeds<br />
only the glyphs it uses: a 13-character subset for the portrait ramp,<br />
a lowercase-and-punctuation subset for headings, and a basic-Latin subset<br />
for the data graphics. About 12 KB total across the whole page.

</details>

<p align="center">
  <img src="assets/heading-credits.svg" alt="credits" width="600" />
</p>

- Portrait pipeline based on the ASCII Portrait README Guide, with a<br />
  darkening-curve fix for washed-out faces.
- Typeface: JetBrains Mono, [SIL OFL 1.1](fonts/OFL.txt).
- All the code that draws this page lives in this repository.
