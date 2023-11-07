import findspark, re
findspark.init()

# Підлкючення до Спарку
from pyspark.sql import SparkSession
spark = SparkSession.builder\
                    .appName('lab_1')\
                    .getOrCreate()
sc=spark.sparkContext

# Зчитування файлу
text_file = sc.textFile("input.txt")

lines = text_file.flatMap(lambda line: [
    word.group() for word in re.finditer(r"\w+", line.lower())
])  # очищення та ділення рядка на слова
words = lines.map(lambda word: (word, 1))  # підрахунок входжень слів
counts = words.reduceByKey(lambda x, y: x + y) # сумування входжень слів

# Вивід результату
output = counts.collect()
for (word, count) in output:
    print(f"{word}: {count}")
