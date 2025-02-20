from pyspark import SparkContext, SparkConf

# парсинг рядка і отримання даних link і links
def parse_line(line):
    data = line.split(":")
    return data[0], data[1].strip().split()

# Обчислення внески важливості посилання в інших посиланнях
def compute_contribs(urls, rank: float):  
    for url in urls:
        yield (url, rank / len(urls))


if __name__ == "__main__":

    conf = SparkConf().setAppName("lab_2")
    sc = SparkContext(conf=conf)

    lines = sc.textFile("input.txt")
    links = lines.map(lambda line: parse_line(line))
    links_count = links.count()
    ranks = links.map(lambda link: (link[0], 1.0 / links_count))  # Початковий ранг для кожного URL

    for iteration in range(25):
        # Обчислення внески важливості посилання в інших посиланнях
        contribs = links.join(ranks).flatMap(
            lambda url_urls_rank: compute_contribs(
            url_urls_rank[1][0], url_urls_rank[1][1]
        ))
        # Використання full outer join щоб не втратити значення при обчисленні
        contribs = links.fullOuterJoin(contribs).mapValues(lambda x : x[1] or 0.0)

        # Сумування важливості по посиланню
        ranks = contribs.reduceByKey(lambda x, y: x + y)
        
        # Обчислення рангів
        ranks = ranks.mapValues(lambda rank: rank * 0.85 + 0.15)

    ranks = ranks.collect()

    rank_total = 0
    for _, rank in ranks:
        rank_total += rank

    for (link, rank) in ranks:
        print(f"{link}: {100 * rank / rank_total}")
