import anthropic
import json
from typing import List, Dict, Optional
import os
import logging
import sys

# Configure minimal logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class ClaudeCoder:
    def __init__(
        self,
        api_key: str,
        model_name: str = "claude-3-opus-20240229",
        max_tokens: int = 4000,
        temperature: float = 0.7
    ):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature

    def code_response(
        self,
        response: str,
        question: str,
        codeframe_path: str = "data/codeframe.json"
    ) -> Dict:
        try:
            # Load codeframe
            with open(codeframe_path, "r") as f:
                codeframe = json.load(f)

            # Construct the prompt
            prompt = f"""You are a consultation coding expert. Your task is to analyze the response and assign the EXACT codes from the provided codeframe.

Question: {question}
Response: {response}

Codeframe:
{json.dumps(codeframe, indent=2)}

IMPORTANT INSTRUCTIONS:
1. You MUST ONLY use the exact codes provided in the codeframe (e.g., "004", "050", "203")
2. Do not create new codes or modify existing ones
3. For each code you assign:
   - Explain why it applies to the response
   - Provide a confidence score (0-1)
   - Quote the relevant part of the response
4. You can assign multiple codes if the response covers multiple aspects
5. If no code exactly matches, do not assign a code

CRITICAL: You must return ONLY a valid JSON object, with no additional text or explanation. The JSON must be properly formatted with double quotes for all strings.

Return your analysis in this EXACT JSON format:
{{
    "codes": ["004", "005", "050", "051", "203"],
    "confidence": {{
        "004": 0.95,
        "005": 0.95,
        "050": 0.90,
        "051": 0.90,
        "203": 0.85
    }},
    "explanation": {{
        "004": "The response mentions 'more reliable' which matches code 004",
        "005": "The response mentions 'quicker' which matches code 005",
        "050": "The response mentions 'encourage more people to use the bus instead of driving' which matches code 050",
        "051": "The response mentions 'better for the environment' which matches code 051",
        "203": "The response mentions 'more frequent bus services' which matches code 203"
    }},
    "relevant_quotes": {{
        "004": "it'll make bus journeys quicker and more reliable",
        "005": "it'll make bus journeys quicker",
        "050": "encourage more people to use the bus instead of driving",
        "051": "better for the environment",
        "203": "we also need more frequent bus services"
    }}
}}

Remember: Return ONLY the JSON object, with no additional text or explanation."""

            # Get response from Claude
            claude_response = self.client.messages.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse the response
            try:
                # Try to parse the JSON
                coded_response = json.loads(claude_response.content[0].text)

                # Validate codes
                valid_codes = []
                for category in codeframe["categories"].values():
                    valid_codes.extend(category.keys())
                
                # Filter out invalid codes
                coded_response["codes"] = [
                    code for code in coded_response.get("codes", [])
                    if code in valid_codes
                ]
                
                return coded_response

            except json.JSONDecodeError:
                # Try to find where the JSON might be in the response
                try:
                    import re
                    json_match = re.search(r'\{.*\}', claude_response.content[0].text, re.DOTALL)
                    if json_match:
                        coded_response = json.loads(json_match.group(0))
                        return coded_response
                except:
                    pass
                
                return {
                    "error": "Failed to parse Claude's response",
                    "raw_response": claude_response.content[0].text
                }

        except Exception as e:
            return {"error": str(e)}

    def batch_code_responses(
        self,
        responses: List[Dict],
        codeframe_path: str = "data/codeframe.json"
    ) -> List[Dict]:
        """
        Code multiple consultation responses in batch.
        
        Args:
            responses: List of dictionaries containing 'question' and 'response'
            codeframe_path: Path to the codeframe JSON file
            
        Returns:
            List of coded responses
        """
        coded_responses = []
        for response in responses:
            coded = self.code_response(
                response=response["response"],
                question=response["question"],
                codeframe_path=codeframe_path
            )
            coded_responses.append({
                "question": response["question"],
                "response": response["response"],
                "coding": coded
            })
        return coded_responses 