PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX p: <http://marclieber.fr/ontology/src/>

SELECT ?name ?wikidata
WHERE {
  ?country rdfs:label ?name ;
           p:wikidata ?wikidata .
}

---

PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX p: <http://marclieber.fr/ontology/src/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?localName ?countryLabel
WHERE {
  ?country a foaf:Country ;
           rdfs:label ?localName ;
           p:wikidata ?wikidataID .

  SERVICE <https://query.wikidata.org/sparql> {
    ?wikidataID rdfs:label ?countryLabel .
    FILTER(LANG(?countryLabel) = "en")
  }
}

---

PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX p: <http://marclieber.fr/ontology/src/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT ?localName ?countryLabel ?capitalLabel ?currencyLabel ?languageLabel
WHERE {
  # Локальна країна
  ?country a foaf:Country ;
           rdfs:label ?localName ;
           p:wikidata ?wikidataID .

  # Запит до Wikidata через SERVICE
  SERVICE <https://query.wikidata.org/sparql> {
    ?wikidataID rdfs:label ?countryLabel .
    OPTIONAL { ?wikidataID wdt:P36 ?capital . ?capital rdfs:label ?capitalLabel . }
    OPTIONAL { ?wikidataID wdt:P38 ?currency . ?currency rdfs:label ?currencyLabel . }
    OPTIONAL { ?wikidataID wdt:P37 ?language . ?language rdfs:label ?languageLabel . }

    FILTER(LANG(?countryLabel) = "en")
    FILTER(LANG(?capitalLabel) = "en" || !BOUND(?capitalLabel))
    FILTER(LANG(?currencyLabel) = "en" || !BOUND(?currencyLabel))
    FILTER(LANG(?languageLabel) = "en" || !BOUND(?languageLabel))
  }
}
