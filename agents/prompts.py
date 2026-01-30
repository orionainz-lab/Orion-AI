"""
LLM Prompt Templates

This module contains prompt templates for code generation.
Separated from llm_clients.py for 200-line rule compliance.
"""

# Plan generation prompt
PLAN_PROMPT_TEMPLATE = """Analyze this coding task and create a brief execution plan.

Task: {task}
{context_section}
Provide a response in the following format:

PLAN:
[2-3 sentences describing what the code should do, the approach, and key considerations]

REQUIREMENTS:
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]
"""

# Code generation prompt
CODE_PROMPT_TEMPLATE = """Generate {language} code for this task.

Task: {task}

Plan: {plan}
{feedback_section}
Requirements:
- Code must be syntactically valid {language}
- Include all necessary imports at the top
- Use type hints for function parameters and return values
- Include a brief docstring
- Follow best practices for {language}

Output ONLY the code, with no explanations or markdown code blocks.
Start directly with the code (imports first if needed):"""
