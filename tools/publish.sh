#!/bin/bash
# Publishes the staged bodies in assets/models/ to the gs-cloud CDN as a store and pins it in content.lock.json.
#   tools/models.py stage <prep output dir>...    # copy the prepared kit GLBs in under the manifest's names
#   tools/models.py pin                           # record bytes + sha256 in classes.json
#   tools/publish.sh VERSION [publish_pack.sh flags, e.g. --lock FILE --token-file F --dry-run]
# gs-cloud is the checkout beside this one, or GS_CLOUD. Site: GS_SITE (dev: https://tmcdev.net), else publish_pack.sh's default. A dev publish uses a -dev.N version.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
V=${1:?usage: tools/publish.sh VERSION [flags]}; shift
python3 "$HERE/tools/models.py" check --files
exec "${GS_CLOUD:-$HERE/../gs-cloud}/tools/publish_pack.sh" publish --source "$HERE/assets/models" --id fc-player-classes --version "$V" \
    --kind store --into assets/models --no-import --name "FC Player Classes" --lock "$HERE/content.lock.json" "$@"
