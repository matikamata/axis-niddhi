#!/usr/bin/env bash
# ==============================================================================
# 🔱 BRASILEIRINHO ENGINE — SG00_reset_workspace.sh
# ==============================================================================
# Versão:  V5.1 (AXIS-NIDDHI Hardening Edition)
# Data:    2026-03-07
# Origem:  reset_brasileirinho_v12.2.sh (Phase v3.2)
#
# HARDENING V5.1 vs v12.2:
#   ★ Todas as variáveis via BENG_BASE env (relocatable)
#   ★ Limpeza de dirs de trabalho do pipeline (01/02 — NOT 09-csl)
#   ★ set -euo pipefail (strict mode)
#   ★ Pre-flight check sem abort desnecessário
#   ★ Cores declaradas explicitamente (RC-02)
#   ★ Cleanup de .tmp e .bak orphans em scripts/
#   ★ Preserva: 09-csl, metadata, logs (não destrutivo para dados SP)
#   ★ BENG_AUTO_RESET=true para CI
#
# SEQUÊNCIA: SG00 → SG01 → SG02 → SG03 → SG04
#
# USO:
#   bash SG00_reset_workspace.sh               # interativo
#   BENG_AUTO_RESET=true bash SG00_...         # CI/headless
# ==============================================================================

set -euo pipefail

# ==============================================================================
# 1. CONFIGURAÇÃO (via env com fallback canônico)
# ==============================================================================

BENG_BASE="${BENG_BASE:-/beng-fut/pipeline}"
BENG_ROOT="${BENG_BASE%/pipeline}"

SOURCES_DIR="$BENG_ROOT/sources"
RUNTIME_DIR="$BENG_ROOT/wordpress/runtime_wp"
PIPELINE_DIR="$BENG_BASE"
WP_DIR="$BENG_ROOT/wordpress"

DB_NAME="beng_wp_21"
DB_WP_USER="wp_user"
DB_WP_PASS="wp_pass123"
WP_ADMIN_USER="${WP_ADMIN_USER:-axis_niddhi}"  # usuário técnico do pipeline — NÃO usar admins reais
WP_ADMIN_EMAIL="${WP_ADMIN_EMAIL:-axis-niddhi@pipeline.local}"
WP_ALIAS="beng_feb2026"

CURRENT_USER="${SUDO_USER:-$USER}"

# Cores (todas declaradas — RC-02)
GREEN='\033[0;32m'
BLUE='\033[0;36m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;96m'
GRAY='\033[0;37m'
NC='\033[0m'

# ==============================================================================
# 🛡️  GUARDIÃO DE ERROS — Remoção segura de diretórios
# ==============================================================================
clean_dir() {
    local target="$1"
    if [ ! -e "$target" ]; then
        return 0  # Já não existe — OK
    fi
    rm -rf "$target" 2>/dev/null || {
        echo -e "${RED}❌ ERRO CRÍTICO: Falha ao limpar $target${NC}"
        echo -e "${YELLOW}💡 CAUSA provável: Arquivos criados por outro usuário (root vs $CURRENT_USER)${NC}"
        echo -e "${CYAN}🚀 AÇÃO: Execute o comando abaixo e tente novamente:${NC}"
        echo -e "   sudo chown -R $CURRENT_USER:$CURRENT_USER $BENG_BASE"
        exit 1
    }
}

# ==============================================================================
# 2. BANNER
# ==============================================================================

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  BRASILEIRINHO ENGINE — SG00 Reset Workspace V5.1        ║"
echo "║  AXIS-NIDDHI Edition                                      ║"
echo "║  DB: beng_wp_21  ·  WP: beng_feb2026                     ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}⚠️  ATENÇÃO: Este script vai:${NC}"
echo "   • Deletar e recriar RUNTIME_DIR: $RUNTIME_DIR"
echo "   • Recriar banco de dados: $DB_NAME"
echo "   • Limpar dirs de trabalho: 01-extracted-htmls/, 02-preprocessed/"
echo "   • PRESERVAR: 09-csl/, metadata/, logs/"
echo ""

# ==============================================================================
# 3. CONFIRMAÇÃO (bypass via BENG_AUTO_RESET=true)
# ==============================================================================

if [ "${BENG_AUTO_RESET:-false}" != "true" ]; then
    read -rp "Confirmar reset completo? [y/N]: " confirm
    if [ "${confirm,,}" != "y" ]; then
        echo -e "${YELLOW}Reset cancelado.${NC}"
        exit 0
    fi
fi

# ==============================================================================
# 4. PRE-FLIGHT
# ==============================================================================

echo -e "\n${BLUE}>>> PRE-FLIGHT. Verificando $BENG_ROOT...${NC}"

if ! mountpoint -q "$BENG_ROOT" 2>/dev/null; then
    # /beng-fut pode não ser um mountpoint separado — verificar se existe e é acessível
    if [ ! -d "$BENG_ROOT" ]; then
        echo -e "${RED}❌ $BENG_ROOT não existe. Abortando.${NC}"
        exit 1
    fi
    echo -e "${GRAY}   ℹ️  $BENG_ROOT não é mountpoint separado — OK (diretório local)${NC}"
else
    echo -e "    ${GREEN}✅ $BENG_ROOT montada${NC}"
    df -h "$BENG_ROOT" | tail -1 | awk '{print "    Espaço livre: " $4 " de " $2}'
fi

if [ ! -d "$SOURCES_DIR" ]; then
    echo -e "${RED}❌ Sources dir não encontrado: $SOURCES_DIR${NC}"
    exit 1
fi

# ==============================================================================
# 5. DETECTAR BACKUP ZIP
# ==============================================================================

echo -e "\n${BLUE}>>> 0. Detectando Backup ZIP...${NC}"
ZIP_FILE=$(find "$SOURCES_DIR" -maxdepth 1 -name "*.zip" 2>/dev/null | sort | tail -1)
if [ -z "$ZIP_FILE" ]; then
    echo -e "${RED}❌ ZIP não encontrado em $SOURCES_DIR${NC}"
    echo "   Coloque o backup .zip em: $SOURCES_DIR"
    exit 1
fi
echo -e "    ZIP: ${CYAN}$ZIP_FILE${NC}"
echo -e "    Tamanho: $(du -sh "$ZIP_FILE" | awk '{print $1}')"

# ==============================================================================
# 6. VERIFICAR DEPENDÊNCIAS
# ==============================================================================

echo -e "\n${BLUE}>>> 1. Verificando dependências...${NC}"
MISSING=0
for cmd in apache2 php mysql wp unzip curl; do
    if command -v "$cmd" &>/dev/null; then
        echo -e "    ${GREEN}✅ $cmd${NC}"
    else
        echo -e "    ${RED}❌ $cmd não encontrado${NC}"
        case "$cmd" in
            wp)    echo "       WP-CLI: curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar && chmod +x wp-cli.phar && sudo mv wp-cli.phar /usr/local/bin/wp" ;;
            mysql) echo "       sudo apt install mysql-server -y" ;;
            *)     echo "       sudo apt install apache2 php php-mysql libapache2-mod-php unzip curl -y" ;;
        esac
        MISSING=1
    fi
done
if [ "$MISSING" -ne 0 ]; then
    echo -e "${RED}❌ Dependências ausentes. Instale e re-execute.${NC}"
    exit 1
fi

# Dependências Python do pipeline
echo -e "    ${GRAY}Verificando módulos Python...${NC}"
PYTHON_DEPS=("pymysql" "requests" "deepl")
for dep in "${PYTHON_DEPS[@]}"; do
    if python3 -c "import $dep" &>/dev/null; then
        echo -e "    ${GREEN}✅ python:$dep${NC}"
    else
        echo -e "    ${YELLOW}⚙️  Instalando python:$dep...${NC}"
        pip3 install "$dep" --break-system-packages -q 2>/dev/null || \
        pip3 install "$dep" -q 2>/dev/null || \
        echo -e "    ${RED}❌ Falha ao instalar $dep — verifique manualmente${NC}"
    fi
done

# ==============================================================================
# 7. INICIAR MYSQL
# ==============================================================================

echo -e "\n${BLUE}>>> 2. Garantindo MySQL ativo...${NC}"
if ! sudo systemctl is-active --quiet mysql; then
    sudo systemctl start mysql
    sleep 2
fi
sudo systemctl enable mysql --quiet 2>/dev/null || true
echo -e "    ${GREEN}✅ MySQL ativo${NC}"

# ==============================================================================
# 8. LIMPEZA E EXTRAÇÃO
# ==============================================================================

echo -e "\n${BLUE}>>> 3. Preparando diretório de trabalho...${NC}"
clean_dir "$RUNTIME_DIR"
mkdir -p "$RUNTIME_DIR"
mkdir -p "$WP_DIR"

echo -e "    Extraindo ZIP... ($(du -sh "$ZIP_FILE" | awk '{print $1}'))"
unzip -q "$ZIP_FILE" -d "$RUNTIME_DIR"
echo -e "    ${GREEN}✅ Extração completa${NC}"

# ==============================================================================
# 9. EXORCISMO DE PLUGINS TÓXICOS
# ==============================================================================

echo -e "\n${BLUE}>>> 4. Exorcizando arquivos tóxicos...${NC}"
rm -f  "$RUNTIME_DIR/wp-content/object-cache.php"     2>/dev/null || true
rm -f  "$RUNTIME_DIR/wp-content/advanced-cache.php"   2>/dev/null || true
rm -f  "$RUNTIME_DIR/wp-content/db.php"               2>/dev/null || true
rm -rf "$RUNTIME_DIR/wp-content/cache"                2>/dev/null || true
rm -rf "$RUNTIME_DIR/wp-content/mu-plugins"           2>/dev/null || true

PLUGINS_DIR="$RUNTIME_DIR/wp-content/plugins"
BAD_PLUGINS=(
    "wps-hide-login"
    "rename-wp-login"
    "all-in-one-wp-security-and-firewall"
    "wordfence"
    "ithemes-security-pro"
    "redirection"
    "safe-redirect-manager"
    "404-to-301"
)
for plugin in "${BAD_PLUGINS[@]}"; do
    if [ -d "$PLUGINS_DIR/$plugin" ]; then
        rm -rf "$PLUGINS_DIR/$plugin"
        echo -e "    ${RED}🔥 Aniquilado: $plugin${NC}"
    fi
done

mkdir -p "$RUNTIME_DIR/wp-content/plugins_QUARANTINE"
for seo in "seo-by-rank-math" "seo-by-rank-math-pro"; do
    if [ -d "$PLUGINS_DIR/$seo" ]; then
        mv "$PLUGINS_DIR/$seo" "$RUNTIME_DIR/wp-content/plugins_QUARANTINE/"
        echo -e "    ${YELLOW}🔒 Quarentena: $seo${NC}"
    fi
done
echo -e "    ${GREEN}✅ Exorcismo completo${NC}"

# ==============================================================================
# 10. BANCO DE DADOS
# ==============================================================================

echo -e "\n${BLUE}>>> 5. Restaurando banco de dados...${NC}"
sudo mysql -e "PURGE BINARY LOGS BEFORE NOW();" 2>/dev/null || true
sudo mysql -e "DROP DATABASE IF EXISTS $DB_NAME;"
sudo mysql -e "CREATE DATABASE $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

sudo mysql <<-EOF
    CREATE USER IF NOT EXISTS '$DB_WP_USER'@'localhost' IDENTIFIED BY '$DB_WP_PASS';
    GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_WP_USER'@'localhost';
    FLUSH PRIVILEGES;
EOF
echo -e "    ${GREEN}✅ DB '$DB_NAME' criado, usuário '$DB_WP_USER' OK${NC}"

# Localizar SQL (dentro do ZIP extraído OU em beng-launch)
SQL_FILE=$(find "$RUNTIME_DIR" -maxdepth 1 -name "*.sql" 2>/dev/null | head -1)
if [ -z "$SQL_FILE" ]; then
    SQL_FILE=$(find "$RUNTIME_DIR" -name "tenweb_backup_db.sql" 2>/dev/null | head -1)
fi
# Fallback: beng-launch
if [ -z "$SQL_FILE" ]; then
    SQL_FILE=$(find "$BENG_ROOT/../beng-launch" -name "*.sql" 2>/dev/null | head -1)
fi
if [ -z "$SQL_FILE" ]; then
    echo -e "${RED}❌ SQL dump não encontrado.${NC}"
    echo "   Deve estar dentro do ZIP ou em /beng-launch/"
    exit 1
fi

echo -e "    SQL: ${CYAN}$SQL_FILE${NC}"
echo -e "    Início: $(date '+%H:%M:%S')"
if command -v pv &>/dev/null; then
    pv "$SQL_FILE" | sudo mysql "$DB_NAME"
else
    sudo mysql "$DB_NAME" < "$SQL_FILE"
fi
echo -e "    ${GREEN}✅ SQL importado — $(date '+%H:%M:%S')${NC}"

# ==============================================================================
# 11. DETECTAR PREFIXO DE TABELA
# ==============================================================================

echo -e "\n${BLUE}>>> 6. Detectando prefixo de tabela...${NC}"
DB_PREFIX=$(sudo mysql "$DB_NAME" -N -e "SHOW TABLES LIKE '%options';" 2>/dev/null | head -1 | sed 's/options$//')
echo -e "    Prefixo: '${CYAN}$DB_PREFIX${NC}'"

# ==============================================================================
# 12. CONFIGURAR WP-CONFIG
# ==============================================================================

echo -e "\n${BLUE}>>> 7. Configurando wp-config.php...${NC}"
CONFIG_FILE="$RUNTIME_DIR/wp-config.php"
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}❌ wp-config.php não encontrado em $RUNTIME_DIR${NC}"
    exit 1
fi

sed -i "/DB_NAME\|DB_USER\|DB_PASSWORD\|DB_HOST\|WP_HOME\|WP_SITEURL\|WP_CACHE\|WP_ENVIRONMENT/d" "$CONFIG_FILE"
sed -i "2i define( 'DB_NAME',             '$DB_NAME' );"                         "$CONFIG_FILE"
sed -i "3i define( 'DB_USER',             '$DB_WP_USER' );"                      "$CONFIG_FILE"
sed -i "4i define( 'DB_PASSWORD',         '$DB_WP_PASS' );"                      "$CONFIG_FILE"
sed -i "5i define( 'DB_HOST',             'localhost' );"                         "$CONFIG_FILE"
sed -i "6i define( 'WP_HOME',             'http://localhost/$WP_ALIAS' );"        "$CONFIG_FILE"
sed -i "7i define( 'WP_SITEURL',          'http://localhost/$WP_ALIAS' );"        "$CONFIG_FILE"
sed -i "8i define( 'WP_ENVIRONMENT_TYPE', 'local' );"                            "$CONFIG_FILE"
sed -i "9i define( 'WP_CACHE',            false );"                              "$CONFIG_FILE"
echo -e "    ${GREEN}✅ wp-config.php configurado${NC}"

# ==============================================================================
# 13. LIMPAR REGRAS DE LOGIN TÓXICAS
# ==============================================================================

echo -e "\n${BLUE}>>> 8. Limpando regras de login...${NC}"
sudo mysql "$DB_NAME" -e \
    "DELETE FROM ${DB_PREFIX}options WHERE option_name IN \
    ('whl_page','rwl_page','admin_slug','aio_wp_security_configs');" 2>/dev/null || true
echo -e "    ${GREEN}✅ Regras removidas${NC}"

# ==============================================================================
# 14. APACHE
# ==============================================================================

echo -e "\n${BLUE}>>> 9. Configurando Apache...${NC}"
# Permissões para www-data atravessar /beng-fut
chmod o+x "$BENG_ROOT"          2>/dev/null || true
chmod o+x "$WP_DIR"             2>/dev/null || true
chmod o+x "$RUNTIME_DIR"        2>/dev/null || true

# .htaccess com RewriteBase correto para o alias do WP
tee "$RUNTIME_DIR/.htaccess" > /dev/null << HTEOF
# BEGIN WordPress
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteBase /$WP_ALIAS/
RewriteRule ^index\.php$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /$WP_ALIAS/index.php [L]
</IfModule>
# END WordPress
HTEOF

# AllowOverride para que o .htaccess seja respeitado (obrigatório para WP REST API)
tee /etc/apache2/conf-available/beng-override.conf > /dev/null << APACHECONF
<Directory /beng-fut/wordpress/runtime_wp>
    Options FollowSymLinks
    AllowOverride All
    Require all granted
</Directory>
<Directory /var/www/html/$WP_ALIAS>
    Options FollowSymLinks
    AllowOverride All
    Require all granted
</Directory>
APACHECONF

# Symlink Apache
APACHE_LINK="/var/www/html/$WP_ALIAS"
if [ -L "$APACHE_LINK" ]; then
    rm -f "$APACHE_LINK"
fi
ln -sf "$RUNTIME_DIR" "$APACHE_LINK"

# Habilitar módulos e conf
a2enconf beng-override 2>/dev/null || true
a2enmod rewrite 2>/dev/null || true
systemctl reload apache2 2>/dev/null || true
echo -e "    ${GREEN}✅ Apache configurado: http://localhost/$WP_ALIAS${NC}"
echo -e "    ${GRAY}   .htaccess: RewriteBase=/$WP_ALIAS/ | AllowOverride: All${NC}"

# ==============================================================================
# 15. SEARCH-REPLACE (WP-CLI)
# ==============================================================================

echo -e "\n${BLUE}>>> 10. Aplicando search-replace (WP-CLI)...${NC}"
OLD_URLS=(
    "http://puredhamma.net"
    "https://puredhamma.net"
    "http://brasileirinho.localhost"
    "http://localhost/brasileirinho"
    "http://localhost/beng_jan2026"
)
NEW_URL="http://localhost/$WP_ALIAS"

for old in "${OLD_URLS[@]}"; do
    wp search-replace "$old" "$NEW_URL" \
        --path="$RUNTIME_DIR" \
        --allow-root \
        --quiet 2>/dev/null || true
done
echo -e "    ${GREEN}✅ Search-replace concluído → $NEW_URL${NC}"

# Desativar plugins incompatíveis com ambiente local
# tenweb-speed-optimizer: CDN/cache do TenWeb quebra CSS em localhost
LOCAL_INCOMPATIBLE_PLUGINS=(
    "tenweb-speed-optimizer"
    "cloudflare"
)
for plugin in "${LOCAL_INCOMPATIBLE_PLUGINS[@]}"; do
    wp --path="$RUNTIME_DIR" --allow-root plugin deactivate "$plugin" --quiet 2>/dev/null && \
        echo -e "    ${YELLOW}🔇 Desativado (incompatível local): $plugin${NC}" || true
done

# ==============================================================================
# 16. LIMPAR DIRS DE TRABALHO DO PIPELINE (01/02 — preserva 09-csl)
# ==============================================================================

echo -e "\n${BLUE}>>> 11. Limpando dirs de trabalho do pipeline...${NC}"
for dir in "01-extracted-htmls" "02-preprocessed"; do
    target="$BENG_BASE/$dir"
    clean_dir "$target"
    echo -e "    ${YELLOW}🗑️  Limpo: $dir${NC}"
done

# Cleanup de .tmp e .bak orphans em scripts/ (RC-05 + cleanup geral)
find "$BENG_BASE/scripts" -name "*.tmp" -delete 2>/dev/null || true
find "$BENG_BASE/scripts" -name "*.bak" -mtime +7 -delete 2>/dev/null || true

# Recrear dirs vazios
mkdir -p "$BENG_BASE/01-extracted-htmls/en-US"
mkdir -p "$BENG_BASE/02-preprocessed/en-US"
mkdir -p "$BENG_BASE/logs"
mkdir -p "$BENG_BASE/recovery"
mkdir -p "$BENG_BASE/metadata"
echo -e "    ${GREEN}✅ Dirs de trabalho limpos e recriados${NC}"
echo -e "    ${GRAY}   ℹ️  09-csl/ PRESERVADA${NC}"

# ==============================================================================
# 17. VERIFICAÇÃO FINAL
# ==============================================================================

echo -e "\n${BLUE}>>> 12. Verificação final...${NC}"

# WordPress acessível
WP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost/$WP_ALIAS/wp-login.php" 2>/dev/null || echo "000")
if [ "$WP_STATUS" = "200" ] || [ "$WP_STATUS" = "302" ]; then
    echo -e "    ${GREEN}✅ WordPress respondendo: http://localhost/$WP_ALIAS (HTTP $WP_STATUS)${NC}"
else
    echo -e "    ${YELLOW}⚠️  WordPress HTTP $WP_STATUS — pode levar alguns segundos para responder${NC}"
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  SG00 CONCLUÍDO — Workspace resetado com sucesso          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${CYAN}WordPress local  :${NC} http://localhost/$WP_ALIAS"
echo -e "  ${CYAN}WP Admin         :${NC} http://localhost/$WP_ALIAS/wp-admin"
echo -e "  ${CYAN}Usuário          :${NC} $WP_ADMIN_USER"
echo -e "  ${CYAN}Runtime dir      :${NC} $RUNTIME_DIR"
echo -e "  ${CYAN}Pipeline base    :${NC} $BENG_BASE"

# ==============================================================================
# 13. GERAR WP APPLICATION PASSWORD AUTOMATICAMENTE
# ==============================================================================

echo ""
echo -e "${BLUE}>>> 13. Criando usuário técnico do pipeline e gerando Application Password...${NC}"

WP_PASSWORD_FILE="$BENG_BASE/scripts/private/wp_password.txt"
WP_PATH="$RUNTIME_DIR"
WP_CLI="wp --path=$WP_PATH --allow-root"

# Warmup: garantir que o WordPress está completamente inicializado antes do user create
# (necessário após restauração do banco — WP-CLI pode falhar sem um request HTTP prévio)
curl -s "http://localhost/$WP_ALIAS/" -o /dev/null --max-time 5 || true
sleep 1

# Criar usuário técnico dedicado se não existir
# NÃO reusar logins reais (Prof. Lal, admins do site) — este é um user de serviço

if $WP_CLI user get "$WP_ADMIN_USER" --field=user_login &>/dev/null; then
    echo -e "    ${GRAY}ℹ️  Usuário '$WP_ADMIN_USER' já existe — reutilizando.${NC}"
else
    TEMP_PASS=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 32)
    CREATE_OUT=$($WP_CLI user create "$WP_ADMIN_USER" "$WP_ADMIN_EMAIL" \
        --role=administrator \
        --user_pass="$TEMP_PASS" \
        --display_name="AXIS-NIDDHI Pipeline" 2>&1)
    if $WP_CLI user get "$WP_ADMIN_USER" --field=user_login &>/dev/null; then
        echo -e "    ${GREEN}✅ Usuário técnico '$WP_ADMIN_USER' criado.${NC}"
    else
        echo -e "    ${RED}❌ Falha ao criar usuário técnico: $CREATE_OUT${NC}"
        WP_ADMIN_USER=""
    fi
fi

# Gerar Application Password para o usuário técnico
if [ -n "$WP_ADMIN_USER" ]; then
    # Limpar senhas antigas deste usuário para evitar acúmulo
    $WP_CLI user application-password list "$WP_ADMIN_USER" \
        --fields=uuid --format=csv 2>/dev/null \
        | tail -n +2 \
        | while read -r uuid; do
            $WP_CLI user application-password delete \
                "$WP_ADMIN_USER" "$uuid" --quiet 2>/dev/null || true
        done

    RAW_PASS=$($WP_CLI \
        user application-password create "$WP_ADMIN_USER" "AXIS-NIDDHI-SD04" \
        --porcelain 2>/dev/null || echo "")

    if [ -n "$RAW_PASS" ]; then
        echo "WP_APP_PASSWORD=$RAW_PASS" > "$WP_PASSWORD_FILE"
        chmod 600 "$WP_PASSWORD_FILE"
        echo -e "    ${GREEN}✅ Application Password gerada e salva automaticamente.${NC}"
        echo -e "       ${GRAY}Arquivo: $WP_PASSWORD_FILE${NC}"
        echo -e "       ${GRAY}Usuário: $WP_ADMIN_USER (conta técnica — não é login real do site)${NC}"
    else
        echo -e "    ${YELLOW}⚠️  Falha ao gerar Application Password via WP-CLI.${NC}"
        echo -e "    ${YELLOW}   Gere manualmente em: WP Admin → Usuários → $WP_ADMIN_USER → Application Passwords${NC}"
        echo -e "    ${YELLOW}   Salve em: $WP_PASSWORD_FILE | Formato: WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx${NC}"
    fi
fi
echo ""
echo -e "  ${YELLOW}Próximo passo: SG01_extract_html.py${NC}"
echo ""
