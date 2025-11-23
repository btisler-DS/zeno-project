---

# **3. `docs/overview.md`**

```markdown
# Zeno Project – Overview

Zeno is an open-source diagnostic framework built to evaluate the behavioral stability of Large Language Models (LLMs) using structured scenarios.

It is designed to expose:
- shortcut reasoning vs rigorous reasoning
- fawning vs correction-of-premise
- handling of underspecified questions
- integrity degradation under coercion

Zeno does **not** require access to model internals and behaves as an entirely black-box evaluator.

---

## Why Zeno Exists

HDT² testing revealed that LLMs often:
- appear logical but produce false “rigor”
- correct premises inconsistently
- hallucinate details when information is missing
- overstate confidence under social, emotional, or coercive pressure

Zeno is the tool to surface these patterns systematically.

---

## Core Components

### 1. Calibration Engine (`zeno_calibration/`)
Runs scenarios and produces:
- raw outputs
- pass/fail verdicts
- reasoning explanations
- a proof packet directory

### 2. Zeno Protocol (`zeno_protocol/`)
JSON schemas describing:
- run metadata  
- test results  
- proof packet structure  

### 3. Scenarios (`zeno_tests/`)
Initial four include:
- shortcut vs rigor
- fawning correction
- unknowns handling
- integrity pressure

More can be added without modifying the engine.

### 4. Model Adapters
Zeno currently supports:
- LM Studio (via REST API)
- OpenAI-style HTTP endpoints
- Any local model exposing a `/v1/chat/completions` route

---

## Output: The Zeno Proof Packet

Each run produces:
```

meta.json
summary.json
shortcut_test.txt
fawning_test.txt
unknowns_test.txt
integrity_test.txt

```

These files form an evidence-grade calibration report.

---

## Mode Assignment

Zeno assigns a session mode based on scores:

- **ZEN0_HI** – high-integrity reasoning  
- **ZEN0_MX** – mixed behavior  
- **ZEN0_RS** – restricted  
  (forced if integrity < 0.4)

Integrity dominates all other dimensions.

---

## Roadmap

### v0.3
- Extended benchmarks  
- Batch model comparison  
- Entropy-aligned scoring  
- CLI improvements

### v0.4
- GUI calibration dashboard  
- Live signal monitoring  

### v1.0
- Full HDT² integration  
- Research-grade statistical calibration  

---

Zeno provides the structural foundation for inspecting LLM behavior before deployment, ensuring users know what a model will do under pressure, ambiguity, or bias.

```

