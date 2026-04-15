#!/usr/bin/env python3
"""
💎 BRASILEIRINHO ENGINE — SP02_upgrade_identity.py
====================================================
Versão:  V5.2 — AXIS-NIDDHI Structural Refactor (SEAL Script)
Data:    2026-03-08

HARDENING V5.1 (vs V1.2):
  ★ [SEAL]  Cobertura expandida: content.html + semantic.json + (optional) assets
  ★ [RC-03] atomic_write_json() — crash-safe
  ★ [SF-03] logging de exceções em extract_*() — não swallows
  ★ [ND-01] log_timestamp() com sub-segundo
  ★ [ND-02] get_utc_now() capturado UMA VEZ por post
  ★ [DCV-02] sha256_file() lê em bytes (rb) — encoding byte-stable
  ★ FailureCounter: abort se erros > FAILURE_THRESHOLD
  ★ SEAL REPORT: imprime resumo de integridade ao final
  ★ Exit code semântico: 0=clean, 1=erros, 2=dry-run

FIX V5.2 — [E1] Preservação de titles.pt / titles.pt_source:
  ★ --force NÃO apaga mais titles.pt se já existir (gravado pelo SP11)
  ★ Guard explícito: só preenche title_pt se o campo atual for None/vazio
  ★ Log WARN quando titles.pt existente é preservado durante --force
  ★ Garante que SEAL 2 (após SP10) não perde títulos PT traduzidos

FUNÇÃO NO PIPELINE:
  SEAL 1: roda após SP06 — lock hashes EN pré-tradução
  SP11  : roda após SEAL 1 — traduz títulos EN→PT (V5.2)
  SEAL 2: roda após SP10 — lock hashes PT pós-tradução
  Ambos SEALs usam: --apply --force
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import (
    DIR_09_CSL,
    LOG_DIR,
    SCHEMA_VERSION,
    SCHEMA_VERSION_SEAL,
    FAILURE_THRESHOLD,
)
from pipeline_utils import (
    atomic_write_json,
    backup_file,
    FailureCounter,
    get_utc_now,
    log_timestamp,
    sha256_file,
    PipelineAbort,
)

CSL_ROOT = DIR_09_CSL

GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
GRAY   = "\033[90m"
RESET  = "\033[0m"


# ==============================================================================
# 📋  CONTADORES
# ==============================================================================

@dataclass
class Stats:
    total:    int = 0
    upgraded: int = 0
    skipped:  int = 0
    forced:   int = 0
    errors:   int = 0
    seal_gaps: list = field(default_factory=list)  # posts com hash ausente após seal


# ==============================================================================
# 🗂️  CANONICAL FINDEX MAP (source: PDPN_02_Historical_Updated.csv)
# Authoritative findex values — survives full CSL rebuild/exorcism.
_FINDEX_CANON = {"..": "0356", "AB.AA.000": "0760", "AB.BB.001": "0761", "AB.BB.002": "0762", "AB.BB.003": "0432", "AB.BB.004": "0764", "AB.BB.005": "0765", "AB.BB.006": "0766", "AB.BB.007": "0218", "AB.BB.008": "0768", "AB.BB.009": "0769", "AB.BB.010": "0770", "AB.CC.001": "0771", "AB.CC.002": "0419", "AB.CC.003": "0773", "AB.CC.004": "0774", "AB.CC.005": "0776", "AB.CC.006": "0777", "AB.CC.007": "0778", "AB.DD.001": "0779", "AB.DD.002": "0780", "AB.DD.003": "0782", "AB.DD.004": "0783", "AB.DD.005": "0784", "AB.DD.006": "0785", "AB.DD.007": "0786", "AB.DD.008": "0787", "AB.EE.001": "0789", "AB.EE.002": "0051", "AB.FF.001": "0792", "AB.FF.002": "0351", "AB.FF.003": "0352", "AB.FF.004": "0353", "AB.GG.001": "0797", "AB.GG.002": "0513", "AB.GG.003": "0514", "AB.GG.004": "0800", "AB.GG.005": "0801", "AB.GG.006": "0802", "BA.AA.000": "0901", "BA.AA.001": "0903", "BA.AA.002": "0496", "BA.AA.003": "0906", "BA.AA.004": "0907", "BA.AA.005": "0908", "BA.BB.001": "0913", "BA.CC.001": "0916", "BC.AA.000": "0823", "BC.AA.001": "0824", "BC.AA.002": "0825", "BC.AA.003": "0826", "BC.AA.004": "0827", "BC.AA.005": "0828", "BC.AA.006": "0829", "BD.AA.000": "0002", "BD.AA.001": "0003", "BD.AA.002": "0043", "BD.AA.003": "0044", "BD.AA.004": "0045", "BD.AA.005": "0054", "BD.AA.006": "0055", "BD.AA.007": "0056", "BD.AA.008": "0063", "BD.AA.009": "0064", "BD.AA.010": "0065", "BD.BB.001": "0006", "BD.BB.002": "0007", "BD.BB.003": "0008", "BD.BB.004": "0009", "BD.BB.005": "0010", "BD.BB.006": "0011", "BD.CC.001": "0012", "BD.CC.002": "0013", "BD.CC.003": "0014", "BD.CC.004": "0015", "BD.CC.005": "0016", "BD.CC.006": "0017", "BD.CC.007": "0018", "BD.DD.001": "0019", "BD.DD.002": "0020", "BD.DD.003": "0021", "BD.DD.004": "0022", "BD.DD.005": "0023", "BD.DD.006": "0024", "BD.EE.001": "0025", "BD.EE.002": "0026", "BD.EE.003": "0027", "BD.EE.004": "0028", "BD.EE.005": "0029", "BD.FF.001": "0035", "BD.FF.002": "0036", "BD.FF.003": "0037", "BD.FF.004": "0038", "BD.GG.001": "0039", "BD.GG.002": "0040", "BD.GG.003": "0041", "BD.GG.004": "0042", "BD.HH.001": "0046", "BD.HH.002": "0047", "BD.HH.003": "0048", "BD.HH.004": "0049", "BD.HH.005": "0050", "BD.HH.006": "0052", "BD.HH.007": "0053", "BD.II.001": "0057", "BD.II.002": "0058", "BD.II.003": "0059", "BD.II.004": "0060", "BD.II.005": "0061", "BD.II.006": "0062", "BD.JJ.001": "0090", "BD.JJ.002": "0091", "BD.JJ.003": "0092", "BM.AA.000": "0714", "BM.AA.001": "0716", "BM.AA.002": "0717", "BM.AA.003": "0718", "BM.AA.004": "0719", "BM.AA.005": "0720", "BM.AA.006": "0721", "BM.AA.007": "0722", "BM.AA.008": "0723", "BM.AA.009": "0724", "BM.AA.010": "0725", "BM.AA.011": "0731", "BM.AA.012": "0732", "BM.AA.013": "0733", "BM.AA.014": "0511", "BM.AA.015": "0735", "BM.BB.001": "0726", "BM.BB.002": "0727", "BM.BB.003": "0728", "BM.BB.004": "0729", "BM.CC.001": "0736", "BM.CC.002": "0737", "BM.CC.003": "0739", "BM.CC.004": "0741", "BM.CC.005": "0742", "BM.CC.006": "0744", "BM.CC.007": "0749", "BM.DD.001": "0750", "BM.DD.002": "0751", "BM.DD.003": "0752", "BM.DD.004": "0753", "BM.DD.005": "0756", "BM.DD.006": "0757", "BM.DD.007": "0758", "BM.DD.008": "0759", "CH.AA.000": "0004", "CH.AA.001": "0902", "CH.AA.002": "0005", "CH.AA.003": "0941", "CH.AA.004": "0481", "CH.AA.005": "0944", "CH.BB.001": "0657", "CH.BB.002": "0658", "CH.BB.003": "0659", "CH.BB.004": "0660", "CH.BB.005": "0661", "CH.BB.006": "0662", "DD.AA.000": "0830", "DD.AA.001": "0831", "DD.AA.002": "0832", "DD.AA.003": "0833", "DD.AA.004": "0834", "DD.AA.005": "0835", "DD.AA.006": "0836", "DD.AA.007": "0837", "DP.AA.000": "0702", "DP.AA.001": "0703", "DP.AA.002": "0704", "DP.AA.003": "0705", "DP.AA.004": "0706", "DP.AA.005": "0707", "DP.BB.001": "0708", "DP.BB.002": "0709", "DP.BB.003": "0710", "DP.BB.004": "0711", "DP.BB.005": "0712", "DP.BB.006": "0713", "DS.AA.000": "0276", "DS.AA.001": "0277", "DS.AA.002": "0278", "DS.BB.001": "0279", "DS.BB.002": "0280", "DS.BB.003": "0281", "DS.BB.004": "0282", "DS.BB.005": "0283", "DS.BB.006": "0284", "DS.BB.007": "0285", "DS.BB.008": "0286", "DS.BB.009": "0287", "DS.BB.010": "0336", "DS.CC.001": "0288", "DS.CC.002": "0289", "DS.CC.003": "0290", "DS.CC.004": "0291", "DS.DD.001": "0292", "DS.DD.002": "0293", "DS.DD.003": "0294", "DS.DD.004": "0295", "DS.DD.005": "0296", "DS.DD.006": "0297", "DS.DD.007": "0298", "DS.DD.008": "0299", "DS.DD.009": "0300", "DS.EE.001": "0301", "DS.EE.002": "0302", "DS.EE.003": "0303", "DS.FF.001": "0311", "DS.FF.002": "0312", "DS.FF.003": "0313", "DS.FF.004": "0314", "DS.FF.005": "0315", "DS.FF.006": "0316", "DS.FF.007": "0317", "DS.FF.008": "0318", "DS.FF.009": "0319", "DS.FF.010": "0320", "DS.GG.001": "0321", "DS.HH.001": "0325", "DS.HH.002": "0326", "DS.HH.003": "0327", "DS.II.001": "0330", "DS.II.002": "0331", "DS.II.003": "0332", "DS.II.004": "0333", "DS.II.005": "0334", "DS.II.006": "0335", "DS.JJ.001": "0337", "DS.JJ.002": "0338", "DS.JJ.003": "0339", "DS.JJ.004": "0340", "DS.JJ.005": "0341", "DS.JJ.006": "0342", "DS.KK.001": "0343", "DS.KK.002": "0344", "DS.KK.003": "0345", "DS.KK.004": "0346", "DS.KK.005": "0347", "DS.KK.006": "0348", "DS.KK.007": "0349", "DS.KK.008": "0350", "ER.AA.000": "0358", "ER.BB.001": "0359", "ER.BB.002": "0032", "ER.BB.003": "0033", "ER.CC.001": "0034", "ER.CC.002": "0364", "ER.CC.003": "0365", "ER.CC.004": "0366", "ER.CC.005": "0367", "ER.CC.006": "0369", "ER.CC.007": "0370", "ER.CC.008": "0371", "ER.CC.009": "0372", "ER.CC.010": "0373", "ER.CC.011": "0374", "ER.CC.012": "0375", "ER.DD.001": "0376", "ER.DD.002": "0377", "ER.EE.001": "0378", "ER.EE.002": "0379", "ER.EE.003": "0380", "ER.EE.004": "0381", "ER.EE.005": "0382", "ER.EE.006": "0383", "ER.EE.007": "0384", "ER.FF.001": "0385", "ER.FF.002": "0386", "ER.FF.003": "0387", "ER.FF.004": "0388", "ER.FF.005": "0389", "ER.GG.001": "0390", "ER.GG.002": "0391", "ER.HH.001": "0031", "FT.AA.000": "0945", "FT.BB.001": "0946", "FT.CC.001": "0947", "FT.DD.001": "0948", "FT.DD.002": "0949", "FT.DD.003": "0950", "FT.DD.004": "0951", "FT.EE.001": "0952", "FT.FF.001": "0953", "FT.GG.001": "0954", "FT.HH.001": "0955", "FT.II.001": "0956", "FT.JJ.001": "0957", "FT.JJ.002": "0958", "FT.JJ.003": "0959", "FT.JJ.004": "0960", "FT.JJ.005": "0961", "FT.JJ.006": "0962", "HB.AA.000": "0803", "HB.AA.001": "0804", "HB.AA.002": "0030", "HB.AA.003": "0806", "HB.AA.004": "0807", "HB.AA.005": "0808", "HB.AA.006": "0809", "HB.AA.007": "0810", "HB.AA.008": "0328", "HB.AA.009": "0329", "HB.AA.010": "0813", "HB.AA.011": "0814", "HB.AA.012": "0815", "HB.AA.013": "0816", "HB.AA.014": "0817", "HB.AA.015": "0818", "HB.AA.016": "0819", "HB.AA.017": "0820", "HB.AA.018": "0100", "HB.AA.019": "0822", "IS.AA.000": "0656", "IS.BB.001": "0663", "IS.BB.002": "0664", "IS.BB.003": "0665", "IS.BB.004": "0666", "IS.BB.005": "0667", "IS.BB.006": "0668", "IS.BB.007": "0669", "IS.BB.008": "0670", "IS.BB.009": "0671", "IS.BB.010": "0672", "IS.BB.011": "0673", "IS.CC.001": "0674", "IS.CC.002": "0304", "IS.CC.003": "0305", "IS.CC.004": "0306", "IS.CC.005": "0307", "IS.CC.006": "0273", "IS.CC.007": "0308", "IS.CC.008": "0309", "IS.CC.009": "0310", "IS.DD.001": "0697", "KD..": "0095", "KD.AA.000": "0066", "KD.AA.001": "0195", "KD.AA.002": "0196", "KD.BB.001": "0067", "KD.BB.002": "0068", "KD.BB.003": "0069", "KD.BB.004": "0070", "KD.BB.005": "0071", "KD.BB.006": "0185", "KD.BB.007": "0153", "KD.CC.001": "0072", "KD.CC.002": "0073", "KD.CC.003": "0074", "KD.CC.004": "0076", "KD.CC.005": "0077", "KD.CC.006": "0078", "KD.CC.007": "0079", "KD.CC.008": "0080", "KD.CC.009": "0081", "KD.DD.001": "0082", "KD.DD.002": "0083", "KD.DD.003": "0084", "KD.DD.004": "0085", "KD.DD.005": "0087", "KD.EE.001": "0088", "KD.EE.002": "0089", "KD.EE.003": "0094", "KD.EE.004": "0096", "KD.FF.001": "0097", "KD.FF.002": "0098", "KD.FF.003": "0099", "KD.FF.004": "0101", "KD.FF.005": "0102", "KD.FF.006": "0103", "KD.FF.007": "0104", "KD.FF.008": "0105", "KD.FF.009": "0106", "KD.FF.010": "0107", "KD.FF.011": "0108", "KD.FF.012": "0109", "KD.FF.013": "0110", "KD.FF.014": "0111", "KD.FF.015": "0112", "KD.FF.016": "0113", "KD.FF.017": "0114", "KD.FF.018": "0115", "KD.FF.019": "0120", "KD.FF.020": "0121", "KD.FF.021": "0122", "KD.FF.022": "0123", "KD.FF.023": "0124", "KD.FF.024": "0125", "KD.FF.025": "0126", "KD.FF.026": "0127", "KD.FF.027": "0128", "KD.FF.028": "0118", "KD.FF.029": "0119", "KD.GG.001": "0131", "KD.GG.002": "0132", "KD.GG.003": "0133", "KD.GG.004": "0134", "KD.GG.005": "0135", "KD.GG.006": "0136", "KD.GG.007": "0137", "KD.GG.008": "0138", "KD.GG.009": "0140", "KD.HH.001": "0141", "KD.HH.002": "0142", "KD.HH.003": "0143", "KD.HH.004": "0144", "KD.HH.005": "0145", "KD.HH.006": "0147", "KD.HH.007": "0150", "KD.HH.008": "0154", "KD.HH.009": "0155", "KD.II.001": "0157", "KD.II.002": "0158", "KD.II.003": "0159", "KD.II.004": "0160", "KD.II.005": "0161", "KD.II.006": "0162", "KD.II.007": "0163", "KD.II.008": "0167", "KD.II.009": "0168", "KD.II.010": "0169", "KD.II.011": "0170", "KD.II.012": "0171", "KD.JJ.001": "0179", "KD.JJ.002": "0180", "KD.JJ.003": "0181", "KD.JJ.004": "0182", "KD.JJ.005": "0183", "KD.JJ.006": "0184", "KD.JJ.007": "0186", "KD.JJ.008": "0187", "KD.JJ.009": "0188", "KD.JJ.010": "0189", "KD.JJ.011": "0190", "KD.JJ.012": "0191", "KD.JJ.013": "0193", "KD.KK.001": "0164", "KD.KK.002": "0173", "KD.KK.003": "0174", "KD.KK.004": "0175", "KD.KK.005": "0176", "KD.KK.006": "0177", "KD.KK.007": "0178", "KD.LL.001": "0194", "KD.LL.002": "0194", "KD.LL.003": "0194", "LD.AA.000": "0197", "LD.AA.001": "0208", "LD.AA.002": "0209", "LD.AA.003": "0210", "LD.AA.004": "0211", "LD.AA.005": "0220", "LD.AA.006": "0146", "LD.AA.007": "0222", "LD.AA.008": "0223", "LD.AA.009": "0224", "LD.AA.010": "0225", "LD.AA.011": "0226", "LD.BB.001": "0198", "LD.BB.002": "0199", "LD.BB.003": "0200", "LD.BB.004": "0201", "LD.BB.005": "0202", "LD.BB.006": "0203", "LD.BB.007": "0204", "LD.BB.008": "0205", "LD.BB.009": "0206", "LD.BB.010": "0207", "LD.CC.001": "0212", "LD.CC.002": "0213", "LD.CC.003": "0214", "LD.CC.004": "0215", "LD.CC.005": "0216", "LD.CC.006": "0217", "LD.CC.007": "0219", "LD.DD.001": "0227", "LD.DD.002": "0228", "LD.DD.003": "0229", "LD.DD.004": "0230", "LD.EE.001": "0231", "LD.EE.002": "0232", "LD.EE.003": "0233", "LD.EE.004": "0235", "LD.FF.001": "0236", "LD.FF.002": "0237", "LD.FF.003": "0238", "LD.FF.004": "0239", "LD.FF.005": "0240", "LD.FF.006": "0241", "LD.FF.007": "0242", "LD.FF.008": "0243", "LD.GG.001": "0244", "LD.GG.002": "0245", "LD.GG.003": "0246", "LD.GG.004": "0247", "LD.GG.005": "0248", "LD.GG.006": "0249", "LD.GG.007": "0250", "LD.GG.008": "0251", "LD.GG.009": "0252", "LD.GG.010": "0253", "LD.HH.001": "0254", "LD.II.001": "0255", "LD.JJ.001": "0256", "LD.KK.001": "0260", "LD.LL.001": "0263", "LD.MM.001": "0268", "LD.NN.001": "0272", "LD.OO.001": "0274", "MR.AA.000": "0869", "MR.AA.001": "0870", "MR.AA.002": "0871", "MR.AA.003": "0872", "MR.AA.004": "0873", "MR.AA.005": "0874", "MR.AA.006": "0875", "MR.AA.007": "0876", "MR.AA.008": "0877", "MR.AA.009": "0878", "MR.BB.001": "0880", "MS.AA.000": "0963", "MS.BB.001": "0970", "MS.CC.001": "0972", "MS.CC.002": "0973", "MS.CC.003": "0974", "MS.CC.004": "0975", "MS.CC.005": "0976", "MS.CC.006": "0977", "MS.CC.007": "0978", "MS.CC.008": "0979", "MS.CC.009": "0980", "NP.AA.000": "0981", "NP.BB.001": "0982", "NP.BB.002": "0983", "NP.BB.003": "0984", "NP.BB.004": "0985", "PD.AA.000": "0001", "PD.BB.000": "0887", "PD.CC.000": "0888", "PS.AA.000": "0529", "PS.AA.001": "0530", "PS.AA.002": "0531", "PS.AA.003": "0638", "PS.AA.004": "0639", "PS.AA.005": "0640", "PS.AA.006": "0623", "PS.AA.007": "0487", "PS.BB.001": "0532", "PS.BB.002": "0550", "PS.BB.003": "0553", "PS.BB.004": "0499", "PS.BB.005": "0555", "PS.BB.006": "0557", "PS.BB.007": "0558", "PS.BB.008": "0559", "PS.BB.009": "0234", "PS.CC.001": "0560", "PS.CC.002": "0561", "PS.CC.003": "0562", "PS.CC.004": "0563", "PS.CC.005": "0564", "PS.CC.006": "0565", "PS.CC.007": "0566", "PS.DD.001": "0568", "PS.DD.002": "0322", "PS.DD.003": "0570", "PS.DD.004": "0086", "PS.DD.005": "0572", "PS.DD.006": "0323", "PS.DD.007": "0324", "PS.EE.001": "0575", "PS.EE.002": "0577", "PS.EE.003": "0578", "PS.EE.004": "0579", "PS.EE.005": "0580", "PS.EE.006": "0581", "PS.EE.007": "0582", "PS.EE.008": "0583", "PS.EE.009": "0584", "PS.EE.010": "0586", "PS.FF.001": "0588", "PS.FF.002": "0589", "PS.FF.003": "0415", "PS.FF.004": "0591", "PS.GG.001": "0592", "PS.GG.002": "0360", "PS.GG.003": "0594", "PS.GG.004": "0595", "PS.GG.005": "0596", "PS.GG.006": "0598", "PS.GG.007": "0599", "PS.GG.008": "0600", "PS.GG.009": "0603", "PS.GG.010": "0606", "PS.GG.011": "0607", "PS.GG.012": "0608", "PS.GG.013": "0609", "PS.GG.014": "0610", "PS.GG.015": "0611", "PS.GG.016": "0612", "PS.GG.017": "0613", "PS.GG.018": "0615", "PS.GG.019": "0616", "PS.GG.020": "0617", "PS.GG.021": "0618", "PS.HH.001": "0619", "PS.HH.002": "0620", "PS.HH.003": "0621", "PS.HH.004": "0622", "PS.II.001": "0624", "PS.II.002": "0625", "PS.II.003": "0626", "PS.II.004": "0627", "PS.II.005": "0628", "PS.II.006": "0629", "PS.II.007": "0632", "PS.II.008": "0633", "PS.II.009": "0139", "PS.II.010": "0635", "PS.II.011": "0636", "PS.II.012": "0637", "PS.JJ.001": "0643", "PS.JJ.002": "0644", "PS.JJ.003": "0149", "PS.JJ.004": "0647", "PS.KK.002": "0498", "QD.AA.000": "0889", "QD.AA.001": "0890", "QD.BB.001": "0891", "QD.BB.002": "0892", "QD.BB.003": "0893", "QD.CC.001": "0894", "QD.CC.002": "0895", "QD.CC.003": "0896", "QD.DD.001": "0897", "QD.DD.002": "0898", "QD.DD.003": "0899", "QD.DD.004": "0900", "SI.AA.000": "0838", "SI.AA.001": "0839", "SI.AA.002": "0840", "SI.AA.003": "0841", "SI.AA.004": "0842", "SI.AA.005": "0850", "SI.AA.006": "0861", "SI.AA.007": "0862", "SI.AA.008": "0863", "SI.AA.009": "0864", "SI.AA.010": "0355", "SI.AA.011": "0866", "SI.AA.012": "0867", "SI.AA.013": "0868", "SI.BB.001": "0843", "SI.BB.002": "0844", "SI.BB.003": "0845", "SI.BB.004": "0846", "SI.BB.005": "0847", "SI.BB.006": "0848", "SI.BB.007": "0849", "SI.CC.001": "0851", "SI.CC.002": "0852", "SI.CC.003": "0556", "SI.CC.004": "0854", "SI.CC.005": "0855", "SI.CC.006": "0856", "SI.DD.001": "0857", "SI.DD.002": "0859", "SI.DD.003": "0860", "TL.AA.000": "0392", "TL.BB.000": "0393", "TL.BB.001": "0394", "TL.BB.002": "0395", "TL.BB.003": "0396", "TL.BB.004": "0397", "TL.BB.005": "0398", "TL.BB.006": "0399", "TL.BB.007": "0400", "TL.BB.008": "0401", "TL.CC.001": "0402", "TL.CC.002": "0403", "TL.CC.003": "0404", "TL.CC.004": "0405", "TL.CC.005": "0406", "TL.CC.006": "0093", "TL.CC.007": "0408", "TL.CC.008": "0409", "TL.CC.009": "0410", "TL.DD.001": "0411", "TL.DD.002": "0412", "TL.DD.003": "0413", "TL.DD.004": "0414", "TL.DD.005": "0416", "TL.DD.006": "0417", "TL.DD.007": "0418", "TL.EE.001": "0420", "TL.EE.002": "0421", "TL.EE.003": "0422", "TL.EE.004": "0423", "TL.EE.005": "0424", "TL.EE.006": "0425", "TL.EE.007": "0426", "TL.EE.008": "0427", "TL.EE.009": "0152", "TL.EE.010": "0429", "TL.EE.011": "0430", "TL.EE.012": "0431", "TL.EE.013": "0151", "TL.EE.014": "0433", "TL.FF.001": "0434", "TL.FF.002": "0435", "TL.FF.003": "0437", "TL.FF.004": "0438", "TL.FF.005": "0439", "TL.GG.001": "0440", "TL.GG.002": "0441", "TL.GG.003": "0442", "TL.GG.004": "0443", "TL.GG.005": "0444", "TL.GG.006": "0445", "TL.GG.007": "0446", "TL.GG.008": "0447", "TL.GG.009": "0448", "TL.GG.010": "0449", "TL.GG.011": "0450", "TL.GG.012": "0451", "TL.HH.001": "0452", "TL.HH.002": "0453", "TL.HH.003": "0454", "TL.HH.004": "0455", "TL.HH.005": "0456", "TL.HH.006": "0457", "TL.HH.007": "0458", "TL.HH.008": "0459", "TL.HH.009": "0460", "TL.HH.010": "0461", "TL.HH.011": "0462", "TL.II.001": "0463", "TL.II.002": "0464", "TL.II.003": "0465", "TL.II.004": "0469", "TL.II.005": "0470", "TL.II.006": "0471", "TL.II.007": "0472", "TL.II.008": "0473", "TL.II.009": "0148", "TL.II.010": "0475", "TL.II.011": "0476", "TL.II.012": "0477", "TL.II.013": "0479", "TL.II.014": "0480", "TL.JJ.001": "0482", "TL.JJ.002": "0483", "TL.JJ.003": "0484", "TL.JJ.004": "0485", "TL.JJ.005": "0486", "TL.JJ.006": "0488", "TL.JJ.007": "0489", "TL.JJ.008": "0490", "TL.JJ.009": "0491", "TL.JJ.010": "0492", "TL.JJ.011": "0501", "TL.JJ.012": "0503", "TL.JJ.013": "0512", "TL.KK.001": "0493", "TL.KK.002": "0494", "TL.KK.003": "0495", "TL.KK.004": "0500", "TL.LL.001": "0504", "TL.LL.002": "0505", "TL.LL.003": "0506", "TL.LL.004": "0507", "TL.LL.005": "0508", "TL.LL.006": "0509", "TS.AA.000": "0515", "TS.AA.001": "0516", "TS.AA.002": "0517", "TS.AA.003": "0518", "TS.AA.004": "0519", "TS.AA.005": "0520", "TS.AA.006": "0521", "TS.AA.007": "0522", "TS.AA.008": "0523", "TS.AA.009": "0524", "TS.AA.010": "0525", "TS.AA.011": "0526", "TS.AA.012": "0527", "TS.AA.013": "0528"}

# ==============================================================================
# 🛠️  LOGGER
# ==============================================================================

def setup_logger(apply: bool, force: bool):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = log_timestamp()
    mode_tag = "APPLY" if apply else "DRY_RUN"
    if force:
        mode_tag += "_FORCE"
    log_path = LOG_DIR / f"SP02_upgrade_identity_{mode_tag}_{ts}.log"
    lines = []

    def log(msg: str, level: str = "INFO", color: str = RESET, verbose_only: bool = False):
        icons = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ", "ERROR": "❌", "SKIP": "⏭️ ", "DRY": "🔍"}
        icon = icons.get(level, "  ")
        lines.append(f"[{get_utc_now()}] [{level}] {msg}")
        print(f"{color}{icon} {msg}{RESET}")

    def flush():
        log_path.write_text("\n".join(lines), encoding="utf-8")

    return log, flush


# ==============================================================================
# 🔧  FUNÇÕES AUXILIARES
# ==============================================================================

def clean_html_text(raw: str) -> str:
    return re.sub(r"<[^>]+>", "", raw).strip()


def extract_title_from_html(html_path: Path, slug_fallback: str, log) -> tuple[str, str]:
    """
    Extrai título do <h1>. Fallback para slug.
    V5.1: logging de exceção — sem swallow silencioso (SF-03).
    """
    if not html_path.exists():
        return slug_fallback.replace("-", " ").title(), "inferred_from_slug"
    try:
        head = html_path.read_text(encoding="utf-8")[:5000]
        match = re.search(r"<h1[^>]*>(.*?)</h1>", head, re.IGNORECASE | re.DOTALL)
        if match:
            title = clean_html_text(match.group(1))
            if title:
                return title, "extracted_h1"
    except Exception as e:
        log(f"extract_title falhou para {html_path}: {e} — usando slug fallback", "WARN", YELLOW)
    return slug_fallback.replace("-", " ").title(), "inferred_from_slug"


def extract_wp_id(html_path: Path, log) -> int | None:
    """
    Lê Source-ID da Tatuagem canônica.
    V5.1: logging de exceção — sem swallow silencioso (SF-04).
    """
    if not html_path.exists():
        return None
    try:
        head = html_path.read_text(encoding="utf-8")[:2000]
        match = re.search(r"Source-ID:\s+(\d+)", head)
        if match:
            return int(match.group(1))
    except Exception as e:
        log(f"extract_wp_id falhou para {html_path}: {e}", "WARN", YELLOW)
    return None


# ==============================================================================
# 🔐  CALCULAR SEAL HASH (expansível)
# ==============================================================================

def compute_seal_hashes(folder: Path, log) -> dict:
    """
    Calcula hashes de todos os artefatos relevantes para o SEAL.
    V5.1: cobre content.html (EN), content.html (PT), semantic.json.
    Todos em bytes (rb) — encoding byte-stable (DCV-02).
    """
    hashes = {}
    artifacts = {
        "en-US": folder / "source" / "en-US" / "content.html",
        "pt-BR": folder / "source" / "pt-BR" / "content.html",
        "semantic": folder / "meta" / "semantic.json",
    }
    for key, path in artifacts.items():
        if path.exists():
            h = sha256_file(path)
            if h:
                hashes[key] = h
            else:
                log(f"sha256_file retornou None para {path} — arquivo corrompido?", "WARN", YELLOW)
    return hashes


# ==============================================================================
# 🧬  UPGRADE DE UM POST
# ==============================================================================

def upgrade_post(folder: Path, apply: bool, force: bool, log, stats: Stats) -> str:
    """
    Faz upgrade do identity.json para Schema V3.1 e sela hashes.
    V5.1: atomic write, backup, expanded seal, logging robusto.
    Retorna: UPGRADED | SKIPPED | FORCED | DRY_UPGRADED | DRY_SKIP | ERROR:<reason>
    """
    pdpn      = folder.name
    json_path = folder / "meta"   / "identity.json"
    source_en = folder / "source" / "en-US" / "content.html"
    source_pt = folder / "source" / "pt-BR" / "content.html"

    stats.total += 1

    if not json_path.exists():
        stats.errors += 1
        return "ERROR:identity.json ausente"

    try:
        old_data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        stats.errors += 1
        return f"ERROR:json_malformed({e})"

    current_schema = old_data.get("schema_version", "0")

    if current_schema == SCHEMA_VERSION_SEAL and not force:
        stats.skipped += 1
        return "SKIPPED"

    if not apply:
        return "DRY_UPGRADED" if current_schema != SCHEMA_VERSION_SEAL else "DRY_WOULD_FORCE"

    # ── ESCRITA REAL ──────────────────────────────────────────────────────

    # Capturar timestamp UMA VEZ (ND-02)
    now = get_utc_now()

    old_identity = old_data.get("identity", {})
    old_sro      = old_data.get("sro", {})
    old_titles   = old_data.get("titles", {})
    old_artifacts = old_data.get("artifacts", {})

    pdpn_val   = old_identity.get("pdpn")   or old_data.get("pdpn",   folder.name)
    # [FF-findex] Canonical map from PDPN_02 takes precedence — survives rebuild
    _canon = _FINDEX_CANON.get(pdpn_val, "")
    findex_val = _canon or old_identity.get("findex") or old_data.get("findex", "0000")
    slug_val   = (old_identity.get("slug_root")
                  or old_data.get("slug_en")
                  or old_data.get("slug", "unknown"))
    section    = pdpn_val.split(".")[0] if "." in pdpn_val else "MS"

    title_en = old_titles.get("en")
    title_en_source = old_titles.get("en_source", "preserved")
    if not title_en:
        title_en, title_en_source = extract_title_from_html(source_en, slug_val, log)

    # ── [E1 V5.2] Guard: preservar titles.pt se já existir ────────────────
    # SP11 grava titles.pt APÓS o SEAL 1. Se SP02 --force rodar em seguida
    # (SEAL 2 ou re-run manual), NÃO deve apagar o título PT já traduzido.
    # Regra: só aceita None/string vazia como "ausente" — preserva qualquer
    # valor não-vazio gravado pelo SP11 ou por migração anterior.
    existing_title_pt = old_titles.get("pt")
    existing_title_pt_source = old_titles.get("pt_source")

    if existing_title_pt:
        # Título PT já existe — preservar sem alteração
        title_pt = existing_title_pt
        title_pt_source = existing_title_pt_source or "preserved"
        if force:
            log(f"{pdpn}: titles.pt preservado durante --force: '{title_pt[:60]}'", "INFO", CYAN)
    else:
        # Título PT ausente — manter None para SP11 preencher depois
        title_pt = None
        title_pt_source = None

    wp_id = (old_sro.get("original_wp_id")
             or old_data.get("source_id")
             or extract_wp_id(source_en, log))

    # ── Calcular SEAL hashes (V5.1 expandido) ─────────────────────────────
    seal_hashes = compute_seal_hashes(folder, log)
    hash_en = seal_hashes.get("en-US") or "missing_file"
    hash_pt = seal_hashes.get("pt-BR")
    hash_semantic = seal_hashes.get("semantic")

    # ── Verificar gap de seal (post traduzido sem hash) ───────────────────
    if source_pt.exists() and not hash_pt:
        log(f"{pdpn}: pt-BR existe mas hash não calculável — arquivo corrompido?", "WARN", YELLOW)
        stats.seal_gaps.append(pdpn)

    # ── Backup ANTES de qualquer escrita ──────────────────────────────────
    backup_file(json_path)

    # ── Construir Schema V3.1 ─────────────────────────────────────────────
    new_artifacts = {
        "en-US": {
            "status":           "canonical",
            "file_path":        "source/en-US/content.html",
            "integrity_sha256": hash_en,
            "last_audit":       now,
        }
    }

    # Preservar pt-BR artifact se existe (não sobrescrever tradução feita pelo SP10)
    if hash_pt:
        existing_pt = old_artifacts.get("pt-BR", {})
        new_artifacts["pt-BR"] = {
            **existing_pt,
            "integrity_sha256": hash_pt,
            "last_audit":       now,
        }
        # Não alterar status="derived" se já estava correto
        if "status" not in new_artifacts["pt-BR"]:
            new_artifacts["pt-BR"]["status"] = "derived"

    # Adicionar hash do semantic.json se existir
    if hash_semantic:
        new_artifacts["semantic"] = {
            "integrity_sha256": hash_semantic,
            "last_audit":       now,
        }

    new_data = {
        "schema_version":   SCHEMA_VERSION_SEAL,
        "last_updated_utc": now,
        "identity": {
            "pdpn":         pdpn_val,
            "findex":       findex_val,
            "slug_root":    slug_val,
            "section_code": section,
        },
        "sro": {
            "source":         "PureDhamma.net",
            "url":            None,
            "original_wp_id": wp_id,
            "author":         "Lal A.",
        },
        "titles": {
            "en":         title_en,
            "en_source":  title_en_source,
            "pt":         title_pt,
            "pt_source":  title_pt_source,
        },
        "artifacts": new_artifacts,
    }

    # ── Escrita atômica (RC-03) ────────────────────────────────────────────
    atomic_write_json(json_path, new_data)

    if current_schema == SCHEMA_VERSION_SEAL:
        stats.forced += 1
        return "FORCED"
    else:
        stats.upgraded += 1
        return "UPGRADED"


# ==============================================================================
# 🚀  MAIN
# ==============================================================================

def is_pdpn_folder(folder: Path) -> bool:
    """
    Retorna True apenas para pastas com padrão de PD#PN: XX.YY.NNN
    Exclui pastas de metadados como 'meta/', 'pronunciation/', etc.
    """
    import re as _re
    return bool(_re.match(r'^[A-Z]{2}\.[A-Z]{2}\.\d{3}$', folder.name))


def main():
    parser = argparse.ArgumentParser(description="SP02 Upgrade Identity — SEAL Script V5.1")
    parser.add_argument("--apply", action="store_true",
                        help="Aplica mudanças. Sem isso: DRY-RUN.")
    parser.add_argument("--force", action="store_true",
                        help="Reprocessa mesmo posts já em schema 3.1 (SEAL).")
    parser.add_argument("--dry-run", action="store_true", dest="dry_run",
                        help="Alias para ausência de --apply (compatibilidade).")
    args = parser.parse_args()

    # --dry-run anula --apply se ambos passados por acidente
    if args.dry_run:
        args.apply = False

    log, flush = setup_logger(args.apply, args.force)
    stats = Stats()
    fc = FailureCounter(max_failures=FAILURE_THRESHOLD, label="SP02")

    mode = "APPLY" + ("_FORCE" if args.force else "") if args.apply else "DRY_RUN"
    log(f"=== SP02 Upgrade Identity ({mode}) ===")
    log(f"CSL: {CSL_ROOT}")
    log(f"Target schema: {SCHEMA_VERSION_SEAL}")

    if not CSL_ROOT.exists():
        raise PipelineAbort(f"CSL não encontrada: {CSL_ROOT}")

    # Filtrar apenas pastas com padrão PD#PN (XX.YY.NNN) — exclui meta/, etc.
    folders = sorted([f for f in CSL_ROOT.iterdir() if f.is_dir() and is_pdpn_folder(f)])
    log(f"Posts encontrados: {len(folders)}")

    for folder in folders:
        pdpn = folder.name
        result = upgrade_post(folder, args.apply, args.force, log, stats)

        if result in ("UPGRADED", "FORCED"):
            log(f"  ✅ {pdpn}: {result}", "OK", GREEN)
        elif result.startswith("DRY"):
            pass  # silencioso em dry-run para não poluir output
        elif result == "SKIPPED":
            pass  # silencioso
        elif result.startswith("ERROR"):
            if fc.fail(pdpn, result):
                flush()
                fc.assert_clean()
                return

    # ── SEAL REPORT ──────────────────────────────────────────────────────
    print(f"\n{CYAN}{'='*62}{RESET}")
    print(f"{CYAN}  SP02 / SEAL REPORT ({mode}){RESET}")
    print(f"{CYAN}{'='*62}{RESET}")
    print(f"  Posts processados  : {stats.total}")
    print(f"  ✅ Upgraded         : {stats.upgraded}")
    print(f"  🔒 Forced (re-seal) : {stats.forced}")
    print(f"  ⏭️  Skipped (já OK)  : {stats.skipped}")
    print(f"  ❌ Erros            : {stats.errors}")

    if stats.seal_gaps:
        print(f"\n  {RED}⚠️  SEAL GAPS: {len(stats.seal_gaps)} post(s) com pt-BR sem hash:{RESET}")
        for p in stats.seal_gaps[:10]:
            print(f"     - {p}")
        if len(stats.seal_gaps) > 10:
            print(f"     ... +{len(stats.seal_gaps) - 10}")
    else:
        print(f"\n  {GREEN}🔐 HASH SEALS: TODOS OS HASHES COBERTOS{RESET}")

    print(f"{CYAN}{'='*62}{RESET}\n")

    flush()

    # ── Exit codes semânticos ─────────────────────────────────────────────
    if not args.apply:
        sys.exit(2)  # dry-run

    if stats.seal_gaps:
        print(f"{RED}❌ SEAL INCOMPLETO: {len(stats.seal_gaps)} post(s) sem hash.{RESET}")
        sys.exit(1)

    fc.assert_clean()
    sys.exit(0)


if __name__ == "__main__":
    main()
