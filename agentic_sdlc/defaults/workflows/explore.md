---
description: Process - Deep Investigation Workflow (HeavySwarm Pattern)
---

# /explore - HeavySwarm Protocol

The `/explore` workflow follows a 5-phase **HeavySwarm** pattern for deep investigation and complex architectural decisions.

## ⚠️ STRICT EXECUTION PROTOCOL (MANDATORY)
1. **USE BEFORE PLANNING:** Run before major architectural decisions.
2. **HEAVY SWARM:** Utilize multi-agent collaboration for deep insights.
3. **EVIDENCE-BASED:** All findings must have supporting evidence.
4. **DOCUMENT FINDINGS:** Create exploration report.

---

## HeavySwarm Phases

### Phase 1: Discovery Swarm (Parallel Research)
**Roles:** @RESEARCH + @SA + @SECA
**Action:** Run parallel research on the topic.

```bash
agentic-sdlc brain concurrent --roles "RESEARCH,SA,SECA" --task "Research [Topic]" \
  --command "agentic-sdlc brain research --task '{TASK}' --type general"
```

- [ ] Identify state-of-the-art solutions
- [ ] List technical constraints
- [ ] Gather security benchmarks

### Phase 2: Analysis Swarm (Multi-Order Thinking)
**Roles:** @SA + @BA + @DEV
**Action:** Apply multi-order analysis to discovery findings.

```bash
agentic-sdlc brain concurrent --roles "SA,BA,DEV" --task "Analyze Findings for [Topic]"
```

- **1st Order:** Surface requirements
- **2nd Order:** Dependencies & ripple effects
- **3rd Order:** Long-term maintenance & scalability

### Phase 3: Debate Swarm (Multi-Agent Group Chat)
**Roles:** @SA + @DEV + @TESTER + @PO
**Action:** Debate the findings and proposed approaches to find edge cases.

```bash
agentic-sdlc brain chat --topic "Debate implementation of [Topic]" --agents "SA,DEV,TESTER,PO" --turns 5
```

- [ ] Challenge assumptions
- [ ] Identify hidden risks
- [ ] Explore alternative perspectives

### Phase 4: Synthesis Swarm (MixtureOfAgents)
**Roles:** @BRAIN (Aggregator)
**Action:** Synthesize all previous phases into a unified recommendation.

```bash
agentic-sdlc brain synthesize --concurrent-result latest --strategy llm
```

- [ ] Resolve contradictions from debate
- [ ] Consolidate key insights
- [ ] Formulate final recommendations

### Phase 5: Conclusion & Report
**Roles:** @REPORTER
**Action:** Generate the official Exploration Report.

```bash
agentic-sdlc brain gen exploration-report '{"topic": "[Topic]", "results": "..."}'
```

---

## Output Template: `Exploration-Report-[Topic].md`

```markdown
# Exploration Report: [Topic]

## 1. Discovery Summary
(Synthesis of Phase 1)

## 2. Multi-Order Impact Analysis
(Synthesis of Phase 2)

## 3. Debate Highlights & Risk Assessment
(Synthesis of Phase 3)

## 4. Final Recommendations
(Synthesis of Phase 4)

## 5. Implementation Roadmap
(Actionable steps for next phases)
```

#explore #heavyswarm #multi-agent #analysis #deep-dive
