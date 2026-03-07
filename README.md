# Multi-Agent PRD Reviewer - Slack Bot

AI-powered Slack bot using multiple specialized agents to provide comprehensive Product Requirements Document reviews. Combines rule-based validation from my years of experience in building elaborate PRDs with AI-driven technical critique.

The purpose is for PMs to push our PRDs to excellence before a Principal engineer or a Lead SE reviews and starts the architecture decisions and commentary.

## 🎯 The Problem

PRD quality varies wildly across product teams:
- ❌ Manual reviews take 1+ hour
- ❌ Quality depends on reviewer's expertise/ time / constraints and limitations identified 
- ❌ Technical risks often missed until engineering starts and many gaps with business knowledge or design decisions can stall us
- ❌ Doesn't scale across 10+ product managers

## ✨ The Solution

Multi-agent AI system that reviews PRDs in seconds:

**Agent 1: Validator**
- Validates completeness against 12 quality standard sections (what modern PRDs should be featuring anyways)
- Scores 0-100 based on weighted sections
- Flags missing critical sections

**Agent 2: Skeptical Tech Lead**
- Challenges assumptions with domain expertise
- Identifies hidden complexity and risks
- Probes feasibility and edge cases
- Asks tough questions PMs often miss

**Orchestrator**
- Coordinates agents autonomously
- Synthesizes findings into comprehensive review
- Posts permanent results in Slack for team visibility

## 📊 Real-World Impact

**Before:**
- 30-minute manual PRD review
- Inconsistent quality across team
- Technical gaps discovered during build (costly rework)

**After:**
- 30-second automated review
- Consistent quality standards enforced
- Risks surfaced before engineering starts

**Example finding:**
> PRD assumed "Apple Pay is trusted" without contingency plan. Skeptic agent asked: "What happens when Apple deprecates this API? What's your migration path?" Caught critical gap pre-engineering, saved 2+ weeks of rework.

## 🚀 Usage

### In Slack
```
/review-prd
# Your PRD Title

## Executive Summary
[Your content here]

## Success Metrics
[Your metrics]

... [rest of PRD]
```

### Output

Bot posts permanent message with:
- **Validation Results:** Score, missing sections, completeness
- **Technical Critique:** AI-generated questions challenging assumptions
- **Overall Recommendation:** Ready/Needs Iteration/Not Ready
- **Author Attribution:** PM's name visible for accountability

## 🏗️ Architecture
```
User runs /review-prd in Slack
    ↓
Slack → Render (Flask server)
    ↓
Agent 1: Validator
    - Rule-based completeness check
    - Scores against YAML template
    ↓
Agent 2: Skeptical Tech Lead (Claude AI)
    - Reviews PRD + validation results
    - Challenges assumptions
    - Identifies risks
    ↓
Orchestrator synthesizes both
    ↓
Posts permanent formatted message to Slack
```

## 🛠️ Tech Stack

- **Python 3.11**
- **Slack Bolt SDK** - Slack integration
- **Anthropic Claude API** - AI-powered tech lead agent (Sonnet 4)
- **Flask** - Web server
- **YAML** - Template configuration
- **Render** - Deployment platform

## 📁 Project Structure
```
multi-agent-prd-reviewer-slack/
├── app.py                      # Main Slack bot + orchestrator
├── agents/
│   ├── validator_agent.py      # Rule-based completeness validator
│   └── skeptic_agent.py        # AI-powered technical challenger
├── formatters/
│   └── slack_formatter.py      # Slack Block Kit formatting
├── prompts/
│   └── skeptic_system.txt      # Tech lead persona & expertise
├── templates/
│   └── prd_template.yaml       # Quality standards
├── requirements.txt
└── README.md
```

## 🎓 What I Learned

**Multi-Agent Systems:**
- Agent specialization and coordination
- Passing structured context between agents
- Prompt engineering for different personas
- Sequential vs parallel agent execution

**Production Engineering:**
- Slack bot architecture and deployment
- Error handling for API failures
- Token usage optimization (~1200 tokens/review)
- Rate limiting and graceful degradation

**Business Impact:**
- Encoding PM judgment into autonomous systems
- Scaling expertise across teams without hiring
- Catching issues pre-build (10x ROI on rework prevention)
- Creating institutional knowledge that survives turnover

## 🔮 Future Enhancements

- [ ] Batch processing (review 10+ PRDs at once)
- [ ] Historical tracking (quality trends over time)
- [ ] Team leaderboard (gamify PRD quality)
- [ ] Agent 3: Design reviewer (UX considerations)
- [ ] Agent 4: Compliance checker (GDPR, PCI)
- [ ] Integration with Confluence/Notion
- [ ] PDF report generation
- [ ] Custom agent personalities per team/domain

## 🔗 Related Projects

- **[Multi-Agent PRD Reviewer (CLI)](https://github.com/dimospapadopoulos/multi-agent-prd-reviewer)** - V1: Command-line version
- **[PRD Validator (Slack)](https://github.com/dimospapadopoulos/prd-validator-slack)** - Single-agent predecessor
- **[PRD Validator (CLI)](https://github.com/dimospapadopoulos/prd-completeness-validator)** - Original validation engine
- **[Voice of Customer Synthesizer](https://github.com/dimospapadopoulos/voc-portfolio-clean)** - Customer feedback automation
- **[Custom PM Skills](https://github.com/dimospapadopoulos/custom-pm-skills)** - Claude AI skills library

## 📈 Portfolio Evolution

**Project Progression:**
1. PRD Validator (CLI) → Individual tool
2. PRD Validator (Slack) → Simple tool deployed as a single agent / output shown to PM and then deleted / not stored in Slack
3. Multi-Agent Reviewer (CLI) → Dual agents, advanced
4. **Multi-Agent Reviewer (Slack)** → Production, team-facing, agentic AI

**Shows:** V1→V2 iteration, CLI→Team integration, Single→Multi-agent, Individual→Organizational impact

"NOTE: This is the public portfolio version. 
The production version is private and includes company-specific enhancements."

---

**Built by:** Dimos Papadopoulos  
**Role:** Product Leader/ Builder 
**Why:** To scale PM expertise through autonomous AI agents that never sleep  
**License:** BSD-3 (name attribution)
**Deployment:** Live on Render  
**Status:** Production (serving 10+ PMs)  
**Cost:** ~$15/month (API calls only, hosting free)
