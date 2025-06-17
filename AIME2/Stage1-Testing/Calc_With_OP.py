import numpy as np
import tensorflow as tf

# Operations: multiplication (*), division (/), addition (+), subtraction (-)
# Encoding operations numerically: * -> 0, / -> 1, + -> 2, - -> 3
operations = {'*': 0, '/': 1, '+': 2, '-': 3}

# Adjusting the input generation to include the operation code
x = np.array([[i, j, operations[op]] for i in range(100) for j in range(100) for op in operations.keys()])

# Adjust the calculate_result function to handle the numerical operation codes
def calculate_result(i, j, op_code):
    if op_code == 0:  # Multiplication
        return i * j
    elif op_code == 1:  # Division, with a check to avoid division by zero
        return i / j if j != 0 else 0
    elif op_code == 2:  # Addition
        return i + j
    elif op_code == 3:  # Subtraction
        return i - j

# Generate labels based on the operation
y = np.array([calculate_result(i, j, op) for [i, j, op] in x])
# Function to create the model
def create_model():
    model = tf.keras.models.Sequential([
      tf.keras.layers.Dense(64, input_dim=3, activation='relu'),
      tf.keras.layers.Dense(32, activation='relu'),
      tf.keras.layers.Dense(1, activation='linear')
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

# Check if the model exists and load it, otherwise create and train it
model_path = 'my_calculator_model'
if os.path.exists(model_path):
    print("Loading existing model...")
    model = load_model(model_path)
else:
    print("Creating and training a new model...")
    model = create_model()
    # Operations and data preparation code remains the same
    # [Insert your existing code for operations, x, and y here]
    # Train the model
    model.fit(x, y, epochs=10)
    # Save the model
    model.save(model_path)

# Prediction function
def predict_with_operation():
    a = float(input("Enter the first number: "))
    sign = input("Enter the operation (e.g., +, -, *, /): ")
    b = float(input("Enter the second number: "))
    op_code = operations[sign]
    prediction = model.predict(np.array([[a, b, op_code]]))
    print(f"The predicted result of {a} {sign} {b} is: {prediction[0][0]}")

# Use the function to predict results
predict_with_operation()ho