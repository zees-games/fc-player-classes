How a class body goes from a source model to the CDN. The source models are private and never committed. The recipe lives in gs-player-char's `tools/avatar_prep/`, and its `docs/avatar-prep.md` explains the numbers.

## 1. Prepare

| Step | Command (from gs-player-char) | Output |
|---|---|---|
| Slim, rename bones, cut hidden skin, decimate to the LOD budgets | `blender -b --factory-startup --python tools/avatar_prep/prep_avatar.py -- tools/avatar_prep/<name>.json <source.glb> <out>` | `<out>/<name>_lod0..2.glb`, fp arms |
| Re-rig onto the kit skeleton, one GLB with meshes `LOD0`..`LOD2` | `blender -b --factory-startup --python tools/avatar_prep/kit_rig.py -- <kit body.glb> <out> <name> tools/avatar_prep/<name>.json` | `<out>/<name>_kit.glb`, `<out>/<name>_kit.webp.glb` |
| Render the LOD lineup for review | `blender -b --python tools/avatar_prep/render.py -- <out> <name> <png prefix>` | `<prefix>_tex.png`, `<prefix>_gib.png` |

`docs/img/*_lods.jpg` are crops of the `_tex.png` renders. Re-shoot them whenever a body changes.

## 2. Stage, pin, publish

| Step | Command (from this repo) |
|---|---|
| Copy the kit GLBs in under the manifest's file names | `python3 tools/models.py stage <out>` |
| Write sizes and hashes into `classes.json` | `python3 tools/models.py pin` |
| Check everything, including the staged files | `python3 tools/models.py check --files` |
| Publish to the store and rewrite `content.lock.json` | `tools/publish.sh <version> --token-file <creator token>` |

`tools/publish.sh` runs the check first, then gs-cloud's `publish_pack.sh` (set `GS_CLOUD` when gs-cloud is not beside this repo). Use `X.Y.Z-dev.N` versions on the dev site. Commit `classes.json` and `content.lock.json` together.

## 3. How Fatal Contact uses them

FC looks up each team body by file name, `<body_id>.glb`, in its team-body folders. It chooses the bodies with the `team_bodies` setting (`fc_swat,fc_military`). The kit skeleton means FC's people clips, aim, crouch and gib roles work on these bodies unchanged. Until FC fetches this pack itself, put the fetched files in one of its team-body folders.
