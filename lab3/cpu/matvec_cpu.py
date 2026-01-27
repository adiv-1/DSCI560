import time
import random
import sys

def matvec_multiply(A, x, b, N):
    for i in range(N):
        sum = 0
        for j in range(N):
            sum += A[i*N + j] * x[j]
        b[i] = sum

def initialize_matvec(N):
    A = [random.randint(0, 10) for _ in range(N * N)]
    x = [random.randint(0, 10) for _ in range(N)]
    b = [0 for _ in range(N)]
    return A, x, b

def main():
    for N in [512, 1024, 2048]:
        A, x, b = initialize_matvec(N)
        start_time = time.time()
        matvec_multiply(A, x, b, N)
        end_time = time.time()
        print(f"Matrix-vector multiplication of size {N}x{N} completed in {end_time - start_time:.10f} seconds.")

if __name__ == "__main__":
    main()