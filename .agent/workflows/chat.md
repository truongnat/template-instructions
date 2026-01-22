---
description: Communication - Multi-Agent Chat - Facilitate a group discussion among agents
---

# Multi-Agent Chat Workflow

This workflow instantiates a group chat session where multiple agents can discuss a topic, debate solutions, or brainstorm ideas.

## 1. Initialize Room
Create a context window (chat room) for the session.

## 2. Invite Participants
Select relevant agents based on the topic:
- Example: @PM, @DEV, @UIUX for a feature kickoff.

## 3. Moderated Discussion
The @BRAIN or User acts as a moderator:
- **Round 1**: Opening statements/ideas.
- **Round 2**: Rebuttals or refinements.
- **Round 3**: Conclusion.

## 4. Summarize
Generate a meeting minute or summary decision document.

## Usage
`/chat "Discuss the pros and cons of using GraphQL vs REST for our new API"`
