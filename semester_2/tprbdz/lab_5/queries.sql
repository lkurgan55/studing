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
