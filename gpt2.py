import time
import json
from datetime import datetime
import requests
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, SimpleRNN, Embedding, Flatten
from tensorflow.keras.preprocessing.sequence import pad_sequences


def get_blaze_data(url, save_file=True):
    r = requests.get(url)

    if save_file:
        save_data_to_file(r.text)
    return json.loads(r.text)


def get_last_1000_colors():
    url = "https://blaze.com/api/roulette_games/history?startDate=2023-04-23T00:00:00.000Z&endDate=2023-04-24T00:00:00.000Z&page=1"
    data = get_blaze_data(url)
    result_array = get_only_result_data(data)
    return [result_array[i:i + 6] for i in range(0, len(result_array), 6)][-1000:]


def save_data_to_file(data):
    with open("result.json", "w") as f:
        f.write(data)


def get_only_result_data(data):
    result = []
    for i, v in enumerate(data["records"]):
        val = v["color"]
        if i < 500:
            result.append(val)
    return result


def create_word_index(result_array):
    result_array = [tuple(seq) if isinstance(seq, list)
                    else seq for seq in result_array]
    word_index = create_word_index(result_array)

    result_array = get_last_1000_colors()
    word_index = create_word_index(result_array)
    X, y, max_length = prepare_data((result_array), word_index)

    # Treinando o modelo
    while True:
        # Obtendo as últimas 5 cores
        last_5_colors = result_array[-5:]
        # Fazendo a previsão da próxima cor
        next_color = predict_next_color(last_5_colors, model, word_index, max_length)
        print("Next color:", next_color)
        # Esperando 5 segundos antes de obter as novas cores
        time.sleep(5)
        # Obtendo as últimas 1000 cores atualizadas
        result_array = get_last_1000_colors()
        break
    model = create_model(len(word_index) + 1, max_length)
    model.fit(X, y, epochs=100)
    return word_index


# Obtém os dados
# Obtendo as últimas 1000 cores

# Fazendo previsões contínuas


def prepare_data(result_array, word_index):
    sequences = []
    for i in range(len(result_array) - 1):
        seq = [word_index[w] for w in result_array[:i + 1]]
        if len(seq) > 5:
            seq = seq[-5:]
        sequences.append(seq)
    max_length = max([len(seq) for seq in sequences])
    sequences = pad_sequences((sequences), maxlen=5, padding='pre')
    X = sequences[:, :-1]
    y = sequences[:, -1]
    return X, y, max_length


def create_model(vocab_size, max_length):
    model = Sequential()
    model.add(Embedding(vocab_size, 10, input_length=max_length - 1))
    model.add(SimpleRNN(50))
    model.add(Dense(10, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model


def predict_next_color(last_5_colors, model, word_index, max_length):
    # Convertendo as cores em índices numéricos
    X_pred = [word_index[w] for w in last_5_colors]
    # Padronizando a sequência para o mesmo comprimento das sequências de treinamento
    X_pred = pad_sequences([X_pred], maxlen=max_length - 1, padding='pre')
    # Fazendo a previsão com o modelo treinado
    y_pred = model.predict_classes(X_pred, verbose=0)
    # Convertendo o índice numérico de volta para a cor correspondente
    for word, index in word_index.items():
        if index == y_pred:
            return word


# Obtém os dados
result_array = get_last_1000_colors()
# Cria o índice de palavras
word_index = create_word_index(result_array)
# Prepara os dados
X, y, max_length = prepare_data(result_array, word_index)
# Cria o modelo
model = create_model(len(word_index) + 1, max_length)
# Treina o modelo
model.fit(X, y, epochs=100)
