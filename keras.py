import tensorflow as tf
from keras.preprocessing import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
import keras
from keras import layers
# Sample data
texts = ["This movie is fantastic!", "Terrible film, waste of time", 
         "Best movie ever", "So boring and slow"]
labels = [1, 0, 1, 0]  # 1 = positive, 0 = negative

# Text preprocessing
tokenizer = Tokenizer(num_words=10000, oov_token="<OOV>")
tokenizer.fit_on_texts(texts)
sequences = tokenizer.texts_to_sequences(texts)
padded = pad_sequences(sequences, maxlen=100, padding='post', truncating='post')

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    padded, labels, test_size=0.2, random_state=42)

# Build model
model = keras.Sequential([
    layers.Embedding(10000, 128, input_length=100),
    layers.LSTM(64, dropout=0.5, recurrent_dropout=0.5),
    layers.Dense(32, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(1, activation='sigmoid')  # Binary classification
])

# Compile
model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])

# Train
history = model.fit(X_train, y_train,
                    epochs=10,
                    batch_size=32,
                    validation_split=0.2,
                    verbose=1)