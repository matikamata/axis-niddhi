#!/bin/bash
# ==============================================================================
# 🔱 BRASILEIRINHO ENGINE - RESET v12.2 (AXIS-NIDDHI EDITION)
# Fase v3.2 — 20260306
#
# Delta vs v12.1:
# - Lê o ZIP canônico de /beng-fut/sources/ (removeu lógica de Pen Drive)
# - RUNTIME_DIR : /beng-fut/wordpress/runtime_wp
# - PIPELINE_DIR: /beng-fut/pipeline
# ==============================================================================

set -e

# --- CONFIGURAÇÃO ---
CURRENT_USER="${SUDO_USER:-$USER}"

# ★ AXIS-NIDDHI
BENG_ROOT="/beng-fut"
SOURCES_DIR="$BENG_ROOT/sources"
RUNTIME_DIR="$BENG_ROOT/wordpress/runtime_wp"
PIPELINE_DIR="$BENG_ROOT/pipeline"
DB_NAME="beng_wp_21"
DB_WP_USER="wp_user"
DB_WP_PASS="wp_pass123"
WP_ADMIN_USER="guardiao"
WP_ADMIN_PASS="admin123"
WP_ALIAS="beng_feb2026"

GREEN='\033[0;32m'
BLUE='\033[0;36m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════╗"
echo "║  BRASILEIRINHO ENGINE — RESET v12.2      ║"
echo "║  AXIS-NIDDHI Edition — Fase v3.2         ║"
echo "║  DB: beng_wp_21  ·  WP: beng_feb2026     ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"

# --- PRE-FLIGHT: /beng-fut montada? ---
echo -e "${BLUE}>>> PRE-FLIGHT. Verificando $BENG_ROOT...${NC}"
if ! mountpoint -q "$BENG_ROOT"; then
    echo -e "${RED}❌ $BENG_ROOT não está montada. Abortando.${NC}"
    echo "   sudo mount $BENG_ROOT"
    exit 1
fi
echo "    ✅ $BENG_ROOT montada"
df -h "$BENG_ROOT" | tail -1 | awk '{print "    Espaço livre: " $4 " de " $2}'

# --- 0. DETECTAR BACKUP ZIP CANÔNICO ---
echo -e "${BLUE}>>> 0. Detectando Backup ZIP...${NC}"
ZIP_FILE=$(find "$SOURCES_DIR" -maxdepth 1 -name "*.zip" | head -1)
if [ -z "$ZIP_FILE" ]; then
    echo -e "${RED}❌ ZIP não encontrado em $SOURCES_DIR${NC}"
    exit 1
fi
echo "    ZIP: $ZIP_FILE"

# --- 1. VERIFICAR DEPENDÊNCIAS ---
echo -e "${BLUE}>>> 1. Verificando dependências...${NC}"
for cmd in apache2 php mysql wp unzip curl; do
    if command -v $cmd &>/dev/null; then
        echo -e "    ✅ $cmd"
    else
        echo -e "    ${RED}❌ $cmd não encontrado${NC}"
        [ "$cmd" = "wp" ] && echo "       WP-CLI: curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar && chmod +x wp-cli.phar && sudo mv wp-cli.phar /usr/local/bin/wp"
        [ "$cmd" != "wp" ] && echo "       sudo apt install apache2 php php-mysql libapache2-mod-php unzip curl -y"
        exit 1
    fi
done

# --- 2. INICIAR MYSQL ---
echo -e "${BLUE}>>> 2. Garantindo MySQL ativo...${NC}"
if ! sudo systemctl is-active --quiet mysql; then
    sudo systemctl start mysql
    sleep 2
fi
sudo systemctl enable mysql --quiet
echo "    ✅ MySQL ativo"

# --- 3. LIMPEZA E EXTRAÇÃO ---
echo -e "${BLUE}>>> 3. Preparando diretório de trabalho...${NC}"
sudo rm -rf "$RUNTIME_DIR"
mkdir -p "$RUNTIME_DIR"
mkdir -p "$BENG_ROOT/wordpress"

echo "    Extraindo ZIP... ($(du -sh "$ZIP_FILE" | awk '{print $1}'))"
unzip -q "$ZIP_FILE" -d "$RUNTIME_DIR"
echo "    ✅ Extração completa"

# --- 4. EXORCISMO ---
echo -e "${BLUE}>>> 4. Exorcizando arquivos tóxicos...${NC}"
rm -f  "$RUNTIME_DIR/wp-content/object-cache.php"
rm -f  "$RUNTIME_DIR/wp-content/advanced-cache.php"
rm -f  "$RUNTIME_DIR/wp-content/db.php"
rm -rf "$RUNTIME_DIR/wp-content/cache"
rm -rf "$RUNTIME_DIR/wp-content/mu-plugins"

PLUGINS_DIR="$RUNTIME_DIR/wp-content/plugins"
BAD_PLUGINS=(
    "wps-hide-login" "rename-wp-login"
    "all-in-one-wp-security-and-firewall" "wordfence" "ithemes-security-pro"
    "redirection" "safe-redirect-manager" "404-to-301"
)
for plugin in "${BAD_PLUGINS[@]}"; do
    [ -d "$PLUGINS_DIR/$plugin" ] && rm -rf "$PLUGINS_DIR/$plugin" && \
        echo -e "    ${RED}Aniquilado: $plugin${NC}"
done

mkdir -p "$RUNTIME_DIR/wp-content/plugins_QUARANTINE"
for seo in "seo-by-rank-math" "seo-by-rank-math-pro"; do
    [ -d "$PLUGINS_DIR/$seo" ] && \
        mv "$PLUGINS_DIR/$seo" "$RUNTIME_DIR/wp-content/plugins_QUARANTINE/"
done
echo "    ✅ Exorcismo completo"

# --- 5. BANCO DE DADOS ---
echo -e "${BLUE}>>> 5. Restaurando banco de dados...${NC}"
sudo mysql -e "PURGE BINARY LOGS BEFORE NOW();" 2>/dev/null || true
sudo mysql -e "DROP DATABASE IF EXISTS $DB_NAME;"
sudo mysql -e "CREATE DATABASE $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

sudo mysql << EOF
CREATE USER IF NOT EXISTS '$DB_WP_USER'@'localhost' IDENTIFIED BY '$DB_WP_PASS';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_WP_USER'@'localhost';
FLUSH PRIVILEGES;
EOF
echo "    ✅ DB '$DB_NAME' criado, usuário '$DB_WP_USER' OK"

# AQUI ELE PROCURA O SQL DENTRO DO RUNTIME_DIR (onde o ZIP foi extraído)
SQL_FILE=$(find "$RUNTIME_DIR" -maxdepth 1 -name "*.sql" | head -1)
[ -z "$SQL_FILE" ] && SQL_FILE=$(find "$RUNTIME_DIR" -name "tenweb_backup_db.sql" | head -1)
if [ -z "$SQL_FILE" ]; then
    echo -e "${RED}❌ SQL não encontrado dentro do ZIP extraído${NC}"; exit 1
fi

echo "    Importando SQL ($(du -sh "$SQL_FILE" | awk '{print $1}'))..."
echo "    Início: $(date '+%H:%M:%S')"
if command -v pv &>/dev/null; then
    pv "$SQL_FILE" | sudo mysql "$DB_NAME"
else
    sudo mysql "$DB_NAME" < "$SQL_FILE"
fi
echo "    ✅ SQL importado — $(date '+%H:%M:%S')"

# --- 6. DETECTAR PREFIXO DE TABELA ---
echo -e "${BLUE}>>> 6. Detectando prefixo de tabela...${NC}"
DB_PREFIX=$(sudo mysql "$DB_NAME" -N -e "SHOW TABLES LIKE '%options';" | head -1 | sed 's/options$//')
echo "    Prefixo: '$DB_PREFIX'"

# --- 7. CONFIGURAR WP-CONFIG ---
echo -e "${BLUE}>>> 7. Configurando wp-config.php...${NC}"
CONFIG_FILE="$RUNTIME_DIR/wp-config.php"
sed -i "/DB_NAME\|DB_USER\|DB_PASSWORD\|DB_HOST\|WP_HOME\|WP_SITEURL\|WP_CACHE\|WP_ENVIRONMENT/d" "$CONFIG_FILE"
sed -i "2i define( 'DB_NAME',             '$DB_NAME' );"           "$CONFIG_FILE"
sed -i "3i define( 'DB_USER',             '$DB_WP_USER' );"        "$CONFIG_FILE"
sed -i "4i define( 'DB_PASSWORD',         '$DB_WP_PASS' );"        "$CONFIG_FILE"
sed -i "5i define( 'DB_HOST',             'localhost' );"           "$CONFIG_FILE"
sed -i "6i define( 'WP_HOME',             'http://localhost/$WP_ALIAS' );" "$CONFIG_FILE"
sed -i "7i define( 'WP_SITEURL',          'http://localhost/$WP_ALIAS' );" "$CONFIG_FILE"
sed -i "8i define( 'WP_ENVIRONMENT_TYPE', 'local' );"              "$CONFIG_FILE"
sed -i "9i define( 'WP_CACHE',            false );"                "$CONFIG_FILE"
echo "    ✅ wp-config.php configurado"

# --- 8. LIMPAR REGRAS DE LOGIN ---
echo -e "${BLUE}>>> 8. Limpando regras de login...${NC}"
sudo mysql "$DB_NAME" -e \
    "DELETE FROM ${DB_PREFIX}options WHERE option_name IN \
    ('whl_page','rwl_page','admin_slug','aio_wp_security_configs');" 2>/dev/null || true
echo "    ✅ Regras removidas"

# --- 9. APACHE ---
echo -e "${BLUE}>>> 9. Configurando Apache...${NC}"
sudo chmod o+x "$BENG_ROOT"
sudo chmod o+x "$BENG_ROOT/wordpress"

cat > "$RUNTIME_DIR/.htaccess" << HTEOF
# BEGIN WordPress
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]
RewriteBase /$WP_ALIAS/
RewriteRule ^index\.php$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /$WP_ALIAS/index.php [L]
</IfModule>
# END WordPress
HTEOF

cat > /tmp/beng_apache.conf << CONFEOF
Alias /$WP_ALIAS "$RUNTIME_DIR"
<Directory "$RUNTIME_DIR">
    Options Indexes FollowSymLinks
    AllowOverride All
    Require all granted
</Directory>
CONFEOF
sudo mv /tmp/beng_apache.conf /etc/apache2/sites-available/beng_feb2026.conf
sudo a2dissite brasileirinho.conf > /dev/null 2>&1 || true
sudo a2ensite beng_feb2026.conf > /dev/null 2>&1
sudo a2enmod rewrite > /dev/null 2>&1
if ! sudo systemctl is-active --quiet apache2; then
    echo "    Apache inativo — iniciando..."
    sudo systemctl start apache2
    sleep 1
fi
sudo systemctl enable apache2 --quiet 2>/dev/null || true
sudo systemctl reload apache2
echo "    ✅ Apache configurado — alias: /$WP_ALIAS"

# --- 10. WP-CLI ---
echo -e "${BLUE}>>> 10. Executando WP-CLI...${NC}"
mv "$PLUGINS_DIR" "${PLUGINS_DIR}_SAFE" 2>/dev/null || true
mkdir -p "$PLUGINS_DIR"

echo "    Substituindo URLs (origem → $WP_ALIAS)..."
for old_url in "https://puredhamma.net" "http://puredhamma.net" \
               "http://localhost/brasileirinho" "http://localhost/beng_feb2025"; do
    wp search-replace "$old_url" "http://localhost/$WP_ALIAS" \
        --path="$RUNTIME_DIR" --all-tables --allow-root --quiet
done

echo "    Criando usuário guardião..."
wp user create $WP_ADMIN_USER guardiao@local.dev \
    --user_pass="$WP_ADMIN_PASS" --role=administrator \
    --path="$RUNTIME_DIR" --allow-root --quiet 2>/dev/null || \
wp user update $WP_ADMIN_USER \
    --user_pass="$WP_ADMIN_PASS" --role=administrator \
    --path="$RUNTIME_DIR" --allow-root --quiet
echo "    ✅ WP-CLI completo"

# --- 11. RESTAURAR PLUGINS ---
echo -e "${BLUE}>>> 11. Restaurando plugins...${NC}"
rm -rf "$PLUGINS_DIR"
mv "${PLUGINS_DIR}_SAFE" "$PLUGINS_DIR" 2>/dev/null || true
for seo in "seo-by-rank-math" "seo-by-rank-math-pro"; do
    [ -d "$RUNTIME_DIR/wp-content/plugins_QUARANTINE/$seo" ] && \
        mv "$RUNTIME_DIR/wp-content/plugins_QUARANTINE/$seo" "$PLUGINS_DIR/"
done
rm -rf "$RUNTIME_DIR/wp-content/plugins_QUARANTINE"

SAFE_PLUGINS=(
    "generatepress" "gp-premium" "ubermenu" "dracula-dark-mode"
    "zeno-font-resizer" "compact-wp-audio-player" "bbpress" "gd-bbpress-toolbox"
)
for plugin in "${SAFE_PLUGINS[@]}"; do
    wp plugin is-installed $plugin --path="$RUNTIME_DIR" --allow-root 2>/dev/null && \
        wp plugin activate $plugin --path="$RUNTIME_DIR" --allow-root --quiet && \
        echo "    + $plugin"
done

# --- 12. PERMISSÕES FINAIS ---
echo -e "${BLUE}>>> 12. Permissões finais...${NC}"
sudo chown -R www-data:www-data "$RUNTIME_DIR"
sudo chmod -R 755 "$RUNTIME_DIR"
sudo chmod o+x "$BENG_ROOT"
sudo chmod o+x "$BENG_ROOT/wordpress"
echo "    ✅ Permissões OK"

# --- RESULTADO FINAL ---
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost/$WP_ALIAS/" 2>/dev/null)

echo ""
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════╗"
echo "║  ✅ RESET v12.2 CONCLUÍDO!               ║"
echo "║  AXIS-NIDDHI — Fase v3.2 — 20260306      ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"
echo "  URL:       http://localhost/$WP_ALIAS"
echo "  Admin:     http://localhost/$WP_ALIAS/wp-admin"
echo "  Login:     $WP_ADMIN_USER / $WP_ADMIN_PASS"
echo "  HTTP:      $HTTP_CODE"
echo "  Runtime:   $RUNTIME_DIR"
echo "  Pipeline:  $PIPELINE_DIR"
echo "  DB:        $DB_NAME"
echo ""
[ "$HTTP_CODE" = "200" ] && \
    echo -e "${GREEN}  Site respondendo. 🌿 Experimentum Crucis v3 pode iniciar.${NC}" || \
    echo -e "${YELLOW}  HTTP $HTTP_CODE — verifique Apache se necessário.${NC}"
