import os
import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load the specific environment file
load_dotenv("keys.env")

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

"""
RE-EVALUATION REFLECTION:
If I spent 2 more hours on this project, I would implement a 'Synthetic User' benchmarking suite 
to quantitatively assess prompt performance. Drawing on my background in technical benchmarking, 
I would create a set of 50 test prompts ranging from standard requests to edge-case, high-risk 
topics. I would automate the evaluation using a more powerful model (like GPT-5.5 Instant/Thinking) to calculate 
semantic similarity and safety compliance scores across different versions of my system prompts. 
I would also add a 'Memory' module using a lightweight vector database to allow for character 
consistency across different story sessions.
"""

# ==========================================
# SYSTEM PROMPTS
# ==========================================

AUTHOR_PROMPT = """
You are a world-class children's storyteller. Your mission is to create bedtime stories for ages 5-10.
Target: Calm, imaginative, and safe content.

STORY REQUIREMENTS:
1. Structure: Introduction, a gentle adventure, and a soothing resolution.
2. Vocabulary: Age-appropriate yet descriptive. Use sensory details.
3. Safety: Strictly avoid violence, death, or frightening monsters.

If you receive a 'CRITIQUE', you must treat it as a mandatory correction and rewrite the story.
"""

JUDGE_PROMPT = """
You are a Safety and Quality Auditor for a children's publishing house. 
Evaluate the story provided based on a 5-10 year old audience.

You must think step-by-step:
1. Is the vocabulary too complex?
2. Does the story have a clear beginning, middle, and end?
3. Is it safe (no scary/violent themes)?

OUTPUT FORMAT:
You MUST respond strictly with a JSON object. No other text.
{
  "scores": {
    "safety": 1-5,
    "age_relevance": 1-5,
    "narrative_quality": 1-5
  },
  "approved": boolean,
  "critique": "Specific feedback if approved is false, else empty string."
}
"""

# ==========================================
# CORE PIPELINE
# ==========================================

class StoryEngine:
    def __init__(self, model: str = "gpt-3.5-turbo", max_retries: int = 2):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("API Key not found. Please check your keys.env file.")
        
        # New OpenAI Client structure (v1.0.0+)
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_retries = max_retries

    def _request_llm(self, messages: list, temperature: float) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=2000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API Failure: {e}")
            return ""

    def generate_story(self, user_prompt: str, critique: Optional[str] = None) -> str:
        messages = [
            {"role": "system", "content": AUTHOR_PROMPT},
            {"role": "user", "content": f"Write a bedtime story about: {user_prompt}"}
        ]
        if critique:
            logger.info("Applying Judge's critique to the next draft...")
            messages.append({"role": "assistant", "content": "The previous draft was rejected by the safety judge."})
            messages.append({"role": "user", "content": f"Please fix the story based on this feedback: {critique}"})
        
        return self._request_llm(messages, temperature=0.8)

    def evaluate_story(self, story: str) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": JUDGE_PROMPT},
            {"role": "user", "content": f"Please audit this story:\n\n{story}"}
        ]
        raw_json = self._request_llm(messages, temperature=0.1)
        
        try:
            # Clean potential markdown backticks from LLM output
            clean_json = raw_json.strip("`").replace("json\n", "").strip()
            return json.loads(clean_json)
        except json.JSONDecodeError:
            logger.warning("Judge failed to return valid JSON. Defaulting to safe retry.")
            return {"approved": False, "critique": "Ensure the story is calming and age-appropriate."}

    def run(self, topic: str):
        logger.info(f"Starting pipeline for topic: '{topic}'")
        current_story = self.generate_story(topic)
        
        for i in range(self.max_retries):
            evaluation = self.evaluate_story(current_story)
            scores = evaluation.get("scores", {})
            
            # --- NEW: VISUAL AUDIT REPORT ---
            print(f"\n--- 📋 JUDGE AUDIT: DRAFT {i+1} ---")
            print(f"🛡️  Safety: {scores.get('safety', 'N/A')}/5")
            print(f"👶 Age Relevance: {scores.get('age_relevance', 'N/A')}/5")
            print(f"📖 Narrative Quality: {scores.get('narrative_quality', 'N/A')}/5")
            
            if evaluation.get("approved") and scores.get("safety", 0) >= 4:
                print("✅ STATUS: APPROVED\n")
                logger.info(f"Story Approved by Judge.")
                return current_story
            else:
                critique = evaluation.get("critique", "General improvement needed.")
                print(f"❌ STATUS: REJECTED")
                print(f"💬 FEEDBACK: {critique}\n")
                
                logger.warning(f"Draft {i+1} rejected. Moving to refinement...")
                current_story = self.generate_story(topic, critique=critique)

        logger.warning("Max retries reached. Outputting best available draft.")
        return current_story

# ==========================================
# ENTRY POINT
# ==========================================

def main():
    try:
        engine = StoryEngine()
    except ValueError as e:
        print(f"Error: {e}")
        return

    print("\n✨ Welcome to the Bedtime Story Weaver (Agentic v2.1) ✨")
    
    while True:
        user_input = input("\n[?] What should our story be about? (q to quit): ")
        if user_input.lower() in ['q', 'quit']:
            break
            
        if not user_input.strip():
            continue

        final_story = engine.run(user_input)
        print("\n" + "="*60)
        print(final_story)
        print("="*60 + "\n")

if __name__ == "__main__":
    main()
