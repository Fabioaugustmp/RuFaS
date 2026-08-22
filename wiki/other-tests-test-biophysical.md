# Other — tests-test_biophysical

# Other — tests/test_biophysical

## Overview

The `tests/test_biophysical` package contains the unit test suite for the biophysical animal simulation layer of RUFAS (Ruminant Farm Systems). It validates two core components:

- **`Genetics`** — the genetic value engine that generates true breeding values (TBV), estimated breeding values (EBV), environmental effects, phenotypes, and ranking indices for individual animals.
- **`Animal`** — the central animal entity that orchestrates daily routines (growth, milk production, reproduction, digestion, nutrient updates) and manages life-stage transitions from newborn calf through lactating/dry cow.

The tests are organized under `test_animal/`, mirroring the `RUFAS.biophysical.animal` package structure:

```
tests/test_biophysical/
└── test_animal/
    ├── animal_genetics/
    │   └── test_animal_genetics.py
    ├── test_animal/
    │   └── test_animal.py
    └── (additional subpackages for config, herd manager, data types, etc.)
```

## Test Infrastructure

### Shared Fixtures

The `genetics` fixture in `test_animal_genetics.py` constructs a `Genetics` instance for a lactating cow born in 2020, seeding `AnimalConfig.average_phenotype` with fat and protein means for that year:

```python
@pytest.fixture
def genetics() -> Genetics:
    AnimalConfig.average_phenotype["fat_kg"] = {2020: 10.0}
    AnimalConfig.average_phenotype["protein_kg"] = {2020: 20.0}
    genetics = Genetics(animal_type=AnimalType.LAC_COW, birth_year=2020)
    return genetics
```

The `mock_time` fixture in `test_animal.py` provides a mocked `RufasTime` with a fixed current date (`2023-01-01`) and simulation day (`18`), and populates `AnimalConfig` with semen and phenotype data covering a 10-year window around that date.

### Helper Functions

`test_animal.py` defines several module-level helpers:

- **`_make_cow_for_305_day_milk_yield(days_in_milk, calves)`** — constructs a bare `Animal` instance (via `Animal.__new__`) with a mocked `MilkProduction` object, used to test the 305-day milk yield update logic in isolation.
- **`mock_submodule_init(mocker)`** — patches the constructors of `Growth`, `DigestiveSystem`, `MilkProduction`, `Nutrients`, and `Reproduction` so that `Animal.__init__` can run without instantiating real submodules.
- **`mock_animal_init_methods(mocker)`** — patches the four life-stage initialization methods (`_initialize_newborn_calf`, `_initialize_calf_or_heiferI`, `_initialize_heiferII_or_heiferIII`, `_initialize_cow`) and returns the mocks for assertion.
- **`assert_animal_init_properties(result, args)`** — verifies that common `Animal` attributes (`id`, `breed`, `animal_type`, `days_born`, `birth_weight`, `cull_reason`) are correctly set from the typed-dict constructor argument.

### Animal Fixtures

Five fixtures provide `Animal` instances at each life stage for property and routine tests:

| Fixture | Animal type | Notes |
|---|---|---|
| `mock_calf` | `Calf` | Basic calf from `CalfValuesTypedDict` |
| `mock_heiferI` | `HeiferI` | Basic heifer I |
| `mock_heiferII` | `HeiferII` | Includes `days_in_pregnancy=10`; `Reproduction.__init__` patched |
| `mock_heiferIII` | `HeiferIII` | Includes `days_in_pregnancy=10`; `Reproduction.__init__` patched |
| `mock_lactating_cow` | `LacCow` | `days_in_milk=10`; full reproduction program config |
| `mock_dry_cow` | `DryCow` | `parity=3`; full reproduction program config |

## Genetics Tests

### Initialization and Value Generation

`test_animal_genetics_init` is parameterized across all animal types and verifies the constructor's dispatch logic:

- For a **newborn calf** (`initialize_newborn_calf=True`), `_calculate_newborn_calf_tbv_values` is called with the dam's TBV values and a `"YYYY-MM"` birth key; `_calculate_tbv_values` is **not** called.
- For all other life stages, `_calculate_tbv_values` is called and the newborn path is skipped.
- `_calculate_ep_values`, `_calculate_et_values`, and `_calculate_phenotype_values` are always called; EBV and ranking index are deferred until lactation start.

### TBV Generation

`_calculate_tbv_values` draws from a bivariate normal distribution via `Utility.generate_bivariate_random_numbers` with zero means and the module constants `TBV_FAT_STD`, `TBV_PROTEIN_STD`, and `TBV_CORRELATION`.

`_calculate_newborn_calf_tbv_values` computes the mean of the dam's TBV and the top-listing semen value for the birth month, then draws from a bivariate normal around that midpoint. The test suite covers three scenarios:

1. **In-range birth month** — uses the exact semen value for that month.
2. **Out-of-range early date** — falls back to the earliest available semen date and logs a warning via `genetics.om.add_warning`.
3. **Out-of-range late date** — falls back to the latest available semen date and logs a warning.
4. **Missing in-range key** — logs an error via `genetics.om.add_error` and re-raises the `KeyError`.

The warning fallbacks are guarded by class-level flags (`set_top_semen_too_early_warning_raised`, `set_birthdate_too_recent_warning_raised`) so the warning is only emitted once per simulation.

### Environmental Effects

`_calculate_ep_values` and `_calculate_et_values` both draw from bivariate normals with zero means, using the permanent (`E_PERMANENT_*`) and temporary (`E_TEMPORARY_*`) standard deviations and correlations respectively.

### Phenotype Calculation

`_calculate_phenotype_values` sums the TBV, permanent effect, and temporary effect, then adds the year-specific population mean from `AnimalConfig.average_phenotype`. Like the newborn TBV path, it handles out-of-range birth years by clamping to the earliest/latest available year with a one-time warning, and re-raises `KeyError` (after logging) when the year is missing from the data range entirely.

### EBV and Ranking Index

`_calculate_ebv_values` applies a parity- and animal-type-specific reliability adjustment to the TBV. The test parameterization verifies that:

- The standard deviation of the EBV noise decreases with parity (more records → higher reliability).
- The EBV is computed as `group_mean + reliability * (TBV - group_mean) + noise`, where noise is drawn from `numpy.random.normal(0, std)`.

`_calculate_ranking_index` combines fat and protein EBV into a single economic index using fixed weights.

`recalculate_values_at_lactation_start` re-draws temporary effects and phenotype, and only recalculates EBV and ranking index for parities 0–3 (the test asserts `_calculate_ebv_values` is **not** called for parity ≥ 4).

### Aggregation Helpers

Two static methods are tested:

- **`calculate_average_genetic_values(genetics_list)`** — returns a dict of mean values for all genetic attributes; returns `None` for every key when the list is empty.
- **`calculate_average_tbv(genetics_list)`** — returns the mean `TBV_fat` and `TBV_protein` as a tuple; returns `(0.0, 0.0)` for an empty list.

### Dict Representation

The `dict_representation` property serializes all genetic attributes into a flat dict with keys `TBV_fat`, `TBV_protein`, `E_permanent_fat`, `E_permanent_protein`, `E_temporary_fat`, `E_temporary_protein`, `phenotype_fat`, `phenotype_protein`, `EBV_fat`, `EBV_protein`, and `ranking_index`.

## Animal Tests

### Constructor Dispatch

`Animal.__init__` routes to one of four initialization methods based on the `animal_type` in the typed-dict argument. The tests verify the dispatch table:

| Animal type | Initialization method |
|---|---|
| `Calf` (newborn, with `dam_tbv_*` fields) | `_initialize_newborn_calf` |
| `Calf` (existing) | `_initialize_calf_or_heiferI` |
| `HeiferI` | `_initialize_calf_or_heiferI` |
| `HeiferII` | `_initialize_heiferII_or_heiferIII` |
| `HeiferIII` | `_initialize_heiferII_or_heiferIII` |
| `LacCow` / `DryCow` | `_initialize_cow` |

### Newborn Calf Initialization

`test_initialize_newborn_calf` is parameterized over semen type (`conventional`, `sexed`, `random`), sex, and stillbirth status. It verifies:

- **Sex determination** — a random draw is compared against `AnimalConfig.male_calf_rate_conventional_semen` or `male_calf_rate_sexed_semen`; an invalid semen type raises `ValueError`.
- **Stillbirth** — a second random draw is compared against `AnimalConfig.still_birth_rate`.
- **Mature body weight** — drawn from a truncated normal via `truncnorm.rvs` with bounds `±STDI` around `AnimalConfig.average_mature_body_weight`.
- **Initial phosphorus** — transferred from the dam via `initial_phosphorus` into `nutrients.total_phosphorus_in_animal`.

### Life-Stage Initialization

- **`_initialize_calf_or_heiferI`** — sets sex to `FEMALE`, copies body weight/wean weight/mature weight from the typed dict, and parses the event history string via `AnimalEvents.init_from_string`.
- **`_initialize_heiferII_or_heiferIII`** — additionally initializes the `Reproduction` object with the heifer reproduction program, sub-protocol (mapped to `HeiferTAISubProtocol` or `HeiferSynchEDSubProtocol` depending on the program), and optional pregnancy state (`days_in_pregnancy`, `ai_day`, `estrus_count`, etc.).
- **`_initialize_cow`** — initializes reproduction with both heifer and cow programs, sets `days_in_milk`, `parity` (as `reproduction.calves`), and `calving_interval` (defaulting to `AnimalConfig.calving_interval`).

### Property Guards

A large portion of the test file verifies that cow-only properties raise `TypeError` (and log via `OutputManager.add_error`) when accessed on non-cow animals. The pattern is consistent:

```python
mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
mock_add_error = mocker.patch.object(OutputManager, "add_error")
with pytest.raises(TypeError):
    _ = animal.days_in_milk
mock_add_error.assert_called_once()
```

Properties covered by this guard pattern include:

- `days_in_milk` (getter/setter)
- `days_in_pregnancy` (getter/setter — also guarded by animal type)
- `future_cull_date` (getter/setter)
- `daily_horizontal_distance`, `daily_vertical_distance`, `daily_distance` (getters/setters)
- `reproduction` (getter/setter)
- `calves`, `calving_interval`, `gestation_length`, `calf_birth_weight` (getters/setters)
- `calving_interval_history` (getter)
- `heifer_reproduction_program`, `heifer_reproduction_sub_program` (getters/setters)
- `cow_reproduction_program`, `cow_presynch_program`, `cow_ovsynch_program`, `cow_resynch_program` (getters/setters)

`future_death_date` is the exception — it is settable for any life stage, reflecting that youngstock mortality and cow death are both modeled.

### 305-Day Milk Yield

`update_305_day_milk_yield` delegates to `MilkProduction.calculate_305_day_milk_yield` in all cases except one: a dry cow that already has a non-zero yield from a prior lactation retains its stored value. The tests verify:

- Cows before day 305 use the calculator.
- Cows at or past day 305 also use the calculator (unified path).
- Dry cows with a prior yield keep it.
- Dry cows with no prior yield (still at the `0.0` init default) get the Wood's-curve integral so they don't drag down the herd mean.

### Daily Routines

`daily_routines` is the main per-day entry point. The test verifies the orchestration order and that the day counter increments:

```python
result = animal.daily_routines(MagicMock(RufasTime))
assert animal.days_born == 11
assert animal.days_in_pregnancy == 1
```

The mocked sub-routines are each asserted to be called once:

- `_daily_nutrients_update`
- `_daily_digestive_system_update`
- `daily_milking_update`
- `daily_growth_update`
- `daily_reproduction_update`
- `animal_life_stage_update`

The return value is a `DailyRoutinesOutput` containing the animal status, any newborn calf config (when a birth occurred), and herd reproduction statistics.

### Daily Sub-Routine Tests

- **`_daily_nutrients_update`** — calls `Nutrients.perform_daily_phosphorus_update` with a `NutrientsInputs` built from current animal state.
- **`_daily_digestive_system_update`** — calls `DigestiveSystem.process_digestion` with a `DigestiveSystemInputs` including nutrient supply and milk composition.
- **`daily_milking_update`** — only calls `MilkProduction.perform_daily_milking_update` for cows; stores the output DIM in `_milk_production_output_days_in_milk` and merges events.
- **`daily_milking_update_without_history`** — same guard; used for animals without milk production history.
- **`daily_growth_update`** — calls `Growth.evaluate_body_weight_change` with a `GrowthInputs` built from current state, then applies the returned body weight and conceptus weight.
- **`daily_reproduction_update`** — the most complex routine. For non-eligible animals (calves) it returns `(None, None)`. For eligible animals it:
  1. Calls `Reproduction.reproduction_update`.
  2. Determines the new DIM via `_determine_days_in_milk` (which prefers the milk-production output DIM, falling back to the reproduction output, and raises `ValueError` if the current DIM is negative).
  3. Updates Wood's lactation curve parameters from `LactationCurve.get_wood_parameters`.
  4. Determines future cull/death dates.
  5. Returns a `NewBornCalfValuesTypedDict` when a calf was born.

### Life-Stage Transitions

Each life stage has an update method that evaluates transition criteria and returns an `AnimalStatus`:

| Method | Transition condition | New status |
|---|---|---|
| `_calf_life_stage_update` | `_evaluate_calf_for_heiferI` (days_born ≥ threshold) | `LIFE_STAGE_CHANGED` |
| `_heiferI_life_stage_update` | `_evaluate_heiferI_for_heiferII` | `LIFE_STAGE_CHANGED` |
| `_heiferII_life_stage_update` | culling check first, then `_evaluate_heiferII_for_heiferIII` | `SOLD`, `LIFE_STAGE_CHANGED`, or `REMAIN` |
| `_heiferIII_life_stage_update` | `evaluate_heiferIII_for_cow` | `LIFE_STAGE_CHANGED` (with newborn config) |
| `_cow_life_stage_update` | `is_milking` toggles between `LAC_COW` and `DRY_COW` | `LIFE_STAGE_CHANGED` |

`animal_life_stage_update` is the dispatcher. It first checks `future_cull_date` and `future_death_date` against the current simulation day — if either has arrived, the animal is marked sold or dead (with `cull_reason` set to `DEATH_CULL` for death) and the routine short-circuits. Otherwise it delegates to the stage-specific method.

### Reproduction Program Determination

`_determine_heifer_reproduction_programs` is tested for three outcomes:

- **TAI program** — maps the sub-protocol string to `HeiferTAISubProtocol`.
- **SynchED program** — maps to `HeiferSynchEDSubProtocol`.
- **Invalid/NA program** — raises an error.

## Relationship to the Codebase

The test suite exercises the following production modules:

- `RUFAS.biophysical.animal.animal` — the `Animal` class under test.
- `RUFAS.biophysical.animal.animal_genetics.animal_genetics` — the `Genetics` class under test.
- `RUFAS.biophysical.animal.animal_config` — `AnimalConfig` holds simulation-wide parameters (semen rates, phenotype means, mature weights) that the tests mutate directly.
- `RUFAS.biophysical.animal.data_types.*` — typed dicts (`NewBornCalfValuesTypedDict`, `CowValuesTypedDict`, etc.), enums (`AnimalType`, `Breed`, `Sex`, `AnimalStatus`), and event/statistics containers.
- `RUFAS.biophysical.animal.*` submodules (`growth`, `milk`, `reproduction`, `nutrients`, `digestive_system`) — mocked in most tests but exercised through their public interfaces in the daily-routine tests.
- `RUFAS.util.Utility` — `generate_bivariate_random_numbers` is the random-number source for all genetic value generation.
- `RUFAS.output_manager.OutputManager` — error/warning logging is asserted throughout.

The tests follow a consistent pattern: **mutate `AnimalConfig` state → construct the object under test → assert on internal method calls and resulting attribute values**. This makes the suite sensitive to configuration-driven behavior (e.g., semen type, phenotype year ranges) and to the guard logic that restricts cow-only properties to the correct life stages.