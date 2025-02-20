import hashlib
import re
import string

import nltk
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')


def clean_text(text: str): # Очищення тексту
    text = re.sub(' +', ' ', text.strip()) # видалення зайвих пробілів
    text = text.lower() # перетворення у нижній регістр
    text = text.translate(str.maketrans('', '', string.punctuation)) # прибирання розділових знаків

    lemmatizer = WordNetLemmatizer()
    stemmer = PorterStemmer()

    tokens = word_tokenize(text)

    tokens = [stemmer.stem(token) for token in tokens] # стемінг тексту
    tokens = [lemmatizer.lemmatize(token) for token in tokens] # лематизація тексту

    stop_words = set(stopwords.words('english'))

    tokens = [token for token in tokens if token not in stop_words] # видалення вставних слів

    return tokens

def shingling(words: list, k: int): # розбиття тексту на шинглі
    shingles = set()
    for i in range(len(words) - k + 1):
        shingle = tuple(words[i:i + k])
        shingles.add(' '.join(shingle))
    return shingles

def hash_shingles(shingles): # хешування шинглів
    hashed_shingles = set()
    for shingle in shingles:
        hash_value = hashlib.md5(shingle.encode()).hexdigest()
        hashed_shingles.add(hash_value)
    return hashed_shingles

def jaccard_similarity(set1, set2): # перевірка подібності через Жаккарда

    intersection = len(set1.intersection(set2)) # кількість елементів в різниці множин
    union = len(set1.union(set2)) # кількість елементів в перетині множин
    
    if union != 0:
        similarity = intersection / union 
    else:
        similarity = 0

    return similarity

if __name__ == "__main__":
    text = '  So,  testing this work,   Yeah!   '
    cleaned_text = clean_text(text)
    print(cleaned_text)

    shingles = shingling(cleaned_text, 3)
    print(shingles)
    
    hashed_shingles = hash_shingles(shingles)
    print(hashed_shingles)