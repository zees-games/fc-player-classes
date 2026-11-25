Fatal Contact's player classes: a manifest, credits and tools. The models are on the CDN.

- Never commit model files. `assets/models/` is ignored except `licence.json`. Fetch with `./fetch-content.sh`.
- `classes.json` is the source of truth. Run `python3 tools/models.py check` after every edit, and add `--files` when models are staged.
- A new body: prepare it in gs-player-char (`tools/avatar_prep`), then `stage`, `pin`, `tools/publish.sh <version>` (docs/models.md). Commit the manifest and `content.lock.json` together, and add the credits to CREDITS.md, both `licence.json` files and the README table.
- Dev publishes come first (`GS_SITE=https://tmcdev.net`, `X.Y.Z-dev.N`). Prod is store asset 152. Public docs carry no dev ids.
- No H1 in the README; keep it as tables. Re-shoot `docs/img/` when a body changes.
- Leftover work goes on Nightly under the fc-player-classes project.
