# airos.works

The public airOS project website. Static HTML, CSS and small progressive
JavaScript enhancements, hosted by GitHub Pages. No framework, database,
third-party fonts, analytics, or visitor login.

## Run locally

Python 3.12 or newer is sufficient. The committed public GitHub snapshot lets
the website build without network access or credentials.

```sh
python3 scripts/build.py
python3 scripts/check.py
python3 -m http.server 8787 --directory dist
```

Refresh source histories and release metadata with a read-only GitHub token
(`GH_TOKEN` / `GITHUB_TOKEN`), or a signed-in `gh` CLI:

```sh
python3 scripts/sync.py
python3 scripts/build.py
python3 scripts/check.py
```

`BASE_PATH=/airos-website` supports a GitHub project URL. `SITE_URL` controls
the canonical URL, sitemap and social metadata. The Pages workflow derives
both from the repository's actual Pages configuration.

## Content and design

- Home: credit Haiku, explain the independent project and AI-assisted approach.
- Apps: six categories as tabs (Office Suite, Media Tools, Developer, Summit Browser,
  Proton and EveryDay). A panel opens when its tab is selected; links to a panel or
  to an app inside one open it. Without JavaScript the tabs are jump links and
  every panel is shown.
- Summit: browser features, compatibility limits and separate airOS/stock-Haiku builds.
- Screenshots: dated application and hardware captures, with full-size viewing.
- New hardware: curated capabilities, gaps and links to the lab's test notes.
- Downloads: actual public `.hpkg` release assets, plus immutable OS images.
- Source: the operating system, apps and every branch in the CI fork manifest.
- Changelog: all collected fork changes, monthly archives and global search.

The established air/OS artwork supplies the identity. The home page opens on the
airOS desktop's hills (`data/artwork/airos/airos-desktop.tga` in jmgasper/haiku,
cropped above its wordmark, with its own top row of sky extended upward as
`static/assets/hero-hills.jpg`). The layout takes cues from Duna's and T1 Energy's
sites: large light headlines over open sky, a stats row, hairline-divided feature
columns, small monospaced `■ LABEL` markers, two-column statements, pill-shaped
navigation and buttons, soft warm-grey rounded panels for captures and a dark
closing band. Warm white, deep teal, sky blue and amber echo the logo. Fonts are
the visitor's own system fonts (Inter where installed); nothing is loaded from a
font service. Real screenshots appear alongside features and in a filterable gallery. Navigation and content work without
JavaScript. With JavaScript, the gallery supports filtering and an accessible
native dialog, and the changelog searches its full local archive.

Curated content lives in `content/`. `static/assets/` holds the logo, original
captures, CSS and JavaScript. The build produces `dist/`. Screenshots are real captures, with capture dates, dimensions and provenance in
`content/screenshots.json`. Fresh native window captures were taken on the Framework
13 on 18 October 2026; DeckCraft and PDFCraft use their same-day native validation
captures. The Cubie and Raspberry Pi gallery entries are dated hardware-test
captures. Earlier app images are explicitly labelled as development captures.
No UI is reconstructed or generated. Summit is represented by a capture of the
airOS website, shared by its feature page and the gallery, and by its install card
on a Firefox Add-ons page (X399, 23 October 2026). The Proton VPN and Proton Mail
Bridge captures are the CI-built packages on the X399 the same day; Proton VPN is
signed in to the repository's stand-in test API (`tools/fake-proton`) and no
connection was made. Clipper, PhotoCraft, LightCraft, Code - OSS, pgAdmin 4, GitHub Desktop and Terminal were captured in a QEMU
VM running the 23 October x86-64 image live, with the separate developer packages
installed and sample files written for the captures. The Mail capture is its acceptance-run evidence
(`docs/evidence/mail-final-inbox.png` in jmgasper/mail), cropped to the window. The favicon uses the
[square airOS mark](https://github.com/jmgasper/haiku/blob/master/data/artwork/airos/airos-mark.svg),
with an SVG and 16/32/48-pixel ICO fallbacks rendered from that vector.
The AirTime and MediaConverter captures include Big Buck Bunny, © Blender Foundation,
[CC BY 3.0](https://creativecommons.org/licenses/by/3.0/).

The Cubie graphics capture includes WebGL Aquarium, © Google Inc. and contributors,
from [WebGL Samples](https://github.com/WebGLSamples/WebGLSamples.github.io/tree/master/aquarium).
Its BSD licence notice is retained in `static/assets/screenshots/webgl-aquarium-LICENSE.txt`.

The Cubie A7S board photo is reproduced unchanged from [Radxa Docs](https://docs.radxa.com/en/cubie/a7s#product-views),
© Radxa Computer (Shenzhen) Co.,Ltd., under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
The [source image](https://github.com/radxa-docs/docs/blob/bfb1f40a31d62ee504951a0b93155bb5a481e752/static/img/cubie/a7s/cubie-a7s-view.webp)
is stored locally in `static/assets/hardware/` and credited on the hardware page.

The other hardware photos are stored in the same directory and credited beside
each image. The Wikimedia images use the supplied 1280-pixel thumbnails, with
no cropping or other edits; the ROCK 5 ITX image is reproduced unchanged.

| Photo | Source | Credit and licence |
| --- | --- | --- |
| `rock-5-itx.webp` | [Radxa Docs](https://docs.radxa.com/en/rock5), [source image](https://docs.radxa.com/home/product-pictures/rock5itx.webp) | © Radxa Computer (Shenzhen) Co.,Ltd., [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| `raspberry-pi-4.jpg` | [Raspberry Pi 4 Model B – Side](https://commons.wikimedia.org/wiki/File:Raspberry_Pi_4_Model_B_-_Side.jpg) | Michael H. (Laserlicht) / Wikimedia Commons, [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| `framework-13.jpg` | [Framework laptop AMD 13](https://commons.wikimedia.org/wiki/File:Framework_laptop_AMD_13.jpg) | Thcipriani / Wikimedia Commons, [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |

The NVIDIA hardware entry distinguishes the recorded Pascal graphics and NVDEC
tests from the experimental NVENC implementation. Its sources are the
[workstation test notes](https://github.com/jmgasper/haiku/blob/master/docs/x399-workstation/STATUS.md)
and [MediaConverter NVENC notes](https://github.com/jmgasper/haiku/blob/master/docs/airos/MEDIACONVERTER.md#nvidia-nvenc).

## Keeping Git history current

The Pages workflow runs on every main-branch push, every six hours, manually,
and on a `source-updated` repository dispatch. It refreshes the site from public
GitHub APIs and deploys only after a complete successful sync and validation.
Failures leave the previous deployment intact.

The sync reads `jmgasper/airos-ci` at a fixed commit for each run. Its
`forks/forks.json` and `forks/forks.lock.json` determine dependency branches
and upstream baselines. `content/project.json` records two explicit history
baseline corrections: linux-drm is an imported Linux subset with no upstream
Git ancestor, and libdrm uses the immutable commit behind an upstream tag that
is absent from the public fork. These corrections keep the scheduled refresh
working without silently discarding history on arbitrary API failures. For Haiku the recorded baseline is the common ancestor
of the fork and upstream at initial site creation. The integration branch and
active `airos-release` and `rpi4` branches are all tracked (`x399-workstation` was
retired into master). App history and imported
repositories have no upstream exclusion. Every API page is fetched; compare
counts are checked, and duplicate commits across branches are displayed once.
The Craft ports have been merged into each fork's `main`, which the source entries
track, so the source links and changelog include the Haiku work.
`hidden_subjects` in `content/project.json` names a retired project that the site
does not mention: commits whose subject matches it are left out of the snapshot, and
`check.py` fails if any built file matches. Nothing else is limited to a recent date window. SHA-keyed cache files accelerate
unchanged histories without hiding force-pushed changes. Private repositories
are never exported. The source page links directly to full upstream history.

The public snapshot in `data/github.json` is a local-development fallback.
Scheduled and manual refreshes save the validated snapshot to main before
deployment. This keeps local builds current and avoids GitHub disabling the
public repository’s schedule after 60 days of inactivity. Snapshot pushes use
the repository’s GITHUB_TOKEN and do not trigger recursive workflow runs.
A concurrent editor push is never overwritten; the next run can save it. Hardware claims and screenshots need human
review when new test evidence arrives; the site does not infer support from
commit messages.

## Downloads

App assets come from each public repository's rolling `latest` prerelease.
Summit lists its browser and required WebKit engine separately. Proton VPN
(x86-64 and ARM64) and Proton Mail Bridge (x86-64) publish their rolling `latest`
releases from airos-ci's reusable app workflow on every push to their forks. The download
page refreshes rolling app links from the public GitHub API when it opens,
with the dated snapshot and release-page links as fallbacks. It identifies architecture and build date and links to checksums in the
release notes. Any app without a public release is explicitly unavailable and links to its
release index. The live refresh also checks those entries, so their first
rolling `latest` package appears without waiting for the next site deployment.
WordCraft has an x86-64 public package; GridCraft, DeckCraft and PDFCraft are
listed with their current public release availability. Media preferences and
MediaConverter are included in system builds. Summit also links to its separate
`latest-haiku` browser/engine pair for stock Haiku R1/beta6.

OS images are discovered from public `jmgasper/haiku` prereleases named
`image-{x86_64,arm64,rpi4}-...`. The newest published release for each target
wins. The downloads page also refreshes these image links when opened, so a
build published between scheduled site updates appears immediately. If the
public API is unavailable, the complete static download links remain. `airos-ci/images/publish-github.py` verifies smoke results and compressed
and uncompressed hashes, uploads to a draft, verifies the server's digests,
then publishes. The site includes the image, SHA-256 file and package manifest.
The repository and Pages deployment contain no OS images or application binaries.

GitHub's [Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)
allow a 1 GB published site. [Release assets](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
are under 2 GiB per file, with no total release storage or bandwidth limit
specified. The current compressed images fit this model.

## Domain

GitHub Pages publishes the site from the Actions workflow, with `airos.works` set
as the custom domain in the repository's Pages settings (no `CNAME` file). DNS at
Namecheap must hold only GitHub's records:

| Host | Type | Value |
|---|---|---|
| `@` | A | `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` |
| `www` | CNAME | `jmgasper.github.io.` |
| `_github-pages-challenge-jmgasper` | TXT | the value shown in GitHub's account Pages settings |

Any other `@` record, such as Namecheap's URL-redirect address `192.64.119.125`,
sends some visitors to Namecheap and stops GitHub from issuing the HTTPS
certificate. Once the certificate exists, turn on **Enforce HTTPS** in the
repository's Pages settings.
