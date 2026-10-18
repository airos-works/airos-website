#!/usr/bin/env python3
"""Dependency-free static site builder; works at a custom domain or Pages subpath."""
from collections import defaultdict
from datetime import datetime
from html import escape as e
import json
import os
from pathlib import Path
import shutil
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
BASE = os.getenv('BASE_PATH', '').rstrip('/')
ORIGIN = os.getenv('SITE_URL', 'https://airos.works').rstrip('/')
D = json.loads((ROOT / 'data/github.json').read_text())
UPDATED = D['updated'][:10]
NAV = [('', 'Project'), ('apps/', 'Apps'), ('summit/', 'Summit'), ('screenshots/', 'Screenshots'), ('hardware/', 'New hardware'), ('downloads/', 'Downloads'), ('source/', 'Source code'), ('changelog/', 'Changelog')]

def url(path=''):
    return BASE + '/' + path

def link(href, label, cls=''):
    return f'<a href="{e(href, quote=True)}" class="{cls}">{label}</a>'

def page(path, title, description, body):
    canonical = ORIGIN + '/' + path
    nav = ''.join(link(url(p), t, 'active' if (p == path or p == 'changelog/' and path.startswith(p)) else '') for p, t in NAV)
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · airOS</title><meta name="description" content="{e(description, quote=True)}">
<link rel="canonical" href="{canonical}"><meta property="og:title" content="{e(title)} · airOS">
<meta property="og:description" content="{e(description, quote=True)}"><meta property="og:type" content="website">
<meta property="og:url" content="{canonical}"><meta property="og:image" content="{ORIGIN}/assets/logo.png">
<link rel="icon" href="{url('favicon.ico')}" sizes="16x16 32x32 48x48"><link rel="icon" type="image/svg+xml" href="{url('assets/favicon.svg')}" sizes="any"><link rel="stylesheet" href="{url('assets/site.css')}">
<script src="{url('assets/site.js')}" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="wrap header-inner">
<a class="brand" href="{url()}" aria-label="airOS home"><img src="{url('assets/logo.png')}" width="191" height="64" alt="air/OS"></a>
<nav aria-label="Main navigation">{nav}</nav></div></header>
<main id="main" class="wrap">{body}</main>
<footer class="wrap"><div class="footer-brand">A little more possibility.</div>
<div>{link('https://www.haiku-os.org/', 'Discover Haiku ↗')}<span>Build data refreshed {UPDATED} UTC</span></div></footer></body></html>'''
    target = OUT / path / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html)

def intro(kicker, title, text):
    return f'<div class="page-intro"><p class="eyebrow">{kicker}</p><h1>{title}</h1><p class="lead">{text}</p></div>'

def home():
    body = f'''<section class="hero"><div class="hero-copy"><p class="eyebrow"><span class="dot"></span> A new horizon for a familiar desktop</p>
<h1>Build on Haiku.<br>Extended with <em>AI.</em></h1>
<p class="lead">airOS is an independent, AI-assisted exploration of what Haiku can do — on more devices, with more native apps, and with the same love for a responsive, personal desktop.</p>
<div class="actions">{link(url('downloads/'), 'Explore the downloads <span aria-hidden="true">↗</span>', 'button primary')}{link(url('screenshots/'), 'See it in action <span aria-hidden="true">→</span>', 'text-link')}</div>
</div><div class="hero-art" aria-hidden="true"><div class="orbit"></div><img src="{url('assets/mark.png')}" alt=""></div></section>
<div class="project-strip"><span>AMD &amp; NVIDIA graphics</span><span>ROCK 5 ITX &amp; Cubie A7S</span><span>Raspberry Pi 4</span></div>
<section class="about-section"><div><p class="eyebrow">The foundation</p><h2>Haiku made<br> this possible.</h2></div><div class="prose"><p>Haiku’s contributors have spent decades building an open-source operating system inspired by BeOS: fast, coherent and thoughtfully designed for personal computing. Its kernel, desktop, native APIs and community are the foundation of everything here.</p><p>airOS builds on that work with device support, desktop improvements and applications. It is an independent fork, with its own development approach.</p>{link('https://www.haiku-os.org/', 'Haiku Project ↗', 'text-link')}</div></section>
<section class="principles"><article><span class="section-number">01 / EXPLORE</span><h3>More hardware.</h3><p>From ARM boards to a desktop workstation, new drivers and ports bring Haiku’s desktop to more places.</p>{link(url('hardware/'), 'See what works →')}</article><article><span class="section-number">02 / MAKE</span><h3>More everyday apps.</h3><p>Browse, listen, watch, capture and create with native applications that feel at home on the desktop.</p>{link(url('screenshots/'), 'Take a look →')}</article><article><span class="section-number">03 / ITERATE</span><h3>A faster feedback loop.</h3><p>AI helps investigate unfamiliar code, develop ports and test ideas quickly. Builds, hardware checks and public Git history make progress inspectable.</p>{link(url('changelog/'), 'Follow the changes →')}</article></section>
<section class="release-highlights"><div class="section-heading"><h2>New on your desktop.</h2><span>October 2026</span></div><div class="highlight-grid">
<article><a href="{url('apps/#office')}"><img src="{url('assets/screenshots/wordcraft.png')}" alt="WordCraft running on Haiku" loading="lazy"></a><p class="eyebrow">Write · calculate · present · read</p><h3>A new office suite.</h3><p>Meet WordCraft, GridCraft, DeckCraft and PDFCraft: four early native ports for documents, spreadsheets, presentations and PDFs.</p>{link(url('apps/#office'), 'Explore the Craft apps →')}</article>
<article><a href="{url('summit/')}"><img src="{url('assets/screenshots/summit.png')}" alt="The Summit browser on Haiku" loading="lazy"></a><p class="eyebrow">A browser that keeps growing</p><h3>More Summit.</h3><p>Reader mode, PDFs, extensions, streaming media and native developer tools, with dedicated builds for airOS and stock Haiku.</p>{link(url('summit/'), 'Discover Summit →')}</article></div>
<div class="update-links"><div><h3>Media, reworked.</h3><p>A clearer Media preferences app and a new MediaConverter with queues, previews and GPU encoding.</p>{link(url('apps/#media'), 'Explore the media tools →')}</div><div><h3>More of your hardware.</h3><p>AMD display and GPU acceleration, Cubie WebGL 2, and Raspberry Pi dual displays and DSI panels.</p>{link(url('hardware/'), 'See the tested configurations →')}</div></div></section>
<section class="closing"><p class="eyebrow">An experiment you can explore</p><h2>Open source. Ongoing work.<br>A desktop with room to grow.</h2><p>Development builds are available now. Check the hardware notes, try the apps, or follow along in the source.</p>{link(url('source/'), 'Explore the code ↗', 'button')}</section>'''
    page('', 'Build on Haiku. Extended with AI.', 'An independent Haiku-based operating system using AI to expand hardware support and native applications.', body)

def capture(id):
    shots = json.loads((ROOT / 'content/screenshots.json').read_text())
    shot = next((s for s in shots if s.get('id') == id), None)
    if shot is None:
        raise ValueError('Missing screenshot: '+id)
    image = url('assets/screenshots/' + shot['file'])
    return f'<figure class="feature-capture"><a href="{image}"><img src="{image}" alt="{e(shot["title"]+": "+shot["description"], quote=True)}" loading="lazy" width="{shot["width"]}" height="{shot["height"]}"></a><figcaption>{e(shot["title"])} · {e(shot["captured"])} · {link(url("screenshots/#"+id), "Capture details →")}</figcaption></figure>'

def feature_row(item, download=None):
    links = link(item['source'], 'Feature and port notes ↗', 'text-link')
    if download:
        links += link(url(download), 'Build availability →', 'text-link')
    return f'''<article class="feature-row" id="{item['id']}"><div><h3>{e(item['title'])}</h3><p>{e(item['text'])}</p><ul class="checks">{''.join('<li>'+e(x)+'</li>' for x in item['features'])}</ul><div class="device-links">{links}</div></div>{capture(item['screenshot'])}</article>'''

def applications():
    data = json.loads((ROOT / 'content/apps.json').read_text())
    body = intro('Made for your desktop', 'More ways to make.', 'Write, calculate, present, convert and create. New native ports and reworked Haiku tools bring more of your day onto the desktop.')
    body += f'<nav class="jump-links" aria-label="Application sections">{link("#office", "Craft office suite")}{link("#media", "Media tools")}{link("#everyday", "Everyday apps")}{link(url("summit/"), "Summit browser →")}</nav>'
    body += '<section id="office"><div class="section-heading"><h2>The Craft office suite</h2><span>Early native x86-64 ports</span></div><p class="section-lead">WordCraft, GridCraft, DeckCraft and PDFCraft bring the open-source Craft applications to airOS. Their Rust editors run inside native Haiku windows, with system file panels, clipboard support and display scaling.</p><aside class="note">These are early ports of alpha applications. They render on the CPU; native printing, IME composition and some desktop integrations remain unfinished. Document compatibility varies by app. The build links below state what is currently published.</aside>'
    body += ''.join(feature_row(a, 'downloads/#'+a['id']) for a in data['office'])
    body += '</section><section id="media"><div class="section-heading"><h2>A fresh look at media</h2><span>Included in airOS system builds</span></div>'
    body += ''.join(feature_row(a, 'downloads/#system') for a in data['media'])
    body += '<p class="note">GPU encoding depends on the installed driver and card: AMD VA-API includes AV1 on verified VCN 4 hardware; NVIDIA NVENC runs a self-test before use. Other codecs and devices may use the CPU. Check the app’s Video hardware window for the current machine.</p></section>'
    body += '<section id="everyday"><div class="section-heading"><h2>And the everyday favourites</h2></div><div class="app-grid">'
    for app in json.loads((ROOT / 'content/project.json').read_text())['apps']:
        if app['repo'] in ('summit', 'wordcraft', 'gridcraft', 'deckcraft', 'pdfcraft'):
            continue
        body += f'<article class="app-card"><h3>{e(app["name"])}</h3><p>{e(app["description"])}</p>{link(url("downloads/#"+app["repo"].lower()), "Latest builds →")}</article>'
    body += '</div></section><p class="meta">Features and port notes reviewed '+data['reviewed']+'. See each project’s source for current limitations.</p>'
    page('apps/', 'Applications', 'Meet WordCraft, GridCraft, DeckCraft, PDFCraft, the new Media preferences and MediaConverter on airOS.', body)

def summit():
    data = json.loads((ROOT / 'content/summit.json').read_text())
    body = intro('Summit · native WebKit browser', 'The web. At home on Haiku.', 'Native controls, a compact toolbar and a modern multiprocess WebKit engine. Summit keeps growing alongside the desktop it runs on.')
    body += f'<div class="actions summit-downloads">{link(url("downloads/#summit"), "Get Summit for airOS ↓", "button primary")}{link("https://github.com/jmgasper/summit/releases/tag/latest-haiku", "Get Summit for Haiku R1/beta6 ↗", "button")}</div>'
    body += '<p class="note">Install both the browser and its matching WebKit engine. airOS builds are available for x86-64 and ARM64; the stock Haiku R1/beta6 build is x86-64. Hardware acceleration, high-density displays and device integration depend on the system and driver.</p>'
    body += capture('summit')
    body += '<div class="section-heading"><h2>More than a page viewer.</h2><span>Development preview</span></div><p class="section-lead">Tabs, saved sessions, bookmarks, downloads, page find, configurable search and per-site zoom are joined by tools for reading, media, extensions and debugging.</p>'
    body += ''.join(feature_row(f) for f in data['features'])
    body += '<aside class="note">Web-platform and extension compatibility are still evolving. Verified examples do not establish support for every extension or streaming service. The <a href="https://github.com/jmgasper/summit">Summit feature notes</a> describe supported subsets and the build tables identify their source commits.</aside>'
    page('summit/', 'Summit browser', 'Explore Summit reader mode, PDFs, extensions, streaming media, privacy controls and native developer tools for airOS and Haiku.', body)

def screenshots():
    shots = json.loads((ROOT / 'content/screenshots.json').read_text())
    body = intro('A look around', 'Screenshots', 'Real captures from our applications and development machines.')
    categories = list(dict.fromkeys(shot['category'] for shot in shots))
    if len(categories) > 1:
        body += '<div class="filter-bar" data-gallery-filters hidden><button class="selected" data-filter="All">All captures</button>'
        body += ''.join(f'<button data-filter="{e(category, quote=True)}">{e(category)}</button>' for category in categories) + '</div>'
    body += '<div class="gallery">'
    for i, shot in enumerate(shots):
        image = url('assets/screenshots/' + shot['file'])
        body += f'''<figure id="{shot['id']}" data-category="{shot['category']}"><a class="screenshot-link" href="{image}" data-caption="{e(shot['title'])}"><img src="{image}" alt="{e(shot['title'] + ': ' + shot['description'], quote=True)}" loading="lazy" width="{shot['width']}" height="{shot['height']}"></a><figcaption><span class="section-number">{i+1:02d} / {shot['category']}</span><h2>{shot['title']}</h2><p>{shot['description']}</p><p class="capture-date">{e(shot['captured'])}</p>{link(shot['source'], 'About this capture ↗', 'subtle')}</figcaption></figure>'''
    body += '</div><dialog id="lightbox"><form method="dialog"><button aria-label="Close full-size screenshot">Close ×</button></form><img alt=""><p></p></dialog>'
    body += '<details class="capture-credits"><summary>Capture credits</summary><p>The AirTime and MediaConverter captures include <a href="https://peach.blender.org/about/">Big Buck Bunny</a>, © Blender Foundation, licensed under <a href="https://creativecommons.org/licenses/by/3.0/">CC BY 3.0</a>. The Cubie capture shows <a href="https://github.com/WebGLSamples/WebGLSamples.github.io/tree/master/aquarium">WebGL Aquarium</a>, © Google Inc. and contributors ('+link(url('assets/screenshots/webgl-aquarium-LICENSE.txt'), 'BSD licence notice')+').</p></details>'
    page('screenshots/', 'Screenshots', 'Explore real airOS application and desktop screenshots.', body)

def hardware():
    body = intro('New hardware', 'New places for Haiku.', 'Device support built in the airOS forks. These notes describe tested configurations, with the remaining gaps alongside them.')
    for i, device in enumerate(json.loads((ROOT / 'content/hardware.json').read_text())):
        photo = ''
        if image := device.get('image'):
            image_url = url('assets/hardware/' + image['file'])
            photo = f'''<figure class="device-photo"><a href="{e(image_url, quote=True)}"><img src="{e(image_url, quote=True)}" alt="{e(image['alt'], quote=True)}" width="{image['width']}" height="{image['height']}" loading="lazy"></a><figcaption>Photo: {link(image['source'], e(image['credit']))} · {link(image['license_url'], e(image['license']))}</figcaption></figure>'''
        body += f'''<article class="hardware-row" id="{device['id']}"><div class="device-title"><span class="section-number">0{i+1} / {device['chip']}</span><h2>{device['name']}</h2><p>{device['summary']}</p><span class="badge">{device['status']}</span>{photo}{capture(device['screenshot']) if device.get('screenshot') else ''}</div><div><h3>What’s working</h3><ul class="checks">{''.join('<li>'+e(f)+'</li>' for f in device['features'])}</ul><p class="limitations"><strong>Still in progress</strong><br>{device['limits']}</p>{link('https://github.com/jmgasper/haiku/blob/master/'+device['source'], 'Read the test notes and history ↗')}<div class="device-links">{''.join(link('https://github.com/jmgasper/haiku/blob/master/'+item['path'], e(item['label'])+' ↗') for item in device.get('links', []))}</div></div></article>'''
    body += '<aside class="note">Hardware notes reviewed 18 October 2026. A working driver on one board or card does not establish support for every device in the same family. The linked test notes carry the detailed evidence and newer results.</aside>'
    page('hardware/', 'New hardware', 'airOS hardware support for ROCK 5 ITX, Cubie A7S, Raspberry Pi 4 and x86-64 PCs.', body)

def size(n):
    return f'{n / 1048576:.1f} MB' if n >= 1048576 else f'{n / 1024:.0f} KB'

def downloads():
    body = intro('Downloads', 'Make yourself at home.', 'Get an airOS development image, or pick up an individual app for your existing installation.')
    body += '<div class="section-heading"><h2 id="system">The operating system</h2><span>Latest successful published builds</span></div><div class="image-grid">'
    titles = {'x86_64': ('x86-64', 'Intel & AMD PCs', 'ISO image · UEFI / BIOS'), 'arm64': ('ARM64', 'ROCK 5 ITX & UEFI ARM64', 'ISO image · UEFI'), 'rpi4': ('Raspberry Pi 4', 'A desktop on an SD card', 'SD card image · Pi 4')}
    for im in D['images']:
        title, subtitle, format = titles[im['target']]
        body += f'<article class="image-card" data-target="{im["target"]}"><span class="section-number">{format}</span><h3>{title}</h3><p>{subtitle}</p><div class="image-download">'
        assets = im['assets']
        image = next((a for a in assets if a['name'].endswith(('.iso.xz', '.img.xz'))), None)
        if image:
            body += link(image['browser_download_url'], 'Download image ↓', 'button primary')
            body += f'<p class="meta">{size(image["size"])} compressed · {im["published"][:10]}</p><div class="asset-extras">'
            for a in assets:
                if a['name'].endswith('.sha256') or a['name'] == 'manifest.json':
                    body += link(a['browser_download_url'], 'SHA-256' if a['name'].endswith('.sha256') else 'Build manifest')
            body += link(im['release'], 'Release notes ↗') + '</div>'
        else:
            body += '<p class="availability">Public image coming soon</p>' + link('https://github.com/jmgasper/haiku/actions/workflows/airos-images.yml', 'Build status ↗')
        body += '</div></article>'
    body += '</div><p class="meta"><strong>Cubie A7S:</strong> no public SD image yet. The ARM64 ISO above is for UEFI machines; see the <a href="'+url('hardware/#cubie')+'">Cubie build notes</a>.</p><aside class="note"><strong>Before installing.</strong> These are experimental development builds. Check the <a href="'+url('hardware/')+'">hardware notes</a> and back up your data. x86 means 64-bit x86 (x86-64); there is no 32-bit image. Extract the ISO images before writing them to USB. For Pi 4, flash the SD image with a tool that supports .xz, such as Etcher.</aside>'
    body += '<div class="section-heading apps-heading"><h2>Native applications</h2><span>Haiku .hpkg packages</span></div><div class="app-grid">'
    for i, entry in enumerate(D['apps']):
        app = {**entry, **next(a for a in json.loads((ROOT / 'content/project.json').read_text())['apps'] if a['repo'] == entry['repo'])}
        body += f'<article class="app-card" data-repo="{app["repo"]}" id="{app["repo"].lower()}"><span class="app-number">{i+1:02d}</span><h3>{app["name"]}</h3><p>{app["description"]}</p>'
        if app.get('note'):
            body += f'<p class="package-note">{app["note"]}</p>'
        body += '<div class="app-packages">'
        if not app['assets']:
            body += '<p class="availability">No public package published yet.</p>'
            body += link('https://github.com/jmgasper/'+app['repo']+'/releases', 'Follow public releases ↗', 'release-fallback')
        else:
            for arch, label in [('x86_64', 'x86-64'), ('arm64', 'ARM64')]:
                assets = [a for a in app['assets'] if a['name'].endswith(arch+'.hpkg')]
                if not assets:
                    body += f'<p>{label}: awaiting a published package.</p>'
                for a in assets:
                    kind = ' · WebKit engine' if a['name'].startswith('summit_webkit') else ''
                    body += link(a['browser_download_url'], f'<span>{label}{kind}</span><small>{size(a["size"])} ↓</small>', 'package-link')
            body += '<div class="app-meta">' + link(app['release'], 'Build details & checksums ↗') + f'<span>{app["published"][:10]}</span></div>'
        body += '</div>'
        if app['repo'] == 'summit':
            body += '<p class="package-note">Using stock Haiku R1/beta6? '+link('https://github.com/jmgasper/summit/releases/tag/latest-haiku', 'Get the dedicated x86-64 browser and engine ↗')+'</p>'
        if app['repo'] in ('wordcraft', 'gridcraft', 'deckcraft', 'pdfcraft'):
            body += link(url('apps/#'+app['repo']), 'Features, screenshots and port notes →', 'subtle')
        body += '</article>'
    body += '</div><section class="install"><h2>Installing an app</h2><div><p>Choose the package for your architecture. Open it with Haiku’s package installer, or run:</p><pre><code>pkgman install /path/to/package.hpkg</code></pre><p>Packages target airOS unless their release notes say otherwise. For stock Haiku, use the dedicated Summit build. Follow dependency notes and install Summit together with its matching WebKit engine.</p></div></section>'
    page('downloads/', 'Downloads', 'Download airOS images and native app packages for ARM64 and x86-64.', body)

def sources():
    body = intro('Source code', 'Every part has a story.', 'The operating system, applications, libraries and firmware that make up airOS. Explore the code, its origins and the changes we build on.')
    body += '<aside class="note">Start with <a href="https://github.com/haiku/haiku">upstream Haiku</a> and <a href="https://www.haiku-os.org/">the Haiku project</a>. airOS is an independent, AI-assisted fork; its work is not presented as upstream-approved. Each repository retains its own licence and attribution.</aside>'
    groups = defaultdict(list)
    for s in D['sources']:
        groups[s['group']].append(s)
    for group, items in groups.items():
        body += f'<div class="section-heading"><h2>{group}</h2><span>{len(items)} source branches</span></div><div class="source-list">'
        for s in items:
            body += f'<article><div><h3>{link(s["url"], e(s["name"])+" ↗")}</h3><p>{e(s["description"])}</p></div><div class="source-ref"><code>{e(s["branch"])}</code>'+link(f'https://github.com/{s["repo"]}/commits/{quote(s["branch"])}', 'Git history ↗')+'</div></article>'
        body += '</div>'
    body += f'<p class="meta">Library list from {link("https://github.com/jmgasper/airos-ci/blob/"+D["ci_head"]+"/forks/forks.lock.json", "the CI source manifest")}. Only public repositories are listed.</p>'
    page('source/', 'Source code', 'Public airOS source repositories, application code, forks and firmware.', body)

def changelog():
    # One commit can occur on multiple tracked branches. Display it once, preserving
    # every branch membership in the downloadable source snapshot.
    unique = {}
    for s in D['sources']:
        for c in s['commits']:
            key = (s['repo'], c['sha'])
            unique[key] = {**c, 'repo': s['repo'], 'name': s['name']}
    commits = sorted(unique.values(), key=lambda c: (c['date'], c['sha']), reverse=True)
    months = defaultdict(list)
    for c in commits:
        months[c['date'][:7]].append(c)
    (OUT / 'changes.json').write_text(json.dumps(commits))
    for month in [None, *months]:
        records = commits[:100] if month is None else months[month]
        path = 'changelog/' + (month+'/' if month else '')
        title = 'Follow the work.' if month is None else datetime.strptime(month, '%Y-%m').strftime('%B %Y')
        body = intro('Changelog · refreshed every 6 hours', title, 'From the Git history of our public forks and apps. Every entry links to the original commit, including fixes, experiments, documentation and merges.')
        body += f'<div class="change-stats"><span><strong>{len(commits):,}</strong> commits archived</span><span><strong>{len(D["sources"])}</strong> source branches</span><span>Updated <strong>{UPDATED}</strong> UTC</span></div>'
        body += '<details class="archive"><summary>Browse the complete archive & scope</summary><p>The main page shows the latest 100 commits. Monthly archives include every collected commit. Fork history starts at the recorded upstream baseline; original apps and imported sources include their complete history. Upstream history before those baselines is available in each source repository.</p><div class="month-links">'
        body += ''.join(link(url('changelog/'+m+'/'), f'{m} <small>({len(v)})</small>') for m, v in months.items())
        body += '</div>'+link(url('source/'), 'View all tracked sources →')+'</details>'
        if month is None:
            names = sorted({c['repo'] for c in commits})
            body += f'<div class="change-search" data-changes="{url("changes.json")}" hidden><label>Search all commits<input type="search" placeholder="Try Wi-Fi, Summit or display…"></label><label>Repository<select><option value="">All repositories</option>'+''.join(f'<option>{e(n)}</option>' for n in names)+'</select></label><p class="search-status" role="status"></p></div>'
        body += '<div class="commit-list">'
        for c in records:
            body += f'<article class="commit"><time datetime="{c["date"]}">{c["date"][:10]}</time><div><span class="commit-repo">{e(c["repo"])}</span><h2>{link(c["url"], e(c["subject"]))}</h2></div><code>{c["sha"][:7]}</code></article>'
        body += '</div>'
        if month is None:
            body += '<p class="meta">Showing the latest 100. Search all commits above, or choose a month from the complete archive.</p>'
        else:
            body += link(url('changelog/'), '← Latest changes', 'button')
        page(path, 'Changelog' + (' · '+month if month else ''), 'Automatically refreshed Git history from the airOS forks and apps.', body)

def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / 'static', OUT)
    for build in [home, applications, summit, screenshots, hardware, downloads, sources, changelog]:
        build()
    page('404/', 'Page not found', 'This airOS page could not be found.', intro('404', 'A little off course.', 'This page has moved or does not exist.') + link(url(), 'Back to the project →', 'button primary'))
    shutil.copy(OUT / '404/index.html', OUT / '404.html')
    paths = sorted(p.parent.relative_to(OUT).as_posix().strip('.') for p in OUT.rglob('index.html') if '/404/' not in str(p))
    (OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{ORIGIN}/{p+"/" if p else ""}</loc></url>' for p in paths)+'</urlset>')
    (OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n')
    (OUT / '.nojekyll').touch()
    print(f'Built {len(paths)} pages in {OUT}')

if __name__ == '__main__':
    main()
