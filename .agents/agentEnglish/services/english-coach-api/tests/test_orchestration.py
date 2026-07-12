from app.orchestration.router import OrchestrationRouter

def test_orchestration_router():
    """Verifies that user queries route to the appropriate product coach based on keywords."""
    router = OrchestrationRouter()

    # 1. Health indicators route to LifeOS
    assert router.route_request("I slept 6 hours last night, how is that?") == "lifeos_coach"
    assert router.route_request("my calorie burn today is 500 calories") == "lifeos_coach"

    # 2. Parental and check-in terms route to Family check-in
    assert router.route_request("Prakash please trigger mother checkin") == "family_checkin"
    assert router.route_request("check-in with parents today") == "family_checkin"

    # 3. Default Hinglish/English correction routes to English Coach
    assert router.route_request("kal client meeting hai update kar dena") == "english_coach"
