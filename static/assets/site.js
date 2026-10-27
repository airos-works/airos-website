// Progressive enhancement: links, app panels and the complete archive work without JS.
// Application categories: each panel stays hidden until its tab is chosen. A
// link to a panel or to an app inside one (apps/#proton, apps/#wordcraft) opens it.
const appTabs = document.querySelector('[data-app-tabs]');
if (appTabs) {
  const tabs = [...appTabs.querySelectorAll('a[data-tab]')];
  const panels = tabs.map(tab => document.getElementById(tab.dataset.tab));
  appTabs.setAttribute('role', 'tablist');
  tabs.forEach((tab, i) => {
    tab.setAttribute('role', 'tab');
    tab.id = 'tab-' + tab.dataset.tab;
    tab.setAttribute('aria-controls', panels[i].id);
    panels[i].setAttribute('role', 'tabpanel');
    panels[i].setAttribute('aria-labelledby', tab.id);
  });
  const select = index => {
    tabs.forEach((tab, i) => {
      const selected = i === index;
      tab.classList.toggle('selected', selected);
      tab.setAttribute('aria-selected', selected);
      tab.tabIndex = selected || (index < 0 && i === 0) ? 0 : -1;
      panels[i].hidden = !selected;
    });
  };
  const openHash = () => {
    const target = location.hash && document.getElementById(decodeURIComponent(location.hash.slice(1)));
    const index = target ? panels.findIndex(panel => panel.contains(target)) : -1;
    if (index < 0) return false;
    select(index);
    target.scrollIntoView();
    return true;
  };
  if (!openHash()) select(-1);
  window.addEventListener('hashchange', openHash);
  tabs.forEach((tab, i) => tab.addEventListener('click', event => {
    event.preventDefault();
    select(i);
    history.replaceState(null, '', '#' + tab.dataset.tab);
  }));
  appTabs.addEventListener('keydown', event => {
    const current = tabs.indexOf(document.activeElement);
    if (current < 0) return;
    const next = {ArrowRight: current + 1, ArrowDown: current + 1, ArrowLeft: current - 1, ArrowUp: current - 1, Home: 0, End: tabs.length - 1}[event.key];
    if (next === undefined) return;
    event.preventDefault();
    const tab = tabs[(next + tabs.length) % tabs.length];
    tab.focus();
    tab.click();
  });
}
const search = document.querySelector('[data-changes]');
if (search) {
  const list = document.querySelector('.commit-list');
  const input = search.querySelector('input');
  const select = search.querySelector('select');
  const status = search.querySelector('[role=status]');
  const more = document.createElement('button');
  more.className = 'button load-more'; more.textContent = 'Show 100 more'; more.hidden = true;
  list.after(more);
  let commits, matches, limit = 100;
  const node = (tag, text, cls) => { const n = document.createElement(tag); n.textContent = text; if (cls) n.className = cls; return n; };
  function render() {
    list.replaceChildren();
    matches.slice(0, limit).forEach(c => {
      const article = node('article', '', 'commit');
      const time = node('time', c.date.slice(0,10)); time.dateTime = c.date;
      const div = node('div',''); const repo = node('span',c.repo,'commit-repo');
      const title = node('h2',''); const a = node('a',c.subject); a.href = c.url; title.append(a);
      div.append(repo,title); article.append(time,div,node('code',c.sha.slice(0,7))); list.append(article);
    });
    more.hidden = matches.length <= limit;
    status.textContent = `${matches.length.toLocaleString()} matching commits · showing ${Math.min(matches.length,limit).toLocaleString()}`;
  }
  function filter() {
    const q = input.value.trim().toLowerCase();
    matches = commits.filter(c => (!select.value || c.repo === select.value) && (!q || `${c.subject} ${c.repo} ${c.sha}`.toLowerCase().includes(q)));
    limit = 100; render();
  }
  fetch(search.dataset.changes).then(r => { if(!r.ok) throw new Error('Archive unavailable'); return r.json(); }).then(data => {
    commits=data; matches=data; search.hidden=false;
    input.addEventListener('input', filter); select.addEventListener('change', filter);
    more.addEventListener('click', () => {limit += 100; render();});
    render();
  }).catch(() => { more.remove(); });
}
// Rolling application releases replace versioned assets. Refresh their links on
// the downloads page so a newly published package does not leave stale buttons.
// If the public API is unavailable, the dated snapshot and release-page fallback
// remain usable. No token or authenticated request is sent from the browser.
document.querySelectorAll('.app-card[data-repo]').forEach(card => {
  fetch(`https://api.github.com/repos/airos-works/${encodeURIComponent(card.dataset.repo)}/releases/tags/latest`, {credentials:'omit'})
    .then(response => { if (!response.ok) throw new Error('Release lookup unavailable'); return response.json(); })
    .then(release => {
      if (release.draft || !Array.isArray(release.assets)) return;
      const assets = release.assets.filter(a => a.state === 'uploaded' && a.name.endsWith('.hpkg'));
      const replacements = [];
      for (const arch of ['x86_64','arm64']) {
        for (const asset of assets.filter(a => a.name.endsWith(arch+'.hpkg'))) {
          const a = document.createElement('a'); a.className = 'package-link';
          const target = new URL(asset.browser_download_url);
          if (target.origin !== 'https://github.com') continue;
          a.href = target.href;
          const label = document.createElement('span');
          label.textContent = (arch === 'x86_64' ? 'x86-64' : 'ARM64') + (asset.name.startsWith('summit_webkit') ? ' · WebKit engine' : '');
          const size = document.createElement('small');
          size.textContent = (asset.size >= 1048576 ? `${(asset.size/1048576).toFixed(1)} MB` : `${Math.round(asset.size/1024)} KB`) + ' ↓';
          a.append(label,size); replacements.push(a);
        }
      }
      if (!replacements.length) return;
      // A browser and engine must be published together for each Summit target.
      if (card.dataset.repo === 'summit' && ['x86_64', 'arm64'].some(arch => {
        const names = assets.filter(a => a.name.endsWith(arch+'.hpkg')).map(a => a.name);
        return names.length && (!names.some(n => n.startsWith('summit-')) || !names.some(n => n.startsWith('summit_webkit-')));
      })) return;
      const releaseURL = new URL(release.html_url);
      if (releaseURL.origin !== 'https://github.com') return;
      const meta = document.createElement('div'); meta.className = 'app-meta';
      const details = document.createElement('a'); details.href = releaseURL.href; details.textContent = 'Build details & checksums ↗';
      const date = document.createElement('span'); date.textContent = release.published_at.slice(0,10);
      meta.append(details, date);
      card.querySelector('.app-packages').replaceChildren(...replacements, meta);
    }).catch(() => {});
});

// Pick up image builds published since the scheduled snapshot. Immutable image
// URLs keep the static links usable if JavaScript or the public API is offline.
const imageCards = [...document.querySelectorAll('.image-card[data-target]')];
const imageLinks = [...document.querySelectorAll('a[data-image-link]')];
if (imageCards.length || imageLinks.length) {
  (async () => {
    const releases = [];
    for (let page = 1; ; page++) {
      const response = await fetch(`https://api.github.com/repos/airos-works/haiku/releases?per_page=100&page=${page}`, {credentials:'omit'});
      if (!response.ok) throw new Error('Image lookup unavailable');
      const batch = await response.json();
      if (!Array.isArray(batch)) throw new Error('Invalid image release list');
      releases.push(...batch);
      if (batch.length < 100) break;
    }
    // SD card boards get .img.xz images; UEFI targets get .iso.xz.
    const latest = target => {
      const release = releases.filter(r => !r.draft && r.tag_name.startsWith(`image-${target}-`))
        .sort((a,b) => b.published_at.localeCompare(a.published_at))[0];
      if (!release) return null;
      const filename = ['rpi4', 'cubie'].includes(target) ? `airos-${target}.img.xz` : `airos-${target}.iso.xz`;
      return {release, filename, assets: release.assets.filter(a => a.state === 'uploaded')};
    };
    for (const link of imageLinks) {
      const found = latest(link.dataset.imageLink);
      const image = found && found.assets.find(a => a.name === found.filename);
      if (image && new URL(image.browser_download_url).origin === 'https://github.com') link.href = image.browser_download_url;
    }
    for (const card of imageCards) {
      const target = card.dataset.target;
      const found = latest(target);
      if (!found) continue;
      const {release, filename, assets} = found;
      const image = assets.find(a => a.name === filename);
      const checksum = assets.find(a => a.name === filename+'.sha256');
      const manifest = assets.find(a => a.name === 'manifest.json');
      // Keep the known complete snapshot if a remote release is incomplete.
      if (!image || !checksum || !manifest) continue;
      const urls = [image.browser_download_url, checksum.browser_download_url, manifest.browser_download_url, release.html_url];
      if (!urls.every(u => new URL(u).origin === 'https://github.com')) continue;
      const anchor = (href, text, cls='') => {
        const a = document.createElement('a'); a.href=href; a.textContent=text; a.className=cls; return a;
      };
      const button = anchor(urls[0], 'Download image ↓', 'button primary');
      const meta = document.createElement('p'); meta.className='meta';
      meta.textContent = `${(image.size/1048576).toFixed(1)} MB compressed · ${release.published_at.slice(0,10)}`;
      const extras = document.createElement('div'); extras.className='asset-extras';
      extras.append(anchor(urls[1], 'SHA-256'), anchor(urls[2], 'Build manifest'), anchor(urls[3], 'Release notes ↗'));
      card.querySelector('.image-download').replaceChildren(button,meta,extras);
    }
  })().catch(() => {});
}
