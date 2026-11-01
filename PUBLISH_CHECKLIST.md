# SLIMEROUTE publication checklist

1. Upload **this v4.1 public-release package** to a GitHub repository. Historical assets are explicitly labeled; do not mix them into the current post. Check that `INTEGRITY.sha256` matches all tracked files.
2. Confirm GitHub shows the current `README.md`, `AUDIT_REPORT.md`, `requirements.txt`, source, tests and data attribution.
3. Check GitHub Actions for green tests. Locally: `python -m pytest -q tests` and `python scripts/prepublish_check.py`.
4. Use `out/slime_india_v4.mp4` as the video. Do **not** use `out/slime_india.mp4`, `out/claude_original_slime_india.mp4`, or `out/slime_vs_schematic.png` as the headline real-rail comparison.
5. Paste `LINKEDIN_POST.md` and replace its placeholder with the **actual repository URL**. Do not publish a placeholder link.
6. Review LinkedIn's video preview, spelling, first frame, legibility on mobile, and the post link before publishing.
7. Keep the description scoped: 16-city computational model, approximate terrain, third-party rail-cell proximity, different denominators for 89% and 18%, and static damage scenarios.
8. If asked: the 10 seeds reflect growth variation, the 250 scenarios are *static* failures, and the 2010 study is prior research.

**Not claimed:** originality of the Physarum algorithm; real-world Indian Railways reconstruction; superiority to rail infrastructure; production-ready transport planning; actual biological experiment.
