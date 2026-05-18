#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║  🖨️  AXIS-NIDDHI — Batch Print Engine v1.0                  ║
║  Automação de impressão de Ensaios (Scientific Essays)      ║
║  para revisão profissional do corpus PureDhamma.net         ║
╚══════════════════════════════════════════════════════════════╝

Fluxo:
  1. Lê Print_Translation_Control_Center.csv
  2. Filtra pelo Lote escolhido (apenas Status=DONE, Printed?=vazio)
  3. Gera PDFs via Chrome headless (com cores preservadas)
  4. Mostra resumo e pede confirmação
  5. Envia para impressora CUPS (Epson L4260)
  6. Atualiza CSV marcando Printed?=DONE

Uso:
  python3 pipeline/scripts/tools/print_batch.py
  python3 pipeline/scripts/tools/print_batch.py --lote 1
  python3 pipeline/scripts/tools/print_batch.py --lote 1 --pdf-only
"""

import csv
import subprocess
import sys
import os
import shutil
import tempfile
import threading
import http.server
import socketserver
import time
from pathlib import Path
from datetime import datetime

# ══════════════════════════════════════════════════════════════
# CONFIGURAÇÃO
# ══════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).resolve().parent
PIPELINE_DIR = SCRIPT_DIR.parent.parent  # pipeline/
PROJECT_ROOT = PIPELINE_DIR.parent       # bengyond-playground/

CSV_PATH = PIPELINE_DIR / "metadata" / "Print_Translation_Control_Center.csv"
STATIC_SITE = PIPELINE_DIR / "13-static-site"
PAGES_DIR = STATIC_SITE / "pages"

CHROME_BIN = shutil.which("google-chrome") or shutil.which("google-chrome-stable") or shutil.which("chromium-browser")
PRINTER_NAME = "EPSON_L4260_Series_USB"
TRAY_CAPACITY = 90  # folhas por carga de bandeja (margem de segurança)

# Cores ANSI
C = "\033[0;96m"   # Cyan
G = "\033[0;32m"   # Green
Y = "\033[1;33m"   # Yellow
R = "\033[0;31m"   # Red
W = "\033[0;37m"   # Gray
B = "\033[1m"      # Bold
N = "\033[0m"      # Reset

if os.environ.get("AXIS_ALLOW_RETIRED_PRINT_BATCH_TOOL") != "1":
    print(
        "ERROR: This print-batch workflow was retired by #FlagFix_033 because "
        "Print_Translation_Control_Center.csv was removed. "
        "Translation_Control_Center.csv remains official for SP10/DeepL. "
        "Do not recreate Print_Translation_Control_Center.csv without explicit review. "
        "Set AXIS_ALLOW_RETIRED_PRINT_BATCH_TOOL=1 only for supervised archaeology.",
        file=sys.stderr,
    )
    sys.exit(2)


def banner():
    print(f"""
{C}╔══════════════════════════════════════════════════════════════╗{N}
{C}║  🖨️  AXIS-NIDDHI — Batch Print Engine v1.0                  ║{N}
{C}║  Impressão automatizada de Ensaios para Revisão             ║{N}
{C}╚══════════════════════════════════════════════════════════════╝{N}
""")


def load_csv():
    """Carrega o CSV e retorna lista de dicts."""
    if not CSV_PATH.exists():
        print(f"{R}❌ CSV não encontrado: {CSV_PATH}{N}")
        sys.exit(1)

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def save_csv(rows, fieldnames):
    """Salva o CSV atualizado (com Printed? marcado)."""
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def get_lotes(rows):
    """Retorna set de lotes disponíveis."""
    lotes = set()
    for row in rows:
        lote = row.get("Lote", "").strip()
        if lote:
            lotes.add(lote)
    return sorted(lotes, key=lambda x: int(x) if x.isdigit() else x)


def filter_printable(rows, lote):
    """Filtra ensaios prontos para impressão: Status=DONE, Printed?=vazio, Lote=lote."""
    printable = []
    for row in rows:
        if (row.get("Lote", "").strip() == str(lote)
                and row.get("Status", "").strip() == "DONE"
                and not row.get("Printed?", "").strip()):
            # Verificar se o HTML existe localmente
            pdpn = row.get("PD#PN", "").strip()
            html_path = PAGES_DIR / pdpn / "index.html"
            if html_path.exists():
                row["_html_path"] = str(html_path)
                printable.append(row)
            else:
                print(f"  {Y}⚠ HTML não encontrado para {pdpn}: {html_path}{N}")
    return printable


class PrintColorHandler(http.server.SimpleHTTPRequestHandler):
    """Intercepta HTML para injetar CSS de impressão (Remove animações + Ativa Cores)"""
    def log_message(self, *args, **kwargs):
        pass

    def do_GET(self):
        if self.path.endswith('.html') or self.path.endswith('/'):
            # Encontrar o local correspondente
            file_path = os.path.join(str(STATIC_SITE), self.path.lstrip('/').split('?')[0])
            if os.path.isdir(file_path):
                file_path = os.path.join(file_path, 'index.html')
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Injetar o CSS/JS de print nativo antes do fechamento do head
                injection = """
                <style>
                @media print {
                    :root {
                        --print-text-color: inherit !important;
                        --print-heading-color: #008800 !important;
                        --print-link-color: #2b5fac !important;
                        --print-color-adjust: exact !important;
                    }
                    html { 
                        -webkit-print-color-adjust: exact !important; 
                        print-color-adjust: exact !important; 
                    }
                    main {
                        animation: none !important;
                        opacity: 1 !important;
                        transform: none !important;
                        visibility: visible !important;
                    }
                    * {
                        transition: none !important;
                    }
                }
                </style>
                <script>document.documentElement.classList.add('print-colors');</script>
                """
                
                content = content.replace('</head>', injection + '</head>')
                
                encoded = content.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)
                return
        
        # Para outros arquivos, usar comportamento padrão
        super().do_GET()


def _start_local_server(directory):
    """Levanta um servidor HTTP temporário em thread daemon."""
    os.chdir(str(directory))
    httpd = socketserver.TCPServer(("127.0.0.1", 0), PrintColorHandler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, port


def generate_pdfs(essays, output_dir):
    """Gera PDFs via Chrome headless + servidor HTTP local temporário.
    O servidor garante que CSS/JS/fontes/áudio sejam resolvidos corretamente."""
    if not CHROME_BIN:
        print(f"{R}❌ Google Chrome não encontrado no sistema.{N}")
        print(f"   Instale com: sudo apt install google-chrome-stable")
        sys.exit(1)

    pdf_paths = []
    total = len(essays)

    # Levantar servidor HTTP temporário para servir o site estático
    print(f"  {W}Levantando servidor local temporário...{N}", end="", flush=True)
    httpd, port = _start_local_server(STATIC_SITE)
    print(f" {G}✔{N} (porta {port})\n")

    try:
        for i, essay in enumerate(essays, 1):
            pdpn = essay["PD#PN"].strip()
            pdf_name = f"{pdpn}.pdf"
            pdf_path = output_dir / pdf_name

            # URL via servidor HTTP local (resolve todos os caminhos relativos)
            page_url = f"http://127.0.0.1:{port}/pages/{pdpn}/index.html"

            progress = f"[{i:3d}/{total}]"
            print(f"  {W}{progress}{N} 📄 {pdpn} → {pdf_name}", end="", flush=True)

            cmd = [
                CHROME_BIN,
                "--headless",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-software-rasterizer",
                "--run-all-compositor-stages-before-draw",
                f"--print-to-pdf={pdf_path}",
                "--print-to-pdf-no-header",
                "--no-pdf-header-footer",
                page_url,
            ]

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True, text=True, timeout=30
                )
                if pdf_path.exists() and pdf_path.stat().st_size > 500:
                    size_kb = pdf_path.stat().st_size / 1024
                    print(f" {G}✔{N} ({size_kb:.0f} KB)")
                    pdf_paths.append((essay, pdf_path))
                else:
                    print(f" {R}✘ (PDF vazio ou sem estilo){N}")
                    if result.stderr:
                        for line in result.stderr.strip().split("\n")[-3:]:
                            print(f"       {W}{line}{N}")
            except subprocess.TimeoutExpired:
                print(f" {R}✘ (timeout 30s){N}")
            except Exception as e:
                print(f" {R}✘ ({e}){N}")
    finally:
        httpd.shutdown()

    return pdf_paths


def estimate_pages(pdf_paths):
    """Estima número total de páginas dos PDFs gerados."""
    total_pages = 0
    for _, pdf_path in pdf_paths:
        # Estimativa rápida: tamanho do PDF / ~15KB por página (heurística)
        # Para contagem exata, usaríamos pdfinfo, mas mantemos simples
        try:
            result = subprocess.run(
                ["pdfinfo", str(pdf_path)],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split("\n"):
                if line.startswith("Pages:"):
                    total_pages += int(line.split(":")[1].strip())
                    break
            else:
                # Fallback: estimativa por tamanho
                total_pages += max(1, int(pdf_path.stat().st_size / 15000))
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # pdfinfo não disponível — estimativa por tamanho
            total_pages += max(1, int(pdf_path.stat().st_size / 15000))
    return total_pages


def prompt_confirm(essays, pdf_paths, total_pages):
    """Mostra resumo e pede confirmação do usuário."""

    # Perguntar sobre duplex
    print(f"\n{C}── Modo de Impressão ──{N}")
    print(f"  {B}[1]{N} Frente apenas (ideal para revisão — verso livre para rascunho)")
    print(f"  {B}[2]{N} Frente e verso (economiza papel — ideal para arquivamento)")
    print()

    while True:
        choice = input(f"  Escolha o modo {W}[1/2]{N} (padrão: 1): ").strip()
        if choice in ("", "1"):
            duplex = False
            duplex_label = "Frente apenas (revisão)"
            break
        elif choice == "2":
            duplex = True
            duplex_label = "Frente e verso (arquivamento)"
            break
        else:
            print(f"  {Y}Digite 1 ou 2.{N}")

    sheets = total_pages if not duplex else (total_pages + 1) // 2

    # Resumo final
    print(f"""
{C}╔══════════════════════════════════════════════════════════════╗{N}
{C}║  📋  RESUMO DA IMPRESSÃO                                    ║{N}
{C}╠══════════════════════════════════════════════════════════════╣{N}
{C}║{N}  Ensaios (Scientific Essays):  {B}{len(pdf_paths)}{N}
{C}║{N}  Páginas estimadas:            {B}~{total_pages}{N}
{C}║{N}  Folhas A4 estimadas:          {B}~{sheets}{N}
{C}║{N}  Modo:                         {B}{duplex_label}{N}
{C}║{N}  Impressora:                   {B}{PRINTER_NAME}{N}
{C}║{N}  Papel:                        {B}A4{N}
{C}║{N}  Cores:                        {B}Preservadas (print-color-adjust: exact){N}
{C}╚══════════════════════════════════════════════════════════════╝{N}
""")

    if sheets > TRAY_CAPACITY:
        batches = (sheets + TRAY_CAPACITY - 1) // TRAY_CAPACITY
        print(f"  {Y}⚠ A bandeja da L4260 comporta ~{TRAY_CAPACITY} folhas.{N}")
        print(f"  {Y}  O script pausará a cada {TRAY_CAPACITY} folhas ({batches} recargas).{N}")
        print()

    while True:
        confirm = input(f"  {B}Confirmar impressão? [s/N]:{N} ").strip().lower()
        if confirm in ("s", "sim", "y", "yes"):
            return duplex
        elif confirm in ("", "n", "nao", "não", "no"):
            print(f"\n  {Y}Impressão cancelada pelo usuário.{N}")
            return None
        else:
            print(f"  {Y}Digite 's' para confirmar ou 'n' para cancelar.{N}")


def send_to_printer(pdf_paths, duplex, total_pages):
    """Envia PDFs para a impressora CUPS, pausando entre lotes de bandeja."""
    sheets_sent = 0
    printed_essays = []

    for i, (essay, pdf_path) in enumerate(pdf_paths, 1):
        pdpn = essay["PD#PN"].strip()

        # Estimar folhas deste PDF
        try:
            result = subprocess.run(
                ["pdfinfo", str(pdf_path)],
                capture_output=True, text=True, timeout=5
            )
            pages = 1
            for line in result.stdout.split("\n"):
                if line.startswith("Pages:"):
                    pages = int(line.split(":")[1].strip())
                    break
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pages = max(1, int(pdf_path.stat().st_size / 15000))

        sheets = pages if not duplex else (pages + 1) // 2

        # Verificar se precisa pausar para recarregar bandeja
        if sheets_sent > 0 and (sheets_sent + sheets) > TRAY_CAPACITY:
            print(f"\n  {Y}📄 Bandeja cheia (~{sheets_sent} folhas enviadas).{N}")
            print(f"  {Y}   Recarregue a bandeja da impressora e pressione ENTER...{N}")
            input()
            sheets_sent = 0

        # Montar comando lp
        lp_cmd = [
            "lp",
            "-d", PRINTER_NAME,
            "-o", "media=A4",
            "-o", "fit-to-page",
        ]

        if duplex:
            lp_cmd.extend(["-o", "sides=two-sided-long-edge"])
        else:
            lp_cmd.extend(["-o", "sides=one-sided"])

        lp_cmd.append(str(pdf_path))

        print(f"  [{i:3d}/{len(pdf_paths)}] 🖨️  {pdpn} ({pages}p, {sheets} folhas)...", end="", flush=True)

        try:
            result = subprocess.run(lp_cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f" {G}✔ enviado{N}")
                sheets_sent += sheets
                printed_essays.append(essay)
            else:
                print(f" {R}✘{N}")
                err = result.stderr.strip()
                if err:
                    print(f"       {W}{err}{N}")
        except Exception as e:
            print(f" {R}✘ ({e}){N}")

    return printed_essays


def update_csv_printed(all_rows, printed_essays, fieldnames):
    """Marca Printed?=DONE e data no CSV para os ensaios impressos."""
    printed_pdpns = {e["PD#PN"].strip() for e in printed_essays}
    timestamp = datetime.now().strftime("%Y-%m-%d")

    for row in all_rows:
        if row.get("PD#PN", "").strip() in printed_pdpns:
            row["Printed?"] = f"DONE ({timestamp})"

    # Remover campos internos antes de salvar
    clean_rows = []
    for row in all_rows:
        clean = {k: v for k, v in row.items() if not k.startswith("_")}
        clean_rows.append(clean)

    save_csv(clean_rows, fieldnames)
    print(f"\n  {G}✅ CSV atualizado: {len(printed_essays)} ensaios marcados como impressos.{N}")


def main():
    banner()

    # ── Verificações iniciais ──
    if not STATIC_SITE.exists():
        print(f"{R}❌ Site estático não encontrado: {STATIC_SITE}{N}")
        print(f"   Rode primeiro: python3 pipeline/13-ssg/build.py")
        sys.exit(1)

    # ── Carregar CSV ──
    all_rows = load_csv()
    fieldnames = list(all_rows[0].keys()) if all_rows else []
    # Limpar campos internos dos fieldnames
    fieldnames = [f for f in fieldnames if not f.startswith("_")]

    lotes = get_lotes(all_rows)

    if not lotes:
        print(f"{Y}Nenhum lote encontrado no CSV.{N}")
        sys.exit(0)

    # ── Selecionar lote ──
    lote_arg = None
    if "--lote" in sys.argv:
        idx = sys.argv.index("--lote")
        if idx + 1 < len(sys.argv):
            lote_arg = sys.argv[idx + 1]

    if lote_arg is None:
        print(f"  {C}Lotes disponíveis:{N} {', '.join(lotes)}")
        lote_arg = input(f"  Qual lote deseja imprimir? ").strip()

    if lote_arg not in lotes:
        print(f"{R}❌ Lote '{lote_arg}' não encontrado. Disponíveis: {', '.join(lotes)}{N}")
        sys.exit(1)

    # ── Filtrar ensaios ──
    essays = filter_printable(all_rows, lote_arg)

    if not essays:
        print(f"\n  {G}✅ Todos os ensaios do Lote {lote_arg} já foram impressos (ou nenhum tem Status=DONE).{N}")
        sys.exit(0)

    print(f"\n  {G}📚 {len(essays)} Ensaios encontrados no Lote {lote_arg} aguardando impressão.{N}\n")

    # ── Gerar PDFs ──
    pdf_only = "--pdf-only" in sys.argv

    pdf_dir = PIPELINE_DIR / "print_output" / f"lote_{lote_arg}"
    pdf_dir.mkdir(parents=True, exist_ok=True)

    print(f"  {C}── Fase 1: Gerando PDFs (Chrome Headless) ──{N}")
    print(f"  📂 Destino: {pdf_dir}\n")

    pdf_paths = generate_pdfs(essays, pdf_dir)

    if not pdf_paths:
        print(f"\n  {R}❌ Nenhum PDF gerado com sucesso.{N}")
        sys.exit(1)

    print(f"\n  {G}✅ {len(pdf_paths)}/{len(essays)} PDFs gerados com sucesso.{N}")

    # ── Estimar páginas ──
    total_pages = estimate_pages(pdf_paths)

    if pdf_only:
        print(f"\n  {C}Modo --pdf-only: PDFs gerados em {pdf_dir}{N}")
        print(f"  Total estimado: ~{total_pages} páginas.")
        print(f"  Para imprimir depois: python3 {__file__} --lote {lote_arg}")
        sys.exit(0)

    # ── Confirmação ──
    print(f"\n  {C}── Fase 2: Preparando Impressão ──{N}")
    duplex = prompt_confirm(essays, pdf_paths, total_pages)

    if duplex is None:
        print(f"  PDFs preservados em: {pdf_dir}")
        sys.exit(0)

    # ── Imprimir ──
    print(f"\n  {C}── Fase 3: Enviando para {PRINTER_NAME} ──{N}\n")
    printed = send_to_printer(pdf_paths, duplex, total_pages)

    # ── Atualizar CSV ──
    if printed:
        update_csv_printed(all_rows, printed, fieldnames)
        print(f"\n{G}══════════════════════════════════════════════════════════════{N}")
        print(f"{G}  ✅ IMPRESSÃO CONCLUÍDA — Lote {lote_arg}{N}")
        print(f"{G}     {len(printed)} Ensaios enviados para a {PRINTER_NAME}{N}")
        print(f"{G}══════════════════════════════════════════════════════════════{N}\n")
    else:
        print(f"\n  {Y}Nenhum ensaio foi impresso.{N}")


if __name__ == "__main__":
    main()
