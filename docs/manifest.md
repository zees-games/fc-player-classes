`classes.json` lists Fatal Contact's player classes. `tools/models.py check` validates it, and CI runs that check on every push.

## Top level

| Key | Meaning |
|---|---|
| `schema` | Always `1`. |
| `game` | The game repo the classes belong to (`game-fatal-contact`). |
| `store.id` | The CDN pack id in `content.lock.json` (`gamemann/fc-player-classes`). |
| `store.into` | The folder the fetch writes into (`assets/models`). |
| `store.lock` | The lock file that pins the pack version and manifest hash. |
| `store.prod_asset` | The prod store asset id (152). |
| `classes` | One entry per class, as below. |

## Class entry

| Key | Meaning | Checked |
|---|---|---|
| `id` | Class id, unique. | unique |
| `display_name`, `description` | UI text. | present |
| `team`, `side` | FC team number (1 or 2) and the side letter it maps to. Each team has one class. | team unique |
| `body_id` | FC's team body id. FC registers bodies by file name, so the model file is `<body_id>.glb`. | `model.file` matches |
| `credits` | The section of CREDITS.md and the row of `assets/models/licence.json`. | present |
| `model.file`, `model.bytes`, `model.sha256` | The desktop GLB and its pinned size and hash. | pinned; `--files` re-hashes |
| `model.web_file`, `model.web_bytes`, `model.web_sha256` | The same body with WebP textures, for web builds. | pinned; `--files` re-hashes |
| `lods` | `[{name, tris}]` in order `LOD0`, `LOD1`, ... These are the mesh names inside the GLB. | order |
| `skeleton` | `rig` (`gs-player-char kit`), `bones`, `height_m`, and `prep_config`: the gs-player-char avatar prep config that built the body. | present |
| `arms` | First-person arms: `source` (`body` means cut from the body mesh) and `forearm_ratio` (the kit_rig forearm stretch, or `null`). | present |
| `stats` | `health`, `speed`, `sprint_speed_scale`, `jump_scale`. These are stubs at FC's defaults; FC does not read them yet. | keys |
| `loadout.spawn`, `loadout.bot_preferred` | fc-weapons ids. | against fc-weapons `IDS` when a checkout is beside this one or given with `--weapons DIR` |

CI has no fc-weapons checkout, so it skips the loadout-id check and says so in its output line.
