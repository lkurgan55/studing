from mrjob.job import MRJob, MRStep
import os
import re


class MRInvertedIndex(MRJob):

    def __init__(self, *args, **kwargs):
        super(MRInvertedIndex, self).__init__(*args, **kwargs)

    def read_files(self, _, file_name):
        line_offset = 0
        file = open(original_path + '/' + file_name)
        for line in file:
            yield(file_name, (line.strip(), line_offset))
            line_offset += len(line)

    def find_words(self, filename, line): # map слово його входження в файлі
        for word in [
                (word.group().lower(), word.start()) 
                for word in re.finditer(r'\w+', line[0])
            ]:
            yield (word[0], f"{filename}@{line[1] + word[1]}   {line[0]}")

    def prepare_result(self, word, data): # reduce слово - список його індексів
        yield (word, list(data))

    def steps(self):
        return [
            MRStep(mapper=self.read_files), # крок 1 - зчитування файлів
            MRStep(mapper=self.find_words, reducer=self.prepare_result) # крок 2 - обробка слів
        ]

if __name__ == '__main__':
    original_path = os.getcwd()
    MRInvertedIndex.run()
