import anthropic
import json
from typing import List, Dict, Optional
import os
import logging
import sys
from functools import lru_cache

# Configure logging
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
        self.codeframe = self._load_codeframe()

    def _load_codeframe(self):
        try:
            with open("data/codeframe.json", "r") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading codeframe: {str(e)}")
            return {"categories": {}}

    @lru_cache(maxsize=100)
    def code_response(self, response, question):
        """
        Analyze a consultation response and assign codes with caching.
        """
        try:
            # Construct a more robust prompt
            prompt = f"""You are an expert at coding consultation responses. Your task is to analyze the response and assign the most appropriate codes from the provided codeframe.

Question: {question}
Response: {response}

Codeframe Categories and Codes:
{json.dumps(self.codeframe, indent=2)}

Instructions:
1. Carefully analyze the response, even if it contains extra information or is verbose.
2. Focus on the core meaning and intent of the response, ignoring any irrelevant details.
3. Assign codes based on the actual content and meaning, not just keywords.
4. For each assigned code:
   - Provide a confidence score (0.0 to 1.0)
   - Explain why this code is appropriate
   - Include the most relevant quote from the response
5. Only assign codes that are clearly supported by the response content.
6. If the response is unclear or doesn't match any codes, return an empty codes list.
7. Your response MUST be a valid JSON object.

Return a JSON object with this EXACT structure:
{{
    "codes": ["code1", "code2", ...],
    "confidence": {{
        "code1": 0.95,
        "code2": 0.85
    }},
    "explanation": {{
        "code1": "explanation text",
        "code2": "explanation text"
    }},
    "relevant_quotes": {{
        "code1": "quote from response",
        "code2": "quote from response"
    }},
    "error": null
}}

IMPORTANT: Your response must be ONLY the JSON object, with no additional text or explanation."""

            # Get response from Claude
            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system="You are an expert at coding consultation responses. Your responses must be valid JSON objects with no additional text.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract and parse the response
            response_text = message.content[0].text.strip()
            
            # Try to find JSON in the response if it's not pure JSON
            if not response_text.startswith('{'):
                # Look for JSON-like content
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    response_text = response_text[start_idx:end_idx]
            
            try:
                result = json.loads(response_text)
                
                # Validate the response structure
                required_keys = ["codes", "confidence", "explanation", "relevant_quotes", "error"]
                if not all(key in result for key in required_keys):
                    raise ValueError("Missing required keys in response")
                
                # Ensure codes is a list
                if not isinstance(result["codes"], list):
                    result["codes"] = []
                
                # Ensure other fields are dictionaries
                for key in ["confidence", "explanation", "relevant_quotes"]:
                    if not isinstance(result[key], dict):
                        result[key] = {}
                
                return result
                
            except json.JSONDecodeError as e:
                logging.error(f"JSON parsing error: {str(e)}")
                logging.error(f"Raw response: {response_text}")
                return {
                    "codes": [],
                    "confidence": {},
                    "explanation": {},
                    "relevant_quotes": {},
                    "error": f"Invalid JSON response: {str(e)}"
                }
                
        except Exception as e:
            logging.error(f"Error in code_response: {str(e)}")
            return {
                "codes": [],
                "confidence": {},
                "explanation": {},
                "relevant_quotes": {},
                "error": str(e)
            }

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
                question=response["question"]
            )
            coded_responses.append({
                "question": response["question"],
                "response": response["response"],
                "coding": coded
            })
        return coded_responses 