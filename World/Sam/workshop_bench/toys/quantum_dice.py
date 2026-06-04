import random
import time

def play():
    print("--- Quantum Dice ---")
    print("The die is in a superposition of 1-6. Choose a face to collapse.")
    balance = 100
    while balance > 0:
        print(f"\nBalance: ${balance} | Bet: $10")
        guess = input("Collapse to (1-6) or 'q' to quit: ").lower()
        if guess == 'q': break
        if not guess.isdigit() or not (1 <= int(guess) <= 6):
            print("Invalid state."); continue
        
        guess = int(guess)
        balance -= 10
        print("Observing...", end="", flush=True)
        for _ in range(3): time.sleep(0.5); print(".", end="", flush=True)
        
        actual = random.randint(1, 6)
        print(f"\nResult: {actual}")
        
        if actual == guess:
            print("Wavefunction collapsed in your favor! +$50")
            balance += 50
        else:
            print("Decoherence failed. You lost the bet.")
    print("Game Over. Final Balance: $" + str(balance))

if __name__ == '__main__':
    play()