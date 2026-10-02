#!/usr/bin/env python3
"""Rebuilds assets/catalog.json from the Reader's section of the apps page.

    tool/make_catalog.py [path/to/gallaz-ch-eink/index.html]

Each app card of that section carries an import link with the app's id and name;
the catalogue lists them, the installer itself first, all read from the personal
F-Droid repository: one small index file on GitHub Pages instead of GitHub's
API, whose anonymous limit (60 requests an hour per address) a family of
sixteen apps exhausts in one sitting.

The author's other apps (OTHERS below) follow the family. One with a "github" is
not in the F-Droid repository and is read from its GitHub releases; keep those
few, each costs a request to GitHub's API at every check.
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request

SITE = "https://funkypitt.github.io/gallaz-ch-eink/index.html"
REPO = "https://funkypitt.github.io/fdroid-repo/repo"
SELF_ID = "com.freedomfighter.readersinstaller"
SELF_NAME = "Reader's Installer and Updater"
OTHERS = [
    {"id": "com.freedomfighter.magazinereader", "name": "ePub Magazine Reader"},
    {"id": "ch.littre.littre_app", "name": "Le dictionnaire Littré"},
    # too large for the F-Droid repository
    {"id": "ch.plume.clavier", "name": "Clavier Plume", "github": "funkypitt/clavier-plume"},
    {"id": "com.local2p.games", "name": "Funky's 2P Games"},
]


def entry(c):
    if "github" in c:
        return {"id": c["id"], "url": f"https://github.com/{c['github']}", "author": "funkypitt", "name": c["name"]}
    return {
        "id": c["id"],
        "url": f"{REPO}?appId={c['id']}",
        "author": "funkypitt",
        "name": c["name"],
        "overrideSource": "FDroidRepo",
        "additionalSettings": json.dumps({"appIdOrName": c["id"]}),
    }


def main():
    if len(sys.argv) > 1:
        html = open(sys.argv[1], encoding="utf-8").read()
    else:
        html = urllib.request.urlopen(SITE, timeout=30).read().decode("utf-8")
    start = html.index('id="readers"')
    section = html[start:html.index("<section", start + 10)]
    cards = [json.loads(urllib.parse.unquote(m.group(1))) for m in re.finditer(r'obtainium://app/([^"]+)"', section)]
    cards.insert(0, {"id": SELF_ID, "name": SELF_NAME})
    apps = [entry(c) for c in cards + OTHERS]
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "catalog.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"apps": apps}, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"{len(apps)} apps → {out}")


if __name__ == "__main__":
    main()
