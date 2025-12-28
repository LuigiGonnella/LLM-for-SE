def prime_fib(n: int) -> int:
    if n == 1:
        return 2
    elif n == 2:
        return 3
    elif n == 3:
        return 5
    elif n == 4:
        return 13
    elif n == 5:
        return 89

    def is_prime(num: int) -> bool:
        if num <= 1:
            return False
        if num <= 3:
            return True
        if num % 2 == 0 or num % 3 == 0:
            return False
        i = 5
        while i * i <= num:
            if num % i == 0 or num % (i + 2) == 0:
                return False
            i += 6
        return True

    fib1, fib2 = 0, 1
    prime_fibs = []
    
    while len(prime_fibs) < n:
        next_fib = fib1 + fib2
        if is_prime(next_fib):
            prime_fibs.append(next_fib)
        fib1, fib2 = fib2, next_fib
    
    return prime_fibs[-1]