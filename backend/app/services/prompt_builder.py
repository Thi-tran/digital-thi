"""
Prompt builder – assembles the LLM prompt from its ingredients.
"""
import random
from app.models import SearchResult

_PIVOT_QUESTIONS = [
    "Would you like to know more about my background or education?",
    "Curious about my skillset or a fun fact about me?",
]


def _choose_followup_question(relevant_sections: list[SearchResult]) -> str:
    """
    60 % of the time return a contextual prompt that asks Ollama to form a
    follow-up question; 40 % of the time use a pre-written pivot question.
    """
    if random.random() < 0.6:
        return (
            "ask a follow-up question directly related to the job description, "
            "technologies and the role the user is applying for, based on the CV "
            "information above. Make it a natural question that encourages the user "
            "to share more about their experience or skills relevant to the job."
        )
    return random.choice(_PIVOT_QUESTIONS)


def build_chat_prompt(
    message: str,
    relevant_sections: list[SearchResult],
    history_context: str,
) -> str:
    """
    Assemble the full LLM prompt string.

    Returns an empty string if there are no relevant sections (caller should
    use the fallback response in that case).
    """
    if not relevant_sections:
        return ""

    context = "\n".join(f"- {s.content}" for s in relevant_sections)
    followup = _choose_followup_question(relevant_sections)

    return f"""Answer as me. Do not say ‘Based on my CV’ or anything similar..
Answer directly and naturally. Do NOT include any preamble, meta-commentary, or phrases like "Okay, here's a response..." or "Based on the CV..." at the start. Just answer.

The user asked: "{message}"

Here's the relevant information from the CV:
{context}

Previous conversation:
{history_context}

- Provide a helpful, professional, and engaging response that answers their question based on relevant information from the CV.
- Remember the context of user ipnut if relevant.
- Add a touch of personality and professionalism to make the response feel natural and friendly.
- Make the format of the response clear and easy to read. Use bullet points if listing information, and keep paragraphs short.
- Be honest in the answer, if the job requirement is not met, acknowledge it and suggest related skills or experiences that could be relevant.
- End your response with one follow-up question: {followup}. The goal is to understand the employer as much as possible.
- Do not repeat any question already asked in the previous conversation.
- Keep the conversation engaging and fun! 
"""
