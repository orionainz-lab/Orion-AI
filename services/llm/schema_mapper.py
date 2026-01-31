"""
LLM Schema Mapper

Uses Claude 3.5 Sonnet to analyze API documentation and suggest field mappings.
"""

from typing import Dict, List, Any, Optional
import json
from pydantic import BaseModel


class MappingSuggestion(BaseModel):
    """Suggested field mapping with confidence"""
    source_path: str
    confidence: float  # 0.0 to 1.0
    transformation: Optional[str] = None
    reasoning: str


class SchemaMapper:
    """
    LLM-powered schema mapping assistant.
    
    Analyzes API documentation and sample responses to suggest
    field mappings to the unified schema.
    """
    
    SCHEMA_MAPPING_PROMPT = """
You are an expert API integration engineer. Analyze the provided API response and suggest mappings to our UnifiedCustomer schema.

API Response Sample:
{sample_response}

Target UnifiedCustomer Schema:
- email (required): EmailStr - Customer's email address
- name (required): str - Full name of the customer
- phone (optional): str - Phone number
- company (optional): str - Company name
- billing_address (optional): UnifiedAddress
  - street: str
  - street2: str (optional)
  - city: str
  - state: str
  - postal_code: str
  - country: str
- tags (optional): List[str] - Category tags
- custom_fields (optional): Dict[str, Any] - Additional fields

Provide a JSON mapping with the following format:
{{
  "field_name": {{
    "source_path": "path.to.field",  // Use dot notation for nested fields
    "confidence": 0.95,                // 0.0 to 1.0
    "transformation": "function_name or null",  // e.g., "split_name", "format_phone"
    "reasoning": "why this mapping"
  }}
}}

Guidelines:
1. Only map fields that exist in the sample response
2. Use confidence scores: 1.0 (exact match), 0.9 (very likely), 0.7 (probable), 0.5 (guess)
3. Suggest transformations for: name splitting, phone formatting, address parsing
4. If multiple source fields could map to one target, choose the best one
5. Return valid JSON only, no markdown or explanation outside JSON

Return the mapping JSON:
"""
    
    def __init__(self, llm_client):
        """
        Initialize schema mapper.
        
        Args:
            llm_client: LLM client (e.g., Anthropic Claude)
        """
        self.llm = llm_client
    
    async def discover_schema(
        self,
        sample_response: dict,
        api_docs: Optional[str] = None
    ) -> Dict[str, MappingSuggestion]:
        """
        Analyze API response and suggest field mappings.
        
        Args:
            sample_response: Sample JSON response from API
            api_docs: Optional API documentation context
        
        Returns:
            Dictionary of field_name -> MappingSuggestion
        """
        # Format sample response
        sample_json = json.dumps(sample_response, indent=2)
        
        # Build prompt
        prompt = self.SCHEMA_MAPPING_PROMPT.format(
            sample_response=sample_json
        )
        
        if api_docs:
            prompt += f"\n\nAdditional API Documentation:\n{api_docs[:2000]}\n"
        
        try:
            # Call LLM (assumes Anthropic Claude API)
            response = await self.llm.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract JSON from response
            content = response.content[0].text
            
            # Parse JSON (handle potential markdown wrapping)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            mapping_data = json.loads(content.strip())
            
            # Convert to MappingSuggestion objects
            suggestions = {}
            for field_name, mapping in mapping_data.items():
                suggestions[field_name] = MappingSuggestion(**mapping)
            
            return suggestions
        
        except Exception as e:
            raise ValueError(f"LLM schema mapping failed: {str(e)}")
    
    async def generate_transformation_code(
        self,
        field_name: str,
        source_field: str,
        sample_values: List[Any],
        target_format: str
    ) -> str:
        """
        Generate Python transformation function.
        
        Args:
            field_name: Target field name
            source_field: Source field path
            sample_values: Sample values from API
            target_format: Description of target format
        
        Returns:
            Python function code as string
        """
        prompt = f"""
Generate a Python function to transform this field:

Field: {field_name}
Source: {source_field}
Sample Values: {sample_values}
Target Format: {target_format}

Return ONLY the Python function code, no explanation:

def transform_{field_name}(value):
    # Your code here
    return transformed_value
"""
        
        try:
            response = await self.llm.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            code = response.content[0].text
            
            # Extract function code
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0]
            elif "```" in code:
                code = code.split("```")[1].split("```")[0]
            
            return code.strip()
        
        except Exception as e:
            raise ValueError(f"Code generation failed: {str(e)}")
    
    async def validate_mapping(
        self,
        mapping: Dict[str, MappingSuggestion],
        sample_response: dict
    ) -> Dict[str, bool]:
        """
        Validate that suggested mappings exist in sample response.
        
        Args:
            mapping: Suggested field mappings
            sample_response: Sample API response
        
        Returns:
            Dictionary of field_name -> is_valid
        """
        validation_results = {}
        
        for field_name, suggestion in mapping.items():
            path_parts = suggestion.source_path.split(".")
            
            # Navigate nested structure
            current = sample_response
            is_valid = True
            
            try:
                for part in path_parts:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        is_valid = False
                        break
            except (KeyError, TypeError):
                is_valid = False
            
            validation_results[field_name] = is_valid
        
        return validation_results
    
    def apply_mapping(
        self,
        data: dict,
        mapping: Dict[str, MappingSuggestion]
    ) -> Dict[str, Any]:
        """
        Apply mapping to transform API response.
        
        Args:
            data: API response data
            mapping: Field mappings
        
        Returns:
            Transformed data matching target schema
        """
        result = {}
        
        for field_name, suggestion in mapping.items():
            path_parts = suggestion.source_path.split(".")
            
            # Navigate nested structure
            current = data
            try:
                for part in path_parts:
                    if isinstance(current, dict):
                        current = current[part]
                    else:
                        break
                
                # Apply transformation if specified
                if suggestion.transformation:
                    # In production, load transformation functions dynamically
                    # For now, just store raw value
                    result[field_name] = current
                else:
                    result[field_name] = current
            
            except (KeyError, TypeError):
                # Field not found, skip
                continue
        
        return result


# Example transformation functions
def split_name(full_name: str) -> tuple[str, str]:
    """Split full name into first and last"""
    parts = full_name.split(" ", 1)
    return parts[0], parts[1] if len(parts) > 1 else ""


def format_phone(phone: str) -> str:
    """Format phone number to E.164"""
    import re
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        return f"+1{digits}"
    elif len(digits) == 11 and digits[0] == "1":
        return f"+{digits}"
    return phone


def extract_email_domain(email: str) -> str:
    """Extract domain from email"""
    return email.split("@")[1] if "@" in email else ""


def parse_address(address_string: str) -> dict:
    """Parse address string into components"""
    # Simple parser - in production, use address parsing library
    return {
        "street": address_string,
        "city": "",
        "state": "",
        "postal_code": "",
        "country": "US"
    }
