import random
from rag.workflow.intent import Intent

SMALL_TALK_REPLIES = [
    "Ciao! 👋 Come posso aiutarti oggi?",
    "Buongiorno! Cerchi qualcosa in particolare?",
    "Ciao! Posso aiutarti a trovare piatti, bicchieri o accessori?",
    "Benvenuto! Dimmi pure cosa stai cercando.",
]

def generate_non_search_reply(intent, memory, user_message: str) -> str:
    """
    Handles only small talk.
    Other intents must be handled earlier in the pipeline.
    """

    if intent == Intent.SMALL_TALK:
        return random.choice(SMALL_TALK_REPLIES)

    # Fallback safeguard (should rarely trigger)
    return "Come posso aiutarti?"
