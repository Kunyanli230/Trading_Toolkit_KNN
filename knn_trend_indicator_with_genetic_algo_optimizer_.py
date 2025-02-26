# -*- coding: utf-8 -*-
"""KNN Trend Indicator with Genetic Algo Optimizer .ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1zh66XwwelG7crJBol-95fE1sdHeaCHEx
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import random


# 1. Load and Preprocess Data

# Load dataset (replace with your data)
data = pd.read_csv('sample_data.csv')  # Replace with your file
price = data['Close']  # Replace with the appropriate column

# Compute indicators
def calculate_indicators(data):
    data['sma'] = data['Close'].rolling(10).mean()
    data['ema'] = data['Close'].ewm(span=10, adjust=False).mean()
    data['volatility'] = data['Close'].rolling(14).std()
    return data.dropna()

data = calculate_indicators(data)

# Create features and target
data['Target'] = np.where(data['Close'].shift(-1) > data['Close'], 1, 0)  # Binary classification (UP/DOWN)
features = ['sma', 'ema', 'volatility']
X = data[features]
y = data['Target']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# 2. Genetic Algorithm Implementation

# Hyperparameter bounds
POPULATION_SIZE = 20
GENERATIONS = 50
MUTATION_RATE = 0.2
CROSSOVER_RATE = 0.8
K_RANGE = (2, 50)  # Range for number of neighbors
WINDOW_RANGE = (10, 100)  # Range for moving average window size

# Random initialization of population
def initialize_population(size):
    return [np.random.randint([K_RANGE[0], WINDOW_RANGE[0]], [K_RANGE[1], WINDOW_RANGE[1]]).tolist() for _ in range(size)]

# Fitness function - KNN accuracy
def fitness_function(params):
    k, window = params
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    # Create and train the KNN model
    model = KNeighborsClassifier(n_neighbors=k)
    model.fit(X_train_scaled, y_train)
    predictions = model.predict(X_test_scaled)
    # Return accuracy as fitness score
    return accuracy_score(y_test, predictions)

# Selection - Tournament
def select_parents(population, fitness_scores):
    selected = []
    for _ in range(2):  # Select 2 parents
        i, j = random.sample(range(len(population)), 2)
        selected.append(population[i] if fitness_scores[i] > fitness_scores[j] else population[j])
    return selected

# Crossover
def crossover(parent1, parent2):
    if np.random.rand() < CROSSOVER_RATE:
        point = np.random.randint(1, len(parent1))
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2
    return parent1, parent2

# Mutation
def mutate(individual):
    if np.random.rand() < MUTATION_RATE:
        individual[0] = np.random.randint(K_RANGE[0], K_RANGE[1])  # Mutate K
    if np.random.rand() < MUTATION_RATE:
        individual[1] = np.random.randint(WINDOW_RANGE[0], WINDOW_RANGE[1])  # Mutate window size
    return individual

# Genetic Algorithm Process
def genetic_algorithm():
    population = initialize_population(POPULATION_SIZE)
    best_solution = None
    best_fitness = 0

    for gen in range(GENERATIONS):
        # Evaluate fitness
        fitness_scores = [fitness_function(ind) for ind in population]

        # Track the best solution
        max_fitness = max(fitness_scores)
        if max_fitness > best_fitness:
            best_fitness = max_fitness
            best_solution = population[fitness_scores.index(max_fitness)]

        print(f"Generation {gen + 1}: Best Fitness = {best_fitness:.4f}")

        # Selection, Crossover, Mutation
        new_population = []
        for _ in range(POPULATION_SIZE // 2):
            parent1, parent2 = select_parents(population, fitness_scores)
            child1, child2 = crossover(parent1, parent2)
            new_population += [mutate(child1), mutate(child2)]
        population = new_population

    return best_solution, best_fitness


# 3. Run Genetic Algorithm
best_params, best_score = genetic_algorithm()
print(f"Optimal Parameters: K = {best_params[0]}, Window Size = {best_params[1]}")
print(f"Best Accuracy: {best_score:.4f}")


# 4. Final Model with Optimal Params
best_k, best_window = best_params

# Train final KNN model with optimal parameters
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
knn = KNeighborsClassifier(n_neighbors=best_k)
knn.fit(X_scaled[:len(X_train)], y_train)

# Predictions
predictions = knn.predict(X_scaled)

# Visualization
plt.figure(figsize=(14, 8))
plt.plot(data['Close'], label='Close Price', color='gray')

# Highlight predictions
data['Color'] = np.where(predictions == 1, 'green', 'red')
for i in range(len(data)):
    plt.axvline(x=i, color=data['Color'].iloc[i], alpha=0.02)

plt.title('AI Trend Navigator - Optimized KNN Prediction')
plt.legend()
plt.show()