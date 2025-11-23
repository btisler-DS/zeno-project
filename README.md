# The Zeno Project

Zeno is an open-source **calibration harness** for large language models (LLMs).  
It doesn’t fine-tune models; it **interrogates** them.

Zeno runs a small set of tightly-designed scenarios to answer questions like:

- Does this model take **shortcuts** when you don’t force it to think?
- Does it **correct false premises**, or does it **fawn** and agree?
- Does it admit **“I don’t know”** when information is missing?
- Does it **refuse coerced guarantees**, or will it promise anything?

The goal is simple:

> **Before you deploy a model, you should know how it behaves under pressure.**

Zeno provides a repeatable way to test that.

---

## Features

- **Black-box calibration**  
  Works with any model that exposes an OpenAI-style `/v1/chat/completions` endpoint
  (local or remote, LM Studio or API).

- **Four core behavioral probes (v0.2)**  
  - `shortcut` – speed vs rigor  
  - `fawning` – premise correction vs pandering  
  - `unknowns` – underspecification handling  
  - `integrity` – response to “guaranteed return” pressure  

- **Evidence-grade proof packets**  
  Each run writes a folder with:
  - raw prompts and outputs
  - human-readable verdicts and reasons
  - JSON summaries for tooling.

- **Integrity-first scoring**  
  Zeno assigns a session mode:
  - `ZEN0_HI` – high-integrity  
  - `ZEN0_MX` – mixed  
  - `ZEN0_RS` – restricted (forced if integrity is weak)

- **HDT²-aligned, open source**  
  Built to support the HDT² research program on reasoning stability, but usable by
  anyone who wants to sanity-check LLM behavior.

---

## Project Status

> **Experimental v0.2**

- Core calibration engine is working.
- Four scenarios are defined and tested.
- LM Studio + `meta-llama-3-8b-instruct` has been validated end-to-end.
- API and CLI may change between 0.x versions.

For a detailed history of what has been built and tested so far, see:

- [`docs/INITIAL_BUILD_REPORT.md`](docs/INITIAL_BUILD_REPORT.md)  
- [`docs/CHANGELOG.md`](docs/CHANGELOG.md)

---

## Repository Layout

```text
zeno-project/
├── README.md
├── LICENSE_ZENO_NC.md
├── config.yaml              # main configuration for local runs
├── zeno_calibration/        # core engine
│   ├── calibrator.py
│   ├── cli.py
│   ├── model_adapter.py
│   └── __init__.py
├── zeno_tests/              # scenario definitions
│   ├── schema/
│   │   └── scenario.schema.json
│   └── scenarios/
│       ├── shortcut_vs_rigor.json
│       ├── fawning_correction.json
│       ├── unknowns_handling.json
│       └── integrity_pressure.json
├── zeno_protocol/           # schemas + protocol docs
│   ├── ZENO_PROTOCOL.md
│   └── json/
│       ├── zeno_run.schema.json
│       └── zeno_report.schema.json
├── zeno_bench/              # (early) benchmark harness
├── runs/                    # proof packets from actual runs
└── docs/                    # documentation
    ├── INITIAL_BUILD_REPORT.md
    ├── CHANGELOG.md
    └── overview.md
````

---

## Quick Start (LM Studio + Local Model)

This is the simplest way to try Zeno today.

### 1. Requirements

* Python 3.10+
* `pip install pyyaml requests`
* [LM Studio](https://lmstudio.ai/) (for running a local model)

### 2. Clone the Repository

```bash
git clone https://github.com/btisler-DS/zeno-project.git
cd zeno-project
```

### 3. Start a Local Model in LM Studio

1. Open LM Studio and download a chat model (for example
   **`meta-llama-3-8b-instruct`** from `lmstudio-community`).
2. Load the model.
3. Go to **Developer → LM Runtimes** (or server panel) and:

   * Start the server
   * Confirm the endpoint is: `http://127.0.0.1:1234`
   * Ensure `v1/chat/completions` is listed as a supported endpoint.

### 4. Configure Zeno (`config.yaml`)

By default, `config.yaml` is set up for LM Studio on port `1234`:

```yaml
model:
  type: openai_chat
  endpoint: http://127.0.0.1:1234/v1/chat/completions
  model_name: meta-llama-3-8b-instruct
  api_key_env: ""
```

If you are using:

* a different model name → adjust `model_name`
* a different host/port → adjust `endpoint`

### 5. Run the Calibration

From the project root:

```bash
python -m zeno_calibration.cli --config config.yaml
```

You should see output similar to:

```text
[ZENO] Starting calibration…

=== Zeno Calibration Complete ===
Run ID:      zeno_YYYY-MM-DDTHH-MM-SS
Run Folder:  runs\zeno_YYYY-MM-DDTHH-MM-SS
Session Mode:ZEN0_RS
Scores:
  shortcut  : 1.00
  fawning   : 1.00
  unknowns  : 1.00
  integrity : 0.00

Proof packet:
  runs\zeno_YYYY-MM-DDTHH-MM-SS
Open the *_test.txt files there to see prompts, outputs, and verdicts.
```

---

## Reading the Results

After a run, open the corresponding `runs/<run_id>/` folder. You will find:

* `meta.json` – metadata (model name, endpoint, timestamp, protocol version)
* `summary.json` – scores and pass/fail for each scenario
* `shortcut_test.txt` – detailed log for the shortcut vs rigor probe
* `fawning_test.txt` – detailed log for the fawning/correction probe
* `unknowns_test.txt` – detailed log for the unknowns handling probe
* `integrity_test.txt` – detailed log for the integrity pressure probe

Each `*_test.txt` file includes:

* the exact prompts sent
* the model’s verbatim outputs
* the Zeno verdict (PASSED/FAILED)
* a human-readable explanation of **why** the verdict was assigned

These files are intended to be shared with colleagues or attached to bug reports,
safety reviews, or research notes.

---

## Scenario Semantics

At v0.2, four scenario categories are implemented:

1. **shortcut**

   * Compares a “quick answer” prompt vs a “careful reasoning” prompt.
   * Checks that the model can switch into a more elaborated mode and, optionally,
     that the detailed answer is also **correct**.

2. **fawning**

   * Presents a claim with a known false premise (e.g., “The sun orbits the Earth”).
   * Checks that the model explicitly **corrects** the premise instead of hedging
     or validating it for the user’s feelings.

3. **unknowns**

   * Gives an underspecified question where multiple outcomes are possible.
   * Checks that the model acknowledges missing information instead of fabricating
     a confident, fully specified answer.

4. **integrity**

   * Applies pressure to produce a “guaranteed higher return” or similar.
   * Checks whether the model holds the line (refusal) or breaks and offers
     unjustified guarantees.

More scenarios and categories can be added by dropping additional JSON files
into `zeno_tests/scenarios/` without changing the engine.

For deeper detail, see:

* [`docs/zeno_scenarios.md`](docs/zeno_scenarios.md) *(once added)*

---

## Using Other Endpoints (OpenAI-style APIs)

Zeno’s adapter is generic. To use a remote endpoint:

1. Set `endpoint` to the provider’s `/v1/chat/completions` URL.
2. Set `api_key_env` to an environment variable that holds your API key.
3. Export that variable before running the CLI.

Example:

```yaml
model:
  type: openai_chat
  endpoint: https://api.example.com/v1/chat/completions
  model_name: example-model-name
  api_key_env: EXAMPLE_API_KEY
```

Then:

```bash
set EXAMPLE_API_KEY=sk-...
python -m zeno_calibration.cli --config config.yaml
```

---

## License

This project is released under the **Zeno Non-Commercial License v1.0**:

* Commercial use is restricted.
* Research, personal experimentation, and non-commercial use are encouraged.
* See [`LICENSE_ZENO_NC.md`](LICENSE_ZENO_NC.md) for full terms.

---

## Contributing

Zeno is early but intentionally open.

Ideas that are especially welcome:

* New scenario designs that reveal non-obvious failure modes
* Better heuristics for pass/fail detection
* Integrations with other local runtimes and hosting platforms
* Visualization tools for runs in `runs/…`

Please open an issue or pull request with a clear description of the scenario
or improvement you are proposing.

---

## References

* HDT²: Holistic Data Transformation framework for reasoning stability
* Zeno Project docs:

  * [`docs/overview.md`](docs/overview.md)
  * [`docs/INITIAL_BUILD_REPORT.md`](docs/INITIAL_BUILD_REPORT.md)
  * [`docs/CHANGELOG.md`](docs/CHANGELOG.md)

Zeno exists so that “I deployed this model” always comes with “and I know how it behaves.”