#!/usr/bin/env python3
"""
💎 BRASILEIRINHO ENGINE — pipeline_utils.py
============================================
Versão:  AXIS-NIDDHI V5.1 (Hardening Edition)
Data:    2026-03-07

FUNÇÕES PARTILHADAS:
  - atomic_write()        : escreve via temp+rename (crash-safe)
  - atomic_write_bytes()  : variante binária para HTML normalizado
  - backup_file()         : cria .bak antes de qualquer mutação
  - sha256_file()         : SHA-256 em bytes (rb) — padrão do pipeline
  - sha256_string()       : SHA-256 de string em UTF-8 normalizado
  - get_utc_now()         : timestamp UTC capturado UMA VEZ por post
  - PipelineAbort         : exceção com exit code
  - FailureCounter        : conta falhas e aborta automaticamente

USO:
  from pipeline_utils import atomic_write, backup_file, sha256_file, \
                             get_utc_now, FailureCounter, PipelineAbort
"""

import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ==============================================================================
# EXCEÇÕES
# ==============================================================================

class PipelineAbort(SystemExit):
    """Sinaliza abort crítico do pipeline com mensagem clara."""
    def __init__(self, message: str, code: int = 1):
        print(f"\n❌ [PIPELINE ABORT] {message}", file=sys.stderr)
        super().__init__(code)


# ==============================================================================
# TIMESTAMP (capturar UMA VEZ por post — ND-02)
# ==============================================================================

def get_utc_now() -> str:
    """Retorna timestamp UTC ISO-8601. Deve ser capturado UMA VEZ por post."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ==============================================================================
# SHA-256 (padrão pipeline: leitura em bytes)
# ==============================================================================

def sha256_file(path: Path) -> Optional[str]:
    """
    Calcula SHA-256 do arquivo em bytes (rb).
    Padrão do pipeline — consistente com SP02, SP03, SP04.
    Retorna None se arquivo não existe.
    """
    if not path.exists():
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_string(text: str) -> str:
    """
    SHA-256 de string normalizada (LF, UTF-8).
    Usado para preview em dry-run — não usar como source-of-truth.
    """
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


# ==============================================================================
# ATOMIC WRITE (RC-03, DCV-01, DCV-02)
# ==============================================================================

def atomic_write(path: Path, content: str, encoding: str = "utf-8") -> None:
    """
    Escrita atômica de texto via temp + rename.
    - Normaliza LF (elimina CRLF — DCV-02)
    - Cria diretório pai se necessário
    - Em caso de falha no rename, limpa o .tmp
    - Compatível com POSIX (rename é atômico no mesmo filesystem)
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_text(normalized, encoding=encoding)
        tmp.replace(path)  # atômico no POSIX
    except Exception as e:
        # Fallback: escrita direta (melhor do que perder o arquivo)
        try:
            path.write_text(normalized, encoding=encoding)
        except Exception as e2:
            raise IOError(f"atomic_write falhou para {path}: {e} | fallback: {e2}") from e2
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except Exception:
                pass


def atomic_write_bytes(path: Path, content: str) -> None:
    """
    Escrita atômica em modo binário com encoding UTF-8 normalizado.
    Garante que o hash SHA-256 (bytes rb) seja determinístico entre plataformas.
    Normaliza CRLF → LF antes de encodar.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    content_bytes = normalized.encode("utf-8")
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_bytes(content_bytes)
        tmp.replace(path)
    except Exception as e:
        try:
            path.write_bytes(content_bytes)
        except Exception as e2:
            raise IOError(f"atomic_write_bytes falhou para {path}: {e} | fallback: {e2}") from e2
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except Exception:
                pass


def atomic_write_json(path: Path, data: dict) -> None:
    """
    Escrita atômica de JSON com indent=2 e ensure_ascii=False.
    """
    atomic_write(path, json.dumps(data, indent=2, ensure_ascii=False))


# ==============================================================================
# BACKUP (RC-04, DCV-01)
# ==============================================================================

def backup_file(path: Path) -> Optional[Path]:
    """
    Cria backup .bak antes de qualquer mutação crítica.
    Retorna o path do .bak criado, ou None se o arquivo não existe.
    Sobrescreve .bak anterior (sempre mantém o backup da última run bem-sucedida).
    """
    path = Path(path)
    if not path.exists():
        return None
    bak = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, bak)
    return bak


# ==============================================================================
# CLEANUP DE TEMP FILES ÓRFÃOS (RC-05)
# ==============================================================================

def cleanup_orphaned_tmp(directory: Path, logger=None) -> int:
    """
    Remove arquivos .tmp órfãos deixados por runs anteriores crashadas.
    Retorna contagem de arquivos removidos.
    """
    count = 0
    for tmp in Path(directory).rglob("*.tmp"):
        try:
            tmp.unlink()
            count += 1
            if logger:
                logger.warning(f"Orphaned .tmp removed: {tmp}")
        except Exception:
            pass
    return count


# ==============================================================================
# FAILURE COUNTER (SF-01, SF-02)
# ==============================================================================

class FailureCounter:
    """
    Conta falhas durante iteração sobre posts CSL.
    Aborta automaticamente se threshold for excedido.

    Uso:
        fc = FailureCounter(max_failures=5, label="SP10")
        for post in posts:
            try:
                process(post)
            except Exception as e:
                if fc.fail(post_id, str(e)):
                    break  # threshold excedido — pipeline abortado
        fc.assert_clean()  # levanta PipelineAbort se houve falhas
    """

    def __init__(self, max_failures: int = 5, label: str = "UNKNOWN"):
        self.max_failures = max_failures
        self.label = label
        self.failures: list[tuple[str, str]] = []  # (pdpn, reason)
        self._aborted = False

    def fail(self, pdpn: str, reason: str) -> bool:
        """
        Registra uma falha.
        Retorna True se o threshold foi atingido (pipeline deve abortar).
        """
        self.failures.append((pdpn, reason))
        count = len(self.failures)
        print(f"❌ [FAILURE {count}/{self.max_failures}] {self.label} — {pdpn}: {reason}",
              file=sys.stderr)
        if count >= self.max_failures:
            self._aborted = True
            print(
                f"\n🛑 [{self.label}] ABORT: {count} falhas ≥ threshold {self.max_failures}.\n"
                f"   Pipeline interrompido para evitar corrupção adicional.",
                file=sys.stderr,
            )
            return True
        return False

    def assert_clean(self) -> None:
        """
        Levanta PipelineAbort se houver qualquer falha registrada.
        Deve ser chamado ao final do loop principal de cada script.
        """
        if self.failures:
            count = len(self.failures)
            pdpns = ", ".join(p for p, _ in self.failures[:10])
            extra = f" ...+{count-10}" if count > 10 else ""
            raise PipelineAbort(
                f"{self.label}: {count} post(s) falharam: {pdpns}{extra}\n"
                f"  Execute com --dry-run para diagnóstico antes de re-tentar.",
                code=1,
            )

    @property
    def count(self) -> int:
        return len(self.failures)

    @property
    def aborted(self) -> bool:
        return self._aborted


# ==============================================================================
# IN-PROGRESS SENTINEL (DCV-01 — SP10 crash recovery)
# ==============================================================================

def mark_in_progress(json_path: Path, pdpn: str) -> None:
    """
    Escreve sentinel status="in_progress" em identity.json antes de iniciar tradução.
    Permite auto-recovery ao reiniciar SP10.
    """
    json_path = Path(json_path)
    if not json_path.exists():
        return
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        if "pt-BR" not in data.setdefault("artifacts", {}):
            data["artifacts"]["pt-BR"] = {}
        data["artifacts"]["pt-BR"]["status"] = "in_progress"
        data["artifacts"]["pt-BR"]["in_progress_since"] = get_utc_now()
        atomic_write_json(json_path, data)
    except Exception as e:
        print(f"⚠️  [WARN] mark_in_progress falhou para {pdpn}: {e}", file=sys.stderr)


def clear_in_progress(json_path: Path) -> None:
    """Remove sentinel in_progress de identity.json."""
    json_path = Path(json_path)
    if not json_path.exists():
        return
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        pt = data.get("artifacts", {}).get("pt-BR", {})
        if pt.get("status") == "in_progress":
            pt.pop("status", None)
            pt.pop("in_progress_since", None)
        atomic_write_json(json_path, data)
    except Exception:
        pass


def find_in_progress_posts(csl_dir: Path) -> list[Path]:
    """
    Varre CSL e retorna lista de pastas com pt-BR status="in_progress"
    ou identity.json corrompido (JSON inválido).
    Usado pelo auto-recovery de SP10.
    """
    problematic = []
    for json_path in sorted(csl_dir.rglob("meta/identity.json")):
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            pt = data.get("artifacts", {}).get("pt-BR", {})
            if pt.get("status") == "in_progress":
                problematic.append(json_path.parents[1])
        except (json.JSONDecodeError, OSError):
            # JSON corrompido = potencial crash mid-write
            problematic.append(json_path.parents[1])
    return problematic


# ==============================================================================
# LOG TIMESTAMP COM MICROSEGUNDOS (ND-01)
# ==============================================================================

def log_timestamp() -> str:
    """
    Timestamp para nomes de log com sub-segundo (evita colisão em runs rápidas).
    Formato: YYYYMMDD_HHMMSS_mmm  (mmm = milissegundos)
    """
    now = datetime.now()
    ms = now.microsecond // 1000
    return f"{now.strftime('%Y%m%d_%H%M%S')}_{ms:03d}"
