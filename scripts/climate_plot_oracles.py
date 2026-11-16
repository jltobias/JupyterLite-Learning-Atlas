"""Independent small-grid oracles for the *rendered* C3S climate traces."""
from math import cos, sin, radians
import numpy as np


def assert_climate_plot(traces,kind):
    expected_type='surface' if kind=='globe' else 'heatmap'
    assert sorted(t['type'] for t in traces)==sorted([expected_type,'scatter3d' if kind=='globe' else 'scatter']),'Rendered climate trace types changed'
    climate=[t for t in traces if t['type']==expected_type]
    assert len(climate)==1,'Expected one rendered climate '+expected_type+' trace'
    trace=climate[0]
    assert trace.get('visible',True) is True,'Climate trace must be visibly rendered'
    def same(actual,expected):
        a=np.asarray(actual,dtype=float);b=np.asarray(expected,dtype=float)
        assert a.shape==b.shape,'Rendered climate coordinate/value shape changed'
        assert np.array_equal(np.isnan(a),np.isnan(b)),'Rendered climate missing mask changed'
        np.testing.assert_allclose(a,b,rtol=0,atol=1e-10,equal_nan=True)
    def value(lon,lat):return 1.4+1.7*sin(radians(lat))**2+.4*cos(radians(lon))*cos(radians(lat))
    if kind=='globe':
        lon=[-180+5*i for i in range(73)];lat=[-90+5*i for i in range(37)]
        same(trace['x'],[[cos(radians(la))*cos(radians(lo)) for lo in lon] for la in lat])
        same(trace['y'],[[cos(radians(la))*sin(radians(lo)) for lo in lon] for la in lat])
        same(trace['z'],[[sin(radians(la)) for _ in lon] for la in lat])
        same(trace['surfacecolor'],[[value(lo,la) for lo in lon] for la in lat])
    else:
        assert kind in {'regional','global-2d'},kind
        lon=[-177.5+5*i for i in range(72)];lat=[-87.5+5*i for i in range(36)]
        same(trace['x'],lon);same(trace['y'],lat)
        same(trace['z'],[[value(lo,la) if kind=='global-2d' or (-10<=lo<=40 and 30<=la<=70) else None for lo in lon] for la in lat])
    return {'kind':kind,'coordinate_values_and_missing_mask':'passed'}
