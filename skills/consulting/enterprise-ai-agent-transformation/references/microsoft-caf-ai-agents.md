# Microsoft Cloud Adoption Framework — AI Agent Adoption Guidance

**Source:** https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai-agents/

## 4-Phase Framework

### (1) Plan for Agents
- Business case definition with measurable outcomes
- Use case selection: efficiency, speed, scalability
- Agent types → Productivity (retrieval), Action (task execution), Automation (multi-step)

### (2) Govern & Secure Agents
- Risk assessment framework
- Role-based access control (RBAC)
- Audit trails for every agent action
- Compliance alignment (regulatory)
- Explainability requirements

### (3) Build Agents
5 core components:
- **Generative AI Model** — reasoning engine
- **Instructions** — scope, boundaries, behavioral guidelines
- **Retrieval** — grounding data and context (reduces hallucinations)
- **Actions** — functions, APIs, or systems to perform tasks
- **Memory** — conversation history and state for multi-turn tasks

### (4) Manage Agents
- Monitoring, lifecycle management
- Continuous refinement
- Feedback loops between business users and engineering

## 3 Agent Types
| Type | Capability | Tools Used |
|------|-----------|------------|
| **Productivity** | Information retrieval + synthesis | Knowledge tools only |
| **Action** | Specific tasks within workflows | Knowledge + Action tools |
| **Automation** | Complex multi-step processes | Knowledge + Action + Triggers |
