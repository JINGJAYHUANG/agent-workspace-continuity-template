# Keep an AI project moving between sessions
## 让 AI 换一个会话，也能接着做项目

[Full documentation](README.md) · [Public tool collection](https://github.com/JINGJAYHUANG/JINGJAYHUANG)

**For:** people using coding agents on a project across multiple sessions.  
**Input:** a local project folder and short, maintained state files.  
**Output:** an inspectable handoff and recovery brief: objective, verified state, unresolved risks and next action.

A useful handoff is smaller than an entire chat history. This tool helps keep that handoff in the project, alongside the work.

## First example: preview, do not overwrite

Requires Python 3.11 or newer. Use an isolated Python environment before installing from source.

```bash
git clone https://github.com/JINGJAYHUANG/agent-workspace-continuity-template.git
cd agent-workspace-continuity-template
python -m venv .venv
```

Activate it with `source .venv/bin/activate` on macOS/Linux, or `.venv\Scripts\Activate.ps1` in Windows PowerShell. Then:

```bash
python -m pip install -e .
mkdir demo-project
awc init ./demo-project --profile project
```

The last command is a preview. It does not apply the scaffold. Inspect the proposal before the optional next step:

```bash
awc init ./demo-project --profile project --apply
awc doctor ./demo-project --strict
awc recover ./demo-project
```

`doctor` may identify fields that still need real project information. A newly created template is not proof that the underlying project has been verified.

## What you should understand after the example

The workspace separates stable instructions from current state. `AGENTS.md` describes working rules; `.agent/brief.md`, `.agent/status.md` and `.agent/handoff.md` help a new session recover the work. Optional planning and decision files add detail when needed.

把“已验证”“继承但未复核”“仍未知”分开记录，比把旧结论反复复制更有用。先在 demo-project 试，不要直接对整个电脑或含私密资料的大目录初始化。

## A practical use case

Before ending a session, record what changed, how it was checked and what remains blocked. At the next session, recover that state and verify the relevant source files before continuing. Keep private logs and sensitive context out of a public repository.

## Boundaries

This is a local continuity tool, not cloud synchronization, a project backup, or a security sandbox. Markdown instructions cannot enforce permissions. Optional hooks are not enabled by this guide; inspect and merge their settings separately.

For complete commands, synthetic examples, conflict behavior and verification procedures, see the [README](README.md). This onboarding page follows the default-branch documentation reviewed on 2026-09-05; it does not certify a new test run in your environment.
