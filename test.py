from ecdsa import ellipticcurve, numbertheory
import hashlib
import random

# Define secp256k1 curve parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
a = 0x0000000000000000000000000000000000000000000000000000000000000000
b = 0x0000000000000000000000000000000000000000000000000000000000000007
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
curve = ellipticcurve.CurveFp(p, a, b)
generator = ellipticcurve.Point(curve, Gx, Gy, n)

# Kangaroo algorithm parameters
step_size = 2**20
num_kangaroos = 100000
max_iterations = 1000000

# index calculus algorithm parameters
factor_base_size = 1000
smoothness_bound = 2**30
num_relations = 1000

def kangaroo_algorithm(initial_point, target_point, eliminated_points):
    kangaroos = [(initial_point, 0) for _ in range(num_kangaroos)]
    try:
        for iteration in range(max_iterations):
            for i, (kangaroo, steps) in enumerate(kangaroos):
                if kangaroo not in eliminated_points:  # Skip eliminated points
                    new_point = kangaroo + steps * generator
                    if new_point == target_point:
                        return kangaroo + steps
                    kangaroos[i] = (new_point, steps + step_size)
    except Exception as e:
        print("Error in Kangaroo algorithm:", e)
    return None

def gaussian_elimination(matrix, eliminated_points):
    rows, cols = len(matrix), len(matrix[0])
    pivot_rows = []
    try:
        # Forward elimination
        for col in range(cols):
            for row in range(len(pivot_rows), rows):
                if matrix[row][col] != 0:
                    pivot_rows.append(row)
                    for j in range(cols):
                        if j != col:
                            matrix[row][j] = (matrix[row][j] - matrix[row][col] * matrix[pivot_rows[0]][j]) % n
                    matrix[row][col] = 1
                    break

        # Backward substitution
        for row in reversed(pivot_rows):
            for i in range(row):
                if matrix[i][row] != 0:
                    matrix[i][row] = (matrix[i][row] - matrix[i][row] * matrix[row][row]) % n

        # Extract the unknown logarithms and update eliminated points
        unknowns = [matrix[row][-1] for row in pivot_rows]
        eliminated_points.extend([matrix[row][-1] for row in pivot_rows])
        return unknowns
    except Exception as e:
        print("Error in Gaussian elimination:", e)
        return []

def index_calculus_algorithm(collision_point, eliminated_points):
    # Generate factor base and precompute smooth numbers
    factor_base = numbertheory.find_factor_base(factor_base_size)
    smooth_numbers = numbertheory.find_smooth_numbers(smoothness_bound, factor_base)

    # Select random points on the curve as relations
    relations = []
    for _ in range(num_relations):
        x = random.randint(1, n - 1)
        relation_point = x * generator
        relations.append((x, relation_point))

    # Build the relation matrix with the collision point
    matrix = []
    for x, point in relations:
        row = []
        for prime in factor_base:
            row.append(point * (n // prime))
        if point == collision_point:
            row.append(point - collision_point)  # Add the collision relation
        matrix.append(row)

    # Solve for the unknown logarithms using Gaussian elimination
    unknowns = gaussian_elimination(matrix, eliminated_points)

    # Use the computed relations to find the private key
    try:
        for x, point in relations:
            if point - x * generator == collision_point:
                return x
    except Exception as e:
        print("Error in index calculus algorithm:", e)
    return None

# Given public key coordinates
public_key = ellipticcurve.Point(curve, 0xd65xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx, 0x3xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx, n)

# Combine Kangaroo and Index Calculus algorithms to find private key
eliminated_points = []  # Keep track of eliminated points during Gaussian elimination
print("Starting Kangaroo algorithm...")
initial_guess = random.randint(1, n - 1)
collided_point = kangaroo_algorithm(initial_guess * generator, public_key, eliminated_points)
if collided_point:
    print("Kangaroo algorithm found a collision.")
    print("Starting index calculus algorithm...")
    private_key = index_calculus_algorithm(collided_point, eliminated_points)
    if private_key:
        print("Private Key Found:", private_key)
    else:
        print("Failed to find private key using index calculus algorithm.")
else:
    print("Failed to find collision using Kangaroo algorithm.")
