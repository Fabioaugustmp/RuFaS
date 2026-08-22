# Other — input

# Other — Input Module

## Overview

The **Other — input** module is a minimal metadata descriptor for the task manager configuration system. It contains no executable logic, no external dependencies, and no runtime calls. Its sole responsibility is to declare the location and basic characteristics of the task configuration data file used by the simulation.

This module exists at `input/task_manager_metadata.json` and acts as a pointer: it tells the broader system where to find the actual task configuration and what to expect from it.

## Purpose

The file answers three questions about the simulation's task data:

1. **Where is the task data?** — It resolves the path to the actual configuration file.
2. **What kind of data is it?** — It declares the format (`json`) and the logical file type (`tasks`).
3. **What schema governs it?** — It references a property definition (`tasks_properties`) that describes the expected fields.

Because the metadata file decouples the file location from the code that consumes it, changing the task configuration path (e.g., switching from `example_freestall_task.json` to a user-supplied file) requires editing this descriptor alone, not the importing code.

## File Structure

The JSON is small and flat. It wraps a single `files` object that contains one entry, `tasks`:

```json
{
  "files": {
    "tasks": {
      "title": "Task manager data",
      "description": "Configuration file for general simulation parameters.",
      "path": "input/data/tasks/example_freestall_task.json",
      "type": "json",
      "properties": "tasks_properties"
    }
  }
}
```

### Field Reference

| Field         | Value                                        | Meaning                                                        |
|---------------|----------------------------------------------|----------------------------------------------------------------|
| `title`       | `"Task manager data"`                        | Human-readable label for the file entry.                       |
| `description` | `"Configuration file for general simulation parameters."` | What the referenced file contains.                 |
| `path`        | `"input/data/tasks/example_freestall_task.json"` | Relative path from the repository root to the actual data file. |
| `type`        | `"json"`                                     | Serialization format of the target file.                       |
| `properties`  | `"tasks_properties"`                         | Logical name of the schema/property set that validates the data. |

The `files` wrapper suggests the design supports multiple named file entries; only `tasks` is defined here, but the structure is extensible if other input descriptors are added in the future.

## Relationship to the Task Configuration Data

The referenced file, `input/data/tasks/example_freestall_task.json`, holds the actual simulation parameters. The metadata does not validate or parse that file itself — it only supplies the pointer. Consumers of this metadata are expected to:

1. Read `task_manager_metadata.json`.
2. Extract `files.tasks.path`.
3. Load and parse the JSON at that path.
4. Optionally use `files.tasks.properties` to look up the validation rules for the file's contents.

## Connections to the Rest of the Codebase

This module has no direct callers or callees detected in the codebase call graph. It is a static data asset, not a runtime component. Its integration is indirect:

- A configuration loader (or bootstrap routine) somewhere in the simulation startup sequence reads this metadata file to discover where task data lives.
- The `properties` value (`tasks_properties`) is a logical key that must be recognized by whatever schema registry or property-validation service the codebase uses. If that registry does not contain an entry for `tasks_properties`, validation of the task file will fail or be skipped, depending on the loader's behavior.

Because the metadata carries no import statements or function calls, understanding its contract requires looking at the loader that consumes it. If you are modifying this file, the two invariants to preserve are:

- The `path` must remain resolvable relative to the repository root.
- The `type` and `properties` values must match what the consuming loader expects.

## Summary

`task_manager_metadata.json` is a static declaration file. It is the entry point for locating task configuration data and the first piece a developer should inspect when tasked with changing which task file the simulation loads. Altering the simulation's task parameters means editing the data file it points to; altering *which* file is used means editing the `path` field here.