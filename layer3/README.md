# Layer 3 — MCP Tool Execution Plane

**Status:** ✅ Tool Response Screener built and wired · rest conceptual

## Purpose
Where tool calls actually execute (APIs, databases, file systems) and,
critically, where every **tool response is screened for indirect prompt
injection (IPI) before it is trusted as clean context.** The Screener does
not block — it tags a response as flagged and lets it flow on to the Causal
Analyzer (3B), which forces causal evaluation even on otherwise low-impact
tools.

## Files
| File | Purpose | Status |
| :--- | :--- | :--- |
| `tool_response_screener.py` | Two independent checks: an LLM semantic scanner **and** a deterministic keyword backstop (`KEYWORD_MARKERS`). A response is flagged if *either* fires — this backstop exists because small local models sometimes write a correct diagnosis in prose while emitting the wrong structured verdict (root README Section 5). | ✅ Built, wired into pipeline |
| `__init__.py` | Package marker | ✅ |

## What's done
- LLM + keyword dual screening with disagreement logging
- Wired into `adaptishield_pipeline.py` ahead of the Policy Engine
- `ScreenResult.matched_markers` reports **every** keyword marker that hit,
  not just the first, and the pipeline forwards it into `EpisodeRecord`
  alongside a truncated mediator snippet. Component 3D consumes these as
  candidate `blocked_patterns`, so it needs the full set — and a flagged
  response with an *empty* marker list is itself the signal that the
  injection's phrasing has drifted away from `KEYWORD_MARKERS`.

## What's pending
- The actual tool-execution surface (APIs / DBs / file systems) is
  simulated in tests today — there is no live MCP tool execution yet.
  Real command execution now happens in a gated sandbox at **Layer 4**
  (`layer4/sandbox.py`), not here.

## Run standalone
```bash
python3 layer3/tool_response_screener.py   # clean vs FLAGGED test cases
```
