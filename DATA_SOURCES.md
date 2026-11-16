# Data status and provenance

The expanded Atlas includes original synthetic companions **and** permitted source-course inputs. The imported collection contains real population excerpts, public-domain Landsat/Census observations, open Earth-observation derivatives, historical teaching data, synthetic fixtures and factual metadata. Each course identifies its own data/runtime scope. There are no newly acquired patient records, controlled datasets or model weights. Ordinary generation/build does not refresh upstream data or query providers.

| Current material | Provenance and scope |
|---|---|
| Public project catalog | 39 core JupyterLite repositories and 7 related/PHI projects; 46 chapters. Prior 42 records are preserved; 4 targeted new chapters added 2026-11-16. |
| Source library | 46 pinned courses, 796 source sections, 46 guides; 825 paths accounted for by 796 imports, 12 aliases and 17 prior exclusions. |
| Canonical Book/Lab content | 900 notebooks, 847 code-bearing; each appears once in the recursive Book TOC and is copied exactly into Lab. |
| Local source-course support | 1147 declared helper/data/license/support placements, each with a checksum and scope. Runtime labels distinguish intended compatibility from actually executed receipts. |
| Real-data map studio | 15 corrected WUR city/model terrain views; four native Lagos population products; Fresno Landsat/Census inputs; distinct published poster reporting scopes; two 672-hour JASL/UHSLC observation windows. Values, dates, units and missingness stay source-specific. |
| Map evidence and observations | [Map data/assets](catalog/map-data.json) and [source map resources](catalog/map-resources.json) identify exact bytes, source versions, rights and preparation. New historical gauge JSON, original CSVs and full producer license metadata are bundled under site/data/. No ordinary build queries a data provider. |
| Browser GIS pathways | 46 subject profiles across 92 project/course landings, plus 6 introduction/foundation routes. Shared Census practice remains distinct from each subject. New C3S/Natural Earth/reference/synthetic inputs retain separate source terms. |
| Dataset attribution | [README register](README.md#dataset-citations-and-attribution-register-2026-11-16) and [file-mapped credits](catalog/data-attributions.json); creator, version, source, rights and modifications remain dataset-specific. |
| Discovery | 72 public records: 68 owner repositories plus 4 external PHI cases; historical dates retained. Owner-list and public-search sets agree as of 2026-11-16. |
| Entry audit | 200 dated source-entry rows; prior 174 retained. All 26 new exact GET entries returned 200 on 2026-11-16. Entry reachability is separate from notebook/scientific execution. |
| Historical milestones | Prior original-companion/source audits remain in the versioned history and validation record. Existing launch evidence and immutable earlier source pins are preserved. |

Population retains native product grids, complete per-layer metadata and zero/NoData semantics; no resampling or source-value replacement was introduced by the Atlas import. OneHealth preserves observed Landsat/Census source records and the distinction between sample summaries, whole-tract totals and area-fraction estimates. Other course transformations are described in their copied provenance files and the dataset register. Original small companion exercises remain labelled synthetic and do not estimate real health outcomes or causal effects.

The primary map links no longer use the fictional 16-cell teaching grid. Terrain inputs already share the WUR MSL reference; no global-average datum correction is applied. Missing cells are neither zero nor necessarily water. A sampled-height threshold is not a flood footprint, area estimate, facility assessment or forecast. Statistical column heights encode their stated source measure, not buildings or elevation. Vertical exaggeration changes presentation only.

The poster facts remain historical Climate Central/Kopp/Muis reporting estimates with city, district and supported-portfolio denominators kept separate. They do not reconstruct private facility sites. July 1994 gauge observations retain station zero; their displayed 28-day anomalies are independent from MSL terrain and AR6 projections. Dataset collection citation and exact subset/metadata response hashes accompany them.

Copyright screening retains explicitly reusable material and author-authorized originals with required notices. Restricted/unclear material is listed by exact path and reason under source-library asset exclusions; missing inputs are visible to the learner. Software licensing is never used as blanket permission for provider observations. Follow scoped noncommercial/share-alike or database conditions where they apply.

## November 2026 course additions

The four new courses retain 72 source notebooks and 76 additional helper/data/notice placements. C3S reference inputs comprise an Apache-2.0 CMIP6 warming-window table, a public-domain Natural Earth coastline and CC BY 4.0 CDS catalogue metadata; they do not supply a new climate-observation archive. TerrIO retains public-domain Natural Earth countries. C3S/DestinE/Urbanity/TerrIO teaching simulations remain explicitly synthetic. The linked dataset-credit ledger distinguishes included inputs, versions, source terms and modifications from optional readings/services. TerrIO 0.9.0 source copies require the matched Pyodide 0.29 Lab; the Atlas remains on 314. Optional widgets and real/native services need their own supported environment.
