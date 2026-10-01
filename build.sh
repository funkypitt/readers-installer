#!/bin/bash
# Builds the release APKs, one per ABI, unsigned unless android/key.properties exists.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
FLUTTER=.flutter/bin/flutter
$FLUTTER pub get
APP_VERSION="$(grep '^version: ' pubspec.yaml | sed 's/version: //; s/+.*//' | head -1)"
$FLUTTER build apk --dart-define=APP_VERSION="$APP_VERSION" --split-per-abi --flavor normal
ls -la build/app/outputs/flutter-apk/*.apk
