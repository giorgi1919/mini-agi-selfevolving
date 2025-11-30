# Mini-AGI Self-Evolving Engine

This project is an experimental **self-improving code system**.

### Goals
- The system reads its own modules.
- Generates improved versions.
- Tests the new version.
- Evaluates safety and performance.
- If it passes — replaces the old module.
- If not — performs rollback.

### Directories
- `manager/` — Controls the self-evolving loop  
- `worker/` — Executes generated code versions  
- `plugins/` — Logic blocks that can be evolved  
- `tests/` — Validation scripts run before applying updates  

### Minimal Safety Rules
The system **cannot**:
- Modify manager core itself
- Access internet
- Perform filesystem writes outside the project
- Import forbidden modules (os, subprocess, requests, etc.)

### Run
