#!/usr/bin/env bash
# BlueHesab Runbook (baba.bluehesab.ir)
# هدف: نرمال‌سازی امن + اجرای تست‌ها/رگرشن‌ها + گزارش خوانا و فارسی‌پسند در ترمینال

set -uo pipefail

############################
# Locale / RTL helpers
############################
# تلاش برای اجبار UTF-8 (برای اینکه فارسی به‌هم نریزد)
export LANG="${LANG:-C.UTF-8}"
export LC_ALL="${LC_ALL:-C.UTF-8}"

# Unicode Direction Marks
# RLI/PDI => راست‌به‌چپ ایزوله، LRI/PDI => چپ‌به‌راست ایزوله
RLI=$'\u2067'
LRI=$'\u2066'
PDI=$'\u2069'

rtl() { printf "%s%s%s\n" "$RLI" "$1" "$PDI"; }
ltr() { printf "%s%s%s\n" "$LRI" "$1" "$PDI"; }

############################
# Config (override via env)
############################
SITE="${SITE:-baba.bluehesab.ir}"
COMPANY="${COMPANY:-BlueAPi}"
RATE="${RATE:-1000000}"
FROM_DATE="${FROM_DATE:-}"                 # مثال: 2026-01-04 (اختیاری برای DIM audit)
HARD_FAIL_VAT18="${HARD_FAIL_VAT18:-0}"    # 1 => vat18 سخت‌گیر
NO_PAUSE="${NO_PAUSE:-0}"                 # 1 => بدون توقف (برای CI)
SHOW_FAIL_TAIL_LINES="${SHOW_FAIL_TAIL_LINES:-140}"

BENCH_DIR="${BENCH_DIR:-/home/frappe/frappe-bench}"
PY="${PY:-/home/frappe/frappe-bench/env/bin/python}"

LOG_DIR_DEFAULT="$BENCH_DIR/sites/$SITE/private/files/bh_regress"
LOG_DIR="${LOG_DIR:-$LOG_DIR_DEFAULT}"

RUN_ID="${RUN_ID:-$(date +%Y%m%d-%H%M%S)-$RANDOM$RANDOM}"
RUN_DIR="$LOG_DIR/runbook_${RUN_ID}"
LAST_TSV="$LOG_DIR/runbook_last.tsv"

############################
# UI helpers (ANSI)
############################
RED='\033[0;31m'
GRN='\033[0;32m'
YLW='\033[0;33m'
BLU='\033[0;34m'
CYN='\033[0;36m'
WHT='\033[0;37m'
BOLD='\033[1m'
DIMC='\033[2m'
NC='\033[0m'

BG_GRN='\033[42m'
BG_RED='\033[41m'
BG_YLW='\033[43m'
BG_BLU='\033[44m'
BG_WHT='\033[47m'
FG_BLK='\033[30m'

ts() { date "+%F %T"; }

line() { printf "%s\n" "================================================================================"; }
line2() { printf "%s\n" "--------------------------------------------------------------------------------"; }

title() {
  line
  echo -e "${BOLD}${BLU}[$(ts)] $*${NC}"
  line
}

badge_pass() { echo -e "${BOLD}${BG_GRN}${FG_BLK} PASS ${NC}"; }
badge_fail() { echo -e "${BOLD}${BG_RED}${WHT} FAIL ${NC}"; }
badge_warn() { echo -e "${BOLD}${BG_YLW}${FG_BLK} WARN ${NC}"; }

pause_if_tty() {
  [[ "$NO_PAUSE" == "1" ]] && return 0
  [[ -t 0 ]] || return 0
  echo
  read -r -p "برای ادامه Enter بزنید..." _
}

need_root() {
  if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
    echo -e "${RED}${BOLD}[FATAL] این اسکریپت باید با root اجرا شود.${NC}"
    echo "مثال: sudo bash $0 all"
    exit 2
  fi
}

require_paths() {
  [[ -d "$BENCH_DIR" ]] || { echo -e "${RED}${BOLD}[FATAL] BENCH_DIR یافت نشد: $BENCH_DIR${NC}"; exit 2; }
  [[ -x "$PY" ]] || { echo -e "${RED}${BOLD}[FATAL] Python venv یافت نشد/قابل اجرا نیست: $PY${NC}"; exit 2; }
}

slugify() {
  local s="$1"
  s="${s// /_}"
  s="$(echo "$s" | tr -cd '[:alnum:]_().-')"
  echo "${s:0:80}"
}

b64() { printf "%s" "$1" | base64 -w0; }

############################
# Runbook state
############################
mkdir -p "$RUN_DIR" "$LOG_DIR" 2>/dev/null || true
TSV_TMP="$RUN_DIR/runbook.tsv"
: > "$TSV_TMP"

declare -a __SEQ=()
declare -a __CAT=()
declare -a __NAME=()
declare -a __USER=()
declare -a __RC=()
declare -a __STATUS=()
declare -a __LOG=()
declare -a __CMD=()

STEP_NO=0

record_step() {
  local cat="$1" name="$2" user="$3" rc="$4" status="$5" log_path="$6" cmd="$7"
  __SEQ+=("$STEP_NO")
  __CAT+=("$cat")
  __NAME+=("$name")
  __USER+=("$user")
  __RC+=("$rc")
  __STATUS+=("$status")
  __LOG+=("$log_path")
  __CMD+=("$cmd")
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$STEP_NO" "$status" "$rc" "$user" "$cat" "$name" "$log_path" "$(b64 "$cmd")" >> "$TSV_TMP"
}

finalize_last_tsv() { cp -f "$TSV_TMP" "$LAST_TSV" 2>/dev/null || true; }

############################
# Intro / Plan
############################
print_intro() {
  title "BlueHesab Runbook — اجرای رگرشن‌ها و نرمال‌سازی"

  echo -e "${BOLD}${CYN}محیط اجرا:${NC}"
  echo -e "  SITE      : ${BOLD}$SITE${NC}"
  echo -e "  COMPANY   : ${BOLD}$COMPANY${NC}"
  echo -e "  RATE      : ${BOLD}$RATE${NC}"
  echo -e "  FROM_DATE : ${BOLD}${FROM_DATE:-'(unset)'}${NC}"
  echo -e "  UTF-8     : LANG=${BOLD}$LANG${NC} | LC_ALL=${BOLD}$LC_ALL${NC}"
  echo

  echo -e "${BOLD}${CYN}مراحل اجرای حالت all:${NC}"
  echo "  1) Preflight"
  echo "  2) Fix Ownership/Permission + پاکسازی bytecode"
  echo "  3) Compile + Clear Cache + Restart"
  echo "  4) DIM suite"
  echo "  5) VAT suite (core + terminal + CI)"
  echo "  6) LEGAL suite"
  echo "  7) Reports/Logs"
  echo "  8) Summary + Excerpts"
  line2
  pause_if_tty
}

############################
# Core runner
############################
run_cmd() {
  # run_cmd <user:root|frappe> <cat> <name> <cmd> [allow_fail=0|1]
  local user="$1"; shift
  local cat="$1"; shift
  local name="$1"; shift
  local cmd="$1"; shift
  local allow_fail="${1:-0}"

  STEP_NO=$((STEP_NO+1))
  local slug log_path
  slug="$(slugify "$name")"
  log_path="$RUN_DIR/$(printf '%03d' "$STEP_NO")_${user}_${slug}.log"

  echo
  echo -e "${BOLD}${CYN}[$(ts)]  مرحله ${STEP_NO}  |  ${cat}${NC}"
  echo -e "${BOLD}${WHT}${name}${NC}"
  echo -e "${DIMC}log: $log_path${NC}"
  echo -e "${DIMC}cmd:${NC} $cmd"
  line2

  local rc=0
  if [[ "$user" == "root" ]]; then
    { bash -lc "cd '$BENCH_DIR'; set -euo pipefail; export LANG='${LANG}' LC_ALL='${LC_ALL}'; $cmd"; } 2>&1 | tee "$log_path"
    rc=${PIPESTATUS[0]}
  else
    { sudo -u frappe -H bash -lc "cd '$BENCH_DIR'; set -euo pipefail; export PATH='/home/frappe/.local/bin:$BENCH_DIR/env/bin:$PATH'; export LANG='${LANG}' LC_ALL='${LC_ALL}'; $cmd"; } 2>&1 | tee "$log_path"
    rc=${PIPESTATUS[0]}
  fi

  local status="PASS"
  if [[ "$rc" -ne 0 ]]; then
    if [[ "$allow_fail" == "1" ]]; then
      status="WARN"
      echo
      echo -e "$(badge_warn)  ${YLW}${BOLD}${cat}${NC} :: ${BOLD}${name}${NC}  (rc=$rc)"
      echo -e "${DIMC}این مرحله اجازه FAIL دارد و ادامه می‌دهیم.${NC}"
    else
      status="FAIL"
      echo
      echo -e "$(badge_fail)  ${RED}${BOLD}${cat}${NC} :: ${BOLD}${name}${NC}  (rc=$rc)"
      echo -e "${YLW}${BOLD}--- خلاصه خطا (tail آخر) ---${NC}"
      tail -n "$SHOW_FAIL_TAIL_LINES" "$log_path" || true
      echo -e "${YLW}${BOLD}---------------------------${NC}"
    fi
  else
    echo
    echo -e "$(badge_pass)  ${GRN}${BOLD}${cat}${NC} :: ${BOLD}${name}${NC}"
  fi

  record_step "$cat" "$name" "$user" "$rc" "$status" "$log_path" "$cmd"
  finalize_last_tsv
}

bench_exec() {
  # bench_exec <cat> <name> <method.path> <kwargs_py_dict_optional>
  local cat="$1"; shift
  local name="$1"; shift
  local method="$1"; shift
  local kwargs="${1:-}"

  if [[ -n "$kwargs" ]]; then
    run_cmd "frappe" "$cat" "$name" "bench --site '$SITE' execute '$method' --kwargs '$kwargs'"
  else
    run_cmd "frappe" "$cat" "$name" "bench --site '$SITE' execute '$method'"
  fi
}

############################
# Sections
############################
step_preflight() {
  title "00) پیش‌نیازها (Preflight)"
  run_cmd "root" "PRE" "بررسی فضای دیسک" "df -h | head -n 60"
  run_cmd "root" "PRE" "بررسی وجود bench و اپ" "test -d '$BENCH_DIR/apps/blue_hesab' && echo OK"
  run_cmd "root" "PRE" "ساخت پوشه لاگ‌ها" "mkdir -p '$LOG_DIR' '$RUN_DIR' && ls -ld '$LOG_DIR' '$RUN_DIR'"
}

step_fix_perms_and_bytecode() {
  title "01) فیکس قطعی Permission/Ownership + پاکسازی bytecode"

  run_cmd "root" "FS" "گزارش فایل‌های مشکوک (root-owned/pycache/pyc)" \
    "set +o pipefail; \
     find apps/blue_hesab \\( -path '*/__pycache__' -o -name '*.pyc' -o -not -user frappe \\) -print 2>/dev/null | sed -n '1,260p'; \
     true" \
    1

  run_cmd "root" "FS" "مالکیت: chown -R frappe:frappe apps/blue_hesab" \
    "chown -R frappe:frappe apps/blue_hesab"

  run_cmd "root" "FS" "پرمیشن: dirs=755 و *.py=644" \
    "find apps/blue_hesab -type d -exec chmod 755 {} +; \
     find apps/blue_hesab -type f -name '*.py' -exec chmod 644 {} +"

  run_cmd "root" "FS" "پاکسازی __pycache__ و *.pyc" \
    "find apps/blue_hesab -type d -name '__pycache__' -prune -exec rm -rf {} +; \
     find apps/blue_hesab -type f -name '*.pyc' -delete 2>/dev/null || true"
}

step_compile_and_restart() {
  title "02) Compile + Clear Cache + Restart"

  run_cmd "frappe" "CORE" "Compile فایل‌های حساس" \
    "$PY -m py_compile \
      apps/blue_hesab/blue_hesab/bh_core/dimensions_policy.py \
      apps/blue_hesab/blue_hesab/bh_core/dimensions_hook_adapter.py \
      apps/blue_hesab/blue_hesab/hooks.py"

  run_cmd "frappe" "CORE" "Compileall bh_core (اسکن سریع سینتکس/ایمپورت)" \
    "$PY -m compileall -q apps/blue_hesab/blue_hesab/bh_core"

  run_cmd "frappe" "CORE" "Clear cache" "bench --site '$SITE' clear-cache"
  run_cmd "frappe" "CORE" "Clear website cache" "bench --site '$SITE' clear-website-cache"
  run_cmd "frappe" "CORE" "Restart bench" "bench restart"
}

step_cache_only() {
  title "02b) فقط پاکسازی Cache (بدون دست‌زدن به فایل‌ها)"
  run_cmd "frappe" "CORE" "Clear cache" "bench --site '$SITE' clear-cache"
  run_cmd "frappe" "CORE" "Clear website cache" "bench --site '$SITE' clear-website-cache"
}

step_dim_suite() {
  title "03) DIM (Dimensions) — تست‌ها"

  bench_exec "DIM" "DIM smoke" \
    "blue_hesab.bh_core.dim_smoke.run_dim_smoke" \
    "{\"company\":\"$COMPANY\"}"

  bench_exec "DIM" "DIM terminal checks (DIM02)" \
    "blue_hesab.bh_core.dim02_terminal_checks.run_cli" \
    "{\"company\":\"$COMPANY\"}"

  if [[ -n "$FROM_DATE" ]]; then
    bench_exec "DIM" "DIM audit GL (DIM04) از تاریخ $FROM_DATE" \
      "blue_hesab.bh_core.dim02_terminal_checks.run_dim04_audit_gl" \
      "{\"company\":\"$COMPANY\",\"from\":\"$FROM_DATE\"}"
  else
    bench_exec "DIM" "DIM audit GL (DIM04)" \
      "blue_hesab.bh_core.dim02_terminal_checks.run_dim04_audit_gl" \
      "{\"company\":\"$COMPANY\"}"
  fi

  bench_exec "DIM" "DIM04 GL stamp (Journal Entry)" \
    "blue_hesab.bh_core.dim02_terminal_checks.run_dim04_gl_stamp_je" \
    "{\"company\":\"$COMPANY\"}"

  bench_exec "DIM" "DIM04 GL stamp linewise (Journal Entry)" \
    "blue_hesab.bh_core.dim02_terminal_checks.run_dim04_gl_stamp_je_linewise" \
    "{\"company\":\"$COMPANY\"}"
}

step_vat_core() {
  title "04) VAT — هسته تست‌ها"

  bench_exec "VAT" "VAT lint (v12)" \
    "blue_hesab.bh_core.vat_lint.run_v12_lint"

  bench_exec "VAT" "VAT intent regress (v01)" \
    "blue_hesab.bh_core.vat_regress_intent_v01.run_v01_cli" \
    "{\"company\":\"$COMPANY\"}"

  bench_exec "VAT" "VAT-13 guard (flip EXCL/INCL + submit-block)" \
    "blue_hesab.bh_core.vat_regress_vat13_guard.run_vat13_guard" \
    "{\"company\":\"$COMPANY\",\"rate\":$RATE}"

  bench_exec "VAT" "VAT period lock v01" \
    "blue_hesab.bh_core.vat_regress_period_lock_v01.run_v01" \
    "{\"company\":\"$COMPANY\"}"

  bench_exec "VAT" "VAT period lock v02" \
    "blue_hesab.bh_core.vat_regress_period_lock_v02.run_v02" \
    "{\"company\":\"$COMPANY\"}"

  bench_exec "VAT" "VAT smoke SI base" \
    "blue_hesab.bh_core.vat_smoke_si_v02.run_base" \
    "{\"rate\":$RATE}"

  bench_exec "VAT" "VAT MIXED regress (PI v01, 8 سناریو)" \
    "blue_hesab.bh_core.vat_regress_pi_v01.run_v01" \
    "{\"rate\":$RATE}"

  bench_exec "VAT" "VAT MIXED regress (SI v02, 8 سناریو)" \
    "blue_hesab.bh_core.vat_regress_si_v02.run_v02" \
    "{\"rate\":$RATE}"

  bench_exec "VAT" "VAT intent regress (v08)" \
    "blue_hesab.bh_core.vat_regress_intent_v08.intent_regress_v08_cli" \
    "{\"company\":\"$COMPANY\",\"rate\":$RATE}"
}

step_vat_terminal_checks() {
  title "05) VAT — Terminal checks (Sanity)"

  bench_exec "VAT" "VAT10b terminal checks" \
    "blue_hesab.bh_core.vat10b_terminal_checks.run_cli" \
    "{\"company\":\"$COMPANY\"}"

  bench_exec "VAT" "VAT11 terminal checks" \
    "blue_hesab.bh_core.vat11_terminal_checks.run_cli" \
    "{\"company\":\"$COMPANY\"}"

  bench_exec "VAT" "VAT16 terminal checks" \
    "blue_hesab.bh_core.vat16_terminal_checks.run_cli" \
    "{\"company\":\"$COMPANY\"}"

  bench_exec "VAT" "VAT17 terminal checks" \
    "blue_hesab.bh_core.vat17_terminal_checks.run_cli" \
    "{\"company\":\"$COMPANY\",\"rate\":$RATE}"

  if [[ "$HARD_FAIL_VAT18" == "1" ]]; then
    bench_exec "VAT" "VAT18 terminal checks (hard_fail=1)" \
      "blue_hesab.bh_core.vat18_terminal_checks.runrun_cli" \
      "{\"company\":\"$COMPANY\",\"rate\":$RATE,\"hard_fail\":1}"
  else
    bench_exec "VAT" "VAT18 terminal checks" \
      "blue_hesab.bh_core.vat18_terminal_checks.run_cli" \
      "{\"company\":\"$COMPANY\"}"
  fi
}

step_vat_ci_wrappers() {
  title "06) VAT — CI Wrappers (آخر سر)"

  bench_exec "VAT" "VAT CI (legacy) EP01 v0.3" \
    "blue_hesab.bh_core.vat_ci.run_ep01_v03_cli" \
    "{\"rate\":$RATE}"

  bench_exec "VAT" "VAT CI v12 (EP01 v0.3 + intent)" \
    "blue_hesab.bh_core.vat_ci_v12.run_ep01_v03_cli_v12" \
    "{\"rate\":$RATE,\"company\":\"$COMPANY\"}"

  # FIX: v15 نباید company بگیرد
  bench_exec "VAT" "VAT CI v15 (اختیاری)" \
    "blue_hesab.bh_core.vat_ci_v15.run_ep01_v03_cli_v15" \
    "{\"rate\":$RATE,\"site\":\"$SITE\"}"
}

step_legal_suite() {
  title "07) LEGAL — تست‌ها"

  bench_exec "LEGAL" "LEGAL05 smoke sales cycle" \
    "blue_hesab.bh_core.legal05_smoke.smoke_legal05_sales_cycle" \
    "{\"company\":\"$COMPANY\",\"qty\":1,\"rate\":$RATE,\"vat_price_mode\":\"Exclusive\",\"mutate_amend\":True}"

  bench_exec "LEGAL" "LEGAL05 smoke purchase cycle" \
    "blue_hesab.bh_core.legal05_smoke.smoke_legal05_purchase_cycle" \
    "{\"company\":\"$COMPANY\",\"qty\":1,\"rate\":$RATE,\"vat_price_mode\":\"Exclusive\",\"mutate_amend\":True}"

  bench_exec "LEGAL" "LEGAL suite (07+08+09)" \
    "blue_hesab.bh_core.regress.legal_ci.run_legal_suite" \
    "{\"company\":\"$COMPANY\"}"

  bench_exec "LEGAL" "LEGAL07 regress" \
    "blue_hesab.bh_core.legal07_regress.run_legal07_regress" \
    "{\"company\":\"$COMPANY\"}"

  bench_exec "LEGAL" "LEGAL08 regress" \
    "blue_hesab.bh_core.legal08_regress.run_legal08_regress" \
    "{\"company\":\"$COMPANY\"}"

  bench_exec "LEGAL" "LEGAL09 regress" \
    "blue_hesab.bh_core.legal09_regress.run_legal09_regress" \
    "{\"company\":\"$COMPANY\"}"
}

step_reports() {
  title "08) گزارش‌ها و لاگ‌ها (Tail)"

  run_cmd "frappe" "REP" "لیست آخرین گزارش‌ها" \
    "ls -lat '$LOG_DIR' | head -n 140 || true" \
    1

  run_cmd "frappe" "REP" "Tail: legal_chain.log" \
    "tail -n 140 '$LOG_DIR/legal_chain.log' 2>/dev/null || true" \
    1

  run_cmd "frappe" "REP" "Tail: legal_policy.log" \
    "tail -n 140 '$LOG_DIR/legal_policy.log' 2>/dev/null || true" \
    1

  run_cmd "frappe" "REP" "Tail: legal_tamper.log" \
    "tail -n 140 '$LOG_DIR/legal_tamper.log' 2>/dev/null || true" \
    1
}

step_migrate_optional() {
  title "09) Migrate (اختیاری)"
  run_cmd "frappe" "CORE" "bench migrate" "bench --site '$SITE' migrate"
  run_cmd "frappe" "CORE" "bench build (اختیاری)" "bench build || true" 1
  step_cache_only
  run_cmd "frappe" "CORE" "Restart bench" "bench restart"
}

############################
# Failure excerpts
############################
print_failure_excerpts() {
  title "EXCERPT خطاها (برای دیباگ سریع)"
  echo -e "${DIMC}مسیر لاگ کامل هر مرحله کنار همان مرحله چاپ شده و داخل SUMMARY هم آمده است.${NC}"
  echo

  local i any=0
  for i in "${!__NAME[@]}"; do
    if [[ "${__STATUS[$i]}" == "FAIL" ]]; then
      any=1
      echo -e "$(badge_fail)  ${RED}${BOLD}${__CAT[$i]}${NC} :: ${BOLD}${__NAME[$i]}${NC} (rc=${__RC[$i]})"
      echo -e "${DIMC}log: ${__LOG[$i]}${NC}"
      echo -e "${DIMC}cmd: ${__CMD[$i]}${NC}"
      echo -e "${YLW}${BOLD}--- tail ---${NC}"
      tail -n "$SHOW_FAIL_TAIL_LINES" "${__LOG[$i]}" || true
      line2
      pause_if_tty
    fi
  done

  if [[ "$any" == "0" ]]; then
    echo -e "$(badge_pass)  ${GRN}${BOLD}هیچ FAILی ثبت نشد.${NC}"
  fi
}

############################
# Summary tables
############################
summary_categories_table() {
  local cats=("PRE" "FS" "CORE" "DIM" "VAT" "LEGAL" "REP")
  echo -e "${BOLD}${CYN}خلاصه دسته‌بندی‌شده:${NC}"
  printf "%-8s | %-5s | %-5s | %-5s\n" "CAT" "PASS" "WARN" "FAIL"
  echo "---------+-------+-------+------"
  local c i tp tf tw
  for c in "${cats[@]}"; do
    tp=0; tf=0; tw=0
    for i in "${!__CAT[@]}"; do
      [[ "${__CAT[$i]}" == "$c" ]] || continue
      [[ "${__STATUS[$i]}" == "PASS" ]] && ((tp++))
      [[ "${__STATUS[$i]}" == "WARN" ]] && ((tw++))
      [[ "${__STATUS[$i]}" == "FAIL" ]] && ((tf++))
    done
    (( tp + tf + tw > 0 )) || continue
    printf "%-8s | %-5s | %-5s | %-5s\n" "$c" "$tp" "$tw" "$tf"
  done
  echo
}

coverage_table() {
  echo -e "${BOLD}${CYN}پوشش تست‌ها (مختصر):${NC}"
  printf "%-8s | %-34s | %s\n" "حوزه" "تست/رگرشن" "هدف"
  echo "---------+------------------------------------+----------------------------------------------"

  # DIM
  printf "%-8s | %-34s | %s\n" "DIM" "$(ltr "DIM smoke + DIM02")" "$(rtl "سلامت تنظیمات ابعاد و هوک‌ها")"
  printf "%-8s | %-34s | %s\n" "DIM" "$(ltr "DIM04 audit GL")" "$(rtl "بررسی GLهای واقعی برای داشتن ابعاد لازم")"
  printf "%-8s | %-34s | %s\n" "DIM" "$(ltr "DIM04 GL stamp JE (+linewise)")" "$(rtl "تست عملی ثبت سند و ثبت ابعاد روی GL")"

  # VAT
  printf "%-8s | %-34s | %s\n" "VAT" "$(ltr "lint")" "$(rtl "کنترل کیفیت ساختار VAT")"
  printf "%-8s | %-34s | %s\n" "VAT" "$(ltr "intent regress v01/v08")" "$(rtl "سناریوهای Intent و جلوگیری از رفتار اشتباه")"
  printf "%-8s | %-34s | %s\n" "VAT" "$(ltr "VAT-13 guard")" "$(rtl "جلوگیری از flip غیرمجاز و submit-block")"
  printf "%-8s | %-34s | %s\n" "VAT" "$(ltr "period lock v01/v02")" "$(rtl "قفل دوره‌ها و جلوگیری از دستکاری")"
  printf "%-8s | %-34s | %s\n" "VAT" "$(ltr "MIXED regress (SI/PI)")" "$(rtl "سناریوهای ترکیبی Mixed برای خرید/فروش")"
  printf "%-8s | %-34s | %s\n" "VAT" "$(ltr "CI v12 + v15")" "$(rtl "بسته کامل CI و چک نهایی")"

  # LEGAL
  printf "%-8s | %-34s | %s\n" "LEGAL" "$(ltr "LEGAL05 smoke cycles")" "$(rtl "چرخه فروش/خرید issue/cancel/amend (Smoke)")"
  printf "%-8s | %-34s | %s\n" "LEGAL" "$(ltr "LEGAL suite (07+08+09)")" "$(rtl "immutability/policy/emit chain")"
  printf "%-8s | %-34s | %s\n" "LEGAL" "$(ltr "LEGAL07/08/09 regress")" "$(rtl "رگرشن‌های دقیق‌تر و جداگانه")"

  echo
}

summary() {
  title "SUMMARY"

  printf "%-4s | %-6s | %-4s | %-6s | %-8s | %s\n" "#" "STAT" "RC" "USER" "CAT" "STEP"
  echo "-----+--------+------+--------+----------+------------------------------------------------------------"

  local i pass=0 fail=0 warn=0
  for i in "${!__NAME[@]}"; do
    local st="${__STATUS[$i]}" rc="${__RC[$i]}" nm="${__NAME[$i]}" cat="${__CAT[$i]}" user="${__USER[$i]}"
    if [[ "$st" == "PASS" ]]; then
      ((pass++))
      printf "%-4s | %b%-6s%b | %-4s | %-6s | %-8s | %s\n" "$((i+1))" "$GRN$BOLD" "$st" "$NC" "$rc" "$user" "$cat" "$nm"
    elif [[ "$st" == "WARN" ]]; then
      ((warn++))
      printf "%-4s | %b%-6s%b | %-4s | %-6s | %-8s | %s\n" "$((i+1))" "$YLW$BOLD" "$st" "$NC" "$rc" "$user" "$cat" "$nm"
    else
      ((fail++))
      printf "%-4s | %b%-6s%b | %-4s | %-6s | %-8s | %s\n" "$((i+1))" "$RED$BOLD" "$st" "$NC" "$rc" "$user" "$cat" "$nm"
    fi
  done

  line
  echo -e "${BOLD}${BLU}TOTAL:${NC} $((pass+fail+warn))   ${GRN}${BOLD}PASS:${NC} $pass   ${YLW}${BOLD}WARN:${NC} $warn   ${RED}${BOLD}FAIL:${NC} $fail"
  echo -e "${DIMC}Run dir : $RUN_DIR${NC}"
  echo -e "${DIMC}Last TSV: $LAST_TSV${NC}"
  echo

  summary_categories_table
  coverage_table

  echo -e "${BOLD}${CYN}راهنمای سریع اجرا:${NC}"
  echo -e "  1) اجرای کامل:        ${BOLD}sudo bash $0 all${NC}"
  echo -e "  2) اجرای سریع:        ${BOLD}sudo bash $0 quick${NC}"
  echo -e "  3) فقط DIM:           ${BOLD}sudo bash $0 dim${NC}"
  echo -e "  4) فقط VAT:           ${BOLD}sudo bash $0 vat${NC}"
  echo -e "  5) فقط LEGAL:         ${BOLD}sudo bash $0 legal${NC}"
  echo -e "  6) restart کامل:      ${BOLD}sudo bash $0 restart${NC}"
  echo -e "  7) فقط cache:         ${BOLD}sudo bash $0 cache${NC}"
  echo -e "  8) فقط bytecode/perms:${BOLD}sudo bash $0 bytecode${NC}"
  echo -e "  9) reports/logs:      ${BOLD}sudo bash $0 reports${NC}"
  echo -e " 10) retry FAILها:      ${BOLD}sudo bash $0 retry${NC}  ${DIMC}(alias: failed)${NC}"
  echo

  if (( fail > 0 )); then
    return 1
  fi
  return 0
}

############################
# Retry (فقط FAILهای آخرین اجرا)
############################
retry_failed() {
  title "RETRY) اجرای مجدد FAILهای آخرین اجرا"

  if [[ ! -f "$LAST_TSV" ]]; then
    echo -e "${RED}${BOLD}[FATAL] فایل runbook_last.tsv پیدا نشد: $LAST_TSV${NC}"
    echo "اول یک بار all/quick/vat/dim/legal را اجرا کنید تا فایل ساخته شود."
    exit 2
  fi

  step_compile_and_restart

  local line_ seq status rc user cat name log cmd_b64 cmd
  while IFS=$'\t' read -r seq status rc user cat name log cmd_b64; do
    [[ "$status" == "FAIL" ]] || continue
    if [[ "$cat" != "DIM" && "$cat" != "VAT" && "$cat" != "LEGAL" && "$cat" != "CORE" ]]; then
      continue
    fi

    cmd="$(printf "%s" "$cmd_b64" | base64 -d 2>/dev/null || true)"
    [[ -n "$cmd" ]] || continue
    run_cmd "$user" "$cat" "RETRY: $name" "$cmd"
  done < "$LAST_TSV"
}

############################
# Usage
############################
usage() {
  cat <<USAGE
Usage (run as root):
  sudo bash $0 all

Modes:
  all          -> preflight + bytecode/perms + compile/restart + DIM + VAT + LEGAL + reports
  quick        -> bytecode/perms + compile/restart + DIM smoke + VAT smoke + VAT-13 guard + legal suite
  dim          -> compile/restart + DIM suite
  vat          -> compile/restart + VAT core + terminal + CI
  legal        -> compile/restart + LEGAL suite
  restart      -> compile + clear-cache + restart
  cache        -> فقط clear-cache + clear-website-cache
  bytecode     -> فقط fix ownership/perms + حذف pycache/pyc
  reports      -> tail logs/reports
  migrate      -> migrate/build (اختیاری)
  retry        -> فقط FAILهای آخرین اجرا (از runbook_last.tsv)
  failed       -> alias برای retry
USAGE
}

############################
# Main
############################
main() {
  need_root
  require_paths

  local mode="${1:-all}"

  print_intro

  case "$mode" in
    all)
      step_preflight
      step_fix_perms_and_bytecode
      step_compile_and_restart
      step_dim_suite
      step_vat_core
      step_vat_terminal_checks
      step_vat_ci_wrappers
      step_legal_suite
      step_reports
      ;;
    quick)
      step_fix_perms_and_bytecode
      step_compile_and_restart
      bench_exec "DIM" "DIM smoke" "blue_hesab.bh_core.dim_smoke.run_dim_smoke" "{\"company\":\"$COMPANY\"}"
      bench_exec "VAT" "VAT smoke SI base" "blue_hesab.bh_core.vat_smoke_si_v02.run_base" "{\"rate\":$RATE}"
      bench_exec "VAT" "VAT-13 guard" "blue_hesab.bh_core.vat_regress_vat13_guard.run_vat13_guard" "{\"company\":\"$COMPANY\",\"rate\":$RATE}"
      bench_exec "LEGAL" "LEGAL suite (07+08+09)" "blue_hesab.bh_core.regress.legal_ci.run_legal_suite" "{\"company\":\"$COMPANY\"}"
      step_reports
      ;;
    dim)
      step_compile_and_restart
      step_dim_suite
      step_reports
      ;;
    vat)
      step_compile_and_restart
      step_vat_core
      step_vat_terminal_checks
      step_vat_ci_wrappers
      step_reports
      ;;
    legal)
      step_compile_and_restart
      step_legal_suite
      step_reports
      ;;
    restart)
      step_compile_and_restart
      ;;
    cache)
      step_cache_only
      ;;
    bytecode)
      step_fix_perms_and_bytecode
      ;;
    reports)
      step_reports
      ;;
    migrate)
      step_migrate_optional
      ;;
    retry|failed)
      retry_failed
      step_reports
      ;;
    -h|--help|help)
      usage
      exit 0
      ;;
    *)
      echo -e "${RED}${BOLD}[FATAL] unknown mode: $mode${NC}"
      usage
      exit 2
      ;;
  esac

  print_failure_excerpts
  summary
}

main "$@"
