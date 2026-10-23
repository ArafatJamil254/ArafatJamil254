#!/usr/bin/env python3
"""Create a branded SVG with *real public GitHub statistics*.

No third-party dashboard service, private data, or third-party Python packages.
Run by .github/workflows/profile-visuals.yml every day.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import html
import json
import os
from pathlib import Path
import sys
from urllib.request import Request, urlopen

DEFAULT_USER = "ArafatJamil254"


def github_json(url: str):
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN", "")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "ArafatJamil254-profile-actions", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = Request(url, headers=headers)
    with urlopen(req, timeout=25) as response:
        return json.load(response)


def get_public_data(user: str):
    profile = github_json(f"https://api.github.com/users/{user}")
    repositories = []
    for page in range(1, 11):
        block = github_json(f"https://api.github.com/users/{user}/repos?per_page=100&type=owner&sort=updated&page={page}")
        repositories.extend(r for r in block if not r.get('private'))
        if len(block) < 100:
            break
    languages = Counter(r.get("language") for r in repositories if r.get("language"))
    return {
        "repos": int(profile["public_repos"]),
        "stars": sum(int(r.get("stargazers_count", 0)) for r in repositories),
        "followers": int(profile["followers"]),
        "langs": ", ".join(k for k, _ in languages.most_common(4)) or "No language data yet",
    }


def card(value, x, label, index):
    value=html.escape(str(value))
    return f'''<g>
      <rect x="{x}" y="80" width="348" height="124" rx="16" fill="#0e3142" stroke="#24596f" stroke-width="1.3" />
      <rect x="{x+20}" y="100" width="4" height="22" rx="2" fill="#46dce9" />
      <text x="{x+40}" y="126" font-family="DejaVu Sans, Arial, sans-serif" font-size="14" fill="#87b9c9" letter-spacing="1.6">{html.escape(label)}</text>
      <text x="{x+22}" y="181" font-family="DejaVu Sans, Arial, sans-serif" font-size="48" font-weight="700" fill="#effbff">{value}</text>
      <text x="{x+301}" y="184" font-family="DejaVu Sans, Arial, sans-serif" font-size="15" fill="#427e98">0{index}</text>
    </g>'''


def make_svg(data, preview=False):
    date=datetime.now(timezone.utc).strftime("%d %b %Y • %H:%M UTC")
    src='LAYOUT PREVIEW · NOT LIVE DATA' if preview else 'DATA: GITHUB PUBLIC API'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="277" viewBox="0 0 1200 277" role="img" aria-label="Live public GitHub account statistics for ArafatJamil254">
<defs><linearGradient id="bg" x1="0" y1="1" x2="1" y2="0"><stop stop-color="#081824"/><stop offset="1" stop-color="#0b2938"/></linearGradient></defs>
<rect width="1200" height="277" rx="18" fill="url(#bg)" stroke="#28667d" stroke-width="2" />
<text x="33" y="52" font-family="DejaVu Sans, Arial, sans-serif" font-size="21" font-weight="700" fill="#dff8fc" letter-spacing="1.6">PUBLIC GITHUB SIGNAL</text>
<circle cx="1060" cy="42" r="5" fill="#4adfcc"/><text x="1075" y="47" font-family="DejaVu Sans, Arial, sans-serif" font-size="15" fill="#92d8df">LIVE</text>
{card(data['repos'], 33, 'PUBLIC REPOSITORIES', 1)}
{card(data['stars'], 427, 'REPOSITORY STARS', 2)}
{card(data['followers'], 821, 'FOLLOWERS', 3)}
<path d="M 35 224 H 1167" stroke="#22576a" />
<text x="34" y="250" font-family="DejaVu Sans, Arial, sans-serif" font-size="13" fill="#84b6c7">{html.escape(src)}</text>
<text x="1166" y="250" font-family="DejaVu Sans, Arial, sans-serif" font-size="12" fill="#84b6c7" text-anchor="end">{html.escape(date if not preview else 'UPDATES AFTER WORKFLOW RUN')}</text>
</svg>'''


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--username',default=DEFAULT_USER)
    p.add_argument('--output',default='dist/github-stats.svg')
    p.add_argument('--preview',action='store_true', help='Render with placeholders, not real data')
    args=p.parse_args()
    if args.preview:
        data={'repos':'—','stars':'—','followers':'—'}
    else:
        data=get_public_data(args.username)
    svg=make_svg(data,args.preview)
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(svg,encoding='utf-8')
    print(f"Written {args.output}: {data}")

if __name__=='__main__':
    main()
