#!/usr/bin/env bash
# /beng-fut/pipeline/scripts/setup_v54_static_site.sh
# ==============================================================================
# AXIS-NIDDHI V5.4 — Setup Static Publication Layer
# ==============================================================================
# O SD03 (build.py) já existe e é uma engine V3.0 completa.
# Este script monta a estrutura de pastas que ele espera,
# copiando os módulos que já existem em /beng-fut/pipeline/scripts/
#
# USO:
#   bash /beng-fut/pipeline/scripts/setup_v54_static_site.sh
#   axis build-site
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ "$(basename "$SCRIPT_DIR")" == "tools" ]]; then
    SCRIPTS="$(cd "$SCRIPT_DIR/.." && pwd)"
elif [[ "$(basename "$SCRIPT_DIR")" == "scripts" ]]; then
    SCRIPTS="$SCRIPT_DIR"
else
    echo "❌ setup_v54_static_site.sh em local inesperado: $SCRIPT_DIR" >&2
    exit 1
fi
PIPELINE="$(cd "$SCRIPTS/.." && pwd)"
SCRIPTS_CORE="$SCRIPTS/core"
SSG="$PIPELINE/13-ssg"
GREEN='\033[0;32m'; CYAN='\033[0;96m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

ok()   { echo -e "${GREEN}✅ $*${NC}"; }
info() { echo -e "\n${CYAN}━━━ $* ━━━${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }
err()  { echo -e "${RED}❌ $*${NC}"; exit 1; }

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║  AXIS-NIDDHI V5.4 — Static Publication Layer Setup  ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ==============================================================================
# PASSO 1 — Verificar que os arquivos fonte existem
# ==============================================================================
info "PASSO 1 — Verificar arquivos fonte"

check_file() {
    if [ ! -f "$1" ]; then
        err "Arquivo não encontrado: $1"
    fi
    ok "$(basename $1)"
}

pick_src() {
    for candidate in "$@"; do
        if [ -f "$candidate" ]; then
            echo "$candidate"
            return 0
        fi
    done
    return 1
}

require_src() {
    local label="$1"
    shift
    local src
    src="$(pick_src "$@")" || err "Fonte ausente para $label"
    check_file "$src" >&2
    echo "$src"
}

sync_copy() {
    local src="$1"
    local dst="$2"
    local label="$3"
    if [ "$src" = "$dst" ]; then
        ok "$label (já presente)"
        return 0
    fi
    cp "$src" "$dst"
    ok "$label"
}

# Engine real + shim (shim é compatibilidade secundária)
BUILD_SRC="$(require_src "build.py (engine real)" \
    "$SCRIPTS_CORE/build.py" \
    "$SCRIPTS/build.py" \
    "$SSG/build.py")"
SHIM_SRC="$(require_src "SD03_static_site_build.py (compat shim)" \
    "$SCRIPTS_CORE/SD03_static_site_build.py" \
    "$SCRIPTS/SD03_static_site_build.py")"

# Módulos Python
MODELS_SRC="$(require_src "models.py" "$SCRIPTS_CORE/models.py" "$SCRIPTS/models.py" "$SSG/src/models.py")"
CSL_LOADER_SRC="$(require_src "csl_loader.py" "$SCRIPTS_CORE/csl_loader.py" "$SCRIPTS/csl_loader.py" "$SSG/src/loaders/csl_loader.py")"
IDENTITY_LOADER_SRC="$(require_src "identity_loader.py" "$SCRIPTS_CORE/identity_loader.py" "$SCRIPTS/identity_loader.py" "$SSG/src/loaders/identity_loader.py")"
POST_RENDERER_SRC="$(require_src "post_renderer.py" "$SCRIPTS_CORE/post_renderer.py" "$SCRIPTS/post_renderer.py" "$SSG/src/renderers/post_renderer.py")"
INDEX_RENDERER_SRC="$(require_src "index_renderer.py" "$SCRIPTS_CORE/index_renderer.py" "$SCRIPTS/index_renderer.py" "$SSG/src/renderers/index_renderer.py")"
NAV_BUILDER_SRC="$(require_src "nav_builder.py" "$SCRIPTS_CORE/nav_builder.py" "$SCRIPTS/nav_builder.py" "$SSG/src/transformers/nav_builder.py")"
LINK_RESOLVER_SRC="$(require_src "link_resolver.py" "$SCRIPTS_CORE/link_resolver.py" "$SCRIPTS/link_resolver.py" "$SSG/src/transformers/link_resolver.py")"
ASSET_MAPPER_SRC="$(require_src "asset_mapper.py" "$SCRIPTS_CORE/asset_mapper.py" "$SCRIPTS/asset_mapper.py" "$SSG/src/transformers/asset_mapper.py")"

# Templates
BASE_TPL_SRC="$(require_src "base.html" "$SCRIPTS_CORE/base.html" "$SCRIPTS/base.html" "$SSG/templates/base.html")"
POST_TPL_SRC="$(require_src "post.html" "$SCRIPTS_CORE/post.html" "$SCRIPTS/post.html" "$SSG/templates/post.html")"
INDEX_TPL_SRC="$(require_src "index.html" "$SCRIPTS_CORE/index.html" "$SCRIPTS/index.html" "$SSG/templates/index.html")"
WELCOME_TPL_SRC="$(require_src "welcome.html" "$SCRIPTS_CORE/welcome.html" "$SCRIPTS/welcome.html" "$SSG/templates/welcome.html")"

# Assets estáticos mínimos
STYLE_CSS_SRC="$(require_src "style.css" "$SCRIPTS_CORE/style.css" "$SCRIPTS/style.css" "$SSG/static/css/style.css")"
TYPOGRAPHY_CSS_SRC="$(require_src "typography-pro.css" "$SCRIPTS_CORE/typography-pro.css" "$SCRIPTS/typography-pro.css" "$SSG/static/css/typography-pro.css")"
MAIN_JS_SRC="$(require_src "main.js" "$SCRIPTS_CORE/main.js" "$SCRIPTS/main.js" "$SSG/static/js/main.js")"
SW_JS_SRC="$(require_src "sw.js" "$SCRIPTS_CORE/sw.js" "$SCRIPTS/sw.js" "$SSG/static/js/sw.js")"
FAVICON_SRC="$(require_src "favicon.svg" "$SCRIPTS_CORE/favicon.svg" "$SCRIPTS/favicon.svg" "$SSG/static/favicon.svg")"
BUDDHA_IMG_SRC="$(require_src "buddha-2.jpg" "$SCRIPTS_CORE/buddha-2.jpg" "$SCRIPTS/buddha-2.jpg" "$SSG/static/buddha-2.jpg")"
LEAF_IMG_SRC="$(require_src "BodhiCircuitLeaf.png" "$SCRIPTS_CORE/BodhiCircuitLeaf.png" "$SCRIPTS/BodhiCircuitLeaf.png" "$SSG/static/assets/BodhiCircuitLeaf.png")"
LEAF_HTML_SRC="$(require_src "leaf.html" "$SCRIPTS_CORE/leaf.html" "$SCRIPTS/leaf.html" "$SSG/static/leaf.html")"
READING_FLOW_SRC="$(pick_src "$SCRIPTS_CORE/reading-flow.js" "$SCRIPTS/reading-flow.js" "$SSG/static/js/reading-flow.js" || true)"

# ==============================================================================
# PASSO 2 — Criar estrutura de pastas 13-ssg/
# ==============================================================================
info "PASSO 2 — Criar estrutura de pastas"

mkdir -p "$SSG/src/loaders"
mkdir -p "$SSG/src/renderers"
mkdir -p "$SSG/src/transformers"
mkdir -p "$SSG/templates"
mkdir -p "$SSG/static/css"
mkdir -p "$SSG/static/js"
mkdir -p "$SSG/static/assets"
mkdir -p "$SSG/cache"

ok "Estrutura de pastas criada em $SSG"

# ==============================================================================
# PASSO 3 — Copiar engine real + shim de compatibilidade
# ==============================================================================
info "PASSO 3 — Engine real + Shim compat"

sync_copy "$BUILD_SRC" "$SSG/build.py" "build.py (engine real)"
sync_copy "$SHIM_SRC" "$SSG/SD03_static_site_build.py" "SD03_static_site_build.py (shim compat)"

# ==============================================================================
# PASSO 4 — Copiar módulos src/
# ==============================================================================
info "PASSO 4 — Módulos src/"

# models.py — na raiz de src/ (importado diretamente como 'from models import')
sync_copy "$MODELS_SRC"              "$SSG/src/models.py" "src/models.py"

# loaders/
sync_copy "$CSL_LOADER_SRC"          "$SSG/src/loaders/csl_loader.py" "src/loaders/csl_loader.py"
sync_copy "$IDENTITY_LOADER_SRC"     "$SSG/src/loaders/identity_loader.py" "src/loaders/identity_loader.py"
touch "$SSG/src/loaders/__init__.py"
ok "src/loaders/"

# renderers/
sync_copy "$POST_RENDERER_SRC"       "$SSG/src/renderers/post_renderer.py" "src/renderers/post_renderer.py"
sync_copy "$INDEX_RENDERER_SRC"      "$SSG/src/renderers/index_renderer.py" "src/renderers/index_renderer.py"
touch "$SSG/src/renderers/__init__.py"
ok "src/renderers/"

# transformers/
sync_copy "$NAV_BUILDER_SRC"         "$SSG/src/transformers/nav_builder.py" "src/transformers/nav_builder.py"
sync_copy "$LINK_RESOLVER_SRC"       "$SSG/src/transformers/link_resolver.py" "src/transformers/link_resolver.py"
sync_copy "$ASSET_MAPPER_SRC"        "$SSG/src/transformers/asset_mapper.py" "src/transformers/asset_mapper.py"
touch "$SSG/src/transformers/__init__.py"
ok "src/transformers/"

# __init__.py na raiz de src/ (para imports relativos funcionarem)
touch "$SSG/src/__init__.py"

# ==============================================================================
# PASSO 5 — Copiar templates
# ==============================================================================
info "PASSO 5 — Templates Jinja2"

sync_copy "$BASE_TPL_SRC"            "$SSG/templates/base.html" "templates/base.html"
sync_copy "$POST_TPL_SRC"            "$SSG/templates/post.html" "templates/post.html"
sync_copy "$INDEX_TPL_SRC"           "$SSG/templates/index.html" "templates/index.html"
sync_copy "$WELCOME_TPL_SRC"         "$SSG/templates/welcome.html" "templates/welcome.html"
ok "templates/ (base.html, post.html, index.html, welcome.html)"

# ==============================================================================
# PASSO 6 — Copiar assets estáticos
# ==============================================================================
info "PASSO 6 — Assets estáticos mínimos (CSS + JS + mídia)"

sync_copy "$STYLE_CSS_SRC"          "$SSG/static/css/style.css" "static/css/style.css"
sync_copy "$TYPOGRAPHY_CSS_SRC"     "$SSG/static/css/typography-pro.css" "static/css/typography-pro.css"
sync_copy "$MAIN_JS_SRC"            "$SSG/static/js/main.js" "static/js/main.js"
sync_copy "$SW_JS_SRC"              "$SSG/static/js/sw.js" "static/js/sw.js"
sync_copy "$FAVICON_SRC"            "$SSG/static/favicon.svg" "static/favicon.svg"
sync_copy "$BUDDHA_IMG_SRC"         "$SSG/static/buddha-2.jpg" "static/buddha-2.jpg"
sync_copy "$LEAF_IMG_SRC"           "$SSG/static/assets/BodhiCircuitLeaf.png" "static/assets/BodhiCircuitLeaf.png"
sync_copy "$LEAF_HTML_SRC"          "$SSG/static/leaf.html" "static/leaf.html"

# reading-flow.js — opcional
if [ -n "${READING_FLOW_SRC:-}" ] && [ -f "$READING_FLOW_SRC" ]; then
    sync_copy "$READING_FLOW_SRC" "$SSG/static/js/reading-flow.js" "static/js/reading-flow.js"
fi

ok "static/ payload mínimo sincronizado"

# ==============================================================================
# PASSO 7 — Corrigir imports relativos nos módulos
# ==============================================================================
info "PASSO 7 — Checagem passiva dos imports"

# csl_loader.py usa: from .identity_loader import load_identity
# post_renderer.py usa: from transformers.link_resolver import LinkResolver
#                       from transformers.asset_mapper import process_assets
# build.py adiciona src/ ao sys.path — os imports devem funcionar

# Não mutacionar build.py automaticamente (protocolo de estabilidade).
if grep -q "sys.path.insert(0, str(_HERE / \"src\"))" "$SSG/build.py"; then
    ok "build.py contém sys.path para src/"
else
    warn "build.py sem sys.path explícito para src/ (checar manualmente)"
fi

# ==============================================================================
# PASSO 8 — Criar netlify.toml
# ==============================================================================
info "PASSO 8 — netlify.toml"

BENG_BASE="${BENG_BASE:-$PIPELINE}"
STATIC_SITE="$BENG_BASE/13-static-site"

cat > "$PIPELINE/netlify.toml" << 'TOML'
# AXIS-NIDDHI V5.4 — Netlify Configuration
# Deploy: arrastar a pasta 13-static-site/ no Netlify UI
# ou conectar o repositório com publish_dir abaixo.

[build]
  # Comando de build executado pelo Netlify
  # (Se usar CI — caso contrário, deploy manual da pasta)
  command   = "python3 ./13-ssg/build.py"
  publish   = "static-site"

[build.environment]
  PYTHON_VERSION = "3.11"

# Redirects para SPA-style navigation (evita 404 em refresh)
[[redirects]]
  from   = "/posts/*"
  to     = "/posts/:splat/index.html"
  status = 200

[[redirects]]
  from   = "/*"
  to     = "/index.html"
  status = 404

# Headers de segurança e cache
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options        = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy        = "strict-origin-when-cross-origin"

[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*.html"
  [headers.values]
    Cache-Control = "public, max-age=0, must-revalidate"
TOML

ok "netlify.toml criado em $PIPELINE/"

# ==============================================================================
# PASSO 9 — Criar $BENG_BASE/13-static-site/ como destino do output
# ==============================================================================
info "PASSO 9 — Diretório de output"

mkdir -p "$STATIC_SITE"
ok "Diretório output: $STATIC_SITE"

# Patch no config.py para apontar DIR_13_SSG para o runtime correto
SCRIPTS_ROOT="$SCRIPTS" python3 - << 'PY'
import os
from pathlib import Path
scripts = Path(os.environ["SCRIPTS_ROOT"])
candidates = [scripts / "core" / "config.py", scripts / "config.py"]
cfg = next((p for p in candidates if p.exists()), None)
if cfg is None:
    print("config.py não encontrado — skip")
    exit(0)

content = cfg.read_text(encoding="utf-8")

canonical = 'DIR_13_SSG         = BASE_DIR / "13-static-site"'
legacy_runtime = 'DIR_13_SSG         = Path("/beng-runtime/static-site")'

if canonical in content:
    print('DIR_13_SSG já aponta para BASE_DIR / "13-static-site" — OK')
elif legacy_runtime in content:
    content = content.replace(legacy_runtime, canonical)
    cfg.write_text(content, encoding="utf-8")
    print('DIR_13_SSG normalizado → BASE_DIR / "13-static-site"')
else:
    print("⚠️  Padrão DIR_13_SSG não encontrado em config.py — verificar manualmente")
PY

# Compat import path: build.py procura config em <pipeline>/scripts/config.py
info "PASSO 9b — Compat config import (scripts/config.py)"
if [ -f "$SCRIPTS/config.py" ]; then
    ok "scripts/config.py já existe"
elif [ -f "$SCRIPTS/core/config.py" ]; then
    sync_copy "$SCRIPTS/core/config.py" "$SCRIPTS/config.py" "scripts/config.py criado a partir de scripts/core/config.py"
else
    warn "Não foi possível criar scripts/config.py (scripts/core/config.py ausente)"
fi

# ==============================================================================
# PASSO 10 — Adicionar 'axis build-site' ao runner
# ==============================================================================
info "PASSO 10 — Alias axis build-site"

RUNNER="$SCRIPTS/tools/axis_runner.sh"
if [ ! -f "$RUNNER" ]; then
    RUNNER="$SCRIPTS/axis_runner.sh"
fi

# Verificar se build-site já existe no runner
if [ ! -f "$RUNNER" ]; then
    warn "axis_runner.sh não encontrado — skip alias build-site"
elif grep -q "build-site" "$RUNNER" 2>/dev/null; then
    ok "axis build-site já existe no runner"
else
    # Inserir antes do 'help|*)'
    sed -i "s|    help|\\\n    build-site)\n        echo \"🏗️  Buildando site estático...\"\n        python3 \"$PIPELINE/13-ssg/build.py\" \"\$@\"\n        echo \"\"\n        echo \"📁 Output: $STATIC_SITE\"\n        echo \"🌐 Preview: cd $STATIC_SITE \&\& python3 -m http.server 8080\"\n        ;;\n\n    help|" "$RUNNER"
    ok "axis build-site adicionado ao runner"
fi

# ==============================================================================
# SUMÁRIO
# ==============================================================================
echo ""
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ✅ V5.4 Setup concluído!                               ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Estrutura:  $PIPELINE/13-ssg/                  ║"
echo "║  Output:     $STATIC_SITE                  ║"
echo "║  Netlify:    $PIPELINE/netlify.toml             ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Para fazer o build:                                     ║"
echo "║    axis build-site                                       ║"
echo "║                                                          ║"
echo "║  Para preview local:                                     ║"
echo "║    cd $STATIC_SITE                          ║"
echo "║    python3 -m http.server 8080                           ║"
echo "║    → http://localhost:8080                               ║"
echo "║                                                          ║"
echo "║  Para deploy Netlify:                                    ║"
echo "║    Arraste 13-static-site/ no netlify.com                ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
