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
NAV = [('', 'Project'), ('apps/', 'Apps'), ('summit/', 'Summit'), ('hardware/', 'New hardware'), ('downloads/', 'Downloads'), ('source/', 'Source code'), ('changelog/', 'Changelog')]

def url(path=''):
    return BASE + '/' + path

def link(href, label, cls=''):
    return f'<a href="{e(href, quote=True)}" class="{cls}">{label}</a>'

def page(path, title, description, body):
    canonical = ORIGIN + '/' + path
    current = lambda p: p == path or p in ('changelog/', 'downloads/') and path.startswith(p)
    nav = ''.join(link(url(p), t, 'active' if current(p) else '') for p, t in NAV if p != 'downloads/')
    cta = link(url('downloads/'), 'Downloads', 'button primary header-cta' + (' active' if current('downloads/') else ''))
    footer_links = ''.join(f'<li>{link(url(p), t)}</li>' for p, t in NAV)
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>air/OS</title><meta name="description" content="{e(description, quote=True)}">
<link rel="canonical" href="{canonical}"><meta property="og:title" content="air/OS">
<meta property="og:description" content="{e(description, quote=True)}"><meta property="og:type" content="website">
<meta property="og:url" content="{canonical}"><meta property="og:image" content="{ORIGIN}/assets/logo.png">
<link rel="icon" href="{url('favicon.ico')}" sizes="16x16 32x32 48x48"><link rel="icon" type="image/svg+xml" href="{url('assets/favicon.svg')}" sizes="any"><link rel="stylesheet" href="{url('assets/site.css')}">
<script src="{url('assets/site.js')}" defer></script></head>
<body class="{'home' if path == '' else 'inner'}"><a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="wrap header-inner">
<a class="brand" href="{url()}" aria-label="airOS home"><img src="{url('assets/logo.png')}" width="191" height="64" alt="air/OS"></a>
<nav aria-label="Main navigation">{nav}</nav>{cta}</div></header>
<main id="main" class="wrap">{body}</main>
<footer class="site-footer"><div class="wrap footer-inner"><div class="footer-brand"><img src="{url('assets/logo.png')}" width="143" height="48" alt="air/OS">{link('https://www.haiku-os.org/', 'Built on Haiku ↗', 'text-link')}</div>
<nav aria-label="Footer"><p class="eyebrow">Explore</p><ul>{footer_links}</ul></nav>
<div class="footer-meta"><p class="eyebrow">Status</p><p>Development builds. Independent of the Haiku project.</p><p>Build data refreshed {UPDATED} UTC</p></div></div></footer></body></html>'''
    target = OUT / path / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html)

def intro(kicker, title, text, wide=False):
    # A wide intro lets a long title use the full content width.
    return f'<div class="page-intro{" wide" if wide else ""}"><p class="eyebrow">{kicker}</p><h1>{title}</h1><p class="lead">{text}</p></div>'

# Small line icons for the home page's three principles.
ICONS = {
    'chip': '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/></svg>',
    'apps': '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="7.5" height="7.5" rx="2"/><rect x="13.5" y="3" width="7.5" height="7.5" rx="2"/><rect x="3" y="13.5" width="7.5" height="7.5" rx="2"/><rect x="13.5" y="13.5" width="7.5" height="7.5" rx="2"/></svg>',
    'loop': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 12a8 8 0 0 1-13.7 5.6M4 12a8 8 0 0 1 13.7-5.6"/><path d="M18 2.5v4.2h-4.2M6 21.5v-4.2h4.2"/></svg>',
}

def home():
    commits = len({(s['repo'], c['sha']) for s in D['sources'] for c in s['commits']})
    apps = len(json.loads((ROOT / 'content/project.json').read_text())['apps'])
    # ARM64 boards with a hardware-tested port; boards still in bring-up are not counted.
    boards = sum(1 for d in json.loads((ROOT / 'content/hardware.json').read_text()) if d['chip'].startswith('ARM64') and d['status'] == 'Tested on hardware')
    stats = [(f'{apps}', 'new native apps'), (f'{boards}', 'new ARM64 SBCs supported'), (f'{len(D["sources"])}', 'tracked source branches'), (f'{commits:,}', 'commits in the public changelog')]
    body = f'''<section class="hero"><div class="hero-copy">
{link(url('apps/#proton'), '<span class="dot" aria-hidden="true"></span>New: Proton VPN and Mail Bridge <span aria-hidden="true">›</span>', 'pill-badge')}
<h1>Built on Haiku.<br>Extended with AI.</h1>
<p class="lead">airOS is an independent, AI-assisted exploration of what Haiku can do — on more devices, with more native apps, and with the same love for a responsive, personal desktop.</p>
<div class="actions">{link(url('downloads/'), 'Explore the downloads', 'button primary')}{link(url('apps/'), 'See it in action <span aria-hidden="true">›</span>', 'button ghost')}</div>
</div></section>
<section class="stats" aria-label="airOS at a glance"><h2>BeOS’s desktop,<br>on more machines.</h2><dl>{''.join(f'<div><dt>{label}</dt><dd>{value}</dd></div>' for value, label in stats)}</dl></section>
<section class="principles"><article>{ICONS['chip']}<h3>More hardware</h3><p>From ARM boards to a desktop workstation, new drivers and ports bring BeOS’s desktop to more places.</p>{link(url('hardware/'), 'See what works ›', 'text-link')}</article><article>{ICONS['apps']}<h3>More everyday apps</h3><p>Browse, listen, watch, capture and create with native applications that feel at home on the desktop.</p>{link(url('apps/'), 'Meet the apps ›', 'text-link')}</article><article>{ICONS['loop']}<h3>A faster feedback loop</h3><p>AI helps investigate unfamiliar code, develop ports and test ideas quickly. Builds, hardware checks and public Git history make progress inspectable.</p>{link(url('changelog/'), 'Follow the changes ›', 'text-link')}</article></section>
<section class="statement"><p class="eyebrow">The foundation</p><div><p class="statement-text">Haiku’s contributors have spent decades building an open-source operating system inspired by BeOS: fast, coherent and thoughtfully designed for personal computing.</p><p class="statement-text">airOS builds on their kernel, desktop and native APIs with device support, desktop improvements and applications. It is an independent fork, with its own development approach.</p>{link('https://www.haiku-os.org/', 'The Haiku Project ↗', 'button ghost')}</div></section>
<section class="release-highlights"><div class="section-heading"><div><p class="eyebrow">October 2026</p><h2>New apps.</h2></div>{link(url('apps/'), 'All apps ›', 'button ghost')}</div><div class="highlight-grid">
<article><a class="highlight-image" href="{url('apps/#office')}"><img src="{url('assets/screenshots/wordcraft.png')}" alt="WordCraft running on Haiku" loading="lazy"></a><span class="tag">Office Suite</span><h3>A new office suite.</h3><p>WordCraft, GridCraft, PDFCraft and DeckCraft: early native ports for documents, spreadsheets, PDFs and presentations.</p>{link(url('apps/#office'), 'Explore the Craft apps ›', 'text-link')}</article>
<article><a class="highlight-image" href="{url('apps/#proton')}"><img src="{url('assets/screenshots/proton-vpn.png')}" alt="Proton VPN on airOS" loading="lazy"></a><span class="tag">Proton</span><h3>Proton apps.</h3><p>Community ports of Proton VPN and Proton Mail Bridge, built by airOS CI and published as rolling releases.</p>{link(url('apps/#proton'), 'Meet the Proton ports ›', 'text-link')}</article>
<article><a class="highlight-image" href="{url('summit/')}"><img src="{url('assets/screenshots/summit-firefox-addon.png')}" alt="Summit offering to install an extension from Firefox Add-ons" loading="lazy"></a><span class="tag">Summit Browser</span><h3>Native WebKit browser called Summit.</h3><p>Reader mode, PDFs, store extensions, streaming media and native developer tools, for airOS and stock Haiku.</p>{link(url('summit/'), 'Discover Summit ›', 'text-link')}</article>
<article><a class="highlight-image" href="{url('apps/#system')}"><img src="{url('assets/screenshots/mediaconverter.png')}" alt="MediaConverter on airOS" loading="lazy"></a><span class="tag">System</span><h3>The system, reworked.</h3><p>A new MediaConverter with GPU encoding, clearer Media preferences, new Wi-Fi and Bluetooth panels, and Quick Look and network shares in Tracker.</p>{link(url('apps/#system'), 'Explore the system apps ›', 'text-link')}</article></div></section>
<section class="closing"><img src="{url('assets/mark.png')}" alt="" aria-hidden="true"><p class="eyebrow">An experiment you can explore</p><h2>Open source. Ongoing work.<br>A desktop with room to grow.</h2><p>Development builds are available now. Check the hardware notes, try the apps, or follow along in the source.</p><div class="actions">{link(url('downloads/'), 'Get airOS', 'button light')}{link(url('source/'), 'Explore the code ↗', 'button ghost-light')}</div></section>'''
    page('', 'Built on Haiku. Extended with AI.', 'An independent Haiku-based operating system using AI to expand hardware support and native applications.', body)

def capture(id):
    shots = json.loads((ROOT / 'content/screenshots.json').read_text())
    shot = next((s for s in shots if s.get('id') == id), None)
    if shot is None:
        raise ValueError('Missing screenshot: '+id)
    image = url('assets/screenshots/' + shot['file'])
    # Third-party content shown in a capture is credited beside it.
    credit = ' · ' + shot['credit'].replace('{base}', BASE) if shot.get('credit') else ''
    return f'<figure class="feature-capture"><a href="{image}"><img src="{image}" alt="{e(shot["title"]+": "+shot["description"], quote=True)}" loading="lazy" width="{shot["width"]}" height="{shot["height"]}"></a><figcaption>{e(shot["title"])} · {e(shot["captured"])} · {link(shot["source"], "About this capture ↗")}{credit}</figcaption></figure>'

def app_icon(id, size):
    # Real app icons, rendered from each app's HVIF resource by Haiku's icon renderer.
    if not (ROOT / 'static/assets/icons' / (id + '.png')).exists():
        return ''
    return f'<img class="app-icon" src="{url("assets/icons/"+id+".png")}" width="{size}" height="{size}" alt="" loading="lazy">'

def feature_row(item, prefix=''):
    links = link(item['source'], 'Feature and port notes ↗', 'text-link')
    if download := item.get('download'):
        label = 'In airOS system builds →' if download == 'downloads/#system' else 'Downloads & availability →'
        links += link(url(download), label, 'text-link')
    links += ''.join(link(x['href'], x['label'], 'text-link') for x in item.get('links', []))
    heading = f'{app_icon(item.get("icon", item["id"]), 56)}<h3>{e(item["title"])}</h3><p>{e(item["text"])}</p>'
    details = f'<ul class="checks">{"".join("<li>"+e(x)+"</li>" for x in item["features"])}</ul><div class="device-links">{links}</div>'
    shots = item.get('screenshots') or ([item['screenshot']] if item.get('screenshot') else [])
    captures = ''.join(capture(id) for id in shots)
    if len(shots) > 1:
        captures = f'<div class="capture-pair">{captures}</div>'
    if shots and item.get('wide'):
        columns = f'<div>{heading}</div><div>{details}</div>{captures}'
    elif shots:
        columns = f'<div>{heading}{details}</div>{captures}'
    else:
        columns = f'<div>{heading}</div><div>{details}</div>'
    wide = ' wide' if item.get('wide') and shots else ''
    return f'<article class="feature-row{wide}" id="{prefix}{item["id"]}">{columns}</article>'

def app_tabs():
    return json.loads((ROOT / 'content/apps.json').read_text())

def tab_summary(tab):
    if tab.get('summit'):
        return 'Chrome and Firefox extension support, hardware-accelerated WebGL and media decoding, developer tools, reader mode, PDF viewing, WebHID and more.'
    if tab.get('summary'):
        return tab['summary']
    return ' · '.join(item['title'] for item in tab['items'])

def applications():
    data = app_tabs()
    summit_data = json.loads((ROOT / 'content/summit.json').read_text())
    body = intro('Made for your desktop', 'Modern support of common tools.', 'Write, listen, build, browse and stay private. Native ports and reworked Haiku tools bring more of your day onto the desktop. Choose a category to see its apps.', wide=True)
    # Without JavaScript these are jump links and every panel stays visible;
    # site.js turns them into tabs whose panels open when selected.
    body += '<nav class="app-tabs" aria-label="Application categories" data-app-tabs>'
    # Items that share an icon (Tracker's features) show it once on the tab.
    icons = lambda tab: ''.join(app_icon(id, 24) for id in (['summit'] if tab.get('summit') else dict.fromkeys(item.get('icon', item['id']) for item in tab['items'])))
    body += ''.join(f'<a href="#{tab["id"]}" data-tab="{tab["id"]}"><span class="tab-icons">{icons(tab)}</span><strong>{e(tab["label"])}</strong><span>{e(tab_summary(tab))}</span></a>' for tab in data['tabs'])
    body += '</nav>'
    for tab in data['tabs']:
        body += f'<section id="{tab["id"]}" class="tab-panel"><div class="section-heading"><h2>{e(tab["heading"])}</h2><span>{e(tab["tag"])}</span></div><p class="section-lead">{e(tab["lead"])}</p>'
        if tab.get('links'):
            body += '<div class="actions panel-actions">' + ''.join(link(url(x['href']) if x.get('internal') else x['href'], e(x['label']), 'button primary' if i == 0 and tab.get('summit') else 'button') for i, x in enumerate(tab['links'])) + '</div>'
        if tab.get('note'):
            body += f'<aside class="note">{e(tab["note"])}</aside>'
        if tab.get('summit'):
            body += capture('summit') + ''.join(feature_row(f, 'summit-') for f in summit_data['features'])
        else:
            body += ''.join(feature_row(item) for item in tab['items'])
        body += '</section>'
    body += '<p class="meta">Features and port notes reviewed '+data['reviewed']+'. See each project’s source for current limitations.</p>'
    page('apps/', 'Applications', 'The airOS apps: the Craft office suite, media tools, developer tools, the Summit browser, Proton VPN and Proton Mail Bridge, Clipper, AirShot, and the reworked system apps and preferences.', body)

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

def image_asset(target):
    im = next((i for i in D['images'] if i['target'] == target), None)
    return next((a for a in im['assets'] if a['name'].endswith(('.iso.xz', '.img.xz'))), None) if im else None

IMAGE_LABELS = {'x86_64': 'Download the x86-64 ISO', 'arm64': 'Download the ARM64 ISO', 'rpi4': 'Download the Pi 4 SD image', 'cubie': 'Download the Cubie SD image'}

def download_button(device):
    # The static link is the snapshot's build; site.js swaps in a newer one.
    target = device.get('download')
    if not target:
        return ''
    image = image_asset(target)
    href = image['browser_download_url'] if image else url('downloads/#system')
    return f'<div class="actions device-download"><a href="{e(href, quote=True)}" class="button primary" data-image-link="{target}">{IMAGE_LABELS[target]} ↓</a>{link(url("downloads/#system"), "All images", "button")}</div>'

def hardware():
    body = intro('New hardware', 'New places for Haiku.', 'Device support built in the airOS forks. These notes describe tested configurations, with the remaining gaps alongside them.')
    for i, device in enumerate(json.loads((ROOT / 'content/hardware.json').read_text())):
        photo = ''
        if image := device.get('image'):
            image_url = url('assets/hardware/' + image['file'])
            photo = f'''<figure class="device-photo"><a href="{e(image_url, quote=True)}"><img src="{e(image_url, quote=True)}" alt="{e(image['alt'], quote=True)}" width="{image['width']}" height="{image['height']}" loading="lazy"></a><figcaption>Photo: {link(image['source'], e(image['credit']))} · {link(image['license_url'], e(image['license']))}</figcaption></figure>'''
        body += f'''<article class="hardware-row" id="{device['id']}"><div class="device-title"><span class="section-number">0{i+1} / {device['chip']}</span><h2>{device['name']}</h2><p>{device['summary']}</p><span class="badge">{device['status']}</span>{photo}{capture(device['screenshot']) if device.get('screenshot') else ''}</div><div><h3>{e(device.get("features_title", "What’s working"))}</h3><ul class="checks">{''.join('<li>'+e(f)+'</li>' for f in device['features'])}</ul><p class="limitations"><strong>Still in progress</strong><br>{device['limits']}</p>{link(device['source_url'], 'Follow the bring-up history ↗') if device.get('source_url') else link('https://github.com/jmgasper/haiku/blob/master/'+device['source'], 'Read the test notes and history ↗')}{download_button(device)}<div class="device-links">{''.join(link('https://github.com/jmgasper/haiku/blob/master/'+item['path'], e(item['label'])+' ↗') for item in device.get('links', []))}</div></div></article>'''
    body += '<aside class="note">Hardware notes reviewed 18 October 2026. A working driver on one board or card does not establish support for every device in the same family. The linked test notes carry the detailed evidence and newer results.</aside>'
    page('hardware/', 'New hardware', 'airOS hardware support for ROCK 5 ITX, Cubie A7S, Radxa Dragon Q8B, Raspberry Pi 4, Framework 13, AMD graphics and NVIDIA graphics, NVDEC decoding and experimental NVENC encoding.', body)

def size(n):
    return f'{n / 1048576:.1f} MB' if n >= 1048576 else f'{n / 1024:.0f} KB'

def downloads():
    body = intro('Downloads', 'Make yourself at home.', 'Get an airOS development image, or pick up an individual app for your existing installation.')
    body += '<div class="section-heading"><h2 id="system">The operating system</h2><span>Latest successful published builds</span></div><div class="image-grid">'
    titles = {'x86_64': ('x86-64', 'Intel & AMD PCs', 'ISO image · UEFI / BIOS'), 'arm64': ('ARM64', 'ROCK 5 ITX, Dragon Q8B & UEFI ARM64', 'ISO image · UEFI'), 'rpi4': ('Raspberry Pi 4', 'A desktop on an SD card', 'SD card image · Pi 4'), 'cubie': ('Cubie A7S', 'Radxa’s Allwinner A733 board', 'SD card image · Cubie A7S')}
    for im in D['images']:
        title, subtitle, format = titles[im['target']]
        body += f'<article class="image-card" data-target="{im["target"]}"><span class="section-number">{format}</span><h3>{title}</h3><p>{subtitle}</p><div class="image-download">'
        assets = im['assets']
        image = next((a for a in assets if a['name'].endswith(('.iso.xz', '.img.xz'))), None)
        if image:
            body += link(image['browser_download_url'], 'Download image ↓', 'button primary')
            body += f'<p class="meta">{size(image["size"])} compressed · {im["published"][:10]}</p><div class="asset-extras">'
            for a in sorted(assets, key=lambda a: a['name'] == 'manifest.json'):
                if a['name'].endswith('.sha256') or a['name'] == 'manifest.json':
                    body += link(a['browser_download_url'], 'SHA-256' if a['name'].endswith('.sha256') else 'Build manifest')
            body += link(im['release'], 'Release notes ↗') + '</div>'
        else:
            body += '<p class="availability">Public image coming soon</p>' + link('https://github.com/jmgasper/haiku/actions/workflows/airos-images.yml', 'Build status ↗')
        body += '</div></article>'
    body += '</div><aside class="note"><strong>Before installing.</strong> These are experimental development builds. Check the <a href="'+url('hardware/')+'">hardware notes</a> and back up your data. x86 means 64-bit x86 (x86-64); there is no 32-bit image. The ARM64 ISO is for UEFI machines and does not boot the Pi 4 or Cubie A7S. <strong>Write every image with dd or Rufus, not balenaEtcher,</strong> which has corrupted an airOS image without reporting an error. '+link(url('downloads/write/'), 'How to write an image to USB or SD safely →')+'</aside>'
    # Each package links back to its feature row on the apps page.
    features = {item['download'].split('#')[1]: item['id'] for tab in app_tabs()['tabs'] for item in tab.get('items', [])
                if item.get('download', 'downloads/#system') != 'downloads/#system'}
    features['summit'] = 'summit'
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
        if target := features.get(app['repo'].lower()):
            body += link(url('apps/#'+target), 'Features, screenshots and port notes →', 'subtle')
        body += '</article>'
    body += '</div><section class="install"><h2>Installing an app</h2><div><p>Choose the package for your architecture. Open it with Haiku’s package installer, or run:</p><pre><code>pkgman install /path/to/package.hpkg</code></pre><p>Packages target airOS unless their release notes say otherwise. For stock Haiku, use the dedicated Summit build. Follow dependency notes and install Summit together with its matching WebKit engine.</p></div></section>'
    page('downloads/', 'Downloads', 'Download airOS images and native app packages for ARM64 and x86-64.', body)

def write_guide():
    pre = lambda *lines: '<pre><code>' + e('\n'.join(lines)) + '</code></pre>'
    body = intro('Downloads · Writing an image', 'From download to first boot.', 'Every airOS image, ISO or SD, is written the same way: the whole file, byte for byte, onto the whole USB stick or SD card. Check the download first and, where you can, the copy afterwards.')
    body += '''<aside class="note caution"><strong>Don’t use balenaEtcher.</strong> balenaEtcher 2.1.4 silently dropped 2 MB from the middle of the x86-64 image while writing it to a USB stick. It reported success; the stick started the boot loader, which then stopped with “No boot volume found”. The same file written with <code>dd</code> booted normally. Etcher wrote a Pi 4 image correctly, but because the failure gives no warning we don’t recommend it for any airOS image. Use <code>dd</code> on Linux and macOS, and Rufus in DD mode on Windows.</aside>'''
    body += '<section class="install"><h2>Before you start</h2><div><ul>'
    body += '<li>A USB stick or SD card of 8 GB or more. Writing erases everything on it.</li>'
    body += '<li>The ISO images (x86-64 and ARM64) go on a USB stick; the Pi 4 and Cubie A7S images go on an SD card and boot directly.</li>'
    body += '<li>Download the image and its <strong>SHA-256</strong> file from the ' + link(url('downloads/#system'), 'downloads page') + ' into the same folder. If your browser renamed the image, such as <code>airos-rpi4(1).img.xz</code>, an older download is in the folder: remove it so you don’t write the wrong file.</li>'
    body += '<li>Check the download. Each command should report <code>OK</code> or print the hash in the SHA-256 file.</li></ul>'
    body += pre('# Linux', 'sha256sum -c airos-x86_64.iso.xz.sha256', '', '# macOS', 'shasum -a 256 -c airos-x86_64.iso.xz.sha256', '', '# Windows (PowerShell)', 'Get-FileHash .\\airos-x86_64.iso.xz')
    body += '<p>Replace <code>airos-x86_64.iso.xz</code> with the image you downloaded throughout this guide.</p></div></section>'
    body += '<section class="install" id="linux"><h2>Linux</h2><div><ol>'
    body += '<li>Insert the stick or card and find its device name. Match the size and model: USB devices are <code>/dev/sdX</code>, built-in card readers <code>/dev/mmcblkN</code>.</li></ol>'
    body += pre('lsblk -o NAME,SIZE,MODEL,TRAN')
    body += '<ol start="2"><li>Unmount any of its partitions your desktop mounted (ignore “not mounted” messages), then decompress and write the image to the <strong>whole device</strong>, not a partition such as <code>sdX1</code>:</li></ol>'
    body += pre('sudo umount /dev/sdX?*', 'xz -dc airos-x86_64.iso.xz | sudo dd of=/dev/sdX bs=4M conv=fsync oflag=direct status=progress', 'sync')
    body += '<p>Double-check the device name: <code>dd</code> overwrites whatever disk you give it without asking. Don’t remove the stick until the prompt returns after <code>sync</code>.</p></div></section>'
    body += '<section class="install" id="macos"><h2>macOS</h2><div><ol>'
    body += '<li>macOS doesn’t include <code>xz</code>. Install it with Homebrew (<code>brew install xz</code>), or extract the image with an archive app such as Keka or The Unarchiver and use <code>if=airos-x86_64.iso</code> in step 3 instead of the pipe.</li>'
    body += '<li>Insert the stick or card, find its disk number by its size, and unmount it:</li></ol>'
    body += pre('diskutil list external', 'diskutil unmountDisk /dev/diskN')
    body += '<ol start="3"><li>Write to the raw device <code>/dev/rdiskN</code> (faster than <code>/dev/diskN</code>). Press Ctrl-T to see progress.</li></ol>'
    body += pre('xz -dc airos-x86_64.iso.xz | sudo dd of=/dev/rdiskN bs=4m', 'diskutil eject /dev/diskN')
    body += '<p>If macOS says the disk isn’t readable, choose <strong>Ignore</strong> or <strong>Eject</strong>, never <strong>Initialize</strong>: macOS can’t read Haiku’s file system, and the disk is fine.</p></div></section>'
    body += '<section class="install" id="windows"><h2>Windows</h2><div><ol>'
    body += '<li>Extract the image with ' + link('https://www.7-zip.org/', '7-Zip') + ': right-click the <code>.xz</code> file and choose <strong>7-Zip → Extract Here</strong>. You get <code>airos-x86_64.iso</code> or an <code>.img</code> file.</li>'
    body += '<li>Run ' + link('https://rufus.ie/', 'Rufus') + ' and choose the stick or card under <strong>Device</strong>. Rufus lists USB devices, including SD cards in a USB reader.</li>'
    body += '<li>Click <strong>Select</strong> and open the extracted file. Leave the other settings alone.</li>'
    body += '<li>Click <strong>Start</strong>. If Rufus asks how to write the image, choose <strong>Write in DD Image mode</strong>. ISO Image mode copies files onto a new FAT partition and the stick won’t boot.</li>'
    body += '<li>Confirm that the device will be erased and wait for <strong>Ready</strong>. If Windows then offers to format the disk, click <strong>Cancel</strong>: Windows can’t read Haiku’s file system, and formatting would erase the image.</li></ol></div></section>'
    body += '<section class="install" id="verify"><h2>Check the copy</h2><div><p>A corrupted write can still look normal, so on Linux and macOS read the image back from the device and compare it with the build. Open the image’s <strong>Build manifest</strong> on the downloads page: <code>image_bytes</code> is the image’s uncompressed size and <code>image_sha256</code> its uncompressed hash.</p>'
    body += pre('# Linux', 'sudo head -c IMAGE_BYTES /dev/sdX | sha256sum', '', '# macOS (insert the disk again if you ejected it)', 'sudo head -c IMAGE_BYTES /dev/diskN | shasum -a 256')
    body += '<p>The printed hash must equal <code>image_sha256</code>. If it doesn’t, write the image again, and try another stick or card if it still differs.</p></div></section>'
    body += '<section class="install" id="booting"><h2>If it doesn’t boot</h2><div><ul>'
    body += '<li><strong>PCs:</strong> turn off Secure Boot in the firmware settings. The airOS boot loader isn’t signed.</li>'
    body += '<li><strong>“No boot volume found”</strong> after the boot loader appears usually means the copy is damaged. Check it as above and rewrite it with <code>dd</code> or Rufus.</li>'
    body += '<li><strong>Pi 4 and Cubie A7S:</strong> use the SD image for that board; the ARM64 ISO doesn’t boot either one. The ' + link(url('hardware/'), 'hardware notes') + ' list what each board supports.</li></ul></div></section>'
    body += '<div class="actions">' + link(url('downloads/#system'), '← Back to the downloads', 'button') + '</div>'
    page('downloads/write/', 'Writing an image', 'How to write airOS images to a USB stick or SD card with dd on Linux and macOS or Rufus on Windows, why not to use balenaEtcher, and how to check the copy.', body)

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
        body = intro('Changelog · refreshed every 6 hours', title, 'The airOS work itself: every commit made to our public forks and apps since the project began. Every entry links to the original commit, including fixes, experiments, documentation and merges.')
        body += f'<div class="change-stats"><span><strong>{len(commits):,}</strong> commits archived</span><span><strong>{len(D["sources"])}</strong> source branches</span><span>Updated <strong>{UPDATED}</strong> UTC</span></div>'
        body += '<details class="archive"><summary>Browse the complete archive & scope</summary><p>The main page shows the latest 100 commits. Monthly archives include every collected commit. Only airOS’s own commits are listed: upstream history, the history of imported projects and automated build commits are left out, and remain available in each source repository.</p><div class="month-links">'
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
    for build in [home, applications, summit, hardware, downloads, write_guide, sources, changelog]:
        build()
    page('404/', 'Page not found', 'This airOS page could not be found.', intro('404', 'A little off course.', 'This page has moved or does not exist.') + link(url(), 'Back to the project →', 'button primary'))
    shutil.copy(OUT / '404/index.html', OUT / '404.html')
    # The screenshots now live beside their features on the apps page. Older links
    # (including Summit's start page) are sent there rather than to a 404.
    (OUT / 'screenshots').mkdir()
    (OUT / 'screenshots/index.html').write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>air/OS</title><link rel="canonical" href="{ORIGIN}/apps/"><meta http-equiv="refresh" content="0; url={url("apps/")}"></head><body><h1>Screenshots have moved</h1><p>{link(url("apps/"), "See them on the apps page →")}</p></body></html>')
    paths = sorted(p.parent.relative_to(OUT).as_posix().strip('.') for p in OUT.rglob('index.html') if '/404/' not in str(p) and '/screenshots/' not in str(p))
    (OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{ORIGIN}/{p+"/" if p else ""}</loc></url>' for p in paths)+'</urlset>')
    (OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n')
    (OUT / '.nojekyll').touch()
    print(f'Built {len(paths)} pages in {OUT}')

if __name__ == '__main__':
    main()
