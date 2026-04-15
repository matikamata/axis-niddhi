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

PIPELINE="/beng-fut/pipeline"
SCRIPTS="$PIPELINE/scripts"
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

check_file "$SCRIPTS/SD03_static_site_build.py"
check_file "$SCRIPTS/models.py"
check_file "$SCRIPTS/csl_loader.py"
check_file "$SCRIPTS/identity_loader.py"
check_file "$SCRIPTS/post_renderer.py"
check_file "$SCRIPTS/index_renderer.py"
check_file "$SCRIPTS/nav_builder.py"
check_file "$SCRIPTS/link_resolver.py"
check_file "$SCRIPTS/asset_mapper.py"
check_file "$SCRIPTS/base.html"
check_file "$SCRIPTS/post.html"
check_file "$SCRIPTS/index.html"
check_file "$SCRIPTS/style.css"
check_file "$SCRIPTS/main.js"
check_file "$SCRIPTS/sw.js"

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
mkdir -p "$SSG/cache"

ok "Estrutura de pastas criada em $SSG"

# ==============================================================================
# PASSO 3 — Copiar build.py
# ==============================================================================
info "PASSO 3 — build.py (SD03)"

cp "$SCRIPTS/SD03_static_site_build.py" "$SSG/build.py"
ok "build.py"

# ==============================================================================
# PASSO 4 — Copiar módulos src/
# ==============================================================================
info "PASSO 4 — Módulos src/"

# models.py — na raiz de src/ (importado diretamente como 'from models import')
cp "$SCRIPTS/models.py"         "$SSG/src/models.py"
ok "src/models.py"

# loaders/
cp "$SCRIPTS/csl_loader.py"     "$SSG/src/loaders/csl_loader.py"
cp "$SCRIPTS/identity_loader.py" "$SSG/src/loaders/identity_loader.py"
touch "$SSG/src/loaders/__init__.py"
ok "src/loaders/"

# renderers/
cp "$SCRIPTS/post_renderer.py"  "$SSG/src/renderers/post_renderer.py"
cp "$SCRIPTS/index_renderer.py" "$SSG/src/renderers/index_renderer.py"
touch "$SSG/src/renderers/__init__.py"
ok "src/renderers/"

# transformers/
cp "$SCRIPTS/nav_builder.py"    "$SSG/src/transformers/nav_builder.py"
cp "$SCRIPTS/link_resolver.py"  "$SSG/src/transformers/link_resolver.py"
cp "$SCRIPTS/asset_mapper.py"   "$SSG/src/transformers/asset_mapper.py"
touch "$SSG/src/transformers/__init__.py"
ok "src/transformers/"

# __init__.py na raiz de src/ (para imports relativos funcionarem)
touch "$SSG/src/__init__.py"

# ==============================================================================
# PASSO 5 — Copiar templates
# ==============================================================================
info "PASSO 5 — Templates Jinja2"

cp "$SCRIPTS/base.html"  "$SSG/templates/base.html"
cp "$SCRIPTS/post.html"  "$SSG/templates/post.html"
cp "$SCRIPTS/index.html" "$SSG/templates/index.html"
ok "templates/ (base.html, post.html, index.html)"

# ==============================================================================
# PASSO 6 — Copiar assets estáticos
# ==============================================================================
info "PASSO 6 — Assets estáticos (CSS + JS)"

cp "$SCRIPTS/style.css"       "$SSG/static/css/style.css"
cp "$SCRIPTS/main.js"         "$SSG/static/js/main.js"
cp "$SCRIPTS/sw.js"           "$SSG/static/js/sw.js"

# reading-flow.js — opcional
if [ -f "$SCRIPTS/reading-flow.js" ]; then
    cp "$SCRIPTS/reading-flow.js" "$SSG/static/js/reading-flow.js"
    ok "static/js/reading-flow.js"
fi

ok "static/css/ + static/js/"

# ==============================================================================
# PASSO 7 — Corrigir imports relativos nos módulos
# ==============================================================================
info "PASSO 7 — Corrigir imports nos módulos"

# csl_loader.py usa: from .identity_loader import load_identity
# post_renderer.py usa: from transformers.link_resolver import LinkResolver
#                       from transformers.asset_mapper import process_assets
# build.py adiciona src/ ao sys.path — os imports devem funcionar

# Verificar se build.py já aponta para src/ corretamente
if grep -q "sys.path.insert(0, str(_HERE / \"src\"))" "$SSG/build.py"; then
    ok "build.py já tem sys.path para src/"
else
    # Adicionar sys.path patch no topo do build.py
    sed -i 's|sys.path.insert(0, str(_HERE / "src"))|# sys.path já configurado|' "$SSG/build.py"
    python3 - << 'PY'
import re
from pathlib import Path

build = Path("/beng-fut/pipeline/13-ssg/build.py")
content = build.read_text(encoding="utf-8")

# Garantir que src/ está no sys.path
patch = '\n_HERE = Path(__file__).parent.resolve()\nsys.path.insert(0, str(_HERE / "src"))\n'
if 'sys.path.insert(0, str(_HERE / "src"))' not in content:
    content = content.replace(
        '_HERE = Path(__file__).parent.resolve()',
        patch.strip()
    )
    build.write_text(content, encoding="utf-8")
    print("sys.path patch aplicado")
else:
    print("sys.path já correto")
PY
fi

# ==============================================================================
# PASSO 8 — Criar netlify.toml
# ==============================================================================
info "PASSO 8 — netlify.toml"

RUNTIME="/beng-runtime"
STATIC_SITE="$RUNTIME/static-site"

cat > "$PIPELINE/netlify.toml" << 'TOML'
# AXIS-NIDDHI V5.4 — Netlify Configuration
# Deploy: arrastar a pasta /beng-runtime/static-site/ no Netlify UI
# ou conectar o repositório com publish_dir abaixo.

[build]
  # Comando de build executado pelo Netlify
  # (Se usar CI — caso contrário, deploy manual da pasta)
  command   = "python3 /beng-fut/pipeline/13-ssg/build.py"
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
# PASSO 9 — Criar /beng-runtime/static-site/ como destino do output
# ==============================================================================
info "PASSO 9 — Diretório de output"

mkdir -p "$STATIC_SITE"
ok "Diretório output: $STATIC_SITE"

# Patch no config.py para apontar DIR_13_SSG para o runtime correto
python3 - << 'PY'
from pathlib import Path
cfg = Path("/beng-fut/pipeline/scripts/config.py")
if not cfg.exists():
    print("config.py não encontrado — skip")
    exit(0)

content = cfg.read_text(encoding="utf-8")

old = 'DIR_13_SSG         = BASE_DIR / "13-static-site"'
new = 'DIR_13_SSG         = Path("/beng-runtime/static-site")'

if new in content:
    print("DIR_13_SSG já aponta para /beng-runtime/static-site — OK")
elif old in content:
    content = content.replace(old, new)
    cfg.write_text(content, encoding="utf-8")
    print("DIR_13_SSG atualizado → /beng-runtime/static-site")
else:
    print("⚠️  Padrão DIR_13_SSG não encontrado em config.py — verificar manualmente")
PY

# ==============================================================================
# PASSO 10 — Adicionar 'axis build-site' ao runner
# ==============================================================================
info "PASSO 10 — Alias axis build-site"

RUNNER="$SCRIPTS/axis_runner.sh"

# Verificar se build-site já existe no runner
if grep -q "build-site" "$RUNNER" 2>/dev/null; then
    ok "axis build-site já existe no runner"
else
    # Inserir antes do 'help|*)'
    sed -i "s|    help|\\\n    build-site)\n        echo \"🏗️  Buildando site estático...\"\n        python3 /beng-fut/pipeline/13-ssg/build.py \"\$@\"\n        echo \"\"\n        echo \"📁 Output: /beng-runtime/static-site/\"\n        echo \"🌐 Preview: cd /beng-runtime/static-site \&\& python3 -m http.server 8080\"\n        ;;\n\n    help|" "$RUNNER"
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
echo "║  Estrutura:  /beng-fut/pipeline/13-ssg/                  ║"
echo "║  Output:     /beng-runtime/static-site/                  ║"
echo "║  Netlify:    /beng-fut/pipeline/netlify.toml             ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Para fazer o build:                                     ║"
echo "║    axis build-site                                       ║"
echo "║                                                          ║"
echo "║  Para preview local:                                     ║"
echo "║    cd /beng-runtime/static-site                          ║"
echo "║    python3 -m http.server 8080                           ║"
echo "║    → http://localhost:8080                               ║"
echo "║                                                          ║"
echo "║  Para deploy Netlify:                                    ║"
echo "║    Arraste /beng-runtime/static-site/ no netlify.com     ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
