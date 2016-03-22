import requests
from questionnaire.models import Definition

def get_definitions():
    query = """
PREFIX obo: <http://purl.obolibrary.org/obo/>
    SELECT DISTINCT ?term ?userdef
    WHERE {
      ?class rdf:type owl:Class .
      ?class rdfs:label ?term .
      ?class obo:OOSTT_00000030 ?userdef .
}
    """
    body = {'query': query, 'Accept': 'application/sparql-results+json' }
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    r = requests.request('POST', 'http://cafe:5000/rdf', data=body, headers=headers)
    if r.ok:
        try:
            data = r.json()
            terms = []
            for term in data['results']['bindings']:
                word = term['term']['value']
                defi = term['userdef']['value']
                terms.append(Definition(word, defi))
            return terms
        except ValueError:
            print('Bad json data')
            print(r.content)
            return False
    else:
        print(r)
        return False


def delete_context(context):
    pass

def run_statements(statments, context, user):
    pass
