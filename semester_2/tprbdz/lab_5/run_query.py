from SPARQLWrapper import SPARQLWrapper, JSON
import json
from tabulate import tabulate

def read_query_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

# Читаємо SPARQL-запити з файлів
local_query = read_query_file("countries_local.rq")
wikidata_template = read_query_file("countries_wikidata.rq")

# Запит до Fuseki
fuseki = SPARQLWrapper("http://localhost:3030/countries/query")
fuseki.setQuery(local_query)
fuseki.setReturnFormat(JSON)

print("Виконую запит до локальної Fuseki...")
fuseki_results = fuseki.query().convert()

# Дістаємо wikidataID
wikidata_ids = []
local_names = {}

for result in fuseki_results["results"]["bindings"]:
    wikidata_uri = result["wikidataID"]["value"]
    wikidata_id = wikidata_uri.split("/")[-1]
    wikidata_ids.append(wikidata_id)
    local_names[wikidata_id] = result["localName"]["value"]

print(f"Знайдено {len(wikidata_ids)} wikidataID: {wikidata_ids}")

if not wikidata_ids:
    print("Немає даних для запиту до Wikidata!")
    exit()

# Формуємо VALUES
values_str = " ".join(f"wd:{id_}" for id_ in wikidata_ids)

# Підставляємо VALUES в шаблон
wikidata_query = wikidata_template.replace("{{VALUES}}", values_str)

# Запит до Wikidata
wikidata = SPARQLWrapper("https://query.wikidata.org/sparql")
wikidata.setQuery(wikidata_query)
wikidata.setReturnFormat(JSON)

print("Виконую запит до Wikidata...")
wikidata_results = wikidata.query().convert()

# Обробка результатів
data_list = []

for res in wikidata_results["results"]["bindings"]:
    wid = res["wikidataID"]["value"].split("/")[-1]
    local_name = local_names.get(wid, "Unknown")
    country_label = res.get("countryLabel", {}).get("value", "N/A")
    capital_label = res.get("capitalLabel", {}).get("value", "N/A")
    currency_label = res.get("currencyLabel", {}).get("value", "N/A")
    language_label = res.get("languageLabel", {}).get("value", "N/A")

    data_list.append({
        "localName": local_name,
        "countryLabel": country_label,
        "capital": capital_label,
        "currency": currency_label,
        "language": language_label
    })

# Вивід результатів у формі таблиці
print(tabulate(data_list, headers="keys", tablefmt="grid"))
