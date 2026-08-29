# Threat Model

## Assets protected

- credentials and tokens;
- personal or customer data;
- private project names and paths;
- proprietary source, strategies, and operational state;
- integrity of pre-existing repository instructions;
- the user’s ability to start and stop an agent session.

## Trust assumptions

AWC assumes the local user can read the workspace and intentionally runs the CLI. It does not defend against a fully compromised operating system, a malicious administrator, or an agent with unrestricted access ignoring all instructions.

## Threats and controls

| Threat | Control | Residual risk |
|---|---|---|
| Installer overwrites project rules | Preview default; conflicts become local proposals | A human can still merge a bad proposal |
| Old claims become “verified” | Mandatory evidence sections and doctor checks | Labels can be written dishonestly |
| Umbrella root causes broad scanning | Explicit non-recursive profile rules | An agent can ignore contextual guidance |
| Hooks retain raw model content | Length/hash-only event rows | Hashes may still correlate identical content |
| Stop hook creates continuation loop | No Stop decision or additional context | Other installed hooks may still continue |
| Machine paths leak into a public repository | Privacy scan for common user-home patterns | Unusual path forms can evade regex checks |
| Credentials are committed | Common secret-pattern scan and release gate | No scanner detects every credential format |
| Local metadata is committed | `.agent/.gitignore` rules and doctor checks | Force-add can bypass ignore rules |
| Runtime snapshot reveals project layout | Counts only; no names or absolute paths | Counts can still reveal approximate scale |
| Generated context is treated as proof | Recovery warning and evidence labels | Model behavior remains probabilistic |

## Non-goals

AWC is not:

- a secrets manager;
- a sandbox or mandatory access-control system;
- an encrypted store;
- a transcript redaction service;
- a multi-machine synchronization protocol;
- a backup or disaster-recovery system;
- a guarantee that an AI agent follows instructions.

Use operating-system permissions, version control, secret scanning, sandboxing, and human review alongside AWC.
