# Governance Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the persisted review/research governance layer on top of the minimal runtime, so human approval becomes an enforced runtime boundary rather than a documentation rule.

**Architecture:** Add two queue stores under the existing `.llm-wiki/state/` runtime surface: one for `ReviewItem`, one for `ResearchTask`. Review items can be imported from generation artifacts and moved through explicit status transitions. Research tasks can only be queued from approved review items unless an explicit override is used.

**Tech Stack:** Python 3.9+, `dataclasses`, `pathlib`, `yaml` via `PyYAML`, existing `ReviewItem` and `ResearchTask` models, existing `pytest` harness, existing runtime artifact directories.

---
