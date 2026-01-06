#!/usr/bin/env bash
set -euo pipefail

# BlueHesab Runbook Regress (ASCII/Finglish output; Bitvise-safe)
# - NO awk usage (to avoid awk syntax issues / aborting report section)
# - Titles BLUE, separators YELLOW; PASS GREEN / WARN YELLOW / FAIL RED
# - Always prints: SUMMARY + CAT SUMMARY + COVERAGE + QUICK GUIDE + FAIL QUICK VIEW
# - Fixes: PI v01 signature (no company); LEGAL07/08/09 entrypoints -> run_cli (WARN on fail)
# - Fixes: report tails from RUN_ROOT (not RUN_DIR)
#
# Modes: all|quick|dim|vat|legal|restart|cache|bytecode|reports|retry|failed|one|tail
# Env: SITE COMPANY RATE FROM_DATE TO_DATE NO_PAUSE NO_COLOR STOP_ON_FAIL DRY_RUN

SITE="${SITE:-baba.bluehesab.ir}"
COMPANY="${COMPANY:-BlueAPi}"
RATE="${RATE:-1000000}"
LEGAL_ENTRYPOINTS="${LEGAL_ENTRYPOINTS:-0}"  # 1 => run LEGAL07/08/09 entrypoints (noisy)
FROM_DATE="${FROM_DATE:-}"
TO_DATE="${TO_DATE:-}"
NO_PAUSE="${NO_PAUSE:-0}"
NO_COLOR="${NO_COLOR:-0}"
STOP_ON_FAIL="${STOP_ON_FAIL:-0}"
DRY_RUN="${DRY_RUN:-0}"

FINGLISH="${FINGLISH:-1}"       # 1=transliterate Persian/Arabic output to Finglish (Bitvise-safe)
SUMMARY_SPACED="${SUMMARY_SPACED:-1}" # 1=blank line after each SUMMARY row (readability)
KEEP_RAW_LOG="${KEEP_RAW_LOG:-0}"     # 1=save UTF-8 raw logs alongside Finglish logs

BENCH="/home/frappe/frappe-bench"
APP_DIR="$BENCH/apps/blue_hesab/blue_hesab"
SITES_DIR="$BENCH/sites/$SITE"
RUN_ROOT="$SITES_DIR/private/files/bh_regress"

export LANG="${LANG:-C.UTF-8}"
export LC_ALL="${LC_ALL:-C.UTF-8}"
export PYTHONIOENCODING="${PYTHONIOENCODING:-utf-8}"

# Colors
if [[ "$NO_COLOR" == "1" ]] || ! [[ -t 1 ]]; then
  RST=""; BLD=""; DIM=""; YLW=""; GRN=""; RED=""; BLU=""; CYN=""
else
  RST=$'\033[0m'
  BLD=$'\033[1m'
  DIM=$'\033[2m'
  YLW=$'\033[33;1m'
  GRN=$'\033[32;1m'
  RED=$'\033[31;1m'
  BLU=$'\033[34;1m'
  CYN=$'\033[36;1m'
fi

ts() { date +"%Y-%m-%d %H:%M:%S"; }
is_tty() { [[ -t 0 && -t 1 ]]; }
pause() {
  if is_tty && [[ "$NO_PAUSE" != "1" ]]; then
    echo -e "${YLW}${BLD}Press Enter to continue...${RST}"
    read -r _
  fi
}
sep() {
  echo -e "${YLW}===============================================================================${RST}"
  echo -e "${YLW}--------------------------------------------------------------------------------${RST}"
}
title() {
  echo
  sep
  echo -e "${BLU}${BLD}$*${RST}"
  sep
}
badge() {
  case "${1:-}" in
    PASS) echo -e "${GRN}${BLD}PASS${RST}" ;;
    WARN) echo -e "${YLW}${BLD}WARN${RST}" ;;
    FAIL) echo -e "${RED}${BLD}FAIL${RST}" ;;
    SKIP) echo -e "${BLU}${BLD}SKIP${RST}" ;;
    *)    echo -e "${DIM}${BLD}${1:-}${RST}" ;;
  esac
}
sanitize() {
  echo "$*" | tr -cs '[:alnum:]_-' '_' | cut -c1-90
}

# Finglish filter (transliterate Persian/Arabic UTF-8 -> Latin ASCII-ish)
# Purpose: Bitvise/terminal safety (no Persian glyphs required).
FINGLISH_FILTER=""
init_finglish_filter() {
  [[ "${FINGLISH:-0}" == "1" ]] || return 0
  command -v python3 >/dev/null 2>&1 || { FINGLISH=0; return 0; }
  FINGLISH_FILTER="$RUN_DIR/finglish_filter.py"
  cat >"$FINGLISH_FILTER" <<'PY'
#!/usr/bin/env python3
import sys, re

# ANSI CSI sequences (keep them intact)
ANSI_RE = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')

# Basic Persian/Arabic -> Finglish map (approx)
M = {
    "آ":"a","ا":"a","أ":"a","إ":"e","ٱ":"a","ء":"'","ؤ":"v","ئ":"y",
    "ب":"b","پ":"p","ت":"t","ث":"s","ج":"j","چ":"ch","ح":"h","خ":"kh",
    "د":"d","ذ":"z","ر":"r","ز":"z","ژ":"zh","س":"s","ش":"sh","ص":"s",
    "ض":"z","ط":"t","ظ":"z","ع":"'","غ":"gh","ف":"f","ق":"gh","ك":"k",
    "ک":"k","گ":"g","ل":"l","م":"m","ن":"n","و":"v","ه":"h","ة":"h",
    "ي":"y","ی":"y","ى":"a","ۀ":"e","ٔ":"'","ـ":"",
    "‌":" ",  # ZWNJ
    "،":",","؛":";","؟":"?","٪":"%","٬":",","٫":".","«":"\"","»":"\"",
    "۰":"0","۱":"1","۲":"2","۳":"3","۴":"4","۵":"5","۶":"6","۷":"7","۸":"8","۹":"9",
    "٠":"0","١":"1","٢":"2","٣":"3","٤":"4","٥":"5","٦":"6","٧":"7","٨":"8","٩":"9",
}

def translit_text(t: str) -> str:
    out = []
    for ch in t:
        if ch in M:
            out.append(M[ch])
            continue
        o = ord(ch)
        if o < 128:
            out.append(ch)
        else:
            # unknown non-ascii: replace with '?'
            out.append("?")
    return "".join(out)

def translit_line(line: str) -> str:
    parts = []
    pos = 0
    for m in ANSI_RE.finditer(line):
        parts.append(translit_text(line[pos:m.start()]))
        parts.append(m.group(0))
        pos = m.end()
    parts.append(translit_text(line[pos:]))
    return "".join(parts)

def main() -> int:
    data = sys.stdin.read()
    if not data:
        return 0
    # Process by lines but keep original newlines
    out = []
    for line in data.splitlines(True):
        try:
            out.append(translit_line(line))
        except Exception:
            out.append(line)
    sys.stdout.write("".join(out))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
PY
  chmod 755 "$FINGLISH_FILTER" || true
}

pipe_finglish() {
  if [[ -n "${FINGLISH_FILTER:-}" ]] && [[ -f "$FINGLISH_FILTER" ]]; then
    python3 "$FINGLISH_FILTER"
  else
    cat
  fi
}

mkdir -p "$RUN_ROOT"
RUN_ID="runbook_$(date +%Y%m%d-%H%M%S)-${RANDOM}${RANDOM}"
RUN_START_EPOCH="$(date +%s)"
RUN_DIR="$RUN_ROOT/$RUN_ID"
mkdir -p "$RUN_DIR"/{log,cmd}

init_finglish_filter

LAST_DIR_FILE="$RUN_ROOT/runbook_last_dir.txt"
LAST_TSV="$RUN_ROOT/runbook_last.tsv"
STEPS_TSV="$RUN_DIR/steps.tsv"

echo -e "idx\tstat\trc\tuser\tcat\tstep\tlog_rel\tcmd_rel" > "$STEPS_TSV"
echo "$RUN_DIR" > "$LAST_DIR_FILE"
echo -e "$(ts)\t$SITE\t$COMPANY\t$RUN_DIR" > "$LAST_TSV"

STEP_NO=0
PASS_N=0
WARN_N=0
FAIL_N=0
SKIP_N=0

write_cmdfile() {
  local rel="${1:-}"
  if [[ -z "$rel" ]]; then
    echo "BUG: write_cmdfile missing rel path" >&2
    return 2
  fi
  local full="$RUN_DIR/$rel"
  umask 022
  mkdir -p "$(dirname "$full")" || true
  cat >"$full"
  chmod 644 "$full" || true
}


frappe_prefix() {
  cat <<'EOF'
set -euo pipefail
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export PYTHONIOENCODING=utf-8
export PATH="/home/frappe/.local/bin:/home/frappe/frappe-bench/env/bin:$PATH"
cd /home/frappe/frappe-bench
EOF
}

cmd_bench_exec() {
  local dotted="$1"
  local kwargs_json="$2"
  cat <<EOF
$(frappe_prefix)
bench --site "$SITE" execute "$dotted" --kwargs '$kwargs_json'
EOF
}

cmd_bench_simple() {
  local one="$1"
  cat <<EOF
$(frappe_prefix)
$one
EOF
}

hint_for() {
  case "${1:-}" in
    PRE_DISK) echo "disk space check" ;;
    PRE_EXISTS) echo "ensure bench/app paths exist" ;;
    FS_SUSPECT) echo "root-owned/pycache/pyc list" ;;
    FS_CHOWN) echo "normalize ownership" ;;
    FS_CHMOD) echo "normalize perms" ;;
    FS_PYC) echo "remove bytecode" ;;
    CORE_COMPILE) echo "py_compile key files" ;;
    CORE_COMPILEALL) echo "compileall bh_core" ;;
    CORE_CACHE) echo "clear caches" ;;
    CORE_RESTART) echo "restart bench" ;;
    DIM_SMOKE) echo "dimension smoke" ;;
    DIM02) echo "dimension terminal checks" ;;
    DIM04_AUDIT) echo "audit GL entries" ;;
    DIM04_STAMP) echo "JE stamp dims" ;;
    DIM04_STAMP_LINE) echo "JE stamp linewise" ;;
    VAT_LINT) echo "VAT lint" ;;
    VAT_INT01) echo "VAT intent v01" ;;
    VAT13) echo "VAT-13 guard" ;;
    VAT_LOCK01) echo "period lock v01" ;;
    VAT_LOCK02) echo "period lock v02" ;;
    VAT_SMOKE) echo "VAT smoke SI base" ;;
    VAT_MIX_PI) echo "MIXED PI v01" ;;
    VAT_MIX_SI) echo "MIXED SI v02" ;;
    VAT_INT08) echo "VAT intent v08" ;;
    VAT10B) echo "VAT10b terminal" ;;
    VAT11) echo "VAT11 terminal" ;;
    VAT16) echo "VAT16 terminal" ;;
    VAT17) echo "VAT17 terminal" ;;
    VAT18) echo "VAT18 terminal" ;;
    VAT_CI_LEGACY) echo "CI legacy EP01 v0.3" ;;
    VAT_CI_V12) echo "CI v12" ;;
    VAT_CI_V15) echo "CI v15 (optional)" ;;
    LEGAL05_S) echo "LEGAL05 sales cycle" ;;
    LEGAL05_P) echo "LEGAL05 purchase cycle" ;;
    LEGAL_SUITE) echo "LEGAL suite 07+08+09" ;;
    LEGAL07) echo "LEGAL07 regress (entrypoint may vary)" ;;
    LEGAL08) echo "LEGAL08 regress (entrypoint may vary)" ;;
    LEGAL09) echo "LEGAL09 regress (entrypoint may vary)" ;;
    REP_LIST) echo "list latest bh_regress" ;;
    REP_TAIL) echo "tail key logs" ;;
    *) echo "" ;;
  esac
}

run_step() {
  local run_user="$1" cat="$2" step="$3" hint="$4"
  local cmd_text="$5"
  local onfail="${6:-FAIL}"   # FAIL|WARN

  STEP_NO=$((STEP_NO+1))

  local safe; safe="$(sanitize "${cat}-${step}")"
  local log_rel="log/${STEP_NO}_${run_user}_${safe}.log"
  local cmd_rel="cmd/${STEP_NO}_${run_user}_${safe}.sh"
  local log="$RUN_DIR/$log_rel"

local wrc=0
set +e
write_cmdfile "$cmd_rel" <<<"$cmd_text"
wrc=$?
set -e
if [[ "$wrc" -ne 0 ]]; then
  echo
  echo -e "${YLW}--------------------------------------------------------------------------------${RST}"
  echo -e "${BLU}${BLD}[${STEP_NO}] ${cat} :: ${step}${RST}"
  echo -e "${DIM}LOG: ${RUN_DIR}/${log_rel}${RST}"
  [[ -n "$hint" ]] && echo -e "${DIM}HINT: ${hint}${RST}"
  echo -e "${CYN}${BLD}CMD:${RST} ${DIM}${RUN_DIR}/${cmd_rel}${RST}"
  echo -e "${YLW}--------------------------------------------------------------------------------${RST}"
  echo -e "${RED}${BLD}ERROR:${RST} write_cmdfile failed (rc=$wrc) — continuing"
  echo "write_cmdfile failed (rc=$wrc) for: $RUN_DIR/$cmd_rel" >"$log"
  local rc="$wrc" stat="$onfail"
  case "$stat" in
    PASS) PASS_N=$((PASS_N+1)) ;;
    WARN) WARN_N=$((WARN_N+1)) ;;
    FAIL) FAIL_N=$((FAIL_N+1)) ;;
    SKIP) SKIP_N=$((SKIP_N+1)) ;;
  esac
  echo -e "${BLD}RESULT:${RST} $(badge "$stat")  ${DIM}rc=${rc}${RST}"
  echo -e "${YLW}--------------------------------------------------------------------------------${RST}"
  echo -e "${STEP_NO}	${stat}	${rc}	${run_user}	${cat}	${step}	${log_rel}	${cmd_rel}" >> "$STEPS_TSV"
  [[ "$stat" == "FAIL" && "$STOP_ON_FAIL" == "1" ]] && return 1
  return 0
fi

  echo
  echo -e "${YLW}--------------------------------------------------------------------------------${RST}"
  echo -e "${BLU}${BLD}[${STEP_NO}] ${cat} :: ${step}${RST}"
  echo -e "${DIM}LOG: ${RUN_DIR}/${log_rel}${RST}"
  [[ -n "$hint" ]] && echo -e "${DIM}HINT: ${hint}${RST}"
  echo -e "${CYN}${BLD}CMD:${RST} ${DIM}${RUN_DIR}/${cmd_rel}${RST}"
  echo -e "${YLW}--------------------------------------------------------------------------------${RST}"

  local rc=0 stat="PASS"

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[DRY_RUN] not executed" | tee "$log"
    rc=0
  else
    set +e
    if [[ "$run_user" == "frappe" ]]; then
if [[ "${KEEP_RAW_LOG:-0}" == "1" ]]; then
  local log_raw="${log%.log}.raw.log"
  sudo -u frappe -H bash -lc "bash '$RUN_DIR/$cmd_rel'" 2>&1 | tee "$log_raw" | pipe_finglish | tee "$log"
  rc="${PIPESTATUS[0]}"
else
  sudo -u frappe -H bash -lc "bash '$RUN_DIR/$cmd_rel'" 2>&1 | pipe_finglish | tee "$log"
  rc="${PIPESTATUS[0]}"
fi
    else
if [[ "${KEEP_RAW_LOG:-0}" == "1" ]]; then
  local log_raw="${log%.log}.raw.log"
  bash -lc "bash '$RUN_DIR/$cmd_rel'" 2>&1 | tee "$log_raw" | pipe_finglish | tee "$log"
  rc="${PIPESTATUS[0]}"
else
  bash -lc "bash '$RUN_DIR/$cmd_rel'" 2>&1 | pipe_finglish | tee "$log"
  rc="${PIPESTATUS[0]}"
fi
    fi
    set -e
  fi

  if [[ "$rc" -ne 0 ]]; then stat="$onfail"; fi

  case "$stat" in
    PASS) PASS_N=$((PASS_N+1)) ;;
    WARN) WARN_N=$((WARN_N+1)) ;;
    FAIL) FAIL_N=$((FAIL_N+1)) ;;
    SKIP) SKIP_N=$((SKIP_N+1)) ;;
  esac

  echo -e "${BLD}RESULT:${RST} $(badge "$stat")  ${DIM}rc=${rc}${RST}"
  echo -e "${YLW}--------------------------------------------------------------------------------${RST}"

  echo -e "${STEP_NO}\t${stat}\t${rc}\t${run_user}\t${cat}\t${step}\t${log_rel}\t${cmd_rel}" >> "$STEPS_TSV"

  if [[ "$stat" == "FAIL" ]]; then
    echo -e "${RED}${BLD}FAIL EXCERPT (last 80 lines):${RST}"
    tail -n 80 "$log" || true
    echo -e "${YLW}--------------------------------------------------------------------------------${RST}"
    [[ "$STOP_ON_FAIL" == "1" ]] && return 1
  fi
  return 0
}

skip_step() {
  # skip_step <user> <cat> <step> <reason>
  local run_user="$1"; shift
  local cat="$1"; shift
  local step="$1"; shift
  local reason="${1:-SKIP}"

  STEP_NO=$((STEP_NO+1))
  local safe log_rel cmd_rel
  safe="$(sanitize "${cat}-${step}")"
  log_rel="log/${STEP_NO}_${run_user}_${safe}.log"
  cmd_rel="cmd/${STEP_NO}_${run_user}_${safe}.sh"

  mkdir -p "$RUN_DIR/log" "$RUN_DIR/cmd" || true
  echo "$reason" > "$RUN_DIR/$log_rel"
  echo "# skipped" > "$RUN_DIR/$cmd_rel"
  chmod 644 "$RUN_DIR/$cmd_rel" 2>/dev/null || true

  echo
  echo -e "${BLD}${CYN}[${STEP_NO}]${RST} ${cat} :: ${step}"
  echo -e "${DIM}LOG: $RUN_DIR/$log_rel${RST}"
  echo -e "${DIM}HINT: skipped${RST}"
  echo -e "${DIM}CMD: $RUN_DIR/$cmd_rel${RST}"
  echo -e "${BLD}RESULT:${RST} $(badge SKIP)  rc=0"
  echo -e "${YLW}--------------------------------------------------------------------------------${RST}"

  SKIP_N=$((SKIP_N+1))
  echo -e "${STEP_NO}	SKIP	0	${run_user}	${cat}	${step}	${log_rel}	${cmd_rel}" >> "$STEPS_TSV"
}

# Steps
step_pre() {
  title "PRE: quick prechecks"
  run_step root PRE "barresi fazaye disk" "$(hint_for PRE_DISK)" \
    'df -h / | sed -n "1p;2p"; echo; df -h "'"$BENCH"'" | sed -n "1p;2p"' "FAIL"

  run_step root PRE "barresi vojood bench va app" "$(hint_for PRE_EXISTS)" \
    '[ -d "'"$BENCH"'" ] && [ -d "'"$APP_DIR"'" ] && echo "OK: bench/app exists"' "FAIL"

  run_step root PRE "sakht poshe log-ha" "" \
    'mkdir -p "'"$RUN_DIR"'" && echo "RUN_DIR='"$RUN_DIR"'"' "FAIL"
}

step_fs() {
  title "FS: perms/ownership/bytecode (root)"
  run_step root FS "gozaresh file-haye mashkook (root-owned/pycache/pyc)" "$(hint_for FS_SUSPECT)" \
    'echo "== root-owned (top 50) =="; find "'"$APP_DIR"'" -xdev -user root -print 2>/dev/null | head -n 50 || true;
     echo;
     echo "== __pycache__ (top 50) =="; find "'"$APP_DIR"'" -xdev -name "__pycache__" -type d -print | head -n 50 || true;
     echo;
     echo "== *.pyc (top 50) =="; find "'"$APP_DIR"'" -xdev -name "*.pyc" -type f -print | head -n 50 || true' "FAIL"

  run_step root FS "malekiat: chown -R frappe:frappe apps/blue_hesab" "$(hint_for FS_CHOWN)" \
    '( getent passwd frappe >/dev/null 2>&1 && getent group frappe >/dev/null 2>&1 || { echo "FATAL: user/group frappe missing"; exit 2; }; chown -R frappe:frappe "'"$BENCH"'/apps/blue_hesab" 2>/dev/null || true; bad="$(find "'"$BENCH"'/apps/blue_hesab" -xdev -not -user frappe -print -quit 2>/dev/null || true)"; if [ -n "$bad" ]; then echo "FAIL: still not owned by frappe: $bad"; exit 2; fi; echo "OK: ownership fixed" )' "WARN"

  run_step root FS "permission: dirs=755 va *.py=644" "$(hint_for FS_CHMOD)" \
    'find "'"$BENCH"'/apps/blue_hesab -type d -exec chmod 755 {} \+;
     find "'"$BENCH"'/apps/blue_hesab -type f -name "*.py" -exec chmod 644 {} \+;
     echo "OK: chmod done"' "FAIL"

  run_step root FS "pak-sazi __pycache__ va *.pyc" "$(hint_for FS_PYC)" \
    'find "'"$BENCH"'/apps/blue_hesab -name "__pycache__" -type d -prune -exec rm -rf {} \+;
     find "'"$BENCH"'/apps/blue_hesab -name "*.pyc" -type f -delete;
     echo "OK: bytecode cleaned"' "FAIL"
}

step_core() {
  title "CORE: compile + cache + restart"
  run_step frappe CORE "compile file-haye hassas" "$(hint_for CORE_COMPILE)" \
"$(cmd_bench_simple "
python -m py_compile apps/blue_hesab/blue_hesab/hooks.py
python -m py_compile apps/blue_hesab/blue_hesab/bh_core/dimensions_policy.py
python -m py_compile apps/blue_hesab/blue_hesab/bh_core/vat_pipeline.py
python -m py_compile apps/blue_hesab/blue_hesab/bh_core/regress/legal_ci.py
echo OK
")" "FAIL"

  run_step frappe CORE "compileall bh_core" "$(hint_for CORE_COMPILEALL)" \
"$(cmd_bench_simple "
python -m compileall -q apps/blue_hesab/blue_hesab/bh_core
echo OK
")" "FAIL"

  run_step frappe CORE "clear-cache" "$(hint_for CORE_CACHE)" \
"$(cmd_bench_simple "bench --site \"$SITE\" clear-cache")" "FAIL"

  run_step frappe CORE "clear-website-cache" "$(hint_for CORE_CACHE)" \
"$(cmd_bench_simple "bench --site \"$SITE\" clear-website-cache")" "FAIL"

  run_step frappe CORE "bench restart" "$(hint_for CORE_RESTART)" \
"$(cmd_bench_simple "bench restart")" "FAIL"
}

step_dim() {
  title "DIM: dimensions"
  run_step frappe DIM "DIM smoke" "$(hint_for DIM_SMOKE)" \
"$(cmd_bench_exec "blue_hesab.bh_core.dim_smoke.run_dim_smoke" "{\"company\":\"$COMPANY\"}")" "FAIL"

  run_step frappe DIM "DIM02 terminal checks" "$(hint_for DIM02)" \
"$(cmd_bench_exec "blue_hesab.bh_core.dim02_terminal_checks.run_cli" "{\"company\":\"$COMPANY\"}")" "FAIL"

  local kwargs
  if [[ -n "$FROM_DATE" && -n "$TO_DATE" ]]; then
    kwargs="{\"company\":\"$COMPANY\",\"from_date\":\"$FROM_DATE\",\"to_date\":\"$TO_DATE\"}"
  elif [[ -n "$FROM_DATE" ]]; then
    kwargs="{\"company\":\"$COMPANY\",\"from_date\":\"$FROM_DATE\"}"
  else
    kwargs="{\"company\":\"$COMPANY\"}"
  fi

  run_step frappe DIM "DIM04 audit GL" "$(hint_for DIM04_AUDIT)" \
"$(cmd_bench_exec "blue_hesab.bh_core.dim02_terminal_checks.run_dim04_audit_gl" "$kwargs")" "FAIL"

  run_step frappe DIM "DIM04 GL stamp JE" "$(hint_for DIM04_STAMP)" \
"$(cmd_bench_exec "blue_hesab.bh_core.dim02_terminal_checks.run_dim04_gl_stamp_je" "{\"company\":\"$COMPANY\"}")" "FAIL"

  run_step frappe DIM "DIM04 GL stamp JE linewise" "$(hint_for DIM04_STAMP_LINE)" \
"$(cmd_bench_exec "blue_hesab.bh_core.dim02_terminal_checks.run_dim04_gl_stamp_je_linewise" "{\"company\":\"$COMPANY\"}")" "FAIL"
}

step_vat() {
  title "VAT: regressions"
  run_step frappe VAT "VAT lint v12" "$(hint_for VAT_LINT)" \
"$(cmd_bench_exec "blue_hesab.bh_core.vat_lint.run_v12_lint" "{}")" "FAIL"

  run_step frappe VAT "VAT intent regress v01" "$(hint_for VAT_INT01)" \
"$(cmd_bench_exec "blue_hesab.bh_core.vat_regress_intent_v01.run_vat12_intent_regress_cli" "{\"company\":\"$COMPANY\"}")" "FAIL"

  run_step frappe VAT "VAT-13 guard" "$(hint_for VAT13)" \
"$(cmd_bench_exec "blue_hesab.bh_core.vat_regress_vat13_guard.run_vat13_guard" "{\"company\":\"$COMPANY\"}")" "FAIL"

  run_step frappe VAT "VAT period lock v01" "$(hint_for VAT_LOCK01)" \
"$(cmd_bench_exec "blue_hesab.bh_core.vat_regress_period_lock_v01.run_v01" "{\"company\":\"$COMPANY\"}")" "FAIL"

  run_step frappe VAT "VAT period lock v02" "$(hint_for VAT_LOCK02)" \
"$(cmd_bench_exec "blue_hesab.bh_core.vat_regress_period_lock_v02.run_v02" "{\"company\":\"$COMPANY\"}")" "FAIL"

  run_step frappe VAT "VAT smoke SI base" "$(hint_for VAT_SMOKE)" \
"$(cmd_bench_exec "blue_hesab.bh_core.vat_smoke_si_v02.run_base" "{\"rate\":$RATE}")" "FAIL"

  # FIX: PI v01 signature does NOT accept company
  run_step frappe VAT "VAT MIXED regress PI v01" "$(hint_for VAT_MIX_PI)" \
"$(cmd_bench_exec "blue_hesab.bh_core.vat_regress_pi_v01.run_v01" "{\"rate\":$RATE}")" "FAIL"

  # safer: SI v02 often only needs rate too (keep company out to avoid TypeError)
  run_step frappe VAT "VAT MIXED regress SI v02" "$(hint_for VAT_MIX_SI)" \
"$(cmd_bench_exec "blue_hesab.bh_core.vat_regress_si_v02.run_v02" "{\"rate\":$RATE}")" "FAIL"

  run_step frappe VAT "VAT intent regress v08" "$(hint_for VAT_INT08)" \
"$(cmd_bench_exec "blue_hesab.bh_core.vat_regress_intent_v08.intent_regress_v08_cli" "{\"company\":\"$COMPANY\",\"rate\":$RATE}")" "FAIL"

  run_step frappe VAT "VAT10b terminal" "$(hint_for VAT10B)" \
"$(cmd_bench_exec "blue_hesab.bh_core.vat10b_terminal_checks.run_cli" "{\"company\":\"$COMPANY\"}")" "FAIL"

  run_step frappe VAT "VAT11 terminal" "$(hint_for VAT11)" \
"$(cmd_bench_exec "blue_hesab.bh_core.vat11_terminal_checks.run_cli" "{\"company\":\"$COMPANY\"}")" "FAIL"

  run_step frappe VAT "VAT16 terminal" "$(hint_for VAT16)" \
"$(cmd_bench_exec "blue_hesab.bh_core.vat16_terminal_checks.run_cli" "{\"company\":\"$COMPANY\"}")" "FAIL"

  run_step frappe VAT "VAT17 terminal" "$(hint_for VAT17)" \
"$(cmd_bench_exec "blue_hesab.bh_core.vat17_terminal_checks.run_cli" "{\"company\":\"$COMPANY\",\"rate\":$RATE}")" "FAIL"

  local hf="${HARD_FAIL_VAT18:-0}"
  run_step frappe VAT "VAT18 terminal" "$(hint_for VAT18)" \
"$(cmd_bench_exec "blue_hesab.bh_core.vat18_terminal_checks.run_cli" "{\"company\":\"$COMPANY\",\"hard_fail\":$hf}")" "FAIL"

  run_step frappe VAT "VAT CI legacy EP01 v0.3" "$(hint_for VAT_CI_LEGACY)" \
"$(cmd_bench_exec "blue_hesab.bh_core.vat_ci.run_ep01_v03_cli" "{\"company\":\"$COMPANY\",\"rate\":$RATE}")" "FAIL"

  run_step frappe VAT "VAT CI v12" "$(hint_for VAT_CI_V12)" \
"$(cmd_bench_exec "blue_hesab.bh_core.vat_ci_v12.run_ep01_v03_cli_v12" "{\"company\":\"$COMPANY\",\"rate\":$RATE}")" "FAIL"

  run_step frappe VAT "VAT CI v15 (optional)" "$(hint_for VAT_CI_V15)" \
"$(cmd_bench_exec "blue_hesab.bh_core.vat_ci_v15.run_ep01_v03_cli_v15" "{\"rate\":$RATE,\"site\":\"$SITE\"}")" "WARN"
}

step_legal() {
  title "LEGAL: legal outputs"
  run_step frappe LEGAL "LEGAL05 smoke sales cycle" "$(hint_for LEGAL05_S)" \
"$(cmd_bench_exec "blue_hesab.bh_core.legal05_smoke.smoke_legal05_sales_cycle" "{\"company\":\"$COMPANY\"}")" "FAIL"

  run_step frappe LEGAL "LEGAL05 smoke purchase cycle" "$(hint_for LEGAL05_P)" \
"$(cmd_bench_exec "blue_hesab.bh_core.legal05_smoke.smoke_legal05_purchase_cycle" "{\"company\":\"$COMPANY\"}")" "FAIL"

  # main gate
  run_step frappe LEGAL "LEGAL suite 07+08+09" "$(hint_for LEGAL_SUITE)" \
"$(cmd_bench_exec "blue_hesab.bh_core.regress.legal_ci.run_legal_suite" "{\"company\":\"$COMPANY\"}")" "FAIL"

  # LEGAL07/08/09 entrypoints -> noisy; run only if explicitly enabled
  if [[ "${LEGAL_ENTRYPOINTS}" == "1" ]]; then
    run_step frappe LEGAL "LEGAL07 regress" "$(hint_for LEGAL07)" \
      "$(cmd_bench_exec "blue_hesab.bh_core.legal07_regress.run_cli" "{\"company\":\"$COMPANY\"}")" "FAIL"

    run_step frappe LEGAL "LEGAL08 regress" "$(hint_for LEGAL08)" \
      "$(cmd_bench_exec "blue_hesab.bh_core.legal08_regress.run_cli" "{\"company\":\"$COMPANY\"}")" "FAIL"

    run_step frappe LEGAL "LEGAL09 regress" "$(hint_for LEGAL09)" \
      "$(cmd_bench_exec "blue_hesab.bh_core.legal09_regress.run_cli" "{\"company\":\"$COMPANY\"}")" "FAIL"
  else
    skip_step frappe LEGAL "LEGAL07 regress" "SKIP: set LEGAL_ENTRYPOINTS=1"
    skip_step frappe LEGAL "LEGAL08 regress" "SKIP: set LEGAL_ENTRYPOINTS=1"
    skip_step frappe LEGAL "LEGAL09 regress" "SKIP: set LEGAL_ENTRYPOINTS=1"
  fi
}

step_reports() {
  title "REP: reports/logs"
  run_step frappe REP "list latest bh_regress" "$(hint_for REP_LIST)" \
"$(cmd_bench_simple "
echo '== bh_regress latest (top 30) =='
ls -lt sites/$SITE/private/files/bh_regress 2>/dev/null | head -n 30 || true
echo
echo 'RUN_DIR=$RUN_DIR'
")" "FAIL"

  # FIX: tails belong to RUN_ROOT (not RUN_DIR)
  run_step frappe REP "tail legal_chain.log" "$(hint_for REP_TAIL)" \
"$(cmd_bench_simple "
f='sites/$SITE/private/files/bh_regress/legal_chain.log'
[ -f \"\$f\" ] && tail -n 120 \"\$f\" || echo \"(not found) \$f\"
")" "FAIL"

  run_step frappe REP "tail legal_policy.log" "$(hint_for REP_TAIL)" \
"$(cmd_bench_simple "
f='sites/$SITE/private/files/bh_regress/legal_policy.log'
[ -f \"\$f\" ] && tail -n 120 \"\$f\" || echo \"(not found) \$f\"
")" "FAIL"

  run_step frappe REP "tail legal_tamper.log" "$(hint_for REP_TAIL)" \
"$(cmd_bench_simple "
f='sites/$SITE/private/files/bh_regress/legal_tamper.log'
[ -f \"\$f\" ] && tail -n 120 \"\$f\" || echo \"(not found) \$f\"
")" "FAIL"
}

# Reporting (no awk)
print_summary() {
  print_kv_table "RUN INFO (table)" \
    "SITE" "$SITE" \
    "COMPANY" "$COMPANY" \
    "MODE" "$MODE" \
    "RATE" "$RATE" \
    "FROM_DATE" "${FROM_DATE:-}" \
    "TO_DATE" "${TO_DATE:-}" \
    "RUN_DIR" "$RUN_DIR" \
    "LAST_TSV" "$LAST_TSV"

  title "SUMMARY (steps table)"
  printf "%-4s | %-5s | %-3s | %-6s | %-6s | %-36s | %s\n" "#" "STAT" "RC" "USER" "CAT" "STEP" "LOG_REL"
  echo "-----+-------+-----+--------+--------+--------------------------------------+------------------------------"

  while IFS=$'\t' read -r idx stat rc user cat step log_rel cmd_rel; do
    [[ "$idx" == "idx" ]] && continue
    local stat_col; stat_col="$(badge "$stat")"
    printf "%-4s | %-5b | %-3s | %-6s | %-6s | %-36s | %s\n" "$idx" "$stat_col" "$rc" "$user" "$cat" "$step" "$log_rel"
    [[ "${SUMMARY_SPACED:-0}" == "1" ]] && echo
  done < "$STEPS_TSV"

  echo "-----+-------+-----+--------+--------+--------------------------------------+------------------------------"

  print_kv_table "TOTALS (table)" \
    "TOTAL_STEPS" "$STEP_NO" \
    "PASS" "$PASS_N 🙂" \
    "WARN" "$WARN_N" \
    "FAIL" "$FAIL_N 😢" \
    "SKIP" "$SKIP_N"
}


print_cat_summary() {
  title "CAT SUMMARY"
  printf "%-6s | %-4s | %-4s | %-4s\n" "CAT" "PASS" "WARN" "FAIL"
  echo "-------+------+-------+------"

  declare -A p w f
  while IFS=$'\t' read -r idx stat rc user cat step log_rel cmd_rel; do
    [[ "$idx" == "idx" ]] && continue
    case "$stat" in
      PASS) p["$cat"]=$(( ${p["$cat"]:-0} + 1 )) ;;
      WARN) w["$cat"]=$(( ${w["$cat"]:-0} + 1 )) ;;
      FAIL) f["$cat"]=$(( ${f["$cat"]:-0} + 1 )) ;;
    esac
  done < "$STEPS_TSV"

  for c in PRE FS CORE DIM VAT LEGAL REP; do
    printf "%-6s | %-4s | %-4s | %-4s\n" "$c" "${p[$c]:-0}" "${w[$c]:-0}" "${f[$c]:-0}"
  done
}


print_kv_table() {
  # print_kv_table "TITLE" "KEY1" "VAL1" "KEY2" "VAL2" ...
  local t="$1"; shift
  title "$t"
  printf "%-16s | %s\n" "KEY" "VALUE"
  echo "-----------------+--------------------------------------------------------------"
  while [[ $# -gt 0 ]]; do
    local k="$1"; local v="${2:-}"; shift 2 || true
    printf "%-16s | %s\n" "$k" "$v"
  done
}

mode_one() {
  local idx="${1:-}"
  [[ -n "$idx" ]] || { echo "Usage: $0 one <STEP_NO>"; exit 2; }
  local last; last="$(load_last_dir)"
  local tsv="$last/steps.tsv"
  [[ -f "$tsv" ]] || { echo "ERROR: missing $tsv"; exit 1; }

  local row=""
  while IFS=$'\t' read -r i stat rc user cat step log_rel cmd_rel; do
    [[ "$i" == "idx" ]] && continue
    [[ "$i" == "$idx" ]] || continue
    row="$i"$'\t'"$stat"$'\t'"$rc"$'\t'"$user"$'\t'"$cat"$'\t'"$step"$'\t'"$log_rel"$'\t'"$cmd_rel"
    break
  done < "$tsv"

  [[ -n "$row" ]] || { echo "ERROR: step $idx not found in last run: $last"; exit 1; }

  IFS=$'\t' read -r i stat rc user cat step log_rel cmd_rel <<<"$row"
  local cmd="$last/$cmd_rel"

  print_kv_table "REPLAY ONE STEP (last run)" \
    "LAST_RUN_DIR" "$last" \
    "STEP_NO" "$i" \
    "USER" "$user" \
    "CAT" "$cat" \
    "STEP" "$step" \
    "CMD_FILE" "$cmd_rel" \
    "LOG_FILE" "$log_rel"

  [[ -f "$cmd" ]] || { echo "ERROR: missing cmd file: $cmd"; exit 1; }

  title "EXEC"
  echo -e "${DIM}cmd: bash '$cmd'${RST}"
  echo -e "${YLW}--------------------------------------------------------------------------------${RST}"

  local out="$RUN_DIR/log/one_${i}_${cat}.log"
  local rc2=0
  set +e
  if [[ "$user" == "frappe" ]]; then
    if [[ "${KEEP_RAW_LOG:-0}" == "1" ]]; then
      local out_raw="${out%.log}.raw.log"
      sudo -u frappe -H bash -lc "bash '$cmd'" 2>&1 | tee "$out_raw" | pipe_finglish | tee "$out"
      rc2="${PIPESTATUS[0]}"
    else
      sudo -u frappe -H bash -lc "bash '$cmd'" 2>&1 | pipe_finglish | tee "$out"
      rc2="${PIPESTATUS[0]}"
    fi
  else
    if [[ "${KEEP_RAW_LOG:-0}" == "1" ]]; then
      local out_raw="${out%.log}.raw.log"
      bash -lc "bash '$cmd'" 2>&1 | tee "$out_raw" | pipe_finglish | tee "$out"
      rc2="${PIPESTATUS[0]}"
    else
      bash -lc "bash '$cmd'" 2>&1 | pipe_finglish | tee "$out"
      rc2="${PIPESTATUS[0]}"
    fi
  fi
  set -e

  echo -e "${YLW}--------------------------------------------------------------------------------${RST}"
  if [[ "$rc2" -eq 0 ]]; then
    echo -e "${GRN}${BLD}OK 🙂${RST}  rc=0  ${DIM}log: $out${RST}"
    exit 0
  fi
  echo -e "${RED}${BLD}FAIL 😢${RST} rc=$rc2  ${DIM}log: $out${RST}"
  exit "$rc2"
}

mode_tail() {
  local idx="${1:-}"
  local nlines="${2:-140}"
  [[ -n "$idx" ]] || { echo "Usage: $0 tail <STEP_NO> [LINES]"; exit 2; }
  local last; last="$(load_last_dir)"
  local tsv="$last/steps.tsv"
  [[ -f "$tsv" ]] || { echo "ERROR: missing $tsv"; exit 1; }

  local log_rel=""
  local cat=""
  local step=""
  while IFS=$'\t' read -r i stat rc user c s lr cr; do
    [[ "$i" == "idx" ]] && continue
    [[ "$i" == "$idx" ]] || continue
    log_rel="$lr"
    cat="$c"
    step="$s"
    break
  done < "$tsv"

  [[ -n "$log_rel" ]] || { echo "ERROR: step $idx not found in last run: $last"; exit 1; }

  local log="$last/$log_rel"
  print_kv_table "TAIL LOG (last run)" \
    "LAST_RUN_DIR" "$last" \
    "STEP_NO" "$idx" \
    "CAT" "$cat" \
    "STEP" "$step" \
    "LOG_FILE" "$log_rel" \
    "LINES" "$nlines"

  [[ -f "$log" ]] || { echo "ERROR: missing log file: $log"; exit 1; }

  title "TAIL"
  tail -n "$nlines" "$log" | pipe_finglish
  exit 0
}

print_next_commands() {
  title "NEXT COMMANDS (table)"
  printf "%-3s | %-86s | %s\n" "#" "COMMAND" "WHEN"
  echo "----+----------------------------------------------------------------------------------------+--------------------"

  local n=0
  add() { n=$((n+1)); printf "%-3s | %-86s | %s\n" "$n" "$1" "$2"; }

  # always useful
  add "sudo bash $APP_DIR/bh_runbook_regress.sh retry"    "rerun FAIL steps (last run)"
  add "sudo bash $APP_DIR/bh_runbook_regress.sh failed"   "show FAIL list + tails (last run)"
  add "sudo bash $APP_DIR/bh_runbook_regress.sh one <N>"   "rerun ONE step by number (last run)"
  add "sudo bash $APP_DIR/bh_runbook_regress.sh tail <N>"  "tail ONE step log (last run)"
  add "sudo bash $APP_DIR/bh_runbook_regress.sh reports"   "latest bh_regress + tails"
  add "sudo bash $APP_DIR/bh_runbook_regress.sh restart"   "compile + cache + restart only"
  add "sudo bash $APP_DIR/bh_runbook_regress.sh cache"     "cache only"
  add "sudo bash $APP_DIR/bh_runbook_regress.sh bytecode"  "ownership/perms + pycache clean"

  # suite reruns
  add "sudo bash $APP_DIR/bh_runbook_regress.sh quick"     "fast smoke suite"
  add "sudo bash $APP_DIR/bh_runbook_regress.sh dim"       "DIM suite only (option: FROM_DATE=YYYY-MM-DD)"
  add "sudo bash $APP_DIR/bh_runbook_regress.sh vat"       "VAT suite only"
  add "sudo HARD_FAIL_VAT18=1 bash $APP_DIR/bh_runbook_regress.sh vat" "VAT18 strict"
  add "sudo bash $APP_DIR/bh_runbook_regress.sh legal"     "LEGAL suite only"
  add "sudo bash $APP_DIR/bh_runbook_regress.sh all"       "full suite"

  print_kv_table "ENV HINTS (table)" \
    "PARAMS" "SITE=... COMPANY=... RATE=... FROM_DATE=YYYY-MM-DD TO_DATE=YYYY-MM-DD" \
    "CI_FLAGS" "NO_PAUSE=1 | DRY_RUN=1 | STOP_ON_FAIL=1"
}


print_coverage() {
  title "COVERAGE (what each group tests)"
  printf "%-6s | %-28s | %s\n" "CAT" "TEST" "GOAL"
  echo "-------+------------------------------+---------------------------------------------"
  printf "%-6s | %-28s | %s\n" "DIM"   "DIM smoke / DIM02"           "dimension policies/hooks sanity"
  printf "%-6s | %-28s | %s\n" "DIM"   "DIM04 audit GL"              "audit GL entries for required dims"
  printf "%-6s | %-28s | %s\n" "DIM"   "DIM04 stamp JE (+linewise)"  "JE->GL stamping validation"
  printf "%-6s | %-28s | %s\n" "VAT"   "lint"                        "VAT config/structure checks"
  printf "%-6s | %-28s | %s\n" "VAT"   "intent v01/v08"              "intent scenarios regress"
  printf "%-6s | %-28s | %s\n" "VAT"   "period lock v01/v02"         "period lock rules"
  printf "%-6s | %-28s | %s\n" "VAT"   "MIXED PI/SI"                 "mixed vat scenarios"
  printf "%-6s | %-28s | %s\n" "VAT"   "CI v12 + v15(optional)"      "CI wrappers"
  printf "%-6s | %-28s | %s\n" "LEGAL" "LEGAL suite 07+08+09"       "immutability/policy/emit-chain"
}

print_guide() {
  title "QUICK GUIDE"
  printf "%-3s | %-86s | %s\n" "#" "COMMAND" "NOTE"
  echo "----+----------------------------------------------------------------------------------------+--------------------"
  printf "%-3s | %-86s | %s\n" "1"  "sudo bash $APP_DIR/bh_runbook_regress.sh all"      "full"
  printf "%-3s | %-86s | %s\n" "2"  "sudo bash $APP_DIR/bh_runbook_regress.sh quick"    "quick"
  printf "%-3s | %-86s | %s\n" "3"  "sudo bash $APP_DIR/bh_runbook_regress.sh dim"      "DIM only"
  printf "%-3s | %-86s | %s\n" "4"  "sudo bash $APP_DIR/bh_runbook_regress.sh vat"      "VAT only"
  printf "%-3s | %-86s | %s\n" "5"  "sudo bash $APP_DIR/bh_runbook_regress.sh legal"    "LEGAL only"
  printf "%-3s | %-86s | %s\n" "6"  "sudo bash $APP_DIR/bh_runbook_regress.sh restart"  "compile+cache+restart"
  printf "%-3s | %-86s | %s\n" "7"  "sudo bash $APP_DIR/bh_runbook_regress.sh cache"    "cache only"
  printf "%-3s | %-86s | %s\n" "8"  "sudo bash $APP_DIR/bh_runbook_regress.sh bytecode" "ownership/perms + pycache clean"
  printf "%-3s | %-86s | %s\n" "9"  "sudo bash $APP_DIR/bh_runbook_regress.sh reports"  "reports/tails"
  printf "%-3s | %-86s | %s\n" "10" "sudo bash $APP_DIR/bh_runbook_regress.sh retry"    "retry FAIL steps (last run)"
  printf "%-3s | %-86s | %s\n" "11" "sudo bash $APP_DIR/bh_runbook_regress.sh failed"   "show FAIL list+tails (last run)"
  printf "%-3s | %-86s | %s\n" "12" "sudo bash $APP_DIR/bh_runbook_regress.sh one <N>"  "rerun ONE step by number (last run)"
  printf "%-3s | %-86s | %s\n" "13" "sudo bash $APP_DIR/bh_runbook_regress.sh tail <N>" "tail ONE step log (last run)"
  printf "%-3s | %-86s | %s\n" "14" "sudo HARD_FAIL_VAT18=1 bash $APP_DIR/bh_runbook_regress.sh vat" "VAT18 strict"

  print_kv_table "ENV PARAMS (table)" \
    "SITE" "target site (default: $SITE)" \
    "COMPANY" "target company (default: $COMPANY)" \
    "RATE" "test rate (default: $RATE)" \
    "FROM_DATE" "DIM audit from date (optional)" \
    "TO_DATE" "optional (future use)"
  print_kv_table "CI FLAGS (table)" \
    "NO_PAUSE" "1 => no interactive pause" \
    "DRY_RUN" "1 => print-only, no execution" \
    "STOP_ON_FAIL" "1 => stop immediately on first FAIL"
}


print_fail_quick_view() {
  title "FAIL QUICK VIEW"
  if [[ "$FAIL_N" -eq 0 ]]; then
    printf "%-16s | %s\n" "KEY" "VALUE"
    echo "-----------------+--------------------------------------------------------------"
    printf "%-16s | %s\n" "STATUS" "OK 🙂 (no FAIL steps)"
    return 0
  fi

  printf "%-4s | %-6s | %-30s | %-28s | %-42s | %-42s\n" \
    "#" "CAT" "STEP" "LOG_REL" "RERUN" "TAIL"
  echo "-----+--------+--------------------------------+------------------------------+--------------------------------------------+--------------------------------------------"

  while IFS=$'\t' read -r idx stat rc user cat step log_rel cmd_rel; do
    [[ "$idx" == "idx" ]] && continue
    [[ "$stat" != "FAIL" ]] && continue
    local rr="sudo bash $APP_DIR/bh_runbook_regress.sh one $idx"
    local tt="sudo bash $APP_DIR/bh_runbook_regress.sh tail $idx"
    printf "%-4s | %-6s | %-30s | %-28s | %-42s | %-42s\n" \
      "$idx" "$cat" "$step" "$log_rel" "$rr" "$tt"
  done < "$STEPS_TSV"
}



load_last_dir() {
  [[ -f "$LAST_DIR_FILE" ]] || { echo "ERROR: no last run dir file: $LAST_DIR_FILE"; exit 1; }
  cat "$LAST_DIR_FILE"
}

mode_failed() {
  local last; last="$(load_last_dir)"
  local tsv="$last/steps.tsv"
  [[ -f "$tsv" ]] || { echo "ERROR: missing $tsv"; exit 1; }

  title "FAILED (last run) - list + tail"
  echo -e "${DIM}LAST_RUN_DIR: $last${RST}"

  while IFS=$'\t' read -r idx stat rc user cat step log_rel cmd_rel; do
    [[ "$idx" == "idx" ]] && continue
    [[ "$stat" != "FAIL" ]] && continue
    echo
    echo -e "${RED}${BLD}#${idx}  ${cat} :: ${step}${RST}"
    echo -e "${DIM}LOG: ${last}/${log_rel}${RST}"
    echo -e "${YLW}--------------------------------------------------------------------------------${RST}"
    tail -n 120 "${last}/${log_rel}" || true
    echo -e "${YLW}--------------------------------------------------------------------------------${RST}"
    pause
  done < "$tsv"
}

mode_retry() {
  local last; last="$(load_last_dir)"
  local tsv="$last/steps.tsv"
  [[ -f "$tsv" ]] || { echo "ERROR: missing $tsv"; exit 1; }

  title "RETRY FAIL steps (last run)"
  echo -e "${DIM}LAST_RUN_DIR: $last${RST}"
  pause

  while IFS=$'\t' read -r idx stat rc user cat step log_rel cmd_rel; do
    [[ "$idx" == "idx" ]] && continue
    [[ "$stat" != "FAIL" ]] && continue
    local cmd="$last/$cmd_rel"
    local out="$RUN_DIR/log/retry_${idx}.log"
    echo
    echo -e "${BLU}${BLD}[RETRY] ${cat} :: ${step}${RST}"
    echo -e "${DIM}CMD: $cmd${RST}"
    echo -e "${DIM}LOG: $out${RST}"
    echo -e "${YLW}--------------------------------------------------------------------------------${RST}"
    set +e
    if [[ "$user" == "frappe" ]]; then
if [[ "${KEEP_RAW_LOG:-0}" == "1" ]]; then
  local out_raw="${out%.log}.raw.log"
  sudo -u frappe -H bash -lc "bash '$cmd'" 2>&1 | tee "$out_raw" | pipe_finglish | tee "$out"
  rc="${PIPESTATUS[0]}"
else
  sudo -u frappe -H bash -lc "bash '$cmd'" 2>&1 | pipe_finglish | tee "$out"
  rc="${PIPESTATUS[0]}"
fi
    else
if [[ "${KEEP_RAW_LOG:-0}" == "1" ]]; then
  local out_raw="${out%.log}.raw.log"
  bash -lc "bash '$cmd'" 2>&1 | tee "$out_raw" | pipe_finglish | tee "$out"
  rc="${PIPESTATUS[0]}"
else
  bash -lc "bash '$cmd'" 2>&1 | pipe_finglish | tee "$out"
  rc="${PIPESTATUS[0]}"
fi
    fi
    set -e
    if [[ "$rc" -eq 0 ]]; then
      echo -e "${BLD}RESULT:${RST} $(badge PASS)  ${DIM}rc=${rc}${RST}"
    else
      echo -e "${BLD}RESULT:${RST} $(badge FAIL)  ${DIM}rc=${rc}${RST}"
    fi
  done < "$tsv"
}

MODE="${1:-all}"

print_kv_table "RUN CONTEXT (table)" \
  "SITE" "$SITE" \
  "COMPANY" "$COMPANY" \
  "MODE" "$MODE" \
  "RATE" "$RATE" \
  "FROM_DATE" "${FROM_DATE:-}" \
  "TO_DATE" "${TO_DATE:-}" \
  "RUN_DIR" "$RUN_DIR" \
  "RUN_ROOT" "$RUN_ROOT"

print_kv_table "PLAN (table)" \
  "ORDER" "PRE -> FS -> CORE -> DIM -> VAT -> LEGAL -> REP" \
  "NOTE" "Outputs are ASCII-only (finglish/english) for Bitvise-safe logs"

pause

case "$MODE" in
  all)     step_pre; step_fs; step_core; step_dim; step_vat; step_legal; step_reports ;;
  quick)   step_pre; step_core; step_dim; step_vat; step_legal ;;
  dim)     step_pre; step_core; step_dim ;;
  vat)     step_pre; step_core; step_vat ;;
  legal)   step_pre; step_core; step_legal ;;
  restart) step_pre; step_core ;;
  cache)
    title "CACHE only"
    run_step frappe CORE "clear-cache" "$(hint_for CORE_CACHE)" "$(cmd_bench_simple "bench --site \"$SITE\" clear-cache")" "FAIL"
    run_step frappe CORE "clear-website-cache" "$(hint_for CORE_CACHE)" "$(cmd_bench_simple "bench --site \"$SITE\" clear-website-cache")" "FAIL"
    ;;
  bytecode) title "BYTECODE/PERMS only"; step_fs ;;
  reports)  title "REPORTS only"; step_reports ;;
  retry)    mode_retry; exit 0 ;;
  failed)   mode_failed; exit 0 ;;
  *)
    echo "Usage: $0 {all|quick|dim|vat|legal|restart|cache|bytecode|reports|retry|failed}"
    exit 2
    ;;
esac

print_summary
print_cat_summary
print_coverage
print_guide
print_fail_quick_view
print_next_commands

RUN_END_EPOCH="$(date +%s)"
RUN_DUR_SEC="$((RUN_END_EPOCH - RUN_START_EPOCH))"

result_txt="OK 🙂"
exit_code=0
if [[ "$FAIL_N" -ne 0 ]]; then
  result_txt="FAIL 😢"
  exit_code=1
fi

print_kv_table "FINAL (table)" \
  "RESULT" "$result_txt" \
  "DURATION" "${RUN_DUR_SEC}s" \
  "TOTAL_STEPS" "$STEP_NO" \
  "PASS" "$PASS_N 🙂" \
  "WARN" "$WARN_N" \
  "FAIL" "$FAIL_N 😢" \
  "SKIP" "$SKIP_N" \
  "RUN_DIR" "$RUN_DIR" \
  "LAST_TSV" "$LAST_TSV"

exit "$exit_code"
