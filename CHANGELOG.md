# Changelog

## 0.1.0 — unreleased

Initial port of `ra-common-java` Phase 1 to Python.

- `Envelope` + `MessageType` / `Action`, factories, routing-slip walk, document
  content/entity/exception/NVP accessors, headers, markers, JSON round-trip.
- `messaging`: `Message` (`DocumentMessage` / `CommandMessage` / `EventMessage` /
  `TextMessage`), `Email`, `Command` / `EventType` enums, `MessageProducer` /
  `MessageConsumer` / `MessageChannel` / `MessageBus` contracts.
- `route`: `RouteMeta`, `SimpleRoute`, `DynamicRoutingSlip` (LIFO),
  `SimpleExternalRoute`, `RelayedExternalRoute`.
- `service`: `Service` + `ServiceCore`, `ServiceStatus` (19 states),
  `ServiceLevel`, `ServiceReport`, `ServiceMessage`, `ServiceStatusObserver`.
- `identity`: `Did` (+ `DidStatus` / `DidType`), `PublicKey`, `Signature`,
  `PiiClearable`.
- `crypto`: `Hash` / `HashAlgorithm`, `hash_util` (digests, fingerprints, salted
  + PBKDF2 password hashing), `Multihash`, `HashCash` (v0/v1),
  `EncryptionAlgorithm`, `Addressable`.
- `content`: `Content` / `ContentKind`, `build`, magnet links.
- `tasks`: `Task` / `TaskConfig` / `TaskStatus`, thread-based `TaskRunner`.
- `config`: `.properties` / args / env loading, `SystemSettings` (XDG dirs).
- `network`: `Network`, `NetworkStatus`, `NetworkPeer` (minimal slice).
- `file`: `Multipart`.
- `util`: `bytes_util`, `strings`, `version_compare`, `random_util`, `UniqueId`,
  `Nonce`.
- `encoding`: base32 (RFC 4648, unpadded), base58 (Bitcoin alphabet).
