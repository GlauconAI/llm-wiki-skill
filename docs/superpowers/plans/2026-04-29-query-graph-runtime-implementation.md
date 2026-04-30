# Query And Graph Runtime Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic query runtime with bounded context assembly, plus explainable graph relevance and insight helpers.

**Architecture:** Keep the lexical retrieval path as the default query backend, then layer a context assembler and runtime wrapper on top. For graph work, add simple deterministic heuristics over the existing graph structure instead of opaque scoring or external dependencies.

**Tech Stack:** Python 3.9+, `dataclasses`, `pathlib`, existing query retrieval helpers, existing graph build output, `pytest`.

---
