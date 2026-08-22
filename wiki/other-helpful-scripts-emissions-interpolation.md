# Other — helpful_scripts-emissions_interpolation

# emissions_interpolation

## Overview

`emissions_interpolation.py` is a standalone utility script located in `helpful_scripts/emissions_interpolation/`. It was written to support [MASM PR #2067](https://github.com/RuminantFarmSystems/MASM/pull/2067), which required filling gaps in feed emissions factors across U.S. states. The script combines several reference datasets — FIPS-to-ZIP crosswalk data, ZIP-code coordinates, FIPS-to-region mappings, and a feed emissions library — to produce interpolated emissions factors for feed items.

The module is fully self-contained: it has no internal dependencies, makes no outgoing calls, and is not imported anywhere else in the codebase. It is run directly, and its output files are manually reviewed before being promoted into `input/data/EEE`.

## Background

Certain feed items in the RuFaS feed library lacked emissions factors for entire U.S. states. To build a complete national dataset, the missing values had to be derived from geographically related data. The interpolation relies on the chain of relationships between counties (identified by FIPS codes), ZIP codes, and lat/long coordinates:

1. FIPS codes identify counties.
2. A crosswalk maps FIPS codes to ZIP codes.
3. GeoNames data provides coordinates for each ZIP code.
4. A regional mapping groups FIPS codes into larger regions.

This chain lets the script aggregate or interpolate emissions factors at state or regional granularity, depending on data availability.

## Files

| File | Source / Purpose |
|---|---|
| `emissions_interpolation.py` | The main script. Contains user-defined configuration values at the top, followed by the interpolation logic. |
| `COUNTY_ZIP_032010.csv` | HUD USPS crosswalk data. Maps FIPS codes to ZIP codes. Uses 2010 census FIPS codes. |
| `geonames_US.csv` | GeoNames US data. Provides lat/long coordinates per ZIP code. Was opened in Excel and converted to CSV. |
| `fips_to_region.csv` | Maps FIPS codes to geographic regions. |
| `Feed Emissions Source RuFaS_Feed_Library_Combined_Final.csv` | Notes the source of emissions factors for each feed item. |
| `*_wheat_regional_averages.csv` | Regional averages for a specific pair of wheat feeds with identical emissions factors; used to fill statewide gaps. |

## How It Works

The script executes a geographic interpolation pipeline:

1. **Load configuration** — user-defined values at the top of the script control the methodology (which feeds to process, how to handle missing data, etc.).
2. **Map FIPS to ZIP** — using `COUNTY_ZIP_032010.csv`.
3. **Map ZIP to coordinates** — using `geonames_US.csv`.
4. **Map FIPS to region** — using `fips_to_region.csv`.
5. **Interpolate emissions factors** — for each feed item, combine the feed library emissions sources with the geographic mappings to fill state-level gaps.
6. **Write output files** — generated files are written to the `emissions_interpolation` directory for evaluation.

```mermaid
flowchart LR
    A[COUNTY_ZIP_032010.csv] --> D[emissions_interpolation.py]
    B[geonames_US.csv] --> D
    C[fips_to_region.csv] --> D
    E[Feed Emissions Source ... csv[".csv"]] --> D
    D --> F[Output CSVs]
    F --> G[Manual review]
    G --> H[input/data/EEE]
```

## Usage

Run the script directly:

```
python emissions_interpolation.py
```

Before running, review the user-defined values in the first section of the file. These parameterize the methodology used in PR #2067 and may need adjustment for future use cases.

Output files are created in the `emissions_interpolation` directory. They should be evaluated before being added to `input/data/EEE`.

## Special Case: Feeds 193 and 197

Feeds 193 and 197 were not found across entire states. For these feeds, the script falls back to regional averages rather than state-level interpolation. This is why the folder contains the supplementary `*_wheat_regional_averages.csv` files.

## Caveats

- The script was written by Joe Waddell and only tested locally.
- It contains some hardcoded paths and was primarily exercised on Windows; it may not work on other platforms without modification.
- FIPS codes are from the 2010 census, not the 2020 census. Some codes have changed, which could affect correctness if the script is reused with newer data.

## Integration with the Codebase

This module is not imported by any other code and has no runtime dependencies on the rest of the repository. Its outputs feed into `input/data/EEE`, the emissions and energy data directory consumed elsewhere in MASM. The script is therefore a data-generation tool used occasionally during dataset preparation, rather than a runtime dependency.