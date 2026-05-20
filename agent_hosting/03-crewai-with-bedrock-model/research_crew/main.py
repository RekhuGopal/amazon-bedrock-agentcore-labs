from crew import ResearchCrew
from datetime import datetime
import time

def run():
    try:
        result = ResearchCrew().crew().kickoff(
            inputs={
                "topic": "Artificial Intelligence in Healthcare"
            }
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        output_file = f"research_output_{timestamp}.md"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(str(result))

        print(f"\nResearch output saved to: {output_file}")

    except Exception as e:
        print(f"\nExecution Failed: {e}")

        print("\nSleeping 70 seconds...")
        time.sleep(70)

if __name__ == "__main__":
    run()