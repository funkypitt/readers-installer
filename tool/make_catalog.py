#!/usr/bin/env python3
"""Rebuilds assets/catalog.json from the Reader's section of the apps page.

    tool/make_catalog.py [path/to/gallaz-ch-eink/index.html]

THE RULE: every app of the catalogue is read from the personal F-Droid
repository (REPO below), never from its GitHub releases. The repository is one
small index file on GitHub Pages, with no limit; GitHub's API allows 60
anonymous requests an hour per address (shared by a whole household or mobile
carrier), each app costs at least one request at every check, and once the
limit is reached every app shows "too many requests" for up to an hour. A
personal access token lifts the limit, but only for a user who has a GitHub
account and pastes a token in the settings, which the catalogue cannot assume.
Version 1.0.0 pointed sixteen apps at GitHub and failed that way on the first
phone.

So, to add an app: publish it in the F-Droid repository first, then list it
here. The Reader's apps come from the cards of the apps page (the GitHub link a
card carries is ignored, only its id and name are used); the author's other
apps are in OTHERS below. The only exception is an app that cannot be in the
repository (too large for GitHub Pages): give it a "github" key. This script
refuses an app that is missing from the repository, a "github" app that is in
it, and more than MAX_GITHUB exceptions.

Desktop versions: a card of the apps page whose download button names desktop
systems ("Windows, macOS, Linux") gives the app a line in the "desktop" part of
the catalogue: the GitHub page of the desktop app and the systems it runs on.
The installer shows it on the app's page as a plain link, opened in the
browser: no request to GitHub's API, so the rule above is not concerned.
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
MAX_GITHUB = 2
OTHERS = [
    {"id": "com.freedomfighter.magazinereader", "name": "ePub Magazine Reader"},
    {"id": "ch.littre.littre_app", "name": "Le dictionnaire Littré"},
    # 226 MB: too large for the F-Droid repository, the one exception to the rule
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
    desktop = {}
    for article in section.split("<article")[1:]:
        card = re.search(r'obtainium://app/([^"]+)"', article)
        twin = re.search(r'href="(https://github\.com/[^/"]+/[^/"]+)/releases/latest">((?:Windows|macOS|Linux)[^<]*)</a>', article)
        if card and twin:
            app_id = json.loads(urllib.parse.unquote(card.group(1)))["id"]
            desktop[app_id] = {"url": twin.group(1), "systems": twin.group(2).split(" (")[0]}
    cards.insert(0, {"id": SELF_ID, "name": SELF_NAME})
    cards = [{"id": c["id"], "name": c["name"]} for c in cards] + OTHERS
    index = json.load(urllib.request.urlopen(f"{REPO}/index-v2.json", timeout=30))
    published = set(index["packages"])
    exceptions = [c for c in cards if "github" in c]
    problems = [f"{c['name']} ({c['id']}) is not in the F-Droid repository: publish it there first" for c in cards if "github" not in c and c["id"] not in published]
    problems += [f"{c['name']} ({c['id']}) is in the F-Droid repository: remove its \"github\" key" for c in exceptions if c["id"] in published]
    if len(exceptions) > MAX_GITHUB:
        problems.append(f"{len(exceptions)} apps read from GitHub, at most {MAX_GITHUB} (60 requests an hour per address)")
    if problems:
        sys.exit("Catalogue not written:\n  " + "\n  ".join(problems))
    apps = [entry(c) for c in cards]
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "catalog.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"apps": apps, "desktop": desktop}, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"{len(apps)} apps → {out} ({len(exceptions)} read from GitHub: {', '.join(c['name'] for c in exceptions) or 'none'})")
    print(f"{len(desktop)} desktop versions: " + ", ".join(f"{k.split('.')[-1]} ({v['systems']})" for k, v in desktop.items()))


if __name__ == "__main__":
    main()
