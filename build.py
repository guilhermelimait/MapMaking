#!/usr/bin/env python3
"""Build index.html: inlines MapLibre GL JS and the home-screen icon into src/index.src.html.

Usage:  python3 build.py
Needs npm on PATH the first time (downloads maplibre-gl into vendor/).
"""
import base64, pathlib, subprocess, tarfile, io

ROOT = pathlib.Path(__file__).resolve().parent
MAPLIBRE = "maplibre-gl@4.7.1"
VENDOR = ROOT / "vendor" / "maplibre-gl"

def ensure_maplibre():
    if (VENDOR / "maplibre-gl.js").exists():
        return
    VENDOR.mkdir(parents=True, exist_ok=True)
    tgz = subprocess.run(["npm", "pack", MAPLIBRE, "--silent"], cwd=VENDOR, check=True,
                         capture_output=True, text=True, shell=(subprocess.os.name == "nt")).stdout.strip().splitlines()[-1]
    with tarfile.open(VENDOR / tgz) as t:
        for name, out in [("package/dist/maplibre-gl.js", "maplibre-gl.js"),
                          ("package/dist/maplibre-gl.css", "maplibre-gl.css"),
                          ("package/LICENSE.txt", "LICENSE.txt")]:
            (VENDOR / out).write_bytes(t.extractfile(name).read())
    (VENDOR / tgz).unlink()

def main():
    ensure_maplibre()
    src = (ROOT / "src" / "index.src.html").read_text(encoding="utf-8")
    js = (VENDOR / "maplibre-gl.js").read_text(encoding="utf-8")
    css = (VENDOR / "maplibre-gl.css").read_text(encoding="utf-8")
    assert "</script" not in js
    icon = "data:image/png;base64," + base64.b64encode((ROOT / "src" / "icon-180.png").read_bytes()).decode()
    out = (src.replace("<!--MAPLIBRE_CSS-->", "<style>/* MapLibre GL JS 4.7.1, BSD-3-Clause */\n" + css + "\n</style>")
              .replace("<!--MAPLIBRE_JS-->", "<script>/* MapLibre GL JS 4.7.1 | BSD-3-Clause | github.com/maplibre/maplibre-gl-js */\n" + js + "\n</script>")
              .replace("<!--TOUCH_ICON-->", icon))
    (ROOT / "index.html").write_text(out, encoding="utf-8")
    print(f"index.html written ({len(out)//1024} KB)")

if __name__ == "__main__":
    main()
