# Variable and feature coverage

The CDS v2.5 documentation identifies 35 base variables/indices. Availability varies
by dataset; bias-adjusted variants and application-only products add other choices.
This is a learning index, not a claim that every product has been downloaded or
that every official algorithm is reproduced. Check the current
[CDS catalogue](https://doi.org/10.24381/cds.h35hb680) for definitions and availability.

| Climate theme | Atlas variable codes | Learning route |
| --- | --- | --- |
| Heat and cold | t, tn, tx, dtr, txx, tx35, tx40, tr, cd, tnn, fd, hd | [Means, extremes, thresholds, and degree-days](05-heat-and-cold.ipynb) |
| Wet and dry | r, r01, sdii, rx1day, rx5day, r10, r20, huss, evspsbl, mrro | [Rainfall and the water cycle](06-rain-and-water.ipynb) |
| Drought | mrsos, cdd, spi6, spei6, pet | [Accumulation and drought definitions](07-drought.ipynb) |
| Wind and radiation | sfcwind, clt, rsds, rlds | [Energy context and nonlinear averaging](08-wind-and-radiation.ipynb) |
| Snow and ice | prsn, siconc | [Water equivalent, concentration, area, and extent](09-snow-and-ice.ipynb) |
| Ocean | sst | [Ocean and circulation patterns](10-ocean-and-circulation.ipynb) |
| Circulation | psl | [Ocean and circulation patterns](10-ocean-and-circulation.ipynb) |

## Application features

| Feature | Chapter |
| --- | --- |
| Information panel, source families, version/units | 1–2 |
| Values, absolute changes, descriptive trends | 3 |
| Annual cycle, climate/seasonal stripes, calendar-aware seasons | 4 |
| Scenarios and ensemble summaries | 11 |
| Global warming levels | 12 (authentic auxiliary table) |
| Uncertainty legends and bias adjustment | 13 (concepts; official methods linked) |
| Predefined/custom regions and weighting | 14 |
| Interactive geographical maps | 15–16 |
| Independent 3D educational scenes | 17 |
| Monitoring and urban context | 18 (concepts; official product linked) |
| Data exports and communication | 19–20 |

For production SPI/SPEI, bias adjustment, significance/robustness hatching, regridding,
and urban diagnostics, use the linked
[C3S Atlas User Tools](https://github.com/ecmwf-projects/c3s-atlas). These lightweight
browser lessons explain the ideas and demonstrate selected calculations.
