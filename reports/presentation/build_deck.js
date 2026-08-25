// Build reports/presentation/Kepler_Refresh_2026.pptx — the 2026 refresh deck.
// Dark, warm slides with amber titles (continuity with the 2020 deck), no blue anywhere.
// Regenerate: `node reports/presentation/build_deck.js` (needs Node.js and `npm install pptxgenjs`;
// the script is optional — the .pptx and .pdf next to it are the deliverables).
const path = require("path");
const pptxgen = require("pptxgenjs");

const FIG = path.join(__dirname, "..", "figures");
const OUT = path.join(__dirname, "Kepler_Refresh_2026.pptx");

// palette (app dark theme, validated 2026-08-25) — hex without '#'
const BG = "15140F", CARD = "23211A", CARD2 = "2C2921", TEXT = "F2F0E8", MUTED = "B8B4A6";
const AMBER = "E08A00", AMBER_D = "CC8016", GREEN = "3FA33F", GREEN_D = "1F7A1F", PLUM = "B8489A";
const FONT = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
pres.author = "Rich Anderson";
pres.title = "Kepler exoplanets — the 2026 refresh";

const W = 13.33, H = 7.5, M = 0.6;

function base(title, notes) {
  const s = pres.addSlide();
  s.background = { color: BG };
  if (title) {
    s.addText(title, { x: M, y: 0.35, w: W - 2 * M, h: 0.8, fontFace: FONT, fontSize: 34, bold: true, color: AMBER, margin: 0 });
  }
  s.addText("Kepler exoplanets · 2026 refresh", { x: M, y: H - 0.45, w: 6, h: 0.3, fontFace: FONT, fontSize: 10, color: MUTED, margin: 0 });
  if (notes) s.addNotes(notes);
  return s;
}
function card(s, x, y, w, h, fill = CARD) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: fill }, rectRadius: 0.12 });
}
function stat(s, x, y, w, value, label, color = AMBER, valueSize = 40) {
  s.addText(value, { x, y, w, h: 0.75, fontFace: FONT, fontSize: valueSize, bold: true, color, margin: 0, valign: "bottom" });
  s.addText(label, { x, y: y + 0.78, w, h: 0.55, fontFace: FONT, fontSize: 12, color: MUTED, margin: 0, valign: "top" });
}
function bullets(s, x, y, w, h, items, size = 15, color = TEXT) {
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: { indent: 14 }, breakLine: i < items.length - 1, paraSpaceAfter: 8 } })),
    { x, y, w, h, fontFace: FONT, fontSize: size, color, margin: 0, valign: "top" });
}
function para(s, x, y, w, h, text, size = 14, color = TEXT, opts = {}) {
  s.addText(text, { x, y, w, h, fontFace: FONT, fontSize: size, color, margin: 0, valign: "top", ...opts });
}
function figure(s, path, x, y, w, h, caption) {
  card(s, x - 0.08, y - 0.08, w + 0.16, h + 0.16 + (caption ? 0.34 : 0), "FCFCFB");
  s.addImage({ path, x, y, w, h, sizing: { type: "contain", w, h } });
  if (caption) s.addText(caption, { x, y: y + h + 0.02, w, h: 0.3, fontFace: FONT, fontSize: 10, color: "52514E", margin: 0, align: "center" });
}
function thenNow(s, x, y, w, h, thenTitle, thenItems, nowTitle, nowItems, size = 14) {
  const gap = 0.3, cw = (w - gap) / 2;
  card(s, x, y, cw, h, CARD);
  card(s, x + cw + gap, y, cw, h, CARD2);
  s.addText(thenTitle, { x: x + 0.25, y: y + 0.15, w: cw - 0.5, h: 0.4, fontFace: FONT, fontSize: 16, bold: true, color: MUTED, margin: 0 });
  s.addText(nowTitle, { x: x + cw + gap + 0.25, y: y + 0.15, w: cw - 0.5, h: 0.4, fontFace: FONT, fontSize: 16, bold: true, color: AMBER, margin: 0 });
  bullets(s, x + 0.25, y + 0.65, cw - 0.5, h - 0.8, thenItems, size, MUTED);
  bullets(s, x + cw + gap + 0.25, y + 0.65, cw - 0.5, h - 0.8, nowItems, size, TEXT);
}

// ------------------------------------------------------------------ 1 title
{
  const s = pres.addSlide();
  s.background = { color: BG };
  s.addText("Kepler exoplanets", { x: M, y: 1.6, w: W - 2 * M, h: 1.0, fontFace: FONT, fontSize: 52, bold: true, color: AMBER, margin: 0 });
  s.addText("the 2026 refresh", { x: M, y: 2.55, w: W - 2 * M, h: 0.8, fontFace: FONT, fontSize: 36, color: TEXT, margin: 0 });
  para(s, M, 3.5, 8.2, 1.0, "Kepler Objects of Interest: honest models, the habitable zone done on insolation, and an app that runs in your browser.", 18, MUTED);
  para(s, M, 4.9, 6.2, 1.6,
    [{ text: "Rich Anderson · August 2026", options: { bold: true, color: TEXT, breakLine: true } },
     { text: "Refresh of the 2020 Columbia Engineering data-analytics bootcamp team project", options: { color: MUTED, breakLine: true } },
     { text: "2020 team: Rich Anderson (ML pipeline), Damien Corr, Priscilla Lin, Tom Greff", options: { color: MUTED } }], 13);
  card(s, 7.6, 4.75, 5.1, 1.9, CARD);
  para(s, 7.85, 4.9, 4.7, 1.7,
    [{ text: "Code, notebooks, research log", options: { bold: true, color: AMBER, breakLine: true } },
     { text: "github.com/Rander417/KeplerExoplanet", options: { color: TEXT, breakLine: true } },
     { text: " ", options: { breakLine: true, fontSize: 6 } },
     { text: "The app, in your browser (GitHub Pages)", options: { bold: true, color: AMBER, breakLine: true } },
     { text: "rander417.github.io/KeplerExoplanet", options: { color: TEXT } }], 13);
  s.addNotes("Title. The project began in 2020 as a four-person bootcamp capstone; this deck presents the 2026 refresh of Rich's fork: same questions, corrected science, modern tooling, and a shareable app. Everything quoted here comes from notebooks or scripts in the repository; the research log has the details.");
}

// ------------------------------------------------------------------ 2 Kepler in one slide
{
  const s = base("Kepler in one slide", "Kepler (2009-2018) watched ~150,000 stars in one patch of sky for periodic dips in brightness: transits. Each promising repeating dip is a Kepler Object of Interest. The NASA Exoplanet Archive's cumulative KOI table (9,564 rows) carries a verdict per KOI: CONFIRMED, CANDIDATE, or FALSE POSITIVE. Figure: our own sky map of the KOIs (notebook 01). Column definitions: exoplanetarchive.ipac.caltech.edu/docs/API_kepcandidate_columns.html");
  bullets(s, M, 1.4, 5.6, 4.6, [
    "A space telescope (2009–2018) that stared at ~150,000 stars in Cygnus and Lyra and measured their brightness continuously.",
    "The transit method: a planet crossing its star dims it slightly and regularly. Earth crossing the Sun would dim it by about 84 parts per million.",
    "A Kepler Object of Interest (KOI) is a repeating dip promising enough to track. The archive's cumulative table holds 9,564 of them, ids like K00752.01.",
    "Each KOI carries the archive's verdict: CONFIRMED (a real planet), CANDIDATE (plausible, unsettled) or FALSE POSITIVE (eclipsing stars, a neighbour's light, noise).",
    "This project asks how far the physics of the signal alone can predict that verdict, and which planets sit in their star's habitable zone.",
  ], 15);
  figure(s, `${FIG}/eda/field_of_view.png`, 6.9, 1.45, 5.7, 4.45, "The 9,564 KOIs on the sky, coloured by verdict (notebook 01)");
}

// ------------------------------------------------------------------ 3 three questions then and now
{
  const s = base("Three big questions — then and now", "The same three questions the 2020 deck asked. 2020 answers came from the bootcamp work; 2026 answers from the refreshed notebooks (03, 05, 07, 08). Numbers: physics-only macro f1 0.747 ± 0.012 on today's labels; 16 confirmed planets ≤ 2 Earth radii in the conservative Kopparapu zone; out-of-time AUC 0.937.");
  const cols = [
    ["I", "Is the KOI an exoplanet?", ["2020: 'GBT and Random Forest reach 90% f1' — with the vetting flags as features", "2026: the flags are the vetting; physics alone reaches macro f1 0.75. Honest, and still useful"], GREEN],
    ["II", "Is it in the habitable zone?", ["2020: 12 confirmed planets, chosen by orbital period and stellar properties", "2026: 16 small confirmed planets, chosen by the starlight they receive (Kopparapu et al. 2014). The two lists share none"], AMBER],
    ["III", "Can future observers use our models?", ["2020: a Flask app on Heroku (offline since 2022)", "2026: trained on 2020 labels, the model predicted later confirmations with AUC 0.937 — and the app runs in any browser"], PLUM],
  ];
  const cw = (W - 2 * M - 0.6) / 3;
  cols.forEach(([num, q, items, color], i) => {
    const x = M + i * (cw + 0.3);
    card(s, x, 1.45, cw, 5.1, CARD);
    s.addShape(pres.shapes.OVAL, { x: x + 0.3, y: 1.7, w: 0.6, h: 0.6, fill: { color }, line: { color } });
    s.addText(num, { x: x + 0.3, y: 1.7, w: 0.6, h: 0.6, fontFace: FONT, fontSize: 16, bold: true, color: BG, align: "center", valign: "middle", margin: 0 });
    s.addText(q, { x: x + 1.05, y: 1.65, w: cw - 1.3, h: 0.75, fontFace: FONT, fontSize: 17, bold: true, color: TEXT, margin: 0, valign: "middle" });
    bullets(s, x + 0.3, 2.65, cw - 0.6, 3.7, items, 14);
  });
}

// ------------------------------------------------------------------ 4 the data then and now
{
  const s = base("The data — a 2017-era snapshot and today's table", "Two sources, both tracked in data/raw with provenance: the Kaggle-era snapshot the 2020 team used (9,564 x 50) and a live pull of the archive's cumulative table via TAP on 2026-08-25 (9,564 x 153, SHA-256 recorded). Same KOIs, identical physics columns (koi_depth differs by rounding only); 925 verdicts (9.7%) changed. Notebook 08.");
  stat(s, M, 1.45, 3.6, "9,564", "KOIs in both tables — the same objects", TEXT, 36);
  stat(s, M, 2.9, 3.6, "925", "verdicts changed since the snapshot (9.7%)", AMBER, 36);
  stat(s, M, 4.35, 3.6, "0", "physics columns that changed (depth: rounding only)", GREEN, 36);
  bullets(s, 4.5, 1.5, 3.4, 4.6, [
    "2020 snapshot: the Kaggle copy of the archive table, 50 columns.",
    "2026 pull: the archive's TAP service, all 153 columns, provenance JSON with the query, time and hash.",
    "443 candidates were confirmed, 148 dismissed; 320 'false positives' became candidates again; 13 former false positives are confirmed planets today.",
    "One retraction: Kepler-503 b, CONFIRMED to FALSE POSITIVE.",
  ], 13);
  figure(s, `${FIG}/live/disposition_transitions.png`, 8.3, 1.45, 4.35, 4.85, "Verdict in 2020 (rows) versus today (columns)");
}

// ------------------------------------------------------------------ 5 two Ys revisited
{
  const s = base("A tale of two Ys, revisited — the flags are the answer key", "Two disposition columns: koi_pdisposition (pipeline, 2 classes) and koi_disposition (archive, 3 classes; the target). The four koi_fpflag_* columns are the pipeline's reasons for calling a false positive; any flag set predicts the pipeline verdict 98% of the time. Between the snapshot and today, the flags were rewritten wherever the verdict changed (koi_fpflag_nt changed on 347 rows, _ss 207, _co 133): the flags are outputs of vetting, not measurements. Figure: notebook 03, 5-fold CV.");
  bullets(s, M, 1.45, 5.3, 4.9, [
    "The 2020 models used the four koi_fpflag_* vetting flags as features. Any flag set means the pipeline already called it a false positive.",
    "Between 2020 and today the archive re-decided 925 KOIs — and rewrote the flags with the verdicts (320 'false positives' became candidates with their flags cleared).",
    "So a flag-fed model learns the vetting logic, not the planets: macro f1 0.86–0.87 with flags versus 0.72 on physics alone, same rows, same models.",
    "On today's labels the gap is wider still: 0.90 with flags, 0.75 without.",
    "The refresh reports both variants, always, and builds the app on physics only.",
  ], 14);
  figure(s, `${FIG}/models/macro_f1_by_feature_set.png`, 6.5, 1.5, 6.15, 3.2, "Same rows, same models, three feature sets (notebook 03, 5-fold CV)");
  card(s, 6.5, 5.15, 6.15, 1.2, CARD);
  para(s, 6.75, 5.3, 5.7, 0.95, [
    { text: "Rule of the refresh: ", options: { bold: true, color: AMBER } },
    { text: "never quote a single f1 without saying which variant — with flags (reproduces the vetting) or physics only (has to earn it).", options: { color: TEXT } }], 13);
}

// ------------------------------------------------------------------ 6 cleaning and EDA
{
  const s = base("Cleaning and EDA — the gaps are information", "2020 dropped the 363 rows with any null after removing the error columns. 2026 keeps all 9,564 rows: missingness tracks the label (most gaps sit in FALSE POSITIVEs), so the model gets 'is this value missing' indicators and a NaN-native gradient boosting. Gain over dropping rows was about 0.007 macro f1 — none — but the catalogue stays complete. Figures: notebook 01.");
  thenNow(s, M, 1.45, 5.6, 5.0,
    "2020", ["Dropped the ± error columns, then the 363 rows with any remaining null.", "Scaled everything and trained on a 75/25 split; scores quoted from one split.", "Imputation tried (mean, median, mode) and rejected — reasonable."],
    "2026", ["All 9,564 rows kept: the gaps are not random, they track the verdict (most sit in false positives).", "'Is this value missing' indicators + NaN-native boosting.", "Every number from 5-fold cross-validation with error bars; nested CV for tuning."], 13);
  figure(s, `${FIG}/eda/nulls_by_column.png`, 6.6, 1.5, 6.05, 2.4, "Missing values by column (notebook 01)");
  figure(s, `${FIG}/eda/class_balance.png`, 6.6, 4.7, 3.3, 1.45, "Class balance: the three verdicts");
  card(s, 10.2, 4.62, 2.45, 1.95, CARD);
  stat(s, 10.4, 4.72, 2.1, "+0.007", "macro f1 from keeping the incomplete rows — none, but the catalogue is whole", GREEN, 26);
}

// ------------------------------------------------------------------ 7 clustering
{
  const s = base("Clustering — a null result, recorded as one", "2020 ran k-means on the confirmed planets (elbow at 4, 'the data is homogeneous'). 2026 ran scaled k-means on all classes and scored the clusters against the verdicts: adjusted Rand index at or below 0.05 for every k. The clusters follow the heavy-tailed physics (depth, SNR, stellar radius), not the verdict. Notebook 02.");
  figure(s, `${FIG}/clustering/pca_map.png`, M, 1.45, 6.0, 4.4, "Scaled k-means on the physics, projected on two principal components (notebook 02)");
  thenNow(s, 6.9, 1.45, 5.75, 3.0,
    "2020", ["k-means on confirmed planets only, unscaled", "Elbow at 4 (3-D) and 6 (PCA); 'most of the data is consistent'"],
    "2026", ["All classes, log1p on the heavy tails, standardised", "Agreement with the verdicts: ARI ≤ 0.05, NMI ≈ 0 for every k"], 13);
  card(s, 6.9, 4.75, 5.75, 1.55, CARD);
  para(s, 7.15, 4.9, 5.3, 1.3, [
    { text: "What it means. ", options: { bold: true, color: AMBER } },
    { text: "Unsupervised structure in these twelve measurements does not line up with what the archive decided. That is a finding, not a failure — it is why the supervised models earn their keep.", options: { color: TEXT } }], 13);
}

// ------------------------------------------------------------------ 8 models re-labelled
{
  const s = base("The models, re-labelled", "The 2020 deck quoted 83 / 90 / 90 / 84 '% f1'. Those were accuracy and weighted f1 on one split; macro f1 (the balanced number) was 0.77 / 0.87 / 0.87 / 0.79, with the flags. On physics only the same models drop to 0.53 / 0.71 / 0.72. The tuned HistGradientBoosting with nested CV on all rows: 0.722 ± 0.006 on snapshot labels, 0.747 ± 0.012 on today's labels. The physics-only ceiling is about 0.72–0.75 in every construction. Table: reports/tables/03_baseline_metrics.csv and 07_models_v2_metrics.csv.");
  const rows = [
    [{ text: "Model", options: { bold: true, color: AMBER } }, { text: "2020 deck said", options: { bold: true, color: AMBER } }, { text: "macro f1, with flags", options: { bold: true, color: AMBER } }, { text: "macro f1, physics only", options: { bold: true, color: AMBER } }],
    ["Logistic regression", "83% f1", "0.768 ± 0.014", "0.527 ± 0.006"],
    ["Gradient boosting (2020 settings)", "90% f1", "0.866 ± 0.009", "0.715 ± 0.015"],
    ["Balanced random forest", "90% f1", "0.867 ± 0.005", "0.715 ± 0.003"],
    ["Deep neural net (2020, Keras)", "84% f1", "0.79 (one split)", "not run yet — Phase 4"],
    [{ text: "Tuned boosting, all rows, nested CV", options: { bold: true } }, "—", "0.862 ± 0.006", { text: "0.722 ± 0.006 (snapshot labels)\n0.747 ± 0.012 (today's labels)", options: { bold: true, color: GREEN } }],
  ].map((r) => r.map((c) => (typeof c === "string" ? { text: c, options: { color: TEXT } } : c)));
  s.addTable(rows, { x: M, y: 1.5, w: W - 2 * M, colW: [3.6, 2.2, 2.9, 3.43], fontFace: FONT, fontSize: 13, color: TEXT, fill: { color: CARD }, border: { type: "solid", color: BG, pt: 2 }, rowH: 0.5, valign: "middle", margin: 0.08 });
  para(s, M, 4.75, W - 2 * M, 0.35, "The 2020 deck's '83 / 90 / 90 / 84% f1' were accuracy and weighted f1 on one 75/25 split; macro f1 is the balanced number. Error bars: 5-fold cross-validation.", 11, MUTED);
  card(s, M, 5.2, 6.0, 1.25, CARD2);
  para(s, M + 0.25, 5.33, 5.5, 1.05, [
    { text: "Why 'macro'? ", options: { bold: true, color: AMBER } },
    { text: "It averages the three verdicts' f1 equally, so the rare class counts as much as the common one. Accuracy and weighted f1 flatter a model that is good at the big class.", options: { color: TEXT } }], 12);
  card(s, 6.9, 5.2, 5.75, 1.25, CARD2);
  para(s, 7.15, 5.33, 5.3, 1.05, [
    { text: "The physics-only ceiling ", options: { bold: true, color: AMBER } },
    { text: "sits at 0.72–0.75 in every construction we tried: different models, all rows, tuning on inner folds, calibration. Confirmation is a follow-up process; the physics cannot see it.", options: { color: TEXT } }], 12);
}

// ------------------------------------------------------------------ 9 calibration and rule
{
  const s = base("Probabilities you can take literally, and a rule you can read", "Isotonic calibration on out-of-fold scores lowers log loss 0.534 to 0.512 and Brier 0.315 to 0.297 on today's labels; its argmax lowers macro f1 slightly, so the app shows probabilities and decides labels by an explicit rule (kepler.verdict). Out-of-fold rule metrics: macro f1 0.744; per class CANDIDATE 0.55, CONFIRMED 0.84, FALSE POSITIVE 0.84; P(planet-like) AUC 0.921; at 0.5 precision 0.848 / recall 0.823. Figure: notebook 07 reliability.");
  figure(s, `${FIG}/models/reliability_physics_only.png`, M, 1.45, 7.4, 2.5, "Reliability of the physics-only model, before and after calibration (notebook 07)");
  card(s, 8.4, 1.45, 4.25, 2.6, CARD);
  para(s, 8.65, 1.6, 3.8, 2.4, [
    { text: "The label rule", options: { bold: true, color: AMBER, breakLine: true } },
    { text: "P(planet-like) = P(CANDIDATE) + P(CONFIRMED)", options: { color: TEXT, breakLine: true } },
    { text: "below 0.5 → FALSE POSITIVE", options: { color: TEXT, breakLine: true } },
    { text: "otherwise → the larger of CONFIRMED / CANDIDATE", options: { color: TEXT, breakLine: true } },
    { text: "The threshold is a slider in the app; no hidden argmax.", options: { color: MUTED } }], 13);
  stat(s, M, 4.45, 2.9, "0.84 / 0.55 / 0.84", "f1 for CONFIRMED / CANDIDATE / FALSE POSITIVE (out-of-fold, today's labels)", TEXT, 24);
  stat(s, 3.9, 4.45, 2.6, "0.921", "AUC, planet-like vs false positive", GREEN, 32);
  stat(s, 6.9, 4.45, 2.9, "0.534 → 0.512", "log loss, before → after calibration", AMBER, 24);
  stat(s, 10.2, 4.45, 2.5, "0.85 / 0.82", "precision / recall for 'planet-like' at 0.5", TEXT, 24);
  para(s, M, 6.05, W - 2 * M, 0.6, "Physics separates planets from false positives well; it separates confirmed from candidate only moderately — confirmation is a follow-up-and-statistics process, not a measurement.", 12, MUTED);
}

// ------------------------------------------------------------------ 10 what matters
{
  const s = base("What the physics-only model actually looks at", "Permutation importance on the out-of-fold physics-only model (notebook 07): transit signal-to-noise 0.166, orbital period 0.089, planet radius 0.089, transit duration 0.073 (drop in macro f1 when the column is shuffled). No flags, no koi_score, no koi_pdisposition anywhere in the inputs.");
  figure(s, `${FIG}/models/permutation_importance_physics_only.png`, M, 1.45, 6.6, 4.0, "Permutation importance, physics-only model (notebook 07)");
  bullets(s, 7.6, 1.5, 5.05, 4.9, [
    "Transit signal-to-noise leads by a wide margin: a clean, deep, repeated dip is the strongest single clue.",
    "Orbital period and planet radius come next: very large 'planets' and very short periods are mostly eclipsing stars.",
    "Transit duration and impact parameter carry shape information: grazing crossings and V-shaped dips point to stars, not planets.",
    "Stellar temperature, gravity and radius matter less on their own — the planet radius already folds the star's size in.",
    "Twelve columns, all measurable from the light curve and the star: nothing that encodes a human's verdict.",
  ], 14);
}

// ------------------------------------------------------------------ 11 out-of-time
{
  const s = base("The out-of-time test — question III, answered honestly", "Train the physics-only model on the 2020 labels only (out-of-fold), score the 2,248 KOIs that were candidates in 2020, and compare with what the archive decided later: 443 confirmed, 148 dismissed, 1,657 still open. Median P(planet-like): 0.946 for the later-confirmed, 0.826 for the still-open, 0.257 for the later-dismissed. AUC 0.937. The flags could not have passed this test: they were rewritten with the verdicts. Notebook 08.");
  figure(s, `${FIG}/live/out_of_time_candidates.png`, M, 1.45, 7.0, 4.0, "What the 2020-trained model thought of the 2020 candidates, split by what happened next (notebook 08)");
  stat(s, 8.0, 1.45, 4.6, "AUC 0.937", "later-confirmed vs later-dismissed, on verdicts the model never saw", GREEN, 40);
  card(s, 8.0, 3.0, 4.65, 3.4, CARD);
  bullets(s, 8.25, 3.15, 4.2, 3.2, [
    "2,248 KOIs were CANDIDATEs in 2020. Since then the archive confirmed 443 and dismissed 148.",
    "The model, trained on 2020 labels, had rated the later-confirmed ones far more planet-like (median 0.95) than the later-dismissed ones (median 0.26).",
    "That is a forecast checked against the future — the closest thing to 'can future observers use this?'",
    "The vetting flags could not have passed this test: they were rewritten along with the verdicts.",
  ], 13);
}

// ------------------------------------------------------------------ 12 habitable zone
{
  const s = base("The habitable zone, done on insolation", "2020 filtered on orbital period (200-400 d), stellar temperature (5,500-6,500 K), radius, gravity and metallicity: star properties, never the planet's insolation, and 'super-Earth' meant the gas giants pictured on the 2020 slide. 2026 uses the Kopparapu et al. 2014 (ApJL 787, L29) stellar-temperature-dependent insolation limits and the Rogers 2015 (ApJ 801, 41) 1.6 Earth-radius rocky ceiling (2.0 loose). Today's table: 16 confirmed planets ≤ 2 R⊕ in the conservative zone (9 ≤ 1.6), 25 in the optimistic zone, 65 candidates ≤ 2 R⊕ in the conservative zone. The 2020 list of 12 shares none. Caveat: the KOI table's stellar parameters are DR25; Kepler-1649 c (Vanderburg et al. 2020) sits outside and Kepler-1649 b (an exo-Venus, Angelo et al. 2017) inside on those numbers. Notebooks 05 and 08.");
  figure(s, `${FIG}/habitable_zone/hz_diagram_confirmed.png`, M, 1.4, 8.3, 3.6, "Circled: confirmed planets ≤ 2 R⊕ in the conservative zone (notebook 05; today's table adds Kepler-1652 b)");
  stat(s, 9.3, 1.4, 3.4, "16", "confirmed planets ≤ 2 R⊕ in the conservative zone today (9 of them ≤ 1.6 R⊕, plausibly rocky)", GREEN, 44);
  stat(s, 9.3, 3.05, 3.4, "0 of 12", "of the 2020 list survive: period and star properties are not the planet's climate", PLUM, 30);
  card(s, M, 5.6, W - 2 * M, 1.05, CARD);
  para(s, M + 0.25, 5.7, W - 2 * M - 0.5, 0.9, [
    { text: "Method. ", options: { bold: true, color: AMBER } },
    { text: "Kopparapu et al. 2014 give the insolation at which a rocky planet loses its water (runaway greenhouse) or freezes (maximum greenhouse) as a function of the star's temperature; Rogers 2015 finds most planets above 1.6 R⊕ are not rocky. Caveat: the table's stellar parameters are Kepler DR25 — Kepler-1649 c sits outside and its exo-Venus sibling 1649 b inside on those numbers. A screen, not a verdict.", options: { color: TEXT } }], 12);
}

// ------------------------------------------------------------------ 13 the app
{
  const s = base("The app — one file, three ways to run it", "app/app.py runs locally (run_app.cmd), on Streamlit Community Cloud, and inside the visitor's browser via stlite on GitHub Pages: Python compiled to WebAssembly, static files, no server, nothing installed. The trained model ships as plain numbers (trees + calibration maps) evaluated with numpy; a test proves it reproduces scikit-learn's probabilities exactly. Every catalogue probability is out-of-fold. Default KOI: Kepler-452 b, where the model says 50/50 — in line with Mullally et al. 2018 (AJ 155, 210), who argue it 'should be considered a candidate planet'.");
  figure(s, `${FIG}/app/catalogue_light.png`, M, 1.4, 4.3, 3.22, "Catalogue: filter, plot, download");
  figure(s, `${FIG}/app/explorer_dark.png`, 5.15, 1.4, 4.3, 3.22, "KOI explorer, dark mode: probabilities and what-if sliders");
  bullets(s, 9.75, 1.4, 2.95, 3.9, [
    "Five tabs: Catalogue, KOI explorer, Habitable zone, Model & honesty, About.",
    "Runs locally, on Streamlit Community Cloud, or entirely in your browser (GitHub Pages).",
    "The model travels as plain numbers and is evaluated with numpy — the same model everywhere.",
    "Plain-language help on every control; light and dark themes.",
  ], 12);
  card(s, M, 5.55, W - 2 * M, 1.05, CARD);
  para(s, M + 0.25, 5.67, W - 2 * M - 0.5, 0.9, [
    { text: "Try Kepler-452 b. ", options: { bold: true, color: AMBER } },
    { text: "The archive says CONFIRMED; the physics-only model says 50/50. Mullally et al. 2018 argued the planet 'can not be confirmed using a purely statistical validation approach'. Sometimes a coin flip is the honest answer.", options: { color: TEXT } }], 12);
}

// ------------------------------------------------------------------ 14 what we learned
{
  const s = base("What we learned", "Five takeaways. Each is backed by a notebook and a research-log entry in the repository.");
  const items = [
    ["Leakage settles arguments", "The vetting flags were rewritten with the verdicts. Any score that uses them is a score for copying.", PLUM],
    ["The ceiling is real", "Physics alone tops out near 0.75 macro f1 in every construction. Confirmation is a process the measurements cannot see.", AMBER],
    ["Forecasts beat fits", "Trained on 2020, the model predicted the archive's later confirmations with AUC 0.937. That is the number to trust.", GREEN],
    ["Ask the planet, not the star", "Habitable-zone screens belong on insolation with temperature-dependent limits. The 2020 list of 12 had zero survivors.", AMBER_D],
    ["Reproducibility is the deliverable", "Locked environment, tracked data with hashes, 41 tests, every number regenerable — and an app anyone can open.", TEXT],
  ];
  items.forEach(([h, t, color], i) => {
    const y = 1.4 + i * 1.0;
    card(s, M, y, W - 2 * M, 0.88, i % 2 ? CARD2 : CARD);
    s.addShape(pres.shapes.OVAL, { x: M + 0.25, y: y + 0.22, w: 0.44, h: 0.44, fill: { color }, line: { color } });
    s.addText(String(i + 1), { x: M + 0.25, y: y + 0.22, w: 0.44, h: 0.44, fontFace: FONT, fontSize: 13, bold: true, color: BG, align: "center", valign: "middle", margin: 0 });
    s.addText(h, { x: M + 0.95, y: y + 0.1, w: 3.3, h: 0.7, fontFace: FONT, fontSize: 16, bold: true, color: TEXT, margin: 0, valign: "middle" });
    s.addText(t, { x: M + 4.4, y: y + 0.1, w: W - 2 * M - 4.7, h: 0.7, fontFace: FONT, fontSize: 13, color: MUTED, margin: 0, valign: "middle" });
  });
}

// ------------------------------------------------------------------ 15 tech, credits, references
{
  const s = base("Tools, credits, references", "Tooling: uv-locked Python 3.12, pandas, scikit-learn 1.9, plotly, Streamlit, stlite on GitHub Pages, Obsidian vault in the repo, pytest (41 tests), ruff. The refresh was built as a tag team: Claude in Cowork authored notebooks, code and notes; Claude Code committed, tested and pushed on Rich's machine; Rich set direction and reviewed. 2020 team credited. References verified 2026-08-24/25.");
  card(s, M, 1.4, 4.0, 5.0, CARD);
  para(s, M + 0.25, 1.55, 3.5, 4.7, [
    { text: "Tools", options: { bold: true, color: AMBER, breakLine: true } },
    { text: "Python 3.12 · uv (locked environment)", options: { breakLine: true } },
    { text: "pandas · numpy · scikit-learn 1.9", options: { breakLine: true } },
    { text: "plotly · matplotlib · Streamlit", options: { breakLine: true } },
    { text: "stlite (Streamlit in the browser) · GitHub Pages", options: { breakLine: true } },
    { text: "NASA Exoplanet Archive TAP service", options: { breakLine: true } },
    { text: "pytest (41 tests) · ruff · JupyterLab", options: { breakLine: true } },
    { text: "Obsidian vault inside the repository", options: { breakLine: true } },
    { text: " ", options: { breakLine: true, fontSize: 6 } },
    { text: "How it was built", options: { bold: true, color: AMBER, breakLine: true } },
    { text: "A tag team: Claude (Cowork) authored notebooks, code and notes; Claude Code tested, committed and pushed; Rich set direction and reviewed every batch.", options: { color: MUTED } }], 14, TEXT);
  card(s, 4.9, 1.4, 7.75, 5.0, CARD2);
  para(s, 5.15, 1.55, 7.25, 4.7, [
    { text: "References", options: { bold: true, color: AMBER, breakLine: true } },
    { text: "Kopparapu, R. K. et al. 2014, ApJL 787, L29 — habitable-zone insolation limits vs stellar temperature (arXiv:1404.5292)", options: { breakLine: true } },
    { text: "Rogers, L. A. 2015, ApJ 801, 41 — 'the majority of 1.6 Earth-radius planets are too low density to be comprised of Fe and silicates alone' (arXiv:1407.4457)", options: { breakLine: true } },
    { text: "Mullally, F. et al. 2018, AJ 155, 210 — Kepler-452 b 'should be considered a candidate planet' (arXiv:1803.11307)", options: { breakLine: true } },
    { text: "Vanderburg, A. et al. 2020, ApJL 893, L27 — Kepler-1649 c, rescued from false-positive status (arXiv:2004.06725)", options: { breakLine: true } },
    { text: "Angelo, I. et al. 2017, AJ 153, 162 — Kepler-1649 b, an exo-Venus (arXiv:1704.03136)", options: { breakLine: true } },
    { text: "NASA Exoplanet Archive — KOI cumulative table, column definitions and TAP service", options: { breakLine: true } },
    { text: " ", options: { breakLine: true, fontSize: 6 } },
    { text: "Credits", options: { bold: true, color: AMBER, breakLine: true } },
    { text: "2020 team (Columbia Engineering data-analytics bootcamp): Rich Anderson — ML pipeline; Damien Corr, Priscilla Lin, Tom Greff. Original repo: tom-jj-G/KeplerExoplanets. 2026 refresh: Rich Anderson with Claude.", options: { color: MUTED, breakLine: true } },
    { text: "An educational analysis of public data, not a product of NASA or the Exoplanet Archive. Verdicts are the archive's; probabilities are ours.", options: { color: MUTED, italic: true } }], 13, TEXT);
}

pres.writeFile({ fileName: OUT }).then((f) => console.log("wrote", f));
