# Publish the website and connect airos.works

The website lives in [jmgasper/airos-website](https://github.com/jmgasper/airos-website).
GitHub Actions builds and validates it, then publishes the generated `dist/`
directory to GitHub Pages. The intended address is `https://airos.works/`, with
`www.airos.works` redirecting there.

## Current configuration

Checked on 18 October 2026 using the GitHub Pages API and public DNS:

| Setting | Current value |
|---|---|
| Pages publishing source | GitHub Actions |
| Pages address | `https://jmgasper.github.io/airos-website/` |
| Pages custom domain | Not set |
| Domain nameservers | `dns1.registrar-servers.com`, `dns2.registrar-servers.com` |
| `airos.works` A record | `192.64.119.125` (Namecheap forwarding) |
| `www.airos.works` CNAME | `parkingpage.namecheap.com` |

The domain is still pointed at Namecheap. The instructions below require access
to the `jmgasper` GitHub account and the Namecheap account managing `airos.works`.

## 1. Publish the committed website

From this repository, push the completed commit when ready to deploy:

```sh
git push origin main
```

Open [the deployment workflow](https://github.com/jmgasper/airos-website/actions/workflows/pages.yml)
and wait for both `build` and `deploy` to succeed. A local commit alone does not
publish the site. Failed builds leave the previous deployment in place.

The workflow refreshes public GitHub histories and downloads, runs the static
builder and link validator, and uploads the site. It reads other repositories;
scheduled/manual runs can also save a refreshed snapshot to this repository.

## 2. Verify domain ownership in GitHub

Recommended: open your **account** [Settings → Pages](https://github.com/settings/pages),
choose **Add a domain**, and enter `airos.works`. Add the TXT record GitHub shows
in Namecheap's **Domain List → Manage → Advanced DNS → Host Records**.

The TXT host is normally `_github-pages-challenge-jmgasper`; copy the exact host
and verification value from GitHub. Namecheap appends `.airos.works` to the host.
Return to GitHub and select **Verify** once the record resolves. Keep the TXT
record afterward. See [GitHub's domain verification instructions](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages).

## 3. Assign the domain to this repository

Open the repository's [Settings → Pages](https://github.com/jmgasper/airos-website/settings/pages).
Keep **Source: GitHub Actions**. Under **Custom domain**, enter `airos.works`
without a scheme or path, then **Save**. Do this before changing the website DNS.

This Actions-based site needs no `CNAME` file in Git. GitHub stores the domain
in Pages settings. See [GitHub's custom-domain setup](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site).

## 4. Replace the Namecheap parking records

Open **Domain List → Manage** next to `airos.works`, then **Advanced DNS → Host
Records**. Keep the existing nameservers, email records and verification TXT
records. Replace only the website records:

| Type | Host | Value | TTL |
|---|---|---|---|
| A Record | `@` | `185.199.108.153` | Automatic |
| A Record | `@` | `185.199.109.153` | Automatic |
| A Record | `@` | `185.199.110.153` | Automatic |
| A Record | `@` | `185.199.111.153` | Automatic |
| CNAME Record | `www` | `jmgasper.github.io` | Automatic |

Remove the old `@` URL Redirect Record and any parking A record pointing to
`192.64.119.125`. Replace the `www` CNAME pointing to `parkingpage.namecheap.com`.
The CNAME value is a hostname: do not append `/airos-website` or `https://`.

A Namecheap URL redirect creates an additional A record that may be hidden
from Host Records. Delete the redirect itself, including any entry under
**Domain → Redirect Domain**, so it stops supplying the forwarding address.
Use GitHub's automatic `www` redirect once the domain is connected.
See [Namecheap's GitHub Pages setup](https://www.namecheap.com/support/knowledgebase/article.aspx/9645/2208/how-do-i-link-my-domain-to-github-pages/)
and [its URL redirect behavior](https://www.namecheap.com/support/knowledgebase/article.aspx/385/2237/how-to-set-up-a-url-redirect-for-a-domain/).

Optionally add four **AAAA Records**, each with host `@`, for IPv6:

```text
2606:50c0:8000::153
2606:50c0:8001::153
2606:50c0:8002::153
2606:50c0:8003::153
```

These are GitHub's [published Pages DNS addresses](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site#dns-records-for-your-custom-domain).

## 5. Rebuild for the domain and enable HTTPS

After saving the custom domain, open the deployment workflow and choose
**Run workflow → main**. Alternatively:

```sh
gh workflow run pages.yml --repo jmgasper/airos-website --ref main
```

The existing `actions/configure-pages` step reads the configured domain. The
builder receives the new `BASE_PATH` and `SITE_URL`, switching navigation,
images and canonical URLs from `/airos-website/` to the domain root. No source
edits are needed for this switch.

Allow up to 24 hours for DNS propagation and the HTTPS option to become
available. Once the repository's Pages settings show a successful DNS check
and a certificate, enable **Enforce HTTPS**. GitHub obtains and manages the
certificate; no separate certificate purchase is needed. See [GitHub's HTTPS
guide](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https).

## 6. Confirm the result

Check DNS from a terminal with `dig` installed:

```sh
dig +short airos.works A
dig +short airos.works AAAA
dig +short www.airos.works CNAME
dig +short _github-pages-challenge-jmgasper.airos.works TXT
```

The A response should contain the four GitHub addresses. AAAA should be empty
if IPv6 was omitted, or contain the four IPv6 addresses above. The `www` CNAME
should be `jmgasper.github.io.`. The TXT query should return the verification
value if step 2 was completed.

Then check HTTP and TLS without bypassing certificate validation:

```sh
curl -I https://airos.works/
curl -I https://airos.works/apps/
curl -I http://airos.works/
curl -I https://www.airos.works/
```

Expect HTTP 200 for the first two requests, an HTTPS redirect for plain HTTP,
and a redirect from `www` to `https://airos.works/`. Open the site in a browser
and check the Apps, Summit and Downloads pages, including their screenshots.

If the parking page persists, recheck the redirect record and cached DNS. If
the domain loads but links or images still use `/airos-website/`, run a fresh
deployment after saving the custom domain. If a build fails, inspect its failed
step in Actions; DNS changes do not fix a build failure. A successful Pages
deployment alone does not establish that domain routing and HTTPS are ready.
