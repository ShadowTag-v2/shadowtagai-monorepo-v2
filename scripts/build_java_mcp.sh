#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/googleapis/mcp-toolbox-sdk-java.git}"
WORKDIR="${WORKDIR:-$HOME/.cache/mcp-toolbox-sdk-java}"
MAVEN_FALLBACK="/tmp/apache-maven-3.9.9/bin/mvn"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 1
  }
}

need_cmd git
need_cmd java

if command -v mvn >/dev/null 2>&1; then
  MVN_BIN="$(command -v mvn)"
elif [ -x "$MAVEN_FALLBACK" ]; then
  MVN_BIN="$MAVEN_FALLBACK"
else
  echo "Maven not found. Install mvn or provide /tmp/apache-maven-3.9.9/bin/mvn" >&2
  exit 1
fi

mkdir -p "$(dirname "$WORKDIR")"

if [ ! -d "$WORKDIR/.git" ]; then
  git clone --depth=1 "$REPO_URL" "$WORKDIR"
else
  git -C "$WORKDIR" fetch --depth=1 origin main
  git -C "$WORKDIR" reset --hard FETCH_HEAD
fi

(
  cd "$WORKDIR"
  "$MVN_BIN" -q -DskipTests clean package
)

JAR_PATH="$(
  find "$WORKDIR" -type f \
    \( -path '*/target/*.jar' -o -path '*/build/libs/*.jar' \) \
    ! -name '*sources.jar' \
    ! -name '*javadoc.jar' \
    | head -n 1
)"

if [ -z "$JAR_PATH" ]; then
  echo "No runnable jar found under $WORKDIR" >&2
  exit 1
fi

printf '%s\n' "$JAR_PATH"
