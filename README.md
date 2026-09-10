# Resolving Architecture Common Library (Python)

A Python port of [`ra-common-java`](https://github.com/resolvingarchitecture/ra-common-java) —
the foundational types for the Resolving Architecture / 1M5 ecosystem.

This package provides:

- **`Envelope`** — the universal message wrapper passed between services.
- **`messaging`** — `Message` (Document / Command / Event / Text), producer/consumer/channel/bus contracts.
- **`route`** — routing slips (`DynamicRoutingSlip`) and external/relayed routes.
- **`service`** — the `Service` / `LifeCycle` contract and `ServiceCore` shared state.
- **`identity`** — `Did`, `PublicKey`, `Signature`.
- **`crypto`** — `Hash`, `Multihash`, `HashCash`, password hashing.
- **`content`** — typed content (text / html / json / image / audio / video / binary).
- **`tasks`** — `Task` + a thread-based `TaskRunner`.
- **`config`** — `.properties` loading + XDG directory resolution.
- utilities: base32/58, version comparison, replay `Nonce`, `UniqueId`, byte packing.

Serialization is JSON-based and **not** wire-compatible with the Java version
(the Java library used a hand-rolled JSON layer and reflective polymorphism).

## Install

```bash
pip install -e .            # from a checkout
pip install -e '.[test]'    # with pytest
```

Requires Python 3.13+ and has **no runtime dependencies**.

## Usage

```python
from ra_common import Envelope

e = Envelope.document()
e.add_route("ra.http.HttpService", "SEND")
e.add_content({"hello": "world"})
e.ratchet()

assert e.get_route().service == "ra.http.HttpService"
assert e.content()["hello"] == "world"

back = Envelope.from_json(e.to_json())
assert back == e
```

## Status

Phase 1 (core). Deferred: currency, locale/i18n, the full network service layer,
`Protocol`, shell/file/browser utilities, `InfoVault`. See `TODO.md`.

## License

MIT — see `LICENSE`.
