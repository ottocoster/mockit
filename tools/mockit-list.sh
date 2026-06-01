#!/usr/bin/env bash
# =============================================================================
# mockit-list.sh — List all running Mock'it device containers
# =============================================================================
# A generic utility for any Mock'it deployment — works regardless of whether
# containers were started via docker run, docker compose, ContainerLab, or
# any other orchestrator.
#
# Finds containers by image name, extracts device type and IP from the
# container runtime — no compose files or topology files needed.
#
# Usage:
#   mockit-list.sh            — formatted table (default)
#   mockit-list.sh --json     — JSON output, one object per line
#   mockit-list.sh --ssh      — ready-to-use SSH commands
#   mockit-list.sh --all      — include stopped containers (default: running only)
#
# Requirements: docker (any version supporting `docker inspect`)
# =============================================================================

if [ -z "$BASH_VERSION" ]; then exec env bash "$0" "$@"; fi
set -euo pipefail

# -----------------------------------------------------------------------
# Colours (disabled automatically if stdout is not a terminal)
# -----------------------------------------------------------------------
if [[ -t 1 ]]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
  CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; CYAN=''; BOLD=''; DIM=''; NC=''
fi

# -----------------------------------------------------------------------
# Args
# -----------------------------------------------------------------------
MODE="table"
SHOW_ALL=false

for arg in "$@"; do
  case "${arg}" in
    --json)   MODE="json"      ;;
    --ssh)    MODE="ssh"       ;;
    --all)    SHOW_ALL=true    ;;
    --help|-h)
      cat << HELP
Usage: $(basename "$0") [OPTIONS]

  (no flag)   Formatted table of running Mock'it devices
  --all       Include stopped/exited containers
  --json      One JSON object per line (pipe to jq for filtering)
  --ssh       Print SSH commands for running devices

Examples:
  $(basename "$0")
  $(basename "$0") --all
  $(basename "$0") --json | jq 'select(.device_type == "cisco_ios")'
  $(basename "$0") --ssh | grep nautobot

HELP
      exit 0
      ;;
    *) printf "Unknown argument: %s\nTry --help\n" "${arg}" >&2; exit 1 ;;
  esac
done

# -----------------------------------------------------------------------
# Find Mock'it containers
# -----------------------------------------------------------------------
MOCKIT_IMAGE_PATTERN="mockit"

# Build docker ps filter args
PS_ARGS=(--format '{{.ID}} {{.Image}} {{.Status}}')
[[ "${SHOW_ALL}" == "false" ]] && PS_ARGS+=(--filter "status=running")

# Get containers whose image name contains "mockit"
mapfile -t CONTAINER_IDS < <(
  docker ps "${PS_ARGS[@]}" 2>/dev/null | \
  awk -v pat="${MOCKIT_IMAGE_PATTERN}" 'tolower($2) ~ pat {print $1}'
)

if [[ ${#CONTAINER_IDS[@]} -eq 0 ]]; then
  if [[ "${SHOW_ALL}" == "false" ]]; then
    printf "${YELLOW}No running Mock'it containers found.${NC}\n"
    printf "  Try --all to include stopped containers.\n"
  else
    printf "${YELLOW}No Mock'it containers found (running or stopped).${NC}\n"
    printf "  Start containers using: docker compose up -d\n"
  fi
  exit 0
fi

# -----------------------------------------------------------------------
# Collect data
# -----------------------------------------------------------------------
declare -a ROWS=()

for CID in "${CONTAINER_IDS[@]}"; do
  # Single docker inspect call per container
  RAW=$(docker inspect "${CID}" \
    --format '{{.Name}}|{{.State.Status}}|{{.Config.Image}}|{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}|{{range .Config.Env}}{{.}};;{{end}}' \
    2>/dev/null) || continue

  IFS='|' read -r RAW_NAME STATUS IMAGE IP_RAW ENV_RAW <<< "${RAW}"

  NAME="${RAW_NAME#/}"

  # Extract relevant env vars
  DEVICE_TYPE="unknown"
  DEVICE_VERSION=""
  SSH_USER="admin"
  SSH_PASS="admin"
  SNMP_V2=""

  # Parse env pairs separated by ";;"
  while IFS= read -r -d $'\0' PAIR; do
    KEY="${PAIR%%=*}"
    VAL="${PAIR#*=}"
    case "${KEY}" in
      DEVICE_TYPE)     DEVICE_TYPE="${VAL}"    ;;
      DEVICE_VERSION)  DEVICE_VERSION="${VAL}" ;;
      SSH_USERNAME)    SSH_USER="${VAL}"        ;;
      SSH_PASSWORD)    SSH_PASS="${VAL}"        ;;
      SNMP_V2_ENABLED) SNMP_V2="${VAL}"         ;;
    esac
  done < <(printf '%s' "${ENV_RAW}" | sed 's/;;/\x00/g')

  # Build device type display string
  DISPLAY_TYPE="${DEVICE_TYPE}"
  [[ -n "${DEVICE_VERSION}" ]] && DISPLAY_TYPE="${DEVICE_TYPE} (${DEVICE_VERSION})"

  # Get first non-empty IP
  IP=""
  for CANDIDATE in ${IP_RAW}; do
    [[ -n "${CANDIDATE}" ]] && { IP="${CANDIDATE}"; break; }
  done

  # Strip image tag for display
  IMAGE_SHORT="${IMAGE##*/}"  # remove registry prefix

  ROWS+=("${NAME}|${DEVICE_TYPE}|${DISPLAY_TYPE}|${IP:-n/a}|${STATUS}|${SSH_USER}|${SSH_PASS}|${SNMP_V2}|${IMAGE_SHORT}")
done

# Sort by device type then IP
if [[ ${#ROWS[@]} -gt 0 ]]; then
  IFS=$'\n' ROWS=($(printf '%s\n' "${ROWS[@]}" | sort -t'|' -k2,2 -k4,4V))
  unset IFS
fi

# -----------------------------------------------------------------------
# Output
# -----------------------------------------------------------------------
case "${MODE}" in

  table)
    COUNT="${#ROWS[@]}"
    printf "\n${BOLD}${CYAN}Mock'it Devices${NC}  ${DIM}(${COUNT} container(s)${SHOW_ALL:+, including stopped})${NC}\n\n"
    printf "${BOLD}%-40s %-28s %-16s %-10s${NC}\n" \
      "CONTAINER NAME" "DEVICE TYPE" "IP ADDRESS" "STATUS"
    printf '%s\n' "$(printf '─%.0s' {1..98})"

    for ROW in "${ROWS[@]}"; do
      IFS='|' read -r NAME _DT DTYPE IP STATUS SSH_USER SSH_PASS SNMP IMAGE <<< "${ROW}"

      # Colour by status
      SC="${NC}"
      [[ "${STATUS}" == "running" ]] && SC="${GREEN}"
      [[ "${STATUS}" == "exited"  ]] && SC="${RED}"
      [[ "${STATUS}" == "created" ]] && SC="${YELLOW}"

      printf "%-40s %-28s %-16s ${SC}%-10s${NC}\n" \
        "${NAME}" "${DTYPE}" "${IP}" "${STATUS}"
    done

    printf "\n${DIM}Default credentials: SSH admin/admin port 22"
    printf " · SNMP v2 community: public (where enabled)${NC}\n\n"
    ;;

  json)
    for ROW in "${ROWS[@]}"; do
      IFS='|' read -r NAME _DT DTYPE IP STATUS SSH_USER SSH_PASS SNMP IMAGE <<< "${ROW}"
      # Minimal, clean JSON — no colour codes
      printf '{"name":"%s","device_type":"%s","ip":"%s","status":"%s","ssh_user":"%s","ssh_pass":"%s","snmp_v2_enabled":"%s","image":"%s"}\n' \
        "${NAME}" "${DTYPE}" "${IP}" "${STATUS}" \
        "${SSH_USER}" "${SSH_PASS}" "${SNMP}" "${IMAGE}"
    done
    ;;

  ssh)
    PRINTED=0
    printf "\n${BOLD}SSH commands — running Mock'it devices:${NC}\n\n"
    for ROW in "${ROWS[@]}"; do
      IFS='|' read -r NAME _DT DTYPE IP STATUS SSH_USER SSH_PASS SNMP IMAGE <<< "${ROW}"
      if [[ "${STATUS}" == "running" && "${IP}" != "n/a" && -n "${IP}" ]]; then
        printf "# %s  (%s)\n" "${NAME}" "${DTYPE}"
        printf "ssh %s@%s\n\n" "${SSH_USER}" "${IP}"
        PRINTED=$(( PRINTED + 1 ))
      fi
    done
    if [[ ${PRINTED} -eq 0 ]]; then
      printf "${YELLOW}No running containers with a reachable IP found.${NC}\n"
    fi
    ;;

esac
