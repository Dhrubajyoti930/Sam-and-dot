import random
import string

class CipherGrid:
    def __init__(self, size=8):
        self.size = size
        self.grid = [['.' for _ in range(size)] for _ in range(size)]
        self.shift = random.randint(1, 25)

    def encode(self, word):
        return ''.join(chr((ord(c.upper()) - 65 + self.shift) % 26 + 65) for c in word)

    def generate(self, secret_word):
        encoded = self.encode(secret_word)
        row = random.randint(0, self.size - 1)
        col = random.randint(0, self.size - len(encoded))
        
        for i, char in enumerate(encoded):
            self.grid[row][col + i] = char
            
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == '.':
                    self.grid[r][c] = random.choice(string.ascii_uppercase)

    def display(self):
        print(f"--- Cipher Grid (Shift: {self.shift}) ---")
        for row in self.grid:
            print(" ".join(row))
        print("\nFind the secret word! (Hint: Caesar shift applied)")

if __name__ == "__main__":
    words = ["PYTHON", "LOGIC", "BUILD", "SYSTEM", "CODE"]
    secret = random.choice(words)
    game = CipherGrid()
    game.generate(secret)
    game.display()
    
    guess = input("\nEnter your guess: ").upper()
    if guess == secret:
        print("Correct! The grid has been decrypted.")
    else:
        print(f"Close, but the secret was {secret}.")