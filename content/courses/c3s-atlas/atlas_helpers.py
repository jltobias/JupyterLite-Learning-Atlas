"""Small, browser-compatible teaching tools for JupyterLite-C3S-Atlas.

Author: JupyterLite-C3S-Atlas contributors (AI assisted); contact: repository issues.
Created/updated: 2026-11-15. Inputs: bundled reference data or labelled simulations.
Outputs: in-memory arrays, data frames, and figures. Python 3.11+; NumPy/pandas/Plotly.
Assumptions: regular latitude-longitude cells; no inferential significance testing.
Change log: 2026-11-15 - initial educational implementation.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from IPython.display import display

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
SYNTHETIC = 'SYNTHETIC teaching data — not C3S measurements'
COLORS = ['#0c8599', '#e67700', '#6842a6', '#c44536', '#52687b']


def show(fig: go.Figure) -> None:
    """Render Plotly in JupyterLite and static HTML books with text fallback.

    Atlas uses an isolated sandboxed frame, without a Plotly Lab extension. HTML uses
    Plotly's versioned CDN; no data are uploaded. A network is needed on first use.
    """
    fig.update_layout(template='plotly_white', font=dict(size=14),
                      margin=dict(l=65, r=45, t=90, b=65), height=470)
    # Atlas has only the Pyodide extension: isolate Plotly's loader and draw
    # scripts in an opaque-origin frame so the CDN is ready before newPlot.
    from html import escape
    document = fig.to_html(full_html=True, include_plotlyjs='cdn', config={'responsive': True})
    title = escape(fig.layout.title.text or 'Interactive teaching figure', quote=True)
    frame = (f'<iframe title="{title}" srcdoc="{escape(document, quote=True)}" '
             'sandbox="allow-scripts allow-downloads" style="width:100%;height:520px;border:0" loading="eager"></iframe>')
    display({'text/html': frame, 'text/plain': str(fig)}, raw=True)


def monthly_demo() -> pd.DataFrame:
    """Return a deterministic fictional regional record (1961–2020).

    A smooth warming component and seasonal cycles are invented for teaching.
    Precipitation and PET columns are mean daily amounts, not monthly totals.
    They are not a climate-model simulation or estimates of any real region.
    """
    dates = pd.date_range('1961-01-01', '2020-12-01', freq='MS')
    year = dates.year.to_numpy()
    month = dates.month.to_numpy()
    rng = np.random.default_rng(381)
    season = np.cos(2 * np.pi * (month - 7) / 12)
    t = 13 + 9 * season + 0.027 * (year - 1961) + rng.normal(0, 0.65, len(dates))
    r = np.maximum(0.08, 2.4 - 1.0 * season - 0.004 * (year - 1961) + rng.normal(0, 0.3, len(dates)))
    pet = np.maximum(0.05, 2.3 + 1.5 * season + 0.008 * (year - 1961))
    return pd.DataFrame(dict(date=dates, year=year, month=month, t=t,
                             r=r, pet=pet, days=dates.days_in_month.to_numpy()))


def anomalies(df: pd.DataFrame, column: str, baseline: tuple[int, int]) -> pd.Series:
    """Subtract a complete monthly baseline climatology without changing input.

    Raises ValueError for missing, duplicate, or nonfinite baseline months.
    Missing months outside the baseline remain missing and are never filled.
    """
    start, end = baseline
    if start > end:
        raise ValueError('Baseline start must precede its end.')
    base = df.loc[df.year.between(start, end)]
    expected = pd.MultiIndex.from_product([range(start, end + 1), range(1, 13)])
    keys = pd.MultiIndex.from_frame(base[['year', 'month']])
    if keys.has_duplicates or len(keys) != len(expected) or set(keys) != set(expected):
        raise ValueError('Baseline must contain exactly one row for every year/month.')
    if not np.isfinite(base[column].to_numpy(dtype=float)).all():
        raise ValueError('Baseline contains missing or nonfinite values.')
    normals = base.groupby('month')[column].mean()
    return df[column] - df.month.map(normals)


def regular_grid() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return a fictional 5° global warming-pattern field and cell centres.

    Coordinates are geographic degrees, with no duplicated cyclic longitude.
    Values are invented anomalies in °C for cartographic practice only.
    """
    lon = np.arange(-177.5, 180, 5)
    lat = np.arange(-87.5, 90, 5)
    xx, yy = np.meshgrid(lon, lat)
    field = 1.4 + 1.7 * np.sin(np.deg2rad(yy)) ** 2 + 0.4 * np.cos(np.deg2rad(xx)) * np.cos(np.deg2rad(yy))
    return lon, lat, field


def area_mean(values: np.ndarray, lat: np.ndarray) -> float:
    """Area-weight a complete regular lat/lon grid, excluding missing cells.

    Cos(latitude) is proportional to cell area for equal angular cell widths.
    Do not use this on curvilinear grids, unequal-width cells, or clipped polygons.
    """
    values = np.asarray(values, dtype=float)
    lat = np.asarray(lat, dtype=float)
    if values.ndim != 2 or values.shape[0] != len(lat) or len(lat) < 2:
        raise ValueError('Expected a latitude × longitude array with at least two rows.')
    if not np.isfinite(lat).all() or np.any(np.abs(lat) >= 90):
        raise ValueError('Latitude centres must be finite and strictly within the poles.')
    if not (np.all(np.diff(lat) > 0) or np.all(np.diff(lat) < 0)):
        raise ValueError('Latitude centres must be strictly monotonic.')
    if not np.allclose(np.diff(lat), np.diff(lat)[0]):
        raise ValueError('Cosine weighting here requires equal latitude spacing.')
    weights = np.broadcast_to(np.cos(np.deg2rad(lat))[:, None], values.shape)
    valid = np.isfinite(values)
    if not valid.any():
        raise ValueError('No valid grid cells; a missing mean is not zero.')
    return float(np.sum(values[valid] * weights[valid]) / weights[valid].sum())


def coastlines() -> list[np.ndarray]:
    """Load public-domain Natural Earth coastline lines in longitude/latitude."""
    data = json.loads((DATA / 'reference/ne_110m_coastline.geojson').read_text(encoding='utf-8'))
    result = []
    for feature in data['features']:
        geom = feature['geometry']
        lines = [geom['coordinates']] if geom['type'] == 'LineString' else geom['coordinates']
        result.extend(np.asarray(line, dtype=float) for line in lines)
    return result


def map_figure(lon: np.ndarray, lat: np.ndarray, field: np.ndarray, title: str) -> go.Figure:
    """Plot a geographic plate carrée heatmap with bundled coastlines.

    Longitude/latitude are geographic degrees. Shapes/areas are distorted toward
    the poles. Hover reports values; no external map tiles or API keys are used.
    """
    fig = go.Figure(go.Heatmap(x=lon, y=lat, z=field, colorscale='Cividis',
                              colorbar=dict(title='Δ °C'),
                              hovertemplate='lon %{x}°<br>lat %{y}°<br>Δ %{z:.2f} °C<extra></extra>'))
    x, y = [], []
    for line in coastlines():
        # Split antimeridian jumps to avoid drawing across the map.
        for segment in np.split(line, np.where(np.abs(np.diff(line[:, 0])) > 180)[0] + 1):
            x.extend(segment[:, 0].tolist() + [None])
            y.extend(segment[:, 1].tolist() + [None])
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color='#172d40', width=0.7),
                             hoverinfo='skip', showlegend=False))
    fig.update_layout(title=title, xaxis_title='Longitude (°)', yaxis_title='Latitude (°)',
                      xaxis=dict(range=[-180, 180]), yaxis=dict(range=[-90, 90]),
                      annotations=[dict(text='Made with Natural Earth · Plate carrée', x=0, y=-0.18,
                                        xref='paper', yref='paper', showarrow=False)])
    return fig


def globe_figure() -> go.Figure:
    """Map a fictional scalar field to a unit sphere; colour is not elevation."""
    lon, lat, field = regular_grid()
    # Include seam and poles for a closed display surface; analytical grid stays unchanged.
    lo = np.linspace(-180, 180, 73)
    la = np.linspace(-90, 90, 37)
    ll, pp = np.meshgrid(np.deg2rad(lo), np.deg2rad(la))
    z = np.sin(pp)
    values = 1.4 + 1.7 * z**2 + 0.4 * np.cos(ll) * np.cos(pp)
    fig = go.Figure(go.Surface(x=np.cos(pp)*np.cos(ll), y=np.cos(pp)*np.sin(ll), z=z,
                               surfacecolor=values, colorscale='Cividis', cmin=1, cmax=3.2,
                               colorbar=dict(title='Δ °C'),
                               customdata=np.dstack((np.rad2deg(ll), np.rad2deg(pp), values)),
                               hovertemplate='lon %{customdata[0]:.1f}°<br>lat %{customdata[1]:.1f}°<br>Δ %{customdata[2]:.2f} °C<extra></extra>'))
    x, y, zz = [], [], []
    for line in coastlines():
        a, b = np.deg2rad(line[:, 0]), np.deg2rad(line[:, 1])
        x.extend((1.006*np.cos(b)*np.cos(a)).tolist()+[None])
        y.extend((1.006*np.cos(b)*np.sin(a)).tolist()+[None])
        zz.extend((1.006*np.sin(b)).tolist()+[None])
    fig.add_trace(go.Scatter3d(x=x, y=y, z=zz, mode='lines', line=dict(color='#142537', width=2),
                               hoverinfo='skip', showlegend=False))
    hidden = dict(visible=False)
    fig.update_layout(title='A climate field on a globe · SYNTHETIC',
                      scene=dict(xaxis=hidden, yaxis=hidden, zaxis=hidden, aspectmode='data'),
                      annotations=[dict(text='Unit sphere; colour = anomaly, not height · Natural Earth coastlines',
                                        x=0, y=-0.1, xref='paper', yref='paper', showarrow=False)])
    return fig


def warming_levels() -> pd.DataFrame:
    """Parse the real upstream two-header CMIP6 table, preserving missing tokens.

    No dates are invented for NA or 9999. Source semantics must be checked before
    making claims about why a window is absent. A valid cell is an inclusive 20-year window.
    """
    with (DATA / 'reference/CMIP6_WarmingLevels.csv').open(newline='') as f:
        rows = list(csv.reader(f))
    out = []
    for row in rows[2:]:
        if len(row) != len(rows[0]):
            raise ValueError('Unexpected warming-level table width.')
        for level, scenario, raw in zip(rows[0][1:], rows[1][1:], row[1:]):
            match = re.fullmatch(r'(\d{4})-(\d{4})', raw)
            start, end = (map(int, match.groups()) if match else (np.nan, np.nan))
            if match and end - start != 19:
                raise ValueError('Expected an inclusive 20-year GWL window.')
            if not match and raw not in {'NA', '9999'}:
                raise ValueError(f'Unexpected source token {raw!r}')
            out.append(dict(member=row[0], scenario=scenario, level=float(level),
                            raw=raw, start=start, end=end,
                            midpoint=(start + end) / 2, status='window' if match else raw))
    return pd.DataFrame(out)


def load_monthly_csv(path: str | Path, value_column: str = 'value') -> pd.DataFrame:
    """Validate a standardized single-series CSV; never guess units or aggregation.

    Required columns: date (ISO month start), value (numeric; blanks allowed).
    Exactly one series with unique, ascending, consecutive months is required.
    Metadata live in the separate source JSON described in the data guide.
    """
    df = pd.read_csv(path)
    if not {'date', value_column}.issubset(df):
        raise ValueError('CSV needs date and the selected value column.')
    df['date'] = pd.to_datetime(df.date, errors='raise')
    if df.empty or df.date.isna().any() or df.date.duplicated().any():
        raise ValueError('Dates must be present and unique.')
    if not df.date.is_monotonic_increasing or not df.date.dt.is_month_start.all():
        raise ValueError('Use ascending ISO month-start dates.')
    expected = pd.date_range(df.date.iloc[0], df.date.iloc[-1], freq='MS')
    if not df.date.reset_index(drop=True).equals(pd.Series(expected)):
        raise ValueError('Missing month: insert an explicit blank value; do not silently compress time.')
    df[value_column] = pd.to_numeric(df[value_column], errors='raise')
    if np.isinf(df[value_column]).any():
        raise ValueError('Infinite values are not valid; use blank for missing.')
    return df.assign(year=df.date.dt.year, month=df.date.dt.month,
                     days=df.date.dt.days_in_month)
