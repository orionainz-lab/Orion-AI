"""
LLM Response Parsing Utilities

This module contains utilities for parsing LLM responses.
Separated from llm_clients.py for 200-line rule compliance.
"""

import re
from typing import Tuple, List


def parse_plan_response(content: str) -> Tuple[str, List[str]]:
    """Parse plan and requirements from LLM response."""
    plan = ""
    requirements = []
    
    # Extract PLAN section
    plan_match = re.search(r"PLAN:\s*\n(.+?)(?=REQUIREMENTS:|$)", content, re.DOTALL)
    if plan_match:
        plan = plan_match.group(1).strip()
    else:
        # Fallback: use entire content
        plan = content.strip()
    
    # Extract REQUIREMENTS section
    req_match = re.search(r"REQUIREMENTS:\s*\n(.+)", content, re.DOTALL)
    if req_match:
        req_text = req_match.group(1)
        # Parse bullet points
        for line in req_text.split("\n"):
            line = line.strip()
            if line.startswith("- "):
                requirements.append(line[2:])
            elif line.startswith("* "):
                requirements.append(line[2:])
    
    return plan, requirements


def extract_code_from_response(content: str) -> str:
    """Extract code from LLM response, removing markdown formatting."""
    # Remove markdown code blocks if present
    code_block_pattern = r"```(?:python|py)?\s*\n(.*?)```"
    match = re.search(code_block_pattern, content, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    # If no code block, return content as-is (already code)
    return content.strip()


def extract_imports(code: str) -> List[str]:
    """Extract import statements from code."""
    imports = []
    
    for line in code.split("\n"):
        line = line.strip()
        if line.startswith("import ") or line.startswith("from "):
            imports.append(line)
    
    return imports
