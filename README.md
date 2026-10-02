# Reader's Installer and Updater

Installs the [Reader's](https://gallaz.ch/eink/#readers) apps and keeps them up to date, from the
author's [F-Droid repository](https://gallaz.ch/eink/#fdroid) (the same files as their GitHub releases). Open it once: the whole family is in the list, each app one tap away
from being installed; after that the updates come by themselves, including the installer's own.

**This is a modified version of [Obtainium](https://github.com/ImranR98/Obtainium)** by Imran
Remtulla and its contributors, under the same licence (GNU GPL v3, see `LICENSE.txt`). It is not
Obtainium and is not endorsed by its authors. Modified from Obtainium v1.6.17 on 1 October 2026.

## Key points

* The list of Reader's apps ships with the installer and is read again from this repository at
  each start (`assets/catalog.json`), so an app published later appears by itself. An app you
  remove from the list is not added back.
* Four other apps by the same author follow the family in the list: ePub Magazine Reader, Le
  dictionnaire Littré, Funky's 2P Games and Clavier Plume. Clavier Plume, too large for the
  F-Droid repository, is the only one read from its GitHub releases.
* The Reader's apps and the installer itself are read from one small index file of the F-Droid
  repository, not from GitHub's API, whose anonymous limit of 60 requests an hour a family of
  sixteen apps exhausts at once ("too many requests").
* Everything Obtainium does is still there: any other app can be added from its GitHub, GitLab,
  Codeberg, F-Droid… page, with the same options.
* Updates in the background; silent on Android 12 and later for the apps this installer installed
  itself. An app installed earlier from F-Droid or an APK asks once for confirmation, then follows.
* Android asks once for the permission to install apps from this source.
* No account, no tracking; it talks to GitHub and to the sources you add, nothing else.

## What was changed from Obtainium

* Name, icon, application id (`com.freedomfighter.readersinstaller`) and link scheme
  (`readersinstaller://` instead of `obtainium://`), so both apps can live on the same phone.
* The app tracks its own releases (through the F-Droid repository) instead of Obtainium's.
* `lib/readers_catalog.dart` and `assets/catalog.json`: the Reader's apps offered at first start.
* Black and white by default (monochrome colour scheme, black background).
* The app's name in the translated texts; Obtainium's logo, screenshots, store texts and
  release workflows removed.

Changes are in the git history on top of the upstream tag `v1.6.17`.

## Install

Download the APK from the [latest release](../../releases/latest) and open it. From then on it
updates itself. The release is built for 64-bit ARM (nearly every phone and tablet since 2017);
`./build.sh` produces the other architectures.

## Build

```
git submodule update --init          # the pinned Flutter SDK
./build.sh                           # build/app/outputs/flutter-apk/app-<abi>-normal-release.apk (unsigned)
```

JDK 21 and the Android SDK are needed. `tool/make_catalog.py` rebuilds `assets/catalog.json`.

## Credits

Obtainium © Imran Remtulla and contributors, GPL-3.0.
Modifications © 2026 Pierre Gallaz, GPL-3.0. Developed with [Claude Code](https://claude.com/claude-code) (Anthropic).
