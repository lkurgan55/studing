PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX bd: <http://www.bigdata.com/rdf#>
PREFIX schema: <http://schema.org/>

SELECT DISTINCT ?country ?countryLabel ?capitalLabel ?population ?area ?currencyLabel
       ?continentLabel ?languageLabel
WHERE {
  ?country wdt:P31 wd:Q6256;              # є країною
           wdt:P36 ?capital;              # столиця
           wdt:P1082 ?population;         # населення
           wdt:P2046 ?area;               # площа
           wdt:P38 ?currency;             # валюта
           wdt:P30 ?continent;            # континент
           wdt:P37 ?language;             # офіційна мова
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en".
  }
}
LIMIT 20

# Оголошуємо префікси (коротші імена для URI)
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>          # RDF schema, використовується для rdfs:label
PREFIX foaf: <http://xmlns.com/foaf/0.1/>                     # FOAF, для типу країни foaf:Country
PREFIX p: <http://marclieber.fr/ontology/src/>                # Власний простір імен, властивість p:wikidata (посилання на QID)
PREFIX wd: <http://www.wikidata.org/entity/>                  # Простір Wikidata для Q-ідентифікаторів
PREFIX wdt: <http://www.wikidata.org/prop/direct/>            # Direct properties Wikidata, типу P36 (столиця), P38 (валюта), P37 (мова)

# Починаємо основний запит SELECT
SELECT ?localName ?wikidataID ?countryLabel ?capitalLabel ?currencyLabel ?languageLabel WHERE {

  # --- Вибираємо країни з локальної бази ---
  ?country a foaf:Country ;           # Об'єкт має тип foaf:Country
           rdfs:label ?localName ;    # Має мітку (назву) локально
           p:wikidata ?wikidataID .   # Має властивість p:wikidata з посиланням на QID у Wikidata

  # --- Звернення до Wikidata через SERVICE ---
  SERVICE <https://query.wikidata.org/sparql> {   # Підключаємо зовнішній SPARQL endpoint Wikidata
    
    ?wikidataID rdfs:label ?countryLabel .        # Отримуємо назву країни у Wikidata

    # Опційно отримуємо столицю
    OPTIONAL {
      ?wikidataID wdt:P36 ?capital .              # Зв'язок країни зі столицею (P36)
      ?capital rdfs:label ?capitalLabel .         # Назва столиці
    }

    # Опційно отримуємо валюту
    OPTIONAL {
      ?wikidataID wdt:P38 ?currency .             # Зв'язок країни з валютою (P38)
      ?currency rdfs:label ?currencyLabel .       # Назва валюти
    }

    # Опційно отримуємо офіційну мову
    OPTIONAL {
      ?wikidataID wdt:P37 ?language .             # Зв'язок країни з офіційною мовою (P37)
      ?language rdfs:label ?languageLabel .       # Назва мови
    }

    # Фільтри для вибору лише англійських назв (де можливо)
    FILTER (LANG(?countryLabel) = "en")           # Назва країни англійською
    FILTER (LANG(?capitalLabel) = "en" || !BOUND(?capitalLabel))   # Столиця англійською, або якщо відсутня — не відфільтровуємо
    FILTER (LANG(?currencyLabel) = "en" || !BOUND(?currencyLabel)) # Валюта англійською або null
    FILTER (LANG(?languageLabel) = "en" || !BOUND(?languageLabel)) # Мова англійською або null
  }
}


