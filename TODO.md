# TODO

## Phase 2 (deferred, mirrors ra-common-rust)

- [ ] `currency/*` (~72 Java files) → enum + table
- [ ] `locale/*` + `LocaleUtil` / `LanguageUtil` / `Resources` (data files)
- [ ] `Scrubber`, `RegExGen` / `IntegerRangeRegex`
- [ ] full `network` service layer (`NetworkService`, sessions, `NetworkState`, reports)
- [ ] `Protocol` (multiaddr)
- [ ] `ShellCommand`, `BrowserUtil`, `FileUtil`
- [ ] `InfoVault*`, `SimpleByteCache`, `LookaheadInputStream`, `OrderedProperties`
- [ ] `social/*`
- [ ] `DLC` is intentionally not ported as a class (folded into `Envelope`)

## Packaging

- [ ] publish to PyPI once the seda-bus / service-bus siblings are cut over and
      pinned (currently path/editable installs only)
