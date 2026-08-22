# Other — tests-test_data_structures

# tests/test_data_structures

## Overview

This package contains the test suite for the data structures that connect the major biophysical modules of the RUFAS (Ruminant Farm Systems) model. These structures are the "plumbing" that moves mass and nutrient data between the animal, feed storage, crop/soil, and manure management components of the simulation.

The tests are organized into four files, each corresponding to a connection point in the model's material flow:

| Test File | Production Code Under Test | Connection |
|---|---|---|
| `test_animal_to_manure_connection.py` | `RUFAS.data_structures.animal_to_manure_connection` | Animal → Manure storage |
| `test_crop_soil_to_feed_storage_connection.py` | `RUFAS.data_structures.crop_soil_to_feed_storage_connection` | Crop/Soil → Feed storage |
| `test_feed_storage_to_animal_connection.py` | `RUFAS.data_structures.feed_storage_to_animal_connection` | Feed storage → Animal |
| `test_manure_nutrients.py` | `RUFAS.data_structures.manure_nutrients` | Manure → Crop/Soil |

## Test Coverage by Module

### 1. Animal → Manure Connection

**File:** `test_animal_to_manure_connection.py`

Tests the `ManureStream` and `PenManureData` classes, which represent manure as it moves from animal pens into the manure management system.

#### Key Behaviors Tested

- **`ManureStream` arithmetic**: The `+` operator combines two streams by summing component masses (water, nitrogen, phosphorus, etc.) and computing a mass-weighted `methane_production_potential`. The `pen_manure_data` fields are summed when both operands have compatible `PenManureData`.
- **`split_stream(ratio, stream_type)`**: Splits a stream into a fraction (`0 < ratio < 1`) of the original, scaling all component masses proportionally. The `pen_manure_data` is also split when present.
- **`make_empty_manure_stream()`**: Class method returning a zeroed stream with `pen_manure_data=None`.
- **`is_empty` property**: Returns `True` only for streams created by `make_empty_manure_stream()`.
- **`PenManureData` validation**: Raises `ValueError` when a non-lactating animal combination is assigned to a `StreamType.PARLOR` stream.
- **`PenManureData` combination rules**:
  - `+` sums numeric fields and sets `pen_type` to `None` (since the combined pen spans multiple types).
  - Raises `ValueError` if the two instances have different `first_processor` values.
  - Raises `ValueError` if either instance has `stream_type == StreamType.GENERAL`.
- **`StreamType` enum**: Verifies `PARLOR` and `GENERAL` members with their string values.

#### Test Fixtures

- `manure_stream`: A `ManureStream` with positional arguments (used to lock the constructor signature).
- `manure_stream_1`, `pen_data_1`, `pen_data_2`: Reusable `ManureStream`/`PenManureData` instances with realistic values.
- `sample_manure_stream`: A stream with `pen_manure_data` attached, used for split tests.

### 2. Crop/Soil → Feed Storage Connection

**File:** `test_crop_soil_to_feed_storage_connection.py`

Tests the `HarvestedCrop` class, which models a crop lot from harvest through storage and feed-out.

#### Key Behaviors Tested

- **Initialization**: Verifies that constructor arguments are stored correctly and that derived properties (`initial_dry_matter_percentage`, `initial_dry_matter_mass`) are computed. Also verifies that `RufasTime` objects are converted to `date` objects for `harvest_time` and `storage_time`.
- **`fresh_mass` property**: Computed as `dry_matter_mass / (dry_matter_percentage / 100)`, with a guard against division by zero.
- **`remove_dry_matter_mass(mass)`**: Reduces dry matter and recomputes `dry_matter_percentage` based on the new fresh mass.
- **`remove_feed_mass(mass)`**: Removes fresh mass, raising `ValueError` if the requested removal exceeds available dry matter.
- **`estimate_maximum_effluent()`**: Returns a positive value only when `dry_matter_percentage < 30%`; otherwise returns `0.0`.
- **`_calculate_bale_density()`**: Empirical relationship between dry matter percentage and bale density.
- **`_calculate_total_sensible_heat_generated()`**: Heat generation model based on dry matter percentage and bale density.

#### Test Fixtures

- `sample_crop_data` (from `tests.test_biophysical.test_feed_storage.sample_crop_data`): A complete, valid `HarvestedCrop` configuration reused across tests.

### 3. Feed Storage → Animal Connection

**File:** `test_feed_storage_to_animal_connection.py`

Tests the feed data model and the `AvailableFeedsBuilder` factory that constructs feed objects from configuration.

#### Key Behaviors Tested

- **`Feed` class hierarchy**: `NASEMFeed` and `NRCFeed` subclasses accept their respective nutrient profiles via `**kwargs`.
- **Enums**: `FeedCategorization`, `FeedComponentType`, and `NutrientStandard` members and their string values.
- **`AvailableFeedsBuilder.setup_available_feeds(config, nutrient_standard)`**:
  - Delegates to `_process_feed_library` to load and convert the feed library.
  - Delegates to `_validate_feed_config` for configuration validation.
  - Sorts feeds by `rufas_id`.
  - Sets `amount_available=0.0` and derives `on_farm_cost` from `purchase_cost` using `ON_FARM_TO_PURCHASED_PRICE_RATIO`.
  - Applies per-feed overrides from the config (`purchased_feed_cost`, `buffer`).
- **`_validate_feed_config`**:
  - Accepts a valid config without error.
  - Raises `ValueError` when a configured `feed_type` is missing from the selected feed library.
  - Raises `ValueError` on duplicate `feed_type` entries in the top-level `feeds` section.
  - Raises `ValueError` on duplicate `feed_type` entries within a ration.
  - Raises `ValueError` when a ration references a feed not in the top-level `feeds` section.
- **`_find_feed_repeats(values)`**: Returns the set of duplicated values (or empty set).
- **`_process_feed_library(nutrient_standard)`**: Loads the correct data key (`"NASEM_Comp"` or `"NRC_Comp"`), converts the columnar library to a list of row dicts, indexes by `rufas_id`, and converts string enum fields to their enum members.

#### Test Fixtures

- `mock_feed`: Base `Feed` fields.
- `mock_NASEM_feed` / `mock_NRC_feed`: Nutrient-standard-specific fields.
- `valid_feed_config`: A minimal but valid configuration with two feeds and one ration.
- `feed_library`: A stub library mapping `feed_type` IDs to `{}`.

### 4. Manure Nutrients

**File:** `test_manure_nutrients.py`

Tests the `ManureNutrients` dataclass and the `NutrientRequestResults` class used for nutrient accounting between manure storage and crop application.

#### Key Behaviors Tested

- **`ManureNutrients` validation** (`__post_init__`):
  - All mass fields must be non-negative.
  - `manure_type` must be a `ManureType` enum member.
- **Arithmetic operators**:
  - `+` / `-`: Element-wise addition/subtraction of all mass fields. Raises `TypeError` when mixing `ManureType` values or non-`ManureNutrients` operands. Raises `ValueError` when subtraction would produce a negative result.
  - `*` / `rmul`: Scales all mass fields by a scalar. Raises `TypeError` for non-numeric scalars and `ValueError` for negative scalars.
- **Composition properties**: `dry_matter_fraction`, `nitrogen_composition`, and `phosphorus_composition` compute mass fractions, returning `0.0` when total mass is zero.
- **`reset_values()`**: Returns a new zeroed `ManureNutrients` with the same `manure_type`.
- **`NutrientRequestResults.__add__`**: Combines two requests with mass-weighted fraction averaging. When total nitrogen (or phosphorus) is zero, the first request's fractions are preserved. The `ammonium_nitrogen_fraction` is weighted by the inorganic nitrogen mass.

## Test Strategy Notes

- **Property-based parameterization**: The `NutrientRequestResults` addition tests use `@pytest.mark.parametrize` with boundary values (`0`, `0.01`, `0.99`) to exercise edge cases in fraction weighting.
- **Mocking boundaries**: `InputManager` is mocked in `test_process_feed_library` to isolate the feed library conversion logic. `HarvestedCrop`'s computational methods are mocked in `test_attributes` to verify constructor-side-effect ordering.
- **Error message contracts**: Many tests assert on exact error message text (e.g., `"Cannot combine PenManureData instances with different first processors."`). Changing these messages requires updating the corresponding tests.
- **Positional constructor calls**: `test_manure_stream` uses positional arguments to lock the `ManureStream.__init__` signature, preventing accidental reordering of parameters.

## Running the Tests

```bash
# From the repository root
pytest tests/test_data_structures/ -v

# Run a single file
pytest tests/test_data_structures/test_manure_nutrients.py -v

# Run a single test
pytest tests/test_data_structures/test_animal_to_manure_connection.py::test_split_stream_valid -v
```

## Relationship to Other Modules

These tests depend on fixtures and utilities from sibling test packages:

- `tests.test_biophysical.test_feed_storage.sample_crop_data` — shared `HarvestedCrop` configuration.
- `RUFAS.rufas_time.RufasTime` — time conversion test in `test_harvest_and_storage_time_with_rufas_time`.
- `RUFAS.input_manager.InputManager` — mocked in `test_process_feed_library`.
- `RUFAS.units.MeasurementUnits` — enum used in feed library conversion.
- `RUFAS.biophysical.animal.data_types.animal_combination.AnimalCombination` — used to construct `PenManureData` instances.