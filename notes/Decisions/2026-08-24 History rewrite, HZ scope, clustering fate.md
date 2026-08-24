---
tags: [decision, security, habitable-zone, clustering]
date: 2026-08-24
status: accepted
---

# 2026-08-24 History rewrite, HZ scope, clustering fate

> [!abstract] Three calls Rich made after the Phase 2 review
> 1. **Rewrite git history** to purge the 2020 database password and swap Rich's private email for his GitHub noreply alias.
> 2. **Habitable-zone scope: all host stars**, with a `sunlike_host` flag column for the 2020-style view.
> 3. **Clustering notebook stays as a null-result notebook.**

## 1. History rewrite

> [!danger] What and why
> A 12-character Postgres password and the AWS RDS endpoint were committed on 2020-10-30 (`359e7de`, *pre-rewrite hash*) and stayed in the tracked tree until batch #2 redacted `archive/database/Connect to AWS postgres.ipynb`. The repo is public. Separately, GitHub's GH007 email-privacy block rejected the first push of the refresh because the new commits carry Rich's private address.

**Decision.** One `git filter-repo` pass on Rich's machine, run by Claude Code with Rich's explicit typed approval ("go B" / "follow your recommendations", 2026-08-24):
- `--replace-text`: the literal password → `[REDACTED-2020-DB-PASSWORD]` in every blob of every commit.
- `--mailmap`: `rich417@gmail.com` → Rich's GitHub noreply address, for every author, committer, and tagger. Teammates' addresses untouched.
- Force-push `main`, `refresh-2026`, and the tag `v1-bootcamp-2020`; re-add the remote; set the repo's `user.email` to the noreply address.
- Keep a bundle backup of the pre-rewrite repo outside the working folder, and commit filter-repo's `commit-map` into `notes/Decisions/` so old hashes cited in the notes stay resolvable.

**Consequences.**
- Every commit hash changes. Hashes quoted in notes dated on or before 2026-08-24 (`9d601d1`, `6dbc107`, `e21f734`, `359e7de`, `c4fcfdb`, `b67a3cc`, …) are pre-rewrite; look them up in the commit map.
- Cowork's cloud clone must be re-cloned; anyone else's clone must be re-cloned too.
- GitHub may keep the old commits reachable by direct URL until its garbage collection runs; GitHub's guidance (["Removing sensitive data from a repository"](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository), link not re-opened this session) is that only GitHub Support can purge cached views, and that forks keep their own copies. The original team repo (`tom-jj-G/KeplerExoplanets`) is outside our control.
- The password should be treated as burned regardless: if it was ever reused, change it.

**Alternative rejected.** Uncheck GitHub's email block and push as-is, leaving the password in history. Simpler, but it leaves a live credential pattern in a public repo that we now know about.

## 2. Habitable-zone host-star scope

**Decision.** Screen every host star. Add `sunlike_host` (5,500–6,500 K) as a boolean column so the "another Earth around another Sun" view remains a filter, not a hidden assumption.

**Why.** The review found 12 of the 13 confirmed planets that sit inside a flat insolation habitable zone with radius ≤ 2 R⊕ orbit stars cooler than 5,500 K; the 2020 temperature window excluded essentially the entire real result. Kepler's temperate small planets live around K and M dwarfs because their habitable zones are close in and transits are frequent.

## 3. Clustering notebook

**Decision.** Keep `notebooks/02_clustering.ipynb`, rewritten as a short null-result notebook: scaled features, all three classes included, k chosen by a stated criterion, and the cluster-vs-disposition agreement reported (ARI/NMI). Its conclusion is expected to be "no natural groupings track the dispositions", which answers the 2020 question "Does EDA reveal interesting groupings?" honestly.

**Alternative rejected.** Archive it. That would drop the question rather than answer it.
