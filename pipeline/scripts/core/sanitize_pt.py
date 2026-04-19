#!/usr/bin/env python3
"""
💎 BRASILEIRINHO ENGINE — sanitize_pt.py
==========================================
Versão:  1.0 (AXIS-NIDDHI V5.4)
Data:    2026-04-19
Origem:  Portado do legado 05_translate_pilot_v5_surgeon.py (The Surgeon)

FUNÇÃO:
  Sanitização pós-tradução DeepL para PT-BR.
  Corrige termos Pālī que o DeepL flexiona incorretamente para português,
  restaurando as grafias canônicas do PureDhamma.net.

REGRA FUNDAMENTAL:
  "Buda" = forma religiosa portuguesa (PROIBIDA no PureDhamma)
  "Buddha" = Bhava + uddha — grafia canônica (OBRIGATÓRIA)

USO:
  from sanitize_pt import sanitize_pt_output

  pt_text = sanitize_pt_output(deepl_raw_output)
"""

import re
from typing import Optional

# ==============================================================================
# 🛡️  REGRAS DE SANITIZAÇÃO PÓS-DEEPL
# ==============================================================================
# Portadas e aprimoradas a partir de 05_translate_pilot_v5_surgeon.py (2026-02)
#
# Cada regra captura uma família de flexões PT incorretas e reconstrói
# a grafia canônica Pālī preservando o sufixo gramatical.
#
# IMPORTANTE: A ordem importa — regras mais específicas vêm primeiro
#             para evitar matches parciais.

_SANITIZATION_RULES = [
    # ─────────────────────────────────────────────────────────────────
    # 1. FAMÍLIA BUDDHA  (a mais crítica!)
    #    "Buda" → "Buddha", "budista" → "Buddhista", "Budismo" → "Buddhismo"
    #    Regex: match "Bud" + sufixo, reconstruir como "Buddh" + sufixo
    #    Grupos: (a|as|ismo|ista|istas|ístico|ísticos|ística|ísticas|ico|icos|ica|icas|os|o)
    # ─────────────────────────────────────────────────────────────────
    {
        "pattern": re.compile(
            r'(?<![A-Za-zÀ-ÿ])'    # lookbehind: não precedido por letra (evita "Sambuddha" → "SamBuddha")
            r'[Bb]ud'               # "Bud" ou "bud"
            r'(a|as|ismo|istas?|ísticos?|ísticas?|icos?|icas?|os|o)'
            r'(?![A-Za-zÀ-ÿ])',    # lookahead: não seguido por letra
            re.UNICODE,
        ),
        "replacement": lambda m: "Buddh" + m.group(1),
    },

    # ─────────────────────────────────────────────────────────────────
    # 2. FAMÍLIA DHAMMA
    #    "Darma/Dharma" → "Dhamma"
    # ─────────────────────────────────────────────────────────────────
    {
        "pattern": re.compile(
            r'(?<![A-Za-zÀ-ÿ])'
            r'[Dd]h?arm'
            r'(a|as|ico|icos|ica|icas|ic)'
            r'(?![A-Za-zÀ-ÿ])',
            re.UNICODE,
        ),
        "replacement": lambda m: "Dhamm" + m.group(1),
    },

    # ─────────────────────────────────────────────────────────────────
    # 3. FAMÍLIA KAMMA
    #    "Carma/Karma" → "Kamma"
    # ─────────────────────────────────────────────────────────────────
    {
        "pattern": re.compile(
            r'(?<![A-Za-zÀ-ÿ])'
            r'[CcKk]arm'
            r'(a|as|ico|icos|ica|icas|ic)'
            r'(?![A-Za-zÀ-ÿ])',
            re.UNICODE,
        ),
        "replacement": lambda m: "Kamm" + m.group(1),
    },

    # ─────────────────────────────────────────────────────────────────
    # 4. FAMÍLIA NIBBĀNA
    #    "Nirvana" → "Nibbāna"
    # ─────────────────────────────────────────────────────────────────
    {
        "pattern": re.compile(
            r'(?<![A-Za-zÀ-ÿ])'
            r'[Nn]irvan'
            r'(a|as|ico|icos)'
            r'(?![A-Za-zÀ-ÿ])',
            re.UNICODE,
        ),
        "replacement": lambda m: "Nibbān" + m.group(1),
    },

    # ─────────────────────────────────────────────────────────────────
    # 5. FAMÍLIA SUTTA
    #    "Sutra" → "Sutta"
    # ─────────────────────────────────────────────────────────────────
    {
        "pattern": re.compile(
            r'(?<![A-Za-zÀ-ÿ])'
            r'[Ss]utr'
            r'(a|as)'
            r'(?![A-Za-zÀ-ÿ])',
            re.UNICODE,
        ),
        "replacement": lambda m: "Sutt" + m.group(1),
    },

    # ─────────────────────────────────────────────────────────────────
    # 6. DIACRÍTICOS — termos que perdem acentuação no DeepL
    # ─────────────────────────────────────────────────────────────────
    {
        "pattern": re.compile(r'(?<![A-Za-zÀ-ÿ])[Pp]ali(?![A-Za-zÀ-ÿ])', re.UNICODE),
        "replacement": "Pālī",
    },
    {
        "pattern": re.compile(r'(?<![A-Za-zÀ-ÿ])[Tt]ipitaka(?![A-Za-zÀ-ÿ])', re.UNICODE),
        "replacement": "Tipiṭaka",
    },
]


# ==============================================================================
# 🔧  API PÚBLICA
# ==============================================================================

def sanitize_pt_output(text: str) -> str:
    """
    Aplica as regras de sanitização canônica ao texto PT-BR pós-DeepL.

    Corrige flexões portuguesas de termos Pālī que o DeepL gera incorretamente,
    restaurando as grafias canônicas do PureDhamma.net.

    Exemplos:
        "o Buda disse"       → "o Buddha disse"
        "ensinamentos do Buda" → "ensinamentos do Buddha"
        "Budismo"            → "Buddhismo"
        "budista"            → "Buddhista"

    Args:
        text: Texto PT-BR bruto recebido do DeepL.

    Returns:
        Texto sanitizado com grafias canônicas Pālī.
    """
    if not text:
        return text

    result = text
    for rule in _SANITIZATION_RULES:
        replacement = rule["replacement"]
        if isinstance(replacement, str):
            result = rule["pattern"].sub(replacement, result)
        else:
            # Lambda replacement — capitalizar primeira letra (termos sagrados)
            def _smart_replace(match, repl=replacement):
                new_word = repl(match)
                return new_word[0].upper() + new_word[1:]
            result = rule["pattern"].sub(_smart_replace, result)

    return result


def audit_pt_text(text: str) -> list[dict]:
    """
    Audita um texto PT-BR em busca de grafias PROIBIDAS.
    Não modifica o texto — apenas retorna as violações encontradas.

    Returns:
        Lista de dicts com 'term', 'position', 'context' para cada violação.
    """
    violations = []

    # Padrão principal: "Buda" isolado (não "Buddha")
    for m in re.finditer(r'(?<![A-Za-zÀ-ÿ])[Bb]ud(a|as|ismo|istas?|ísticos?|ísticas?|icos?|icas?|os|o)(?![A-Za-zÀ-ÿdh])', text, re.UNICODE):
        start = max(0, m.start() - 30)
        end   = min(len(text), m.end() + 30)
        violations.append({
            "term":     m.group(0),
            "position": m.start(),
            "context":  text[start:end].replace("\n", " "),
        })

    return violations


# ==============================================================================
# 🧪  SELF-TEST
# ==============================================================================

if __name__ == "__main__":
    print("🧪 sanitize_pt.py — Self-Test\n")

    test_cases = [
        ("o Buda disse",                    "o Buddha disse"),
        ("ensinamentos do Buda",            "ensinamentos do Buddha"),
        ("um Buda nasce no mundo",          "um Buddha nasce no mundo"),
        ("pelo Buda",                       "pelo Buddha"),
        ("Budismo Theravāda",              "Buddhismo Theravāda"),
        ("era budista de nascimento",       "era Buddhista de nascimento"),
        ("o Dharma antigo",                 "o Dhamma antigo"),
        ("carma pesado",                    "Kamma pesado"),
        ("alcançar o Nirvana",              "alcançar o Nibbāna"),
        ("nos Sutras antigos",              "nos Suttas antigos"),
        ("Buddha Dhamma",                   "Buddha Dhamma"),  # já correto — não deve mudar
        ("Sambuddha",                       "Sambuddha"),      # não deve mexer (composto Pālī)
    ]

    passed = 0
    failed = 0
    for input_text, expected in test_cases:
        result = sanitize_pt_output(input_text)
        ok = result == expected
        icon = "✅" if ok else "❌"
        print(f"  {icon} '{input_text}' → '{result}'", end="")
        if not ok:
            print(f"  (esperado: '{expected}')")
            failed += 1
        else:
            print()
            passed += 1

    print(f"\n  Resultado: {passed} ok, {failed} falhas")

    # Test audit
    violations = audit_pt_text("O Buda disse que o Budismo é diferente.")
    print(f"\n  Audit test: {len(violations)} violações encontradas")
    for v in violations:
        print(f"    → '{v['term']}' em pos {v['position']}: ...{v['context']}...")
