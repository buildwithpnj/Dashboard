import logging
import time
from app.providers.base import BaseLLMProvider, ProviderResponse

logger = logging.getLogger(__name__)

class MockLLMProvider(BaseLLMProvider):
    """Deterministic mock provider returning formatted JSON string responses with usage accounting."""

    async def generate_structured_response(self, prompt: str, system_prompt: str) -> ProviderResponse:
        logger.info("Mock provider evaluating input")
        start_time = time.perf_counter()
        
        # Extract only the user input section of the prompt to avoid matching on prompt template headers
        user_input = prompt
        if "[CURRENT USER INPUT]" in prompt:
            user_input = prompt.split("[CURRENT USER INPUT]")[-1]
            
        user_input_lower = user_input.lower()
        
        # Simulating a light computation latency
        latency_ms = 85.0
        
        # Realistic token sizes
        input_tokens = 35
        cached_tokens = 0
        
        if "network issue tha" in user_input_lower:
            raw_content = """{
              "detected_input_style": "Mixed",
              "intent": "correct",
              "natural_english": "I wasn't able to join because of a network issue.",
              "professional_english": "I was unable to join the meeting due to network connectivity issues.",
              "explanation": "Replaced Hinglish 'network issue tha' with 'due to a network issue' or 'because of a network issue' to make the sentence clean and natural.",
              "ambiguity": false,
              "clarification_question": null,
              "mistake_tags": ["vocabulary", "clarity"],
              "confidence": 0.95
            }"""
            output_tokens = 110
            estimated_cost_usd = 0.000071
        elif "kal client ko update dena hai" in user_input_lower:
            raw_content = """{
              "detected_input_style": "Hinglish",
              "intent": "translate",
              "natural_english": "We need to update the client tomorrow.",
              "professional_english": "We are scheduled to provide an update to the client tomorrow.",
              "explanation": "Translated 'kal' to 'tomorrow' and 'client ko update dena hai' to 'we need to update the client' or 'provide an update'.",
              "ambiguity": false,
              "clarification_question": null,
              "mistake_tags": [],
              "confidence": 0.98
            }"""
            output_tokens = 95
            estimated_cost_usd = 0.000062
        elif "kal usko bol dena" in user_input_lower or "ambiguous" in user_input_lower:
            raw_content = """{
              "detected_input_style": "Hinglish",
              "intent": "correct",
              "natural_english": null,
              "professional_english": null,
              "explanation": null,
              "ambiguity": true,
              "clarification_question": "Do you mean you want to update the client tomorrow, or that the client is expected to update us?",
              "mistake_tags": [],
              "confidence": 0.85
            }"""
            output_tokens = 70
            estimated_cost_usd = 0.000047
        elif "rewrite" in user_input_lower or "professional" in user_input_lower:
            raw_content = """{
              "detected_input_style": "English",
              "intent": "rewrite_professional",
              "natural_english": "Please rewrite this professionally.",
              "professional_english": "Could you please revise this to sound more professional?",
              "explanation": "Refined the sentence structures for proper business tone.",
              "ambiguity": false,
              "clarification_question": null,
              "mistake_tags": ["tone"],
              "confidence": 0.90
            }"""
            output_tokens = 85
            estimated_cost_usd = 0.000056
        elif "slept" in user_input_lower or "calories" in user_input_lower or "steps" in user_input_lower or "exercise" in user_input_lower:
            # LifeOS healthy mock
            raw_content = """{
              "detected_metrics": {
                "sleep": "7 hours",
                "diet": "healthy 2000 calories",
                "activity": "10000 steps"
              },
              "analysis": "Prakash's health indicators are within optimal bounds. Activity level is excellent.",
              "recommendations": ["Try to maintain consistent 7-8 hours sleep.", "Stay hydrated during exercise."],
              "disclaimer_triggered": false
            }"""
            output_tokens = 90
            estimated_cost_usd = 0.000058
        elif "gira" in user_input_lower or "gir" in user_input_lower or "dard" in user_input_lower or "chhati" in user_input_lower or "pain" in user_input_lower or "chest" in user_input_lower:
            # Wellness distress / escalation check-in mock
            if "parent" in prompt.lower() or "family" in prompt.lower() or "hindi" in prompt.lower() or "mom" in prompt.lower() or "chhati" in user_input_lower or "gir" in user_input_lower or "dard" in user_input_lower:
                raw_content = """{
                  "checkin_status": "escalated",
                  "response_text": "मुझे यह जानकर बहुत चिंता हो रही है। क्या आप ठीक हैं? मैं प्रकाश को तुरंत कॉल कर रहा हूँ।",
                  "notes": "Parent reported chest pain or falling. Escalation triggered.",
                  "escalation_triggered": true
                }"""
            else:
                # LifeOS medical trigger mock
                raw_content = """{
                  "detected_metrics": {"sleep": null, "diet": null, "activity": null},
                  "analysis": "WARNING: Reported physical symptoms.",
                  "recommendations": ["Consult a medical physician immediately."],
                  "disclaimer_triggered": true
                }"""
            output_tokens = 85
            estimated_cost_usd = 0.000055
        elif "theek" in user_input_lower or "thik" in user_input_lower or "ok" in user_input_lower or "good" in user_input_lower:
            # Family Check-in normal wellness mock
            raw_content = """{
              "checkin_status": "normal",
              "response_text": "यह जानकर बहुत अच्छा लगा कि आप ठीक हैं। अपना ख्याल रखिएगा।",
              "notes": "Parent reports normal wellness.",
              "escalation_triggered": false
            }"""
            output_tokens = 80
            estimated_cost_usd = 0.000052
        else:
            raw_content = """{
              "detected_input_style": "English",
              "intent": "correct",
              "natural_english": "I am working on this task.",
              "professional_english": "I am currently working on this task.",
              "explanation": "Refined for natural professional context.",
              "ambiguity": false,
              "clarification_question": null,
              "mistake_tags": [],
              "confidence": 0.90
            }"""
            output_tokens = 60
            estimated_cost_usd = 0.000041

        # Calculate final latency (in ms)
        actual_latency = (time.perf_counter() - start_time) * 1000.0 + latency_ms

        return ProviderResponse(
            raw_content=raw_content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            estimated_cost_usd=estimated_cost_usd,
            latency_ms=actual_latency
        )
