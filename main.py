import json
from linkedin_generator.graph import build_graph

def main():
    print("Initializing Multi-Agent LinkedIn Content Generator...")
    app = build_graph()
    
    # Initialize the state
    initial_state = {
        "research": None,
        "ranking": None,
        "draft": None,
        "review": None,
        "revision_count": 0
    }
    
    print("Starting execution workflow...")
    
    # Run the graph
    try:
        final_state = app.invoke(initial_state)
        
        print("\n" + "="*50)
        print("FINAL POST")
        print("="*50)
        draft = final_state.get("draft")
        if draft:
            print(f"TOPIC: {draft.topic}\n")
            print(draft.post)
            print("\n" + " ".join(draft.hashtags))
            
            review = final_state.get("review")
            if review:
                print("\n" + "-"*50)
                print(f"Review Score: {review.overall_score}/10")
                print(f"Approved: {review.approved}")
                print(f"Strengths: {', '.join(review.strengths)}")
        else:
            print("Failed to generate draft.")
            
    except Exception as e:
        print(f"An error occurred during execution: {e}")

if __name__ == "__main__":
    main()
