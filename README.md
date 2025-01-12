
- `out/` contains the rendered static files
- `web/` contains the source files which includes jinja templates and static files which are copied to `out/`
- `generator.py` is a simple script which recursively finds templates in `web/`, renders them, and outputs the contents to `out/`. It's also responsible for copying the static files from `web/` to `out/`.

Anything within `out/` will be deleted when `generate.py` runs.

The idea is to point Cloudflare pages or some other static pages site to the `out/` directory.