import numpy as np
import tensorflow as tf

#Goal for today is to create a calculator with 3 inputs, a number a sign and another number

# Generate synthetic data for training: pairs of numbers and their sum

x = np.array([[i, j] for i in range(100) for j in range(100)])


y = np.array([i + j for [i, j] in x])

# Define a simple sequential model
model = tf.keras.models.Sequential([
  tf.keras.layers.Dense(4, input_dim=2, activation='relu'),
  tf.keras.layers.Dense(2, activation='relu'),
  tf.keras.layers.Dense(1, activation='linear')
])

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(x, y, epochs=10)

# Now you can use the model to predict sums
def predict_sum():
    a = float(input("Enter the first number: "))
    b = float(input("Enter the second number: "))
    prediction = model.predict(np.array([[a, b]]))
    print(f"The predicted sum of {a} and {b} is: {prediction[0][0]}")

# Use the function to predict sums
predict_sum()
