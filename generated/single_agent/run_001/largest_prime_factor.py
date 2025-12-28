def largest_prime_factor(n: int) -> int:
    largest_prime = -1
    
    # Divide n by 2 to remove all even factors
    while n % 2 == 0:
        largest_prime = 2
        n //= 2
    
    # Check for odd factors from 3 onwards
    factor = 3
    while factor * factor <= n:
        if n % factor == 0:
            largest_prime = factor
            n //= factor
        else:
            factor += 2
    
    # If n is a prime number greater than 2
    if n > 2:
        largest_prime = n
    
    return largest_prime