from dotenv import load_dotenv
load_dotenv()

from predict import FearForecast
from chat import AICoach


def test_predict():
    print("\n" + "="*50)
    print("FEAR FORECAST TEST")
    print("="*50)

    forecast = FearForecast()

    # Step 1: Generate forecast
    print("\n--- Step 1: Generate Forecast ---")
    result = forecast.generate_forecast(
        fear="I'll have a panic attack in the meeting and everyone will stare at me.",
        belief_strength=80
    )
    print(f"Fear: {result['fear']}")
    print(f"Belief Strength: {result['belief_strength']}%")
    print(f"AI Response:\n{result['ai_response']}")

    # Step 2: Log outcome + get insight
    print("\n--- Step 2: After Event Insight ---")
    insight = forecast.generate_insight(
        fear=result["fear"],
        prediction=result["ai_response"],
        outcome="It Was Fine"
    )
    print(f"Outcome: {insight['outcome']}")
    print(f"Insight:\n{insight['insight']}")


def test_chat():
    print("\n" + "="*50)
    print("AI COACH CHAT TEST")
    print("="*50)

    coach = AICoach()

    messages = [
        "I've been overthinking everything lately and it's exhausting.",
        "I feel like I can't stop even when I try.",
    ]

    for msg in messages:
        print(f"\nYou: {msg}")
        reply = coach.chat(msg)
        print(f"Coach: {reply}")


if __name__ == "__main__":
    test_predict()
    test_chat()