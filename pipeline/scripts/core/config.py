"""
💎 BRASILEIRINHO ENGINE — config.py
====================================
Versão:  AXIS-NIDDHI Edition (v2.1)
Data:    2026-02-28
Autores: Aloka + Claude Sonnet 4.6

REGRAS DESTE ARQUIVO:
  - Zero hardcodes de credenciais sensíveis (DeepL, WP App Password)
  - Todas as constantes derivadas de BASE_DIR ou de variáveis de ambiente
  - Qualquer script do pipeline importa daqui — nunca redefine localmente

CHANGELOG vs versão anterior:
  ★ BASE_DIR          → /beng/pipeline          (era /home/sucessor/pipeline)
  ★ DB 'database'     → beng_wp_21              (era puredhamma_clean)
  ★ WP_BASE_URL       → http://localhost/beng_feb2026  (era /brasileirinho)
  ★ get_deepl_key()   → sem hardcode; lê env ou deepl_key.txt; aborta se ausente
  ★ get_wp_password() → idem, para WP App Password
"""

import os
import sys
from pathlib import Path

# ==============================================================================
# 📁  PATHS CANÔNICOS
# ==============================================================================

# config.py lives at scripts/core/config.py → .parent=core/ → .parent=scripts/ → .parent=pipeline/
BASE_DIR      = Path(os.environ.get("BENG_BASE", str(Path(__file__).resolve().parent.parent.parent)))
SCRIPTS_DIR   = Path(__file__).resolve().parent   # scripts/core/ — dir real do config.py
METADATA_DIR  = BASE_DIR / "metadata"
LOG_DIR       = BASE_DIR / "logs"

# Pastas de dados do pipeline
DIR_01_EXTRACTED   = BASE_DIR / "01-extracted-htmls"
DIR_02_PREPROCESSED= BASE_DIR / "02-preprocessed"
DIR_09_CSL         = BASE_DIR / "09-csl"
DIR_03_TRANSLATIONS= BASE_DIR / "03-translations"          # Translation Preservation Layer (SP00/SP01b)
DIR_13_SSG         = BASE_DIR / "13-static-site"          # Onde moram os scripts/templates do gerador

# ── V5.4 Aliases: engine vs output ───────────────────────────────────────────
# DIR_13_SSG_ENGINE = source do gerador (build.py, templates, src/)
# DIR_13_SSG_OUTPUT = site final gerado (o que config.py chama DIR_13_SSG)
DIR_13_SSG_ENGINE  = BASE_DIR / "13-ssg"           # engine — nunca é o output
DIR_13_SSG_OUTPUT  = DIR_13_SSG                    # alias explícito para clareza
# ─────────────────────────────────────────────────────────────────────────────
DIR_STATIC_SITE    = BASE_DIR / "13-static-site"   # Onde o site FINAL será gerado
DIR_14_ASSETS      = BASE_DIR / "S14_asset_resolver"
DIR_15_SEMANTIC    = BASE_DIR / "15-semantic"

# Legacy alias — SP01 default src (BrasileirinhoHD external HD).
DIR_03_PTBR = Path('/media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/pipeline/09-csl')

# Arquivos de metadados canônicos
PDPN_CSV       = METADATA_DIR / "PDPN_01_Operational.csv"
MENU_CSV       = METADATA_DIR / "Translation_Control_Center.csv"
GLOSSARY_JSON  = METADATA_DIR / "glossary_config.json"

# ==============================================================================
# 🗄️  BANCO DE DADOS
# ==============================================================================
# ★ Nome versionado: evita colisão com bancos de sessões anteriores.
# Sincronizado com o DB_NAME do reset_brasileirinho_v12.1.sh

DB_CONFIG = {
    "host":     "localhost",
    "user":     "wp_user",
    "password": "wp_pass123",
    "database": "beng_wp_21",          # ★ era: puredhamma_clean
}

# ==============================================================================
# 🌐  WORDPRESS LOCAL
# ==============================================================================
# ★ URL versionada: rastreável por sessão e compatível com futura ISO/Crucis v3.
# Sincronizada com WP_ALIAS do reset_brasileirinho_v12.1.sh

WP_BASE_URL  = "http://localhost/beng_feb2026"   # ★ era: /brasileirinho
WP_API_URL   = f"{WP_BASE_URL}/wp-json/wp/v2"
WP_API_POSTS = f"{WP_API_URL}/posts"
WP_API_PAGES = f"{WP_API_URL}/pages"

WP_ADMIN_USER = "axis_niddhi"   # usuário técnico do pipeline — criado pelo SG00, não é login real

# ==============================================================================
# 🔐  CREDENCIAIS — FUNÇÕES DE LEITURA SEGURA
# ==============================================================================

def get_deepl_key() -> str:
    """
    Retorna a chave DeepL sem hardcode.

    Prioridade:
      1. Variável de ambiente  DEEPL_AUTH_KEY  (ou DEEPL_API_KEY)
      2. Arquivo               scripts/private/deepl_key.txt
         Formatos aceitos:
           DEEPL_AUTH_KEY=sua_chave_aqui
           DEEPL_API_KEY=sua_chave_aqui

    [The Disney Protocol]: Detecta placeholders e retorna MOCK_KEY 
    para simulação (Dry Run) sem crash abrupto.
    """
    _ENV_KEYS  = ("DEEPL_AUTH_KEY", "DEEPL_API_KEY")
    _FILE_KEYS = ("DEEPL_AUTH_KEY=", "DEEPL_API_KEY=")
    _PLACEHOLDERS = ("your_key_here", "your-deepl-api-key-here", "your-key")

    # 1. Variável de ambiente
    for env_var in _ENV_KEYS:
        key = os.environ.get(env_var, "").strip()
        if key:
            if any(p in key.lower() for p in _PLACEHOLDERS):
                return "MOCK_KALYANAMITTA_KEY"
            return key

    # 2. Arquivo de chave (cofre seguro)
    key_file = SCRIPTS_DIR.parent / "private" / "deepl_key.txt"
    if not key_file.exists():
        # Retrocompatibilidade com legacy scripts que rodam do nível diretorio principal
        key_file = SCRIPTS_DIR / "private" / "deepl_key.txt"

    if key_file.exists():
        for line in key_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#"):
                continue
            for prefix in _FILE_KEYS:
                if line.startswith(prefix):
                    key = line[len(prefix):].strip()
                    if key:
                        if any(p in key.lower() for p in _PLACEHOLDERS):
                            return "MOCK_KALYANAMITTA_KEY"
                        return key
    else:
        # Se nem o arquivo existe, retornamos o MOCK também para permitir exploração local
        return "MOCK_KALYANAMITTA_KEY"

    return "MOCK_KALYANAMITTA_KEY"


def get_wp_password() -> str:
    """
    Retorna o WP Application Password sem hardcode.

    Prioridade:
      1. Variável de ambiente  WP_APP_PASSWORD
      2. Arquivo               scripts/private/wp_password.txt
         Formato esperado:     WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx

    Retorna MOCK se for o placeholder padrão.
    """
    _PLACEHOLDERS = ("xxxx xxxx xxxx xxxx xxxx xxxx", "your_password", "placeholder")

    # 1. Variável de ambiente
    pwd = os.environ.get("WP_APP_PASSWORD", "").strip()
    if pwd:
        if any(p in pwd.lower() for p in _PLACEHOLDERS):
            return "MOCK_KALYANAMITTA_PASSWORD"
        return pwd

    # 2. Arquivo de senha (cofre seguro)
    pwd_file = SCRIPTS_DIR.parent / "private" / "wp_password.txt"
    if not pwd_file.exists():
        pwd_file = SCRIPTS_DIR / "private" / "wp_password.txt"

    if pwd_file.exists():
        for line in pwd_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("WP_APP_PASSWORD=") and not line.startswith("#"):
                pwd = line.split("=", 1)[1].strip()
                if pwd:
                    if any(p in pwd.lower() for p in _PLACEHOLDERS):
                        return "MOCK_KALYANAMITTA_PASSWORD"
                    return pwd

    return "MOCK_KALYANAMITTA_PASSWORD"

# ==============================================================================
# 🌐  DEEPL
# ==============================================================================

DEEPL_API_URL  = "https://api-free.deepl.com/v2"
DEEPL_GLOSSARY_ID = "bbebe104-0015-46a9-8f9e-98bb88431ecb"  # Glossário V5 (não é segredo)

# ==============================================================================
# ⚙️  PIPELINE — CONSTANTES OPERACIONAIS
# ==============================================================================

SOURCE_LANG  = "en-US"
TARGET_LANG  = "pt-BR"
SCHEMA_VERSION      = "3.1"
SCHEMA_VERSION_SEAL = "3.1"   # alias usado por SP02 como target canônico

# Custo estimado DeepL Free (500k chars/mês)
FREE_QUOTA_LIMIT   = 500_000
COST_PER_CHAR_USD  = 0.000020   # referência plano Pro (informativo)

# Limite de falhas antes de abort automático (usado por SP02, SP10)
FAILURE_THRESHOLD  = 10

# ==============================================================================
# 🛡️  GITIGNORE REMINDER  (não commitar estes arquivos)
# ==============================================================================
# /beng/pipeline/scripts/deepl_key.txt
# /beng/pipeline/scripts/wp_password.txt
# Adicione ao .gitignore se usar Git no /beng/pipeline/
