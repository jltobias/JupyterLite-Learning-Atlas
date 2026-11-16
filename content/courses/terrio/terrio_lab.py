"""Small, transparent utilities shared by the original teaching notebooks."""
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import terrio

DATA = Path("data")
OUTPUT = Path("outputs")
OUTPUT.mkdir(exist_ok=True)
CRS = "EPSG:32613"
TRANSFORM = (500000.0, 30.0, 0.0, 4400000.0, 0.0, -30.0)
CREDIT = "Synthetic teaching data · JupyterLite-terrio contributors"


def terrain(n=96):
    """Deterministic elevation, metres; illustrative, not a surveyed landscape."""
    y, x = np.mgrid[-1:1:complex(n), -1:1:complex(n)]
    z = 1200 + 600*np.exp(-4*(x*x+y*y)) + 110*np.sin(5*x)*np.cos(3*y) + 90*x
    return z.astype("float32")


def raster(z=None):
    return terrio.Raster.from_array(terrain() if z is None else np.asarray(z, dtype="float32"),
                                   TRANSFORM, crs=CRS, nodata=-9999)


def countries():
    return json.loads((DATA / "countries.geojson").read_text(encoding="utf-8"))


def rings(collection):
    """Yield exterior rings; teaching outlines only (holes are not filled)."""
    for feature in collection["features"]:
        g = feature["geometry"]
        if g is None:
            continue
        polygons = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for polygon in polygons:
            yield np.asarray(polygon[0], dtype=float)


def map_outlines(collection=None, title="Natural Earth country outlines"):
    fig, ax = plt.subplots(figsize=(10, 4.8))
    for ring in rings(countries() if collection is None else collection):
        ax.plot(ring[:, 0], ring[:, 1], color="#007f83", linewidth=.6)
    ax.set(xlim=(-180, 180), ylim=(-90, 90), xlabel="Longitude (degrees)", ylabel="Latitude (degrees)", title=title)
    ax.grid(alpha=.2)
    fig.text(.12, .01, "Made with Natural Earth · Patterson, Kelso & contributors · public domain", fontsize=8)
    fig.tight_layout(rect=(0, .03, 1, 1))
    return fig, ax


def image_grid(arrays, titles, cmaps=None, units="m"):
    fig, axes = plt.subplots(1, len(arrays), figsize=(5*len(arrays), 4), squeeze=False)
    for i, (array, title) in enumerate(zip(arrays, titles)):
        a = np.asarray(array, dtype=float)
        a = np.ma.masked_where(~np.isfinite(a) | (a == -9999), a)
        im = axes[0, i].imshow(a, cmap=(cmaps or ["terrain"]*len(arrays))[i])
        axes[0, i].set(title=title, xlabel="Column", ylabel="Row")
        fig.colorbar(im, ax=axes[0, i], shrink=.75, label=units)
    fig.text(.05, .01, CREDIT, fontsize=8)
    fig.tight_layout(rect=(0, .03, 1, 1))
    return fig


def interactive(fig):
    """An isolated frame loads Plotly before drawing in Book and Lite outputs."""
    import html
    from IPython.display import HTML, display
    fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=65, b=35))
    document = fig.to_html(full_html=True, include_plotlyjs="cdn", config={"responsive": True})
    title = html.escape(fig.layout.title.text or "Interactive data visualization", quote=True)
    display(HTML(f'<iframe title="{title}" srcdoc="{html.escape(document, quote=True)}" '
                 'sandbox="allow-scripts" style="width:100%;height:600px;border:0" loading="eager"></iframe>'))


def surface(z=None, exaggeration=1):
    import plotly.graph_objects as go
    z = terrain() if z is None else z
    xs = TRANSFORM[0] + (np.arange(z.shape[1])+.5)*30
    ys = TRANSFORM[3] - (np.arange(z.shape[0])+.5)*30
    fig = go.Figure(go.Surface(x=xs, y=ys, z=z, colorscale="Viridis", colorbar=dict(title="m")))
    fig.update_layout(title=f"Synthetic terrain · {exaggeration:g}× vertical exaggeration",
                      scene=dict(xaxis_title="Easting (m)", yaxis_title="Northing (m)", zaxis_title="Elevation (m)",
                                 camera=dict(eye=dict(x=1.8, y=1.8, z=1.5)),
                                 aspectmode="manual", aspectratio=dict(x=1, y=1, z=float(np.ptp(z))/(30*z.shape[0])*exaggeration)))
    return fig


def globe():
    """Convert real outline coordinates to a unit sphere; no external basemap."""
    import plotly.graph_objects as go
    lon = np.linspace(-np.pi, np.pi, 80)
    lat = np.linspace(-np.pi/2, np.pi/2, 40)
    lo, la = np.meshgrid(lon, lat)
    fig = go.Figure(go.Surface(x=np.cos(la)*np.cos(lo), y=np.cos(la)*np.sin(lo), z=np.sin(la),
                              colorscale=[[0, "#112b45"], [1, "#112b45"]], showscale=False, hoverinfo="skip"))
    for ring in rings(countries()):
        lo, la = np.radians(ring[:, 0]), np.radians(ring[:, 1])
        fig.add_trace(go.Scatter3d(x=1.005*np.cos(la)*np.cos(lo), y=1.005*np.cos(la)*np.sin(lo),
                                   z=1.005*np.sin(la), mode="lines", line=dict(color="#40ded0", width=2),
                                   showlegend=False, hoverinfo="skip"))
    fig.update_layout(title="A sphere of country outlines · Made with Natural Earth",
                      scene=dict(aspectmode="data", xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)))
    return fig
