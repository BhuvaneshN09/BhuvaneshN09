# Bhuvanesh Nallapati

**Student developer building reliable developer tools and practical AI systems.**

<p>
  <img src="https://github.com/BhuvaneshN09/BhuvaneshN09/blob/main/assets/Untitled%20design.png?raw=true" alt="Bhuvanesh project illustration" width="180" />
</p>

I care about clear interfaces, validation, reproducible experiments, and software that is useful outside a demo. My main language is Python; I also work with TypeScript, Linux, and embedded/drone control concepts.

## Flagship projects

### [FuncWire](https://github.com/BhuvaneshN09/funcwire)

Provider-neutral contracts for typed Python callables. FuncWire turns ordinary functions into deterministic JSON Schema contracts, validates nested data strictly, binds Python signatures exactly, supports sync/async invocation, and exports provider-neutral tool metadata.

- **Zero runtime dependencies** and Python 3.10+ support
- Supports positional-only, keyword-only, variadic, dataclass, TypedDict, Enum, UUID, date/time, Decimal, `Literal`, `Annotated`, and union annotations
- Includes sync/async APIs, result validation, versioned serialization, compatibility diffs, and OpenAI/Anthropic/Gemini/MCP-shaped exports without importing provider SDKs
- [Architecture](https://github.com/BhuvaneshN09/funcwire/blob/main/docs/design/architecture.md) · [API and examples](https://github.com/BhuvaneshN09/funcwire#readme) · [Benchmarks](https://github.com/BhuvaneshN09/funcwire/tree/main/benchmarks)

The repository includes CI, typed-package metadata, a release audit, and a test suite with a 90% minimum branch-coverage gate. I publish measured benchmark and coverage results with releases rather than guessing at performance numbers.

### [BinlyticAI](https://github.com/BhuvaneshN09/BinlyticAI)

An AI-assisted waste-sorting project focused on making recycling decisions easier to understand. Model accuracy and latency should be reported from a reproducible evaluation set before being presented as production metrics.

## Selected work

### [Bhuvanesh Aerospace Controls](https://github.com/BhuvaneshN09/bhuvanesh-aerospace-controls)

An educational, dependency-light quadrotor PID toolkit: bounded PID control, X-frame motor mixing, deterministic roll and three-axis attitude simulation, CSV telemetry, and optional Matplotlib plots. It is explicitly a simulation and is **not flight-certified**.

### [Chess Engine](https://github.com/BhuvaneshN09/Chess-Engine)

A focused exploration of chess search and evaluation, including alpha-beta search and UCI-oriented engine work.

## Engineering practice

- Small, typed interfaces with explicit failure modes
- Tests for edge cases and serialization boundaries
- CI and release checks for maintained libraries
- Architecture notes and runnable examples before adding abstraction
- Honest metrics: measured, reproducible, and tied to a commit or release

## Connect

- [GitHub repositories](https://github.com/BhuvaneshN09)
- [FuncWire on PyPI](https://pypi.org/project/funcwire/)
- [Email](mailto:bhuvanallapati@gmail.com)

I am open to thoughtful collaboration on developer infrastructure, educational tools, and robotics simulations.
