# Manure

# Manure Module

## Overview

The Manure module simulates the complete on-farm manure management system: collection from animal housing, processing through a configurable network of handlers, digesters, separators, and storages, and eventual application to fields as fertilizer. It is the biophysical counterpart to the animal and crop/soil modules, receiving daily manure streams from animals and fulfilling nutrient requests from fields.

The module is built around a directed graph of **processors**. Each processor receives a `ManureStream`, transforms it (adding water, destroying volatile solids, emitting gases), and passes it downstream. The graph topology is defined in configuration files and validated at startup.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ManureManager                               │
│                                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────────┐  │
│  │ Processor   │  │ Adjacency    │  │ Topological sort          │  │
│  │ registry    │  │ matrix       │  │ (processing order)        │  │
│  └─────────────┘  └──────────────┘  └───────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ run_daily_update()                                          │   │
│  │  • receive manure from animal module                        │   │
│  │  • process each processor in topological order              │   │
│  │  • route outputs to downstream processors                   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ request_nutrients()                                         │   │
│  │  • fulfill field nutrient requests from storage pools       │   │
│  │  • handle daily-spread and supplemental manure paths        │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼──────────────────────┐
        ▼                     ▼                      ▼
   ┌─────────┐          ┌──────────┐           ┌──────────┐
   │ Handler │          │ Digester │           │ Storage  │
   │         │          │          │           │          │
   │ • Manual│          │ • Conti- │           │ • Anaero-│
   │   Scraper│         │   nuous  │           │   bic    │
   │ • Alley │          │   Mix    │           │   Lagoon │
   │   Scraper│         │   (CSTR) │           │ • Slurry │
   │ • Flush │          │          │           │   Outdoor│
   │   System│          │          │           │ • Slurry │
   │ • Parlor│          │          │           │   Under- │
   │   Clean-│          │          │           │   floor  │
   │   ing   │          │          │           │ • Bedded │
   │         │          │          │           │   Pack   │
   │         │          │          │           │ • Compost│
   │         │          │          │           │ • Open   │
   │         │          │          │           │   Lot    │
   │         │          │          │           │ • Daily  │
   │         │          │          │           │   Spread │
   └─────────┘          └──────────┘           └──────────┘
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               ▼
                        ┌────────────┐
                        │ Separator  │
                        │ (optional) │
                        └────────────┘
```

## Core Components

### `ManureManager`

The `ManureManager` is the module's entry point and orchestrator. It is constructed once per simulation with weather-derived temperature parameters (`intercept_mean_temp`, `phase_shift`, `amplitude`).

**Initialization sequence:**

1. **Load configuration** — reads `manure_management` and `manure_processor_connection` from the `InputManager`.
2. **Validate processor definitions** — checks for duplicate names and unknown references.
3. **Instantiate processors** — uses `ProcessorType.get_processor_class()` to map config `processor_type` strings to concrete classes. Temperature-sensitive storages (`AnaerobicLagoon`, `SlurryStorageOutdoor`) receive the weather parameters.
4. **Build adjacency matrix** — a `dict[str, dict[str, float]]` mapping each origin (processor or separator output port) to destination processors with flow proportions. Separators get three rows: `{name}_input`, `{name}_solid_output`, `{name}_liquid_output`.
5. **Validate the matrix** — rejects self-loops and columns whose proportions do not sum to 0 or 1.
6. **Topological sort** — merges separator rows, computes in-degrees, and runs Kahn's algorithm to produce a valid processing order. Cycles raise a `ValueError`.

**Daily update** (`run_daily_update`):

1. Receives a `dict[str, ManureStream]` from the animal module. Each stream carries `pen_manure_data.first_processor`, naming the processor that should receive it.
2. Dispatches each stream to its first processor via `receive_manure()`.
3. Iterates processors in topological order, calling `process_manure()` on each.
4. Routes each output stream to downstream destinations, splitting streams when a connection proportion is not 1.0.
5. Rebuilds the aggregated nutrient pools for field application.

**Nutrient requests** (`request_nutrients`):

The crop/soil module calls this method to obtain manure for field application. The method supports three paths:

- **`spread_all_available_manure`** — pools everything in `DailySpread` storages and clears them.
- **`use_daily_spread_source`** — fulfills the request from `DailySpread` storages only, using a temporary `ManureNutrientManager` so the farm-wide pool is untouched.
- **Default** — fulfills from the aggregated stored-manure pool via `ManureNutrientManager.handle_nutrient_request()`.

After a request is fulfilled, `_remove_nutrients_from_storage()` draws down the matching storages proportionally. The limiting nutrient (nitrogen or phosphorus) determines the removal proportion; non-limiting nutrients are removed at the same proportion. If the request cannot be fully met and `use_supplemental_manure` is set, the shortfall is sourced from `FieldManureSupplier`.

### `Processor` (base class)

All manure processors inherit from `Processor`. It provides:

- `check_manure_stream_compatibility()` — validates that a stream is non-empty and has valid `pen_manure_data`.
- `_report_manure_stream()` / `_report_processor_output()` — write daily outputs to the `OutputManager`.
- `_calculate_ammonia_emissions()` — shared ammonia emission calculation used by handlers and storages.
- `_determine_barn_temperature()` — converts ambient temperature to barn temperature.

### `Handler`

Handlers represent manure collection at the housing level. The base `Handler` class implements the common processing logic:

1. Computes cleaning water volume (`determine_handler_cleaning_water_volume`), which depends on handler type and whether a parlor flush is used.
2. Determines barn temperature from ambient conditions.
3. Calculates ammonia emissions for pen-based handlers (`ManualScraper`, `AlleyScraper`, `FlushSystem`) using a resistance model.
4. Adds cleaning water and milking water to the manure stream.
5. Subtracts ammonia-N from the nitrogen pools.
6. Emits the processed stream with `pen_manure_data` set to `None` (housing data is no longer needed downstream).

Two concrete handler subclasses exist:

- **`SingleStreamHandler`** — base for handlers that accept exactly one stream per day. Raises `ValueError` if a second stream arrives. Adds housing CO₂ and CH₄ emissions (temperature- and surface-area-dependent) and applies volatile-solid loss proportional to methane emissions.
- **`ParlorCleaningHandler`** — accepts multiple streams (accumulates them via `+=`), reports zero CO₂/CH₄ housing emissions, and adds fresh water used for milking.

### `Digester`

The `Digester` base class is a thin marker subclass of `Processor`. The only concrete implementation is `ContinuousMix`, a continuously-stirred tank reactor (CSTR) anaerobic digester.

**Processing flow** (`process_manure`):

1. If no manure was received, reports zero outputs and returns an empty dict.
2. Increases ammoniacal nitrogen by `TAN_INCREASE_FACTOR` (capped at total nitrogen).
3. Calculates generated methane mass and volume using the CSTR equation:

   ```
   methane_volume = total_volatile_solids × methane_production_potential
   ```

   Methane density is computed from the ideal gas law at the digester's temperature set point.

4. Calculates generated CO₂ from the methane volume using the volumetric ratio `CO₂:CH₄ = 4:6`.
5. Destroys volatile solids proportional to the combined gas mass, distributing the loss across degradable, non-degradable, and bedding non-degradable VS pools.
6. Computes methane leakage (a configurable fraction of generated methane) and captured biogas/methane volumes.
7. Reports outputs (`captured_biogas_volume`, `captured_methane_volume`, `methane_leakage_mass`) and returns the digested manure stream.

The `_destroy_volatile_solids` method guards against over-destruction: if the calculated destruction exceeds available VS, it logs an error and zeroes all VS pools rather than producing negative values.

### `Storage`

Storage processors accumulate manure over time and are the source for field application. The module includes:

| Class | Manure type | Notes |
|---|---|---|
| `AnaerobicLagoon` | Liquid | Temperature-modelled via sine wave; minimum temperature 1°C |
| `SlurryStorageOutdoor` | Liquid | Minimum temperature −20°C |
| `SlurryStorageUnderfloor` | Liquid | Uses barn temperature |
| `BeddedPack` | Solid | Tilled/untilled bedding options |
| `Composting` | Solid | Static pile or windrow; MCF depends on temperature |
| `OpenLot` | Solid | MCF from IPCC regression |
| `DailySpread` | Solid | Manure available for immediate field application |

Liquid storages share methane emission logic in the `Storage` base class, using an Arrhenius temperature response:

```
methane_emission = VS × exp(ln(A) − Ea / (R × T))
```

Ammonia emissions from storage use a resistance model with `STORAGE_RESISTANCE` and a default pH of 7.5.

### `Separator`

Separators split a manure stream into solid and liquid fractions. They are special in the graph: a separator has three ports (`_input`, `_solid_output`, `_liquid_output`), and the adjacency matrix tracks them separately. The topological sort merges these into a single node for ordering, but routing at runtime uses the individual ports.

### `ManureConstants`

A central constants class covering:

- Manure densities (liquid, slurry, solid)
- Handler parameters (housing resistance constant, default pH, milking water rate)
- Digester parameters (molar masses, CO₂:CH₄ ratio, TAN increase factor)
- Storage parameters (VS-to-methane loss ratio, activation energy, Arrhenius constant, storage resistance)
- Solid storage parameters (MCF values, emission coefficients, decomposition rates)
- Temperature modelling parameters (damping factor, lag, minimum temperatures)

## Data Structures

### `ManureStream`

The core data object flowing through the system. Fields include:

- `water`, `ammoniacal_nitrogen`, `nitrogen`, `phosphorus`, `potassium`
- `ash`, `degradable_volatile_solids`, `non_degradable_volatile_solids`, `bedding_non_degradable_volatile_solids`
- `volume`, `total_solids`, `methane_production_potential`
- `pen_manure_data` — housing metadata (animal count, surface area, urine mass, first processor); set to `None` once manure leaves the housing system

The class supports `+=` accumulation and `split_stream(proportion)` for routing.

### `ManureNutrients`

Aggregated nutrient pool used for field application requests. Tracks nitrogen, phosphorus, potassium, total mass, and dry matter for a given `ManureType`.

## Configuration

The module is configured through two input groups:

**`manure_management`** — a dict keyed by processor category (`anaerobic_digester`, `separator`, `storage`, `handler`), each a list of processor configs. Each config requires a unique `name` and a `processor_type` string that maps to a class via `ProcessorType`. Additional keys are passed as constructor arguments.

**`manure_processor_connection`** — a dict with `processor_connections` and `separator_connections` lists. Each connection specifies a `processor_name` and either `destinations` (for standard processors) or `solid_output_destinations` / `liquid_output_destinations` (for separators). Each destination has a `receiving_processor_name` and a `proportion` (must sum to 0 or 1 per origin).

## Integration with Other Modules

- **Animal module** — produces daily `ManureStream` objects with `pen_manure_data` indicating the first processor. The `ManureManager.run_daily_update()` receives these and routes them.
- **Crop/soil module** — calls `ManureManager.request_nutrients()` with a `NutrientRequest`. The manager returns a `NutrientRequestResults` object (or `None` if no manure is available) and records the application in the `OutputManager` under `on_farm_manure`.
- **OutputManager** — all processors report daily outputs (gas emissions, water volumes, manure stream composition) through `_report_processor_output` and `_report_manure_stream`. Errors and warnings are logged with structured info maps.
- **InputManager** — supplies the configuration dicts at construction time.
- **`FieldManureSupplier`** — external source for supplemental manure when on-farm supply is insufficient.

## Error Handling

The module uses a consistent pattern: log a structured error via `OutputManager.add_error()` and raise an exception. Key failure modes:

| Condition | Exception |
|---|---|
| Duplicate processor names in config | `ValueError` |
| Unknown processor referenced in connections | `ValueError` |
| Processor missing connection definition | `ValueError` |
| Cycle in processor graph | `ValueError` |
| Self-loop or non-normalized proportions in adjacency matrix | `ValueError` |
| Invalid manure stream received by handler/digester | `ValueError` |
| `None`-type `ManureStream` during processing | `TypeError` |
| Multiple streams to a `SingleStreamHandler` | `ValueError` |
| Destination receiving both solid and liquid separator output | `ValueError` |
| VS destruction exceeding available VS | Logs error, zeroes VS pools (no exception) |