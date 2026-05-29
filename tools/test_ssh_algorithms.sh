#!/usr/bin/env bash
# =============================================================================
# test_ssh_algorithms.sh
#
# Tests SSH KEX algorithms and ciphers against a running mockit container.
# Each algorithm/cipher is tested individually — PASS means the server
# accepted the negotiation; FAIL means the server rejected it.
#
# How it works:
#   We specify ONLY the algorithm under test so the server must accept or
#   reject it explicitly with no fallback. -F /dev/null ignores local ssh
#   config which could override algorithm choices. NumberOfPasswordPrompts=0
#   makes ssh exit immediately on auth challenge without waiting for input.
#
#   Both outcomes exit 255 on macOS, distinguished by output:
#     PASS: "Permission denied" in output -> negotiation succeeded, auth
#           failed as expected (no valid credentials supplied)
#     FAIL: empty output -> server rejected during KEX (asyncssh silently
#           closes the connection at LogLevel=ERROR)
#
# Usage:
#   ./test_ssh_algorithms.sh [OPTIONS]
#
# Options:
#   -h, --host      Target host (default: 127.0.0.1)
#   -p, --port      SSH port   (default: 22)
#   -u, --user      SSH user   (default: test)
#   --kex           Comma-separated KEX algorithms to test
#   --ciphers       Comma-separated ciphers to test
#   --kex-only      Only run KEX tests
#   --ciphers-only  Only run cipher tests
#   --timeout       ConnectTimeout in seconds (default: 5)
#
# Examples:
#   ./test_ssh_algorithms.sh
#   ./test_ssh_algorithms.sh --kex "diffie-hellman-group1-sha1,curve25519-sha256"
#   ./test_ssh_algorithms.sh -h 172.16.240.45 --ciphers "aes128-ctr,3des-cbc"
#   ./test_ssh_algorithms.sh --kex-only
# =============================================================================

set -euo pipefail

# ---- Defaults ---------------------------------------------------------------
HOST="127.0.0.1"
PORT="22"
USER="test"
TIMEOUT="5"
RUN_KEX=true
RUN_CIPHERS=true

DEFAULT_KEX="diffie-hellman-group1-sha1,diffie-hellman-group14-sha1,diffie-hellman-group14-sha256,diffie-hellman-group-exchange-sha1,diffie-hellman-group-exchange-sha256,curve25519-sha256,curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521"

DEFAULT_CIPHERS="aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com,chacha20-poly1305@openssh.com,aes128-cbc,aes192-cbc,aes256-cbc,3des-cbc"

KEX_LIST="$DEFAULT_KEX"
CIPHER_LIST="$DEFAULT_CIPHERS"

# ---- Colours ----------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# ---- Argument parsing -------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--host)       HOST="$2";        shift 2 ;;
        -p|--port)       PORT="$2";        shift 2 ;;
        -u|--user)       USER="$2";        shift 2 ;;
        --kex)           KEX_LIST="$2";    shift 2 ;;
        --ciphers)       CIPHER_LIST="$2"; shift 2 ;;
        --kex-only)      RUN_CIPHERS=false; shift ;;
        --ciphers-only)  RUN_KEX=false;    shift ;;
        --timeout)       TIMEOUT="$2";     shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# ---- State ------------------------------------------------------------------
PASS_COUNT=0
FAIL_COUNT=0

# ---- Helpers ----------------------------------------------------------------
check_deps() {
    command -v ssh &>/dev/null || { echo -e "${RED}ssh not found — install openssh-client${RESET}"; exit 1; }
}

print_header() {
    echo -e "\n${BOLD}${CYAN}========================================${RESET}"
    echo -e "${BOLD}${CYAN}  SSH Algorithm Tester — mockit${RESET}"
    echo -e "${BOLD}${CYAN}========================================${RESET}"
    echo -e "  Target : ${BOLD}${HOST}:${PORT}${RESET}"
    echo -e "  User   : ${USER}"
    echo -e "  Timeout: ${TIMEOUT}s"
    echo ""
}

print_section() {
    echo -e "\n${BOLD}${YELLOW}--- $1 ---${RESET}"
}

print_summary() {
    echo -e "\n${BOLD}${CYAN}========================================${RESET}"
    echo -e "${BOLD}  Results: ${GREEN}${PASS_COUNT} passed${RESET}  ${RED}${FAIL_COUNT} failed${RESET}"
    echo -e "${BOLD}${CYAN}========================================${RESET}\n"
}

# opt_name and opt_value are passed separately so the shell never has to
# word-split a combined "-o Key=Value" string — each becomes its own argument.
run_ssh_test() {
    local opt_name="$1"
    local opt_value="$2"
    local label="$3"

    local output
    output=$(ssh \
        -F /dev/null \
        -o "StrictHostKeyChecking=no" \
        -o "ConnectTimeout=${TIMEOUT}" \
        -o "NumberOfPasswordPrompts=0" \
        -o "PubkeyAuthentication=no" \
        -o "RequiredRSASize=0" \
        -o "LogLevel=ERROR" \
        -o "${opt_name}=${opt_value}" \
        -p "$PORT" \
        "${USER}@${HOST}" 2>&1) || true

    if echo "$output" | grep -qiE "Permission denied|password"; then
        echo -e "  ${GREEN}PASS${RESET}  ${label}"
        PASS_COUNT=$(( PASS_COUNT + 1 ))
    else
        echo -e "  ${RED}FAIL${RESET}  ${label}"
        [[ -n "$output" ]] && echo -e "        ${RED}${output}${RESET}"
        FAIL_COUNT=$(( FAIL_COUNT + 1 ))
    fi
}

test_kex() {
    run_ssh_test "KexAlgorithms" "$1" "$1"
}

test_cipher() {
    run_ssh_test "Ciphers" "$1" "$1"
}

# ---- Main -------------------------------------------------------------------
check_deps
print_header

if $RUN_KEX; then
    print_section "KEX Algorithm Tests"
    IFS=',' read -ra KEXES <<< "$KEX_LIST"
    for alg in "${KEXES[@]}"; do
        alg="$(echo "$alg" | xargs)"
        [[ -z "$alg" ]] && continue
        test_kex "$alg"
    done
fi

if $RUN_CIPHERS; then
    print_section "Cipher Tests"
    IFS=',' read -ra CIPHERS <<< "$CIPHER_LIST"
    for cipher in "${CIPHERS[@]}"; do
        cipher="$(echo "$cipher" | xargs)"
        [[ -z "$cipher" ]] && continue
        test_cipher "$cipher"
    done
fi

print_summary
