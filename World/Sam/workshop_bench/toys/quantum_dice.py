import random
import time

def play():
    print("--- Quantum Dice: The Wave Function Collapse ---")
    print("The die exists in all states 1-6 simultaneously.")
    print("Predict the outcome to force a collapse. Win if you match the reality.")
    
    credits = 10
    while credits > 0:
        print(f"\nCredits: {credits}")
        try:
            guess = int(input("Predict (1-6): "))
        except ValueError:
            continue

        if guess < 1 or guess > 6:
            continue

        print("Observing superposition...")
        for _ in range(3):
            time.sleep(0.3)
            print(".", end="", flush=True)
        
        # Quantum-ish: 50% chance to be fair, 50% chance to be malicious
        if random.random() > 0.5:
            actual = random.randint(1, 6)
        else:
            # Try to avoid the user's guess
            actual = (guess % 6) + 1
            
        print(f"\nResult: {actual}")
        
        if actual == guess:
            print("Wave function collapsed in your favor! +2 credits.")
            credits += 2
        else:
            print("Reality rejected your observation. -1 credit.")
            credits -= 1
            
    print("\nEntropy claimed your credits. Game over.")

if __name__ == '__main__':
    play()