#!/usr/bin/env bash
# ==============================================================================
# AXIS-NIDDHI - create_bilingual_review_snapshot.sh
# ==============================================================================
# Canonical bilingual review flow (single-command operator workflow):
#   1) Validate/seal bilingual CSL in LAB
#   2) Freeze approved bilingual CSL snapshot
#   3) Create clean review workspace (/beng-release baseline)
#   4) Overlay frozen bilingual snapshot into review workspace
#   5) Execute SD-only in review workspace (no SG/SP/SA)
#   6) Verify CSL immutability during review build
#
# Non-negotiables preserved:
#   - CSL remains source of truth
#   - Review build is derived
#   - No CSL mutation during review
#   - No external translation restore dependency in review
# ==============================================================================

set -euo pipefail

GREEN='\033[0;32m'
CYAN='\033[0;96m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;37m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

LAB_ROOT_DEFAULT="$(cd "$(dirname "$0")/../../.." && pwd)"
LAB_ROOT="${LAB_ROOT:-$(cd "$(dirname "$0")/../../.." && pwd)}"

REVIEW_ROOT_DEFAULT="$LAB_ROOT_DEFAULT/review"
REVIEW_ROOT="${REVIEW_ROOT:-$LAB_ROOT/review}"
SNAPSHOT_ROOT_DEFAULT="$LAB_ROOT_DEFAULT/snapshots"
SNAPSHOT_ROOT="$SNAPSHOT_ROOT_DEFAULT"
SNAP_TAG="bilingual_review_$(date -u +%Y%m%dT%H%M%SZ)"
FORCE=false
SKIP_LAB_VALIDATION=false
SOURCES_MODE="reference"
ALLOW_TMP_HEAVY=false
COMPACT_LONG_LOGS="${COMPACT_LONG_LOGS:-0}"
COMPACT_FIRST_LINES="${COMPACT_FIRST_LINES:-20}"
ENABLE_FINAL_CLEAR="${ENABLE_FINAL_CLEAR:-0}"
FINAL_PAUSE_SECONDS="${FINAL_PAUSE_SECONDS:-1}"
MIN_HEAVY_FREE_GIB="${MIN_HEAVY_FREE_GIB:-20}"

usage() {
    cat <<EOF
Usage:
  bash create_bilingual_review_snapshot.sh [options]

Options:
  --lab-root <path>          LAB root (default: $LAB_ROOT_DEFAULT)
  --review-root <path>       Review workspace root (default: $REVIEW_ROOT_DEFAULT)
  --snapshot-root <path>     Snapshot root base (default: $SNAPSHOT_ROOT_DEFAULT)
  --snapshot-tag <tag>       Snapshot tag (default: bilingual_review_<utc>)
  --force                    Overwrite existing snapshot tag if present
  --skip-lab-validation      Skip LAB seal/validation stage
  --include-sources          Copy source ZIP into snapshot/review sources
  --sealed-full-copy         Same as --include-sources; explicit archival mode
  --allow-tmp-heavy          Allow copy/sealed mode under /tmp (still checks free space)
  -h, --help                 Show this help

Notes:
  - This script intentionally runs SD-only in review workspace.
  - build_release_snapshot_v2.sh must use LAB_ROOT/REVIEW_ROOT env defaults.
  - COMPACT_LONG_LOGS=1 enables optional condensed terminal view for repetitive logs.
  - COMPACT_FIRST_LINES controls visible repetitive lines before collapsing (default: 20).
  - ENABLE_FINAL_CLEAR=1 clears terminal before ceremonial close (default: 0).
  - FINAL_PAUSE_SECONDS adds a small pause before final close (default: 1).
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --lab-root)
            LAB_ROOT="$2"; shift 2 ;;
        --review-root)
            REVIEW_ROOT="$2"; shift 2 ;;
        --snapshot-root)
            SNAPSHOT_ROOT="$2"; shift 2 ;;
        --snapshot-tag)
            SNAP_TAG="$2"; shift 2 ;;
        --force)
            FORCE=true; shift ;;
        --skip-lab-validation)
            SKIP_LAB_VALIDATION=true; shift ;;
        --include-sources|--sealed-full-copy)
            SOURCES_MODE="copy"; shift ;;
        --allow-tmp-heavy)
            ALLOW_TMP_HEAVY=true; shift ;;
        -h|--help)
            usage; exit 0 ;;
        *)
            echo -e "${RED}[FAIL] Unknown argument: $1${NC}" >&2
            usage
            exit 1 ;;
    esac
done

LAB_PIPELINE="$LAB_ROOT/pipeline"
LAB_CORE="$LAB_PIPELINE/scripts/core"
LAB_TOOLS="$LAB_PIPELINE/scripts/tools"
LAB_SOURCES="$LAB_ROOT/sources"

REVIEW_PIPELINE="$REVIEW_ROOT/pipeline"
REVIEW_SCRIPTS="$REVIEW_PIPELINE/scripts"
LAB_WORDPRESS_UPLOADS="$LAB_ROOT/wordpress/wp-content/uploads"

SNAP_ROOT="$SNAPSHOT_ROOT/$SNAP_TAG"
BUILD_RELEASE_SCRIPT="$LAB_TOOLS/build_release_snapshot_v2.sh"
SESSION_LOG_DIR="$LAB_ROOT/logs/review-build/$SNAP_TAG"
SUMMARY_REPORT="$REVIEW_ROOT/review_build_summary.md"

ok()   { echo -e "${GREEN}[OK] $*${NC}"; }
info() { echo -e "\n${CYAN}=== $* ===${NC}"; }
WARNINGS=()
warn() {
    WARNINGS+=("$*")
    echo -e "${YELLOW}[WARN] $*${NC}"
}
fail() { echo -e "${RED}[FAIL] $*${NC}" >&2; exit 1; }

need_file() {
    local f="$1"
    [[ -f "$f" ]] || fail "Missing file: $f"
}

need_dir() {
    local d="$1"
    [[ -d "$d" ]] || fail "Missing directory: $d"
}

tree_hash() {
    local dir="$1"
    (
        cd "$dir"
        find . -type f -print0 \
            | sort -z \
            | xargs -0 sha256sum \
            | sha256sum \
            | awk '{print $1}'
    )
}

existing_parent_for_df() {
    local path="$1"

    while [[ ! -e "$path" && "$path" != "/" ]]; do
        path="$(dirname "$path")"
    done

    printf '%s\n' "$path"
}

check_heavy_target_safety() {
    local target_path="$1"
    local target_label="$2"
    local recommended_root="$3"
    local probe_path avail_kb mount_point avail_gib
    local min_heavy_free_kb=$((MIN_HEAVY_FREE_GIB * 1024 * 1024))

    [[ "$SOURCES_MODE" == "copy" ]] || return 0

    if [[ "$target_path" == /tmp || "$target_path" == /tmp/* ]]; then
        if ! $ALLOW_TMP_HEAVY; then
            fail "Copy/sealed mode refuses ${target_label} under /tmp by default. Use a larger filesystem such as $recommended_root or another <large-volume>/axis-review-tests path. If you really want to force /tmp, re-run with --allow-tmp-heavy."
        fi
        warn "Heavy copy mode was explicitly allowed under /tmp for ${target_label} via --allow-tmp-heavy."
    fi

    probe_path="$(existing_parent_for_df "$target_path")"
    read -r avail_kb mount_point < <(df -Pk "$probe_path" | awk 'NR==2 {print $4, $6}')
    avail_gib="$(awk -v kb="$avail_kb" 'BEGIN {printf "%.1f", kb / 1024 / 1024}')"

    if [[ "$mount_point" == "/" && "$avail_kb" -lt "$min_heavy_free_kb" ]]; then
        fail "Copy/sealed mode refused because ${target_label} resolves to the OS root filesystem with only ${avail_gib} GiB free. Use a larger filesystem such as $recommended_root or another <large-volume>/axis-review-tests path."
    fi
}

write_source_reference_json() {
    local dest_file="$1"
    local source_path="$2"
    local mode="$3"
    local generated_at="$4"

    cat > "$dest_file" <<EOF
{
  "filename": "$(basename "$source_path")",
  "canonical_path": "$source_path",
  "size_bytes": $SOURCE_SIZE_BYTES,
  "sha256": "$SOURCE_SHA256",
  "generated_at": "$generated_at",
  "mode": "$mode"
}
EOF
}

write_uploads_reference_json() {
    local dest_file="$1"
    local uploads_path="$2"
    local generated_at="$3"
    local exists_at_build="false"

    if [[ -d "$uploads_path" ]]; then
        exists_at_build="true"
    fi

    cat > "$dest_file" <<EOF
{
  "canonical_path": "$uploads_path",
  "generated_at": "$generated_at",
  "mode": "reference",
  "exists_at_build_time": $exists_at_build
}
EOF
}

run_with_live_log() {
    local step_name="$1"
    shift
    local log_file="$SESSION_LOG_DIR/${step_name}.log"
    mkdir -p "$SESSION_LOG_DIR"
    echo -e "${GRAY}log: $log_file${NC}"

    if [[ "$COMPACT_LONG_LOGS" == "1" ]]; then
        "$@" 2>&1 \
            | tee "$log_file" \
            | awk -v keep="$COMPACT_FIRST_LINES" '
                function is_repetitive(line) {
                    return (
                        line ~ /[A-Z]{2}\.[A-Z]{2}\.[0-9]{3}.*FORCED/ ||
                        line ~ /titles\.pt preservado durante --force/ ||
                        line ~ /^[[:space:]]*✅[[:space:]]+✅[[:space:]]+[A-Z]{2}\.[A-Z]{2}\.[0-9]{3}/
                    )
                }
                {
                    if (is_repetitive($0)) {
                        repetitive_total++
                        if (repetitive_total <= keep) {
                            print
                        } else {
                            repetitive_hidden++
                        }
                        next
                    }
                    print
                }
                END {
                    if (repetitive_hidden > 0) {
                        printf("... (%d similar items)\n", repetitive_hidden)
                    }
                }
            '
    else
        "$@" 2>&1 | tee "$log_file"
    fi
}

collect_log_warnings() {
    local collected=()
    local line

    if [[ -d "$SESSION_LOG_DIR" ]]; then
        while IFS= read -r line; do
            [[ -z "$line" ]] && continue
            collected+=("$line")
        done < <(
            rg -h -n "WARNING|\\[WARN\\]|⚠|not found|Not found|passthrough|skip" "$SESSION_LOG_DIR"/*.log 2>/dev/null \
                | sed -E 's/^[0-9]+://g' \
                | sed -E 's/[[:space:]]+/ /g' \
                | sed -E 's/^[[:space:]]+|[[:space:]]+$//g' \
                | sort -u
        )
    fi

    if [[ "${#collected[@]}" -gt 0 ]]; then
        for w in "${collected[@]}"; do
            WARNINGS+=("$w")
        done
    fi
}

count_total_posts() {
    find "$REVIEW_PIPELINE/09-csl" -mindepth 1 -maxdepth 1 -type d \
        -regextype posix-extended -regex '.*/[A-Z]{2}\.[A-Z]{2}\.[0-9]{3}' \
        | wc -l | tr -d ' '
}

count_ptbr_posts() {
    local count=0
    while IFS= read -r -d '' post_dir; do
        if find "$post_dir" -maxdepth 1 -type f \( -name "pt-BR.md" -o -name "*pt-BR*.md" \) | grep -q .; then
            count=$((count + 1))
        fi
    done < <(
        find "$REVIEW_PIPELINE/09-csl" -mindepth 1 -maxdepth 1 -type d \
            -regextype posix-extended -regex '.*/[A-Z]{2}\.[A-Z]{2}\.[0-9]{3}' -print0
    )
    echo "$count"
}

check_heavy_target_safety "$REVIEW_ROOT" "review root" "/media/sanghop/BrasileirinhoHD/axis-review-tests"
check_heavy_target_safety "$SNAPSHOT_ROOT" "snapshot root" "/media/sanghop/BrasileirinhoHD/axis-review-tests/snapshots"

echo -e "${CYAN}"
echo "=================================================================="
echo " AXIS-NIDDHI - Bilingual Review Snapshot Builder"
echo "=================================================================="
echo -e "${NC}"
echo -e "${GRAY}LAB_ROOT      : $LAB_ROOT${NC}"
echo -e "${GRAY}REVIEW_ROOT   : $REVIEW_ROOT${NC}"
echo -e "${GRAY}SNAPSHOT_ROOT : $SNAPSHOT_ROOT${NC}"
echo -e "${GRAY}SNAPSHOT_TAG  : $SNAP_TAG${NC}"
echo -e "${GRAY}SOURCES_MODE  : $SOURCES_MODE${NC}"

need_dir "$LAB_ROOT"
need_dir "$LAB_PIPELINE"
need_dir "$LAB_CORE"
need_dir "$LAB_TOOLS"
need_dir "$LAB_SOURCES"
need_file "$BUILD_RELEASE_SCRIPT"

LATEST_ZIP="$(find "$LAB_SOURCES" -maxdepth 1 -name '*.zip' 2>/dev/null | sort | tail -n1)"
[[ -n "$LATEST_ZIP" ]] || fail "No source ZIP found in $LAB_SOURCES"
SOURCE_SIZE_BYTES="$(stat -c '%s' "$LATEST_ZIP")"
SOURCE_SHA256="$(sha256sum "$LATEST_ZIP" | awk '{print $1}')"
SOURCE_REFERENCE_GENERATED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
UPLOADS_REFERENCE_GENERATED_AT="$SOURCE_REFERENCE_GENERATED_AT"

if [[ -e "$SNAP_ROOT" ]]; then
    if $FORCE; then
        warn "Snapshot tag already exists. Removing: $SNAP_ROOT"
        rm -rf "$SNAP_ROOT"
    else
        fail "Snapshot path exists: $SNAP_ROOT (use --force or a different --snapshot-tag)"
    fi
fi

if ! $SKIP_LAB_VALIDATION; then
    info "1) [SP/SA] LAB validation + seal (bilingual CSL candidate)"
    run_with_live_log "01_sp02_upgrade_identity" \
        env BENG_BASE="$LAB_PIPELINE" python3 "$LAB_CORE/SP02_upgrade_identity.py" --apply --force
    run_with_live_log "01_sa01_final_audit" \
        env BENG_BASE="$LAB_PIPELINE" python3 "$LAB_CORE/SA01_final_audit.py" --apply
    run_with_live_log "01_sa02_freeze_manifest" \
        env BENG_BASE="$LAB_PIPELINE" python3 "$LAB_CORE/SA02_freeze_manifest.py"
    run_with_live_log "01_sa03_translation_progress" \
        env BENG_BASE="$LAB_PIPELINE" python3 "$LAB_CORE/SA03_translation_progress.py"
    run_with_live_log "01_sa04_generate_canon_manifest" \
        env BENG_BASE="$LAB_PIPELINE" python3 "$LAB_CORE/SA04_generate_canon_manifest.py"
    run_with_live_log "01_sa06_generate_build_seal" \
        env BENG_BASE="$LAB_PIPELINE" python3 "$LAB_CORE/SA06_generate_build_seal.py"

    if [[ -f "$LAB_TOOLS/rebuild_translation_status.py" ]]; then
        python3 "$LAB_TOOLS/rebuild_translation_status.py" \
            --csl "$LAB_PIPELINE/09-csl" \
            --out "$LAB_PIPELINE/metadata/translation_status.json"
    else
        warn "rebuild_translation_status.py not found. Skipping translation_status refresh."
    fi
else
    warn "Skipping LAB validation/seal stage (--skip-lab-validation)."
fi

info "2) [SNAPSHOT] Freeze approved bilingual CSL snapshot"
mkdir -p "$SNAP_ROOT/09-csl" "$SNAP_ROOT/metadata" "$SNAP_ROOT/sources"
rsync -a --delete "$LAB_PIPELINE/09-csl/" "$SNAP_ROOT/09-csl/"
rsync -a "$LAB_PIPELINE/metadata/" "$SNAP_ROOT/metadata/"
write_source_reference_json \
    "$SNAP_ROOT/sources/source_reference.json" \
    "$LATEST_ZIP" \
    "$SOURCES_MODE" \
    "$SOURCE_REFERENCE_GENERATED_AT"
cp "$SNAP_ROOT/sources/source_reference.json" "$SNAP_ROOT/metadata/source_reference.json"
write_uploads_reference_json \
    "$SNAP_ROOT/metadata/uploads_reference.json" \
    "$LAB_WORDPRESS_UPLOADS" \
    "$UPLOADS_REFERENCE_GENERATED_AT"
if [[ "$SOURCES_MODE" == "copy" ]]; then
    cp "$LATEST_ZIP" "$SNAP_ROOT/sources/"
fi

(
    cd "$SNAP_ROOT"
    find . -type f -print0 \
        | sort -z \
        | xargs -0 sha256sum > SNAPSHOT_MANIFEST.sha256
)

cat > "$SNAP_ROOT/SNAPSHOT_CONTEXT.txt" <<EOF
snapshot_tag=$SNAP_TAG
generated_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
lab_root=$LAB_ROOT
lab_pipeline=$LAB_PIPELINE
source_zip=$(basename "$LATEST_ZIP")
source_mode=$SOURCES_MODE
source_sha256=$SOURCE_SHA256
source_size_bytes=$SOURCE_SIZE_BYTES
source_reference=$SNAP_ROOT/sources/source_reference.json
uploads_reference=$SNAP_ROOT/metadata/uploads_reference.json
EOF
ok "Snapshot frozen at: $SNAP_ROOT"

info "3) [REVIEW] Create clean review workspace baseline ($REVIEW_ROOT)"
run_with_live_log "03_build_release_snapshot" \
    env LAB_ROOT="$LAB_ROOT" REVIEW_ROOT="$REVIEW_ROOT" bash "$BUILD_RELEASE_SCRIPT" --force --sources-mode "$SOURCES_MODE"
need_dir "$REVIEW_PIPELINE"
need_dir "$REVIEW_SCRIPTS"

info "4) [REVIEW] Overlay frozen bilingual snapshot into review workspace"
rsync -a --delete "$SNAP_ROOT/09-csl/" "$REVIEW_PIPELINE/09-csl/"
rsync -a "$SNAP_ROOT/metadata/" "$REVIEW_PIPELINE/metadata/"
rsync -a --delete "$SNAP_ROOT/sources/" "$REVIEW_ROOT/sources/"
cp "$SNAP_ROOT/SNAPSHOT_MANIFEST.sha256" "$REVIEW_PIPELINE/metadata/review_snapshot_manifest.sha256"
cp "$SNAP_ROOT/SNAPSHOT_CONTEXT.txt" "$REVIEW_PIPELINE/metadata/review_snapshot_context.txt"

# Print helper is not copied by release builder; include it so review static site is operationally ready.
if [[ -f "$LAB_TOOLS/print_batch.py" ]]; then
    mkdir -p "$REVIEW_SCRIPTS/tools"
    cp "$LAB_TOOLS/print_batch.py" "$REVIEW_SCRIPTS/tools/print_batch.py"
    chmod +x "$REVIEW_SCRIPTS/tools/print_batch.py"
fi

need_file "$REVIEW_SCRIPTS/SD01_generate_asset_map.py"
need_file "$REVIEW_SCRIPTS/setup_v54_static_site.sh"

info "5) [SD] SD-only in review workspace (no SG/SP/SA)"
PRE_CSL_HASH="$(tree_hash "$REVIEW_PIPELINE/09-csl")"
echo -e "${GRAY}Pre-SD CSL hash: $PRE_CSL_HASH${NC}"

run_with_live_log "05_sd01_generate_asset_map" \
    env BENG_BASE="$REVIEW_PIPELINE" BENG_WP_UPLOADS_DIR="$LAB_WORDPRESS_UPLOADS" python3 "$REVIEW_SCRIPTS/SD01_generate_asset_map.py"
run_with_live_log "05_setup_v54_static_site" \
    env BENG_BASE="$REVIEW_PIPELINE" bash "$REVIEW_SCRIPTS/setup_v54_static_site.sh"
run_with_live_log "05_sd03_static_site_build" \
    bash -c "cd \"$REVIEW_PIPELINE/13-ssg\" && BENG_BASE=\"$REVIEW_PIPELINE\" python3 build.py"

POST_CSL_HASH="$(tree_hash "$REVIEW_PIPELINE/09-csl")"
echo -e "${GRAY}Post-SD CSL hash: $POST_CSL_HASH${NC}"

if [[ "$PRE_CSL_HASH" != "$POST_CSL_HASH" ]]; then
    fail "CSL changed during review build. Aborting to preserve immutability."
fi

info "6) [SUMMARY] Done - bilingual review artifact ready"
ok "Static site: $REVIEW_PIPELINE/13-static-site"
ok "Review snapshot manifest: $REVIEW_PIPELINE/metadata/review_snapshot_manifest.sha256"
ok "CSL immutability check: PASS"

TOTAL_POSTS="$(count_total_posts)"
PTBR_POSTS="$(count_ptbr_posts)"
CSL_IMMUTABILITY_RESULT="PASS"
RELEASE_SEAL_PATH="$REVIEW_ROOT/release-manifest.sha256"
RELEASE_SEAL_META="$REVIEW_ROOT/release-sealed-at.txt"
BUILD_SEAL_PATH="$REVIEW_PIPELINE/metadata/build_seal.json"
SNAPSHOT_MANIFEST_PATH="$REVIEW_PIPELINE/metadata/review_snapshot_manifest.sha256"
SNAPSHOT_CONTEXT_PATH="$REVIEW_PIPELINE/metadata/review_snapshot_context.txt"
SOURCE_REFERENCE_PATH="$REVIEW_ROOT/sources/source_reference.json"

collect_log_warnings

if [[ "${#WARNINGS[@]}" -gt 0 ]]; then
    mapfile -t WARNINGS < <(printf "%s\n" "${WARNINGS[@]}" | sed '/^$/d' | sort -u)
fi

{
    echo "# AXIS-NIDDHI Review Build Summary"
    echo ""
    echo "- Snapshot tag: \`$SNAP_TAG\`"
    echo "- LAB root: \`$LAB_ROOT\`"
    echo "- REVIEW root: \`$REVIEW_ROOT\`"
    echo "- Source ZIP: \`$(basename "$LATEST_ZIP")\`"
    echo "- Source mode: \`$SOURCES_MODE\`"
    echo "- Source SHA-256: \`$SOURCE_SHA256\`"
    echo "- Source reference: \`$SOURCE_REFERENCE_PATH\`"
    echo "- Total posts: \`$TOTAL_POSTS\`"
    echo "- PT-BR posts: \`$PTBR_POSTS\`"
    echo "- Output path: \`$REVIEW_PIPELINE/13-static-site\`"
    echo "- Snapshot manifest: \`$SNAPSHOT_MANIFEST_PATH\`"
    echo "- Snapshot context: \`$SNAPSHOT_CONTEXT_PATH\`"
    echo "- Release seal manifest: \`$RELEASE_SEAL_PATH\`"
    echo "- Release seal metadata: \`$RELEASE_SEAL_META\`"
    echo "- Build seal path: \`$BUILD_SEAL_PATH\`"
    echo "- CSL immutability: \`$CSL_IMMUTABILITY_RESULT\`"
    echo "- Session logs: \`$SESSION_LOG_DIR\`"
    echo ""
    echo "## Relevant Warnings"
    if [[ "${#WARNINGS[@]}" -eq 0 ]]; then
        echo "- None"
    else
        for w in "${WARNINGS[@]}"; do
            echo "- $w"
        done
    fi
    echo ""
    echo "## Next Steps"
    echo "1. Review and print from \`$REVIEW_PIPELINE/13-static-site\`."
    echo "2. Do not use or recreate \`Print_Translation_Control_Center.csv\`; that print-batch workflow was retired by #FlagFix_033."
    echo "3. If approved, promote this snapshot toward canonical release governance."
    echo ""
    echo "Thank you for this careful run. May this effort support continuity and future translators."
} > "$SUMMARY_REPORT"

ok "Review summary report: $SUMMARY_REPORT"

echo ""
echo -e "${CYAN}Print batch workflow retired${NC}"
echo -e "  Retired by   : #FlagFix_033"
echo -e "  Official CSV : Translation_Control_Center.csv remains official for SP10/DeepL"
echo -e "  Do not recreate Print_Translation_Control_Center.csv without explicit review."
echo ""

sleep "$FINAL_PAUSE_SECONDS" 2>/dev/null || true
if [[ "$ENABLE_FINAL_CLEAR" == "1" ]]; then
    clear
fi

echo -e "${CYAN}Closing / Encerramento${NC}"
echo "        .-."
echo "    .--(   )--."
echo "   (___/ \\___)   <><"
echo "      /_ _\\      []"
echo "       / \\"
echo ""
echo "EN: Thank you for your care, patience, and stewardship."
echo "EN: Another layer of the honey has crystallized."
echo "PT-BR: Gratidao pelo cuidado, paciencia e zelo."
echo "PT-BR: Mais uma camada do mel foi cristalizada."
echo ""
echo "EN: May the merits of this work benefit all beings."
echo "PT-BR: Que os meritos deste trabalho beneficiem todos os seres."
echo ""
echo -e "${GREEN}Mission complete.${NC}"
