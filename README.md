# Cockpit Pages

Public product guide for Cockpit, a macOS PR operations workspace.

The application and worker source remain in a separate private repository. This
repository contains only the static public guide and its deployment workflow.

## Local preview

```bash
python3 -m http.server 8080 --directory site
```

Open <http://127.0.0.1:8080/>.

## Deployment

Pushes to `main` that change `site/**` deploy through GitHub Actions. The
workflow uploads only `site/` and rejects symbolic links, common secret formats,
local user paths, and internal repository identifiers before deployment.
