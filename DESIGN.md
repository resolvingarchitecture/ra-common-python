# ra-common-python — design notes

A Python port of [`ra-common-java`](https://github.com/resolvingarchitecture/ra-common-java),
tracking the same Phase 1 scope as [`ra-common-rust`](https://github.com/resolvingarchitecture/ra-common-rust).

## Decisions

- **No wire compatibility with the Java JSON.** Java's `toMap`/`fromMap` +
  hand-rolled `JSONParser` + reflective `Class.forName` polymorphism are dropped.
  Every serializable type exposes `to_dict()` / `from_dict()`; `to_json` /
  `from_json` wrap `json`. Polymorphic types (`Message`, `Route`) carry a string
  tag on the wire (`kind` / `type`) and are rebuilt by `message_from_dict` /
  `route_from_dict`.
- **No runtime dependencies.** `hashlib` / `secrets` / `base64` cover crypto;
  base58 and unpadded base32 are implemented in `encoding.py`.
- **Sync concurrency.** `TaskRunner` uses `threading`; `Service` / `LifeCycle` /
  `MessageConsumer` are plain ABCs. No async runtime dependency.
- **Idiom mapping**
  | Java | Python |
  |---|---|
  | `JSONSerializable` | `to_dict` / `from_dict` + `_serde.to_json`/`from_json` |
  | abstract base + `Class.forName("type")` | small class hierarchy + a `*_from_dict` dispatcher on a `type`/`kind` tag |
  | abstract base w/ shared fields (`BaseRoute`) | a `RouteMeta` dataclass held by each route |
  | abstract class w/ behaviour (`BaseService`) | base class methods + a `ServiceCore` state object the impl holds |
  | static utility class (`HashUtil`) | a module of functions |
  | `enum X { A("a") }` + `value()` | `class X(str, Enum)` with the wire string as the value |
  | checked `*Exception` | `RaError` subclasses |
  | `Stack<T>` / `DequeStack` | `collections.deque` (LIFO via `appendleft` / `popleft`) |
  | `Properties` | `dict[str, str]` |

## Bugs fixed during the port (from the Java original)

- `Signature` (de)serialization was an empty stub — implemented fully.
- `BaseRoute.fromMap` read the key `"routedId"` instead of `"routeId"` — corrected.
- `Nonce` prune computed `max * (pct / 100)` → 0 — now `max * pct // 100`, with an
  O(1) `set` membership check plus a `deque` for eviction order.
- `DID.getPassphraseHashAlgorithm()` could NPE — `effective_passphrase_hash_algorithm()`
  falls back to the stored field.
- `Multihash.toHex` was not zero-padded — uses `bytes.hex()`.

## Phase 2 (deferred)

`currency/*`, `locale/*` + `LocaleUtil`/`LanguageUtil`/`Resources`, `Scrubber`,
`RegExGen`, the full network service layer, `Protocol` (multiaddr),
`ShellCommand`, `BrowserUtil`, `FileUtil`, `InfoVault*`, `SimpleByteCache`,
`OrderedProperties`. `DLC` is folded into `Envelope` methods (not ported as a
class). `social/*` is deferred.
