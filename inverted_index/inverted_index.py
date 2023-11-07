from mrjob.job import MRJob, MRStep
import os
import re

WORD_RE = re.compile(r"[\w']+")


class  MRInvertedIndex(MRJob):

    def __init__(self, *args, **kwargs):
        super(MRInvertedIndex, self).__init__(*args, **kwargs)

    def read_files(self, _, file_name):
        line_offset = 0
        file = open(file_name)
        for line in file:
            yield(file_name, (line.strip(), line_offset))
            line_offset += len(line)
    
    def find_words(self, filename, line):
        for word in [
                (word.group().lower(), word.start()) 
                for word in re.finditer(r'\S+', line[0])
            ]:
            yield (word[0], f"{filename}@{line[1] + word[1]}   {line[0]}")
    
    def posting_lists(self, word, data):
        yield (word, list(data))

    def steps(self):
        # This function specifies the process pipeline. In this case we have a two-phases map-reduce process. 
        # The first phase process the input files and creates an entry per each file line. The second phase 
        # processes the lines and build the inverted index. The first process only has a mapper function,
        # while the second one has both mapper and reducer.
        return [
            MRStep(mapper=self.read_files),
            MRStep(mapper=self.find_words, reducer=self.posting_lists)
        ]

if __name__ == '__main__':
    MRInvertedIndex.run()

