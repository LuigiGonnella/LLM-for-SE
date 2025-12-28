def modp(n: int, p: int) -> int:
    if p <= 0:
        raise ValueError("Modulus p must be greater than 0")
    
    result = 1
    base = 2 % p
    
    while n > 0:
        if n % 2 == 1:
            result = (result * base) % p
        base = (base ** 2) % p
        n //= 2
    
    return result