from app.products.english_coach.schemas import (
    CoachRespondRequest,
    CoachRespondResponse,
    CoachFeedbackRequest,
    CoachFeedbackResponse,
    TokenUsage
)
# Deprecated backward compatibility aliases
CoachRequest = CoachRespondRequest
CoachResponse = CoachRespondResponse
FeedbackRequest = CoachFeedbackRequest
FeedbackResponse = CoachFeedbackResponse
