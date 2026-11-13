import inspect, sys
DATASETS = {
    "Meuse": {"format": "CSV/vector", "source": "https://github.com/Nowosad/spData", "use": "Exploratory spatial statistics.", "jupyterlite": "Use a small CSV or synthetic sample."},
    "SIDS": {"format": "GeoPackage", "source": "https://r-spatial.github.io/spdep/articles/sids.html", "use": "County attributes and zonal summaries.", "jupyterlite": "Use GeoJSON/CSV derivatives; GeoPackage is native-only."},
    "DEM": {"format": "GeoTIFF", "source": "https://www.usgs.gov/3d-elevation-program", "use": "Terrain and hydrology.", "jupyterlite": "Use small arrays for concepts; raster execution is native-only."},
    "LiDAR": {"format": "LAS/LAZ", "source": "https://opentopography.org/", "use": "Point clouds and surface models.", "jupyterlite": "Use metadata; LAS/LAZ execution is native-only."},
    "Hydrography": {"format": "vector", "source": "https://www.usgs.gov/national-hydrography", "use": "Reference streams and drainage.", "jupyterlite": "Use hosted GeoJSON; native vector processing is recommended."},
}
def is_jupyterlite(): return "pyodide" in sys.modules
def whitebox_class():
    from whitebox.whitebox_tools import WhiteboxTools
    return WhiteboxTools
def api_search(keywords=(), limit=40):
    cls = whitebox_class(); words = [w.lower() for w in keywords]; rows = []
    for name, fn in inspect.getmembers(cls, inspect.isfunction):
        if name.startswith('_'): continue
        doc = inspect.getdoc(fn) or ''
        if not words or any(w in (name + ' ' + doc).lower() for w in words):
            try: signature = str(inspect.signature(fn))
            except Exception: signature = '(...)'
            rows.append((name, signature, doc.splitlines()[0] if doc else ''))
    return rows[:limit]
def show_tool(name):
    cls = whitebox_class(); fn = getattr(cls, name, None)
    if fn is None: print(f"{name}: wrapper method not found in this installed version."); return None
    print(f"{name}{inspect.signature(fn)}"); print(inspect.getdoc(fn) or "No docstring."); return fn
def show_dataset(name):
    d = DATASETS[name]; print(f"{name}: {d['format']}\nSource: {d['source']}\nUse: {d['use']}\nJupyterLite: {d['jupyterlite']}"); return d
def native_message(): print("JupyterLite detected: native execution skipped." if is_jupyterlite() else "Native Python kernel detected: native execution available.")

