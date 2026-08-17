# OpenRoot Copilot Instructions
# Matches GitHub Copilot recommended workflow (repo-wide)
# Foundational for every script and every spoke node

## Project Overview
OpenRoot is an offline-first, open-source appropriate-technology lattice for raising the bottom floor of human capability.
Core law: η = useful_joules / human_joules
R = 1.0 (Agape) zeros coordination cost.
Serve the lowest node first.
No patents. Ever. Absolute paths only.

## Tech Stack
- Phone-native: Samsung Galaxy A15 + Termux + Shizuku/rish
- Heavy spoke: OptiPlex Debian + local llama.cpp
- Materials: AeroCement (AR-GFRC), Black Locust RMH, ferrocement
- Token: ACRE (minted only on verified physical work + Merkle)
- Network: Syncthing + IPFS + BLE mesh + sneakernet
- Governance: R=1.0 fractal swarm (base-6)

## Absolute Path Discipline (non-negotiable)
- Never emit or accept tilde
- Prefer /sdcard/openroot/... and /data/data/com.termux/files/home/...
- All scripts must load PATH_INVENTORY.yaml first
- Single source of truth: /sdcard/openroot/context_bridge/context.json

## Coding Guidelines
- Shebang + executable bit on every script
- SHA-256 footer on critical files
- YAML frontmatter with agape_score on Markdown
- Prefer pure stdlib Python on the phone
- One-hot RAM discipline (3.5 GB usable)
- Degrade cleanly when rish is absent

## Workflow Priority (A → B → C)
1. A — Infrastructure: PATH_INVENTORY, .coderabbit.yaml, copilot-instructions.md, CI, CODEOWNERS
2. B — Kernel Loading: local LLM, vector index, context_bridge
3. C — Mesh Networking: Syncthing, IPFS, peer discovery

## Agape Alignment Checklist (every change)
- [ ] Increases η?
- [ ] Preserves Merkle integrity?
- [ ] Absolute and deterministic paths?
- [ ] Amplifies Agape or feeds entropy?

## Required Files in Every Repo
- PATH_INVENTORY.yaml (root)
- .coderabbit.yaml (root) — free Pro for public OSS
- .github/copilot-instructions.md
- .github/workflows/openroot-ci.yml
- .github/CODEOWNERS

## Response Style When Generating Code
- Dense, high-η, terminal-ready blocks
- Absolute paths only
- No explanatory comments the shell will execute
- Serve the least among us
