# Cockpit Pages

Public product guide and user manual for Cockpit, a macOS development operations workspace.

The application and worker source remain in a separate private repository. This
repository contains only the static public guide and its deployment workflow.

## Local preview

```bash
python3 -m http.server 8080 --directory site
```

Open <http://127.0.0.1:8080/>.

- Product overview: `/`
- App and worker manual: `/guide/`

## Deployment

Pushes to `main` that change `site/**` deploy through GitHub Actions. The
workflow uploads only `site/` and rejects symbolic links, common secret formats,
local user paths, and internal repository identifiers before deployment.

## Validation

```bash
python3 scripts/check_site.py
git diff --check
```

The static site has no build dependencies. Check both pages at desktop and
320–390 px widths, including image tabs, keyboard navigation, the mobile menu,
guide anchors and enlarged images. Automated checks cannot inspect image pixels
for sensitive information; review every image before publishing.

## Keeping the guide current

- Current documentation and UI basis: **Cockpit 1.34.22**, reviewed **2026-09-06**.
- Update recent changes, setup requirements, automation defaults and permission
  limits against the shipped application. Do not describe planned behavior as live.
- Update the version/date in both pages and `site/assets/screens/manifest.json`.
- Bump the same asset query revision in both pages when public assets change.
- The six PNGs are unmodified production SwiftUI Views rendered in isolated test
  windows with fictional fixture data, not screenshots of an installed account.
  PRs, ticket keys, quotas and successful jobs are illustrative, not real results.
- Regenerate images from the matching app version with isolated settings, no real
  credentials, no network and no worker or child-process execution. Do not export
  private source, raw captures containing real data, configuration or logs here.
- Keep captions, alternative text, pixel dimensions and SHA-256 manifest entries
  in sync. Preserve the visible distinction between real UI and example data.
