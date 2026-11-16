# Sources, attribution, and reuse

This is an independent educational project by the JupyterLite-C3S-Atlas contributors.
It is not an official Copernicus, ECMWF, CSIC, Predictia, IPCC, or Jupyter publication.
The lessons and illustrations are newly created for this repository. They do not
reproduce the source guides, screenshots, logos, or videos. Source media are linked
at their original publishers.

## Climate sources

- **Copernicus Climate Change Service (C3S), implemented by ECMWF on behalf of the
  European Union:** [Copernicus Interactive Climate Atlas](https://atlas.climate.copernicus.eu/).
- **C3S/ECMWF:** [Gridded dataset underpinning the Copernicus Interactive Climate
  Atlas](https://doi.org/10.24381/cds.h35hb680). The
  [CDS catalogue](https://cds.climate.copernicus.eu/datasets/multi-origin-c3s-atlas?tab=overview)
  and its [machine-readable metadata](https://cds.climate.copernicus.eu/api/catalogue/v1/collections/multi-origin-c3s-atlas)
  identify **CC BY 4.0**. Consult the [dataset licence](https://cds.climate.copernicus.eu/licences/cc-by)
  and [full terms](https://creativecommons.org/licenses/by/4.0/legalcode) when obtaining a new release.
- **CSIC and Predictia:** [Atlas user guide](https://confluence.ecmwf.int/spaces/CKB/pages/394237545/Copernicus+Interactive+Climate+Atlas+User+Guide)
  and [C3S Atlas User Tools](https://github.com/ecmwf-projects/c3s-atlas).
  The upstream repository carries **Copyright 2023, European Union** and the
  **Apache License 2.0**. Its code is linked, not copied into this project's lesson implementation.
- **Gutiérrez, José Manuel; San Martín, Daniel; Horányi, András; Brookshaw, Anca;
  Buontempo, Carlo; Díez-Sierra, Javier; Goddard, Christopher; and Tuni, Max (2024).**
  *The Copernicus Interactive Climate Atlas: a tool to explore regional climate
  change.* ECMWF Newsletter 181. [doi:10.21957/ah52ufc369](https://doi.org/10.21957/ah52ufc369).
- **Iturbide, M., et al. (2020).** *An update of IPCC climate reference regions for
  subcontinental analysis of climate model data: definition and aggregated datasets.*
  Earth System Science Data 12, 2959–2970.
  [doi:10.5194/essd-12-2959-2020](https://doi.org/10.5194/essd-12-2959-2020).
  Credit this work when using its reference regions. Our rectangular demonstration
  masks are not IPCC reference-region boundaries.

## What to attach to a real-data result

Include the dataset title and DOI, provider, access date, version, original variable,
units, source model/member or reanalysis, scenario, region, calendar, reference
period, and all transformations. Preserve source-file global attributes and their
references. Include underlying dataset/model citations supplied by the downloaded
product; a citation to the Atlas alone does not replace them.

Suggested acknowledgement for a modified CDS Atlas product:

> Contains modified Copernicus Climate Change Service information, accessed [date],
> from the Gridded dataset underpinning the Copernicus Interactive Climate Atlas,
> doi:10.24381/cds.h35hb680, [version], licensed under CC BY 4.0. Processing:
> [subset, aggregation, reference period, and other changes].

This text is a reusable acknowledgement template; complete the brackets for the
actual product. Do not place it on a synthetic illustration as if the illustration
contained Copernicus measurements. Do not imply endorsement by data providers.

## Bundled material

See the machine-readable data manifest and data README for file-level provenance,
checksums, licences, and transformations. Teaching simulations are original and are
explicitly labelled **synthetic**, including in chart titles. They are not measurements,
forecasts, official Atlas products, or a validation of the underlying climate models.

The splash artwork was generated for this repository with OpenAI's built-in image
generation tool on 2026-11-15. It is an illustration, not a quantitative climate map.
The prompt is recorded in `assets/PROVENANCE.md`. No third-party image was supplied.

Jupyter, JupyterLite, Pyodide, Jupyter Book, NumPy, pandas, Matplotlib, and Plotly
are projects of their respective contributors. Their distributions retain their own
licences. The project's licence does not relicense third-party data, software, linked
media, trademarks, or source publications.
