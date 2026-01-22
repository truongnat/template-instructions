---
description: Intelligence - MoA Synthesis - Mixture of Agents synthesis for high-quality outputs
---

# Mixture of Agents (MoA) Synthesis Workflow

This workflow implements the Mixture of Agents pattern to generate high-quality outputs by synthesizing responses from multiple models or agents.

## 1. Propose
Generate initial proposals from multiple diverse agents (e.g., @DEV, @SA, @SECA).

## 2. Critique
Have each agent critique the proposals of the others.

## 3. Synthesize
Aggregator agent (@BRAIN or @ORCHESTRATOR) reviews all proposals and critiques to create a single, superior solution.

## 4. Verify
Final verification of the synthesized output against requirements.

## Usage
`/synthesize "Propose a secure and scalable database schema for the user data module"`
