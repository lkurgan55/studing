from functions import *

def main(file_path_1, file_path_2):
    with open(file_path_1, 'r', encoding='utf-8') as file:
            text1 = file.read()
    with open(file_path_2, 'r', encoding='utf-8') as file:
            text2 = file.read()

    k = 5  # Розмір шинглу

    cleaned_text1 = clean_text(text1)
    cleaned_text2 = clean_text(text2)

    shingles1 = shingling(cleaned_text1, k)
    shingles2 = shingling(cleaned_text2, k)

    hashed_shingles1 = hash_shingles(shingles1)
    hashed_shingles2 = hash_shingles(shingles2)

    similarity = jaccard_similarity(hashed_shingles1, hashed_shingles2)

    print(f"Очищений текст 1: {cleaned_text1}")
    print(f"Очищений текст 2: {cleaned_text2}")
    print(f"Схожість текстів за Жаккардом: {similarity:.2%}")

if __name__ == "__main__":
    file_path_1 = 'text_1.txt'
    file_path_2 = 'text_2.txt'

    main(file_path_1, file_path_2)
