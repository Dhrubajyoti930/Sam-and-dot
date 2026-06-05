"""
s_example_script.py
Tagline: [script | s_example_script | purpose: Demo script that greets and does basic math using s_example module]
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.s_example import S_GREET, S_ADD, S_REPEAT, S_IS_EVEN


def main():
    print(S_GREET("World"))
    result = S_ADD(7, 13)
    print(f"7 + 13 = {result}, even: {S_IS_EVEN(result)}")
    print(S_REPEAT("beep", 3))


if __name__ == "__main__":
    main()
