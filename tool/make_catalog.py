#!/usr/bin/env python3
"""Rebuilds assets/catalog.json from the Reader's section of the apps page.

    tool/make_catalog.py [path/to/gallaz-ch-eink/index.html]

Each app card of that section carries an import link with the app's id, source
URL, author and name; the catalogue is that list.
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request

SITE = "https://funkypitt.github.io/gallaz-ch-eink/index.html"


def main():
    if len(sys.argv) > 1:
        html = open(sys.argv[1], encoding="utf-8").read()
    else:
        html = urllib.request.urlopen(SITE, timeout=30).read().decode("utf-8")
    start = html.index('id="readers"')
    section = html[start:html.index("<section", start + 10)]
    apps = [json.loads(urllib.parse.unquote(m.group(1))) for m in re.finditer(r'obtainium://app/([^"]+)"', section)]
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "catalog.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"apps": apps}, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"{len(apps)} apps → {out}")


if __name__ == "__main__":
    main()
