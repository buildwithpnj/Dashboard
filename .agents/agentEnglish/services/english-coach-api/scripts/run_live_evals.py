import asyncio
import sys
import os
import json
import time
import logging

# Add project root directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.api.deps import get_coach_service, get_lifeos_coach_service, get_family_checkin_service, get_llm_provider
from app.schemas.coach import CoachRespondRequest
from app.products.lifeos_coach.schemas import LifeOSRespondRequest
from app.products.family_checkin.schemas import FamilyCheckinRequest

logger = logging.getLogger("run_live_evals")

async def main():
    logger_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    # Open database session and resolve services
    from app.db.session import AsyncSessionLocal
    db = AsyncSessionLocal()
    provider = get_llm_provider()
    coach_service = await get_coach_service(db=db, provider=provider)
    lifeos_service = await get_lifeos_coach_service(db=db, provider=provider)
    family_service = await get_family_checkin_service(db=db, provider=provider)
    
    print("==================================================================")
    print("           WARBORN AGENT PLATFORM - LIVE EVAL LANE")
    print("==================================================================")
    print(f"Eval Mode:      {settings.EVAL_MODE.upper()}")
    print(f"Provider:       {provider.__class__.__name__} | Model: {settings.MODEL_NAME}")
    print("-" * 66)

    # Define targets
    eval_targets = [
        {"file": os.path.join(base_dir, "data", "evals", "translation_eval.jsonl"), "product": "english_coach"},
        {"file": os.path.join(base_dir, "data", "evals", "correction_eval.jsonl"), "product": "english_coach"},
        {"file": os.path.join(base_dir, "data", "evals", "rewrite_eval.jsonl"), "product": "english_coach"},
        {"file": os.path.join(base_dir, "data", "evals", "ambiguity_eval.jsonl"), "product": "english_coach"},
        {"file": os.path.join(base_dir, "data", "evals", "lifeos_eval.jsonl"), "product": "lifeos_coach"},
        {"file": os.path.join(base_dir, "data", "evals", "family_checkin_eval.jsonl"), "product": "family_checkin"}
    ]

    total_cases = 0
    passed_cases = 0
    run_records = []

    for target in eval_targets:
        file_path = target["file"]
        product = target["product"]
        if not os.path.exists(file_path):
            print(f"Skipping missing file: {os.path.basename(file_path)}")
            continue

        print(f"Evaluating {os.path.basename(file_path)}...")
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                case = json.loads(line)
                case_id = case["id"]
                input_text = case["input_text"]
                target_phrases = case.get("target_phrases", [])
                
                total_cases += 1
                score = 0.0
                status = "FAIL"
                response_text = ""

                try:
                    if product == "english_coach":
                        req = CoachRespondRequest(text=input_text)
                        res = await coach_service.process_request(req)
                        response_text = (res.natural_english or "") + " " + (res.explanation or "")
                        # Simple overlap score
                        words = response_text.lower()
                        matches = sum(1 for phrase in target_phrases if phrase.lower() in words)
                        score = matches / len(target_phrases) if target_phrases else 1.0
                    elif product == "lifeos_coach":
                        req = LifeOSRespondRequest(text=input_text)
                        res = await lifeos_service.process_request(req)
                        response_text = res.analysis + " " + " ".join(res.recommendations)
                        words = response_text.lower()
                        matches = sum(1 for phrase in target_phrases if phrase.lower() in words)
                        score = matches / len(target_phrases) if target_phrases else 1.0
                    elif product == "family_checkin":
                        req = FamilyCheckinRequest(user_id="parent_1", message_text=input_text)
                        res = await family_service.process_request(req)
                        response_text = res.response_text + " " + str(res.notes)
                        words = response_text.lower()
                        matches = sum(1 for phrase in target_phrases if phrase.lower() in words)
                        score = matches / len(target_phrases) if target_phrases else 1.0
                except Exception as e:
                    logger.error(f"Failed to process case {case_id}: {e}")
                    response_text = f"Error: {e}"

                if score >= 0.7:
                    passed_cases += 1
                    status = "PASS"

                run_records.append({
                    "id": case_id,
                    "product": product,
                    "input_text": input_text,
                    "response_text": response_text,
                    "score": score,
                    "status": status
                })

    await db.close()

    pass_rate = passed_cases / total_cases if total_cases > 0 else 0.0
    summary = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_cases": total_cases,
        "passed_cases": passed_cases,
        "pass_rate": pass_rate,
        "records": run_records
    }

    # Write output runs JSON
    runs_dir = os.path.join(logger_dir, "data", "evals", "runs")
    os.makedirs(runs_dir, exist_ok=True)
    with open(os.path.join(runs_dir, "live_run_latest.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("-" * 66)
    print(f"Completed! Pass Rate: {pass_rate*100:.2f}% ({passed_cases}/{total_cases})")
    
    threshold = 0.8
    if pass_rate < threshold:
        print(f"FAIL: Pass rate falls below {threshold*100:.2f}% threshold.", file=sys.stderr)
        sys.exit(1)
    else:
        print("PASS: Success!")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
