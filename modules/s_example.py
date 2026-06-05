"""
s_example.py
Tagline: [module | s_example | theme:demo | funcs: S_GREET(name:str)->str, S_ADD(a:int,b:int)->int, S_REPEAT(text:str,n:int)->str, S_IS_EVEN(n:int)->bool | purpose: demonstration module showing Sam conventions]
"""


def S_GREET(name: str) -> str:
    """Return a greeting string for the given name."""
    return f"Hello, {name}! Sam here. Ready to do something cool."


def S_ADD(a: int, b: int) -> int:
    """Add two integers and return the result."""
    return a + b


def S_REPEAT(text: str, n: int) -> str:
    """Repeat a string n times with a space separator."""
    return " ".join([text] * n)


def S_IS_EVEN(n: int) -> bool:
    """Return True if n is even, False otherwise."""
    return n % 2 == 0
