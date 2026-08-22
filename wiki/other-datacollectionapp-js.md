# Other — DataCollectionApp-js

# Object.assign Polyfill

## Overview

`assign.js` is a standalone polyfill that provides a standards-compliant implementation of [`Object.assign()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/assign) for JavaScript environments that lack native support (notably older browsers such as Internet Explorer 11 and earlier). The module is self-contained, has zero dependencies, and performs no action when `Object.assign` is already available.

## Usage

Include the script before any code that depends on `Object.assign`:

```html
<script src="js/assign.js"></script>
<script>
  // Safe to use Object.assign from this point forward
  const config = Object.assign({}, defaults, overrides);
</script>
```

The polyfill is **idempotent** — loading it multiple times or in an environment that already supports `Object.assign` has no side effects.

## How It Works

The polyfill guards its installation with a feature check:

```js
if (typeof Object.assign !== 'function') {
  // ... install polyfill
}
```

If `Object.assign` is already defined as a function, the module exits immediately. Otherwise, it defines the method on `Object` using `Object.defineProperty` with the following descriptor:

| Attribute     | Value  | Rationale                                                                 |
| ------------- | ------ | ------------------------------------------------------------------------- |
| `writable`    | `true` | Matches the native property descriptor; allows reassignment.              |
| `configurable`| `true` | Matches the native property descriptor; allows future redefinition.       |
| `enumerable`  | `false`| **Not set** — defaults to `false`, so the polyfill never appears in `for...in` iteration over `Object`. |

## Implementation Details

### Signature

```js
Object.assign(target, ...sources)
```

### Algorithm

1. **Validate the target.** Throws a `TypeError` if `target` is `null` or `undefined`, matching the native behavior.
2. **Box the target.** `Object(target)` coerces primitives (e.g., strings, numbers) into wrapper objects so properties can be assigned.
3. **Iterate sources.** For each source argument, skip `null`/`undefined` values (they are ignored per spec).
4. **Copy properties.** For each source, iterate with `for...in` and copy only **own enumerable** properties. The check uses `Object.prototype.hasOwnProperty.call(nextSource, nextKey)` rather than `nextSource.hasOwnProperty(nextKey)` to guard against a shadowed `hasOwnProperty` on the source object.
5. **Return** the modified target object.

### Key Implementation Choices

**`for...in` + `hasOwnProperty` instead of `Object.keys`:** The polyfill targets environments without ES2015 features. `Object.keys` exists in ES5, but `for...in` with an own-property check is the more conservative choice and works in ES3+ engines.

**`Object.defineProperty` for installation:** Using `Object.defineProperty` with an explicit descriptor ensures the polyfilled method is non-enumerable, mirroring the native property's attributes. A naive `Object.assign = function () {}` would create an enumerable property, which could break `for...in` loops over `Object` in some code.

**Strict mode inside the polyfill function:** The `'use strict'` directive ensures that assignments to a read-only target property throw instead of failing silently, matching native behavior in strict mode.

## Edge Cases Handled

| Input | Behavior |
| ----- | -------- |
| `Object.assign(null)` | Throws `TypeError` |
| `Object.assign(undefined)` | Throws `TypeError` |
| `Object.assign({}, null, undefined)` | Returns `{}` — nullish sources are skipped |
| `Object.assign("str")` | Returns `String {"str"}` — primitive target is boxed |
| Source with shadowed `hasOwnProperty` | Works correctly — uses `Object.prototype.hasOwnProperty.call` |
| `Object.assign({}, {a: 1}, {a: 2})` | Later sources overwrite earlier ones: `{a: 2}` |

## Integration with the Codebase

This module is a **dependency-free utility** with no imports and no exports. It is loaded purely for its side effect of installing the polyfill globally. It does not reference other modules and is not referenced by them at the source level — it exists to normalize the runtime environment before application code executes.

### Load Order

Because the polyfill must be installed before any code calls `Object.assign`, ensure the `<script>` tag for `assign.js` appears **before** other application scripts in the HTML:

```html
<!-- Polyfills first -->
<script src="js/assign.js"></script>
<!-- Application code -->
<script src="js/app.js"></script>
```

### Compatibility

- **Works on:** Any environment where `Object.defineProperty` is available (IE9+).
- **Not needed on:** Modern evergreen browsers, Node.js 4+, and any environment with native ES2015 support — the feature check short-circuits immediately.

## Limitations

- Does **not** polyfill `Object.assign` in environments lacking `Object.defineProperty` (IE8 and below). This is an intentional trade-off; supporting those engines would require a fundamentally different approach (e.g., a shim that pollutes `Object.prototype`).
- Does not copy **symbol-keyed properties** (irrelevant for the target environments, but worth noting).
- Does not trigger **setters** on the target — it uses `to[nextKey] = ...` assignment, which is consistent with the spec's `Set` semantics.