import requests
from questionnaire.models import Definition

def get_definitions():
    query = """
PREFIX obo: <http://purl.obolibrary.org/obo/>
    SELECT DISTINCT ?term ?userdef ?otherdef
    FROM <https://raw.githubusercontent.com/OOSTT/OOSTT/master/oostt.owl>
    WHERE {
      ?class rdf:type owl:Class .
      ?class rdfs:label ?term .
      optional {?class obo:OOSTT_00000030 ?userdef . }
      optional {?class obo:IAO_0000115 ?otherdef . }
}
    """
    body = {'query': query, 'Accept': 'application/sparql-results+json' }
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    r = requests.request('POST', 'http://dideo.cafe-trauma.com/rdf', data=body, headers=headers)
    if r.ok:
        try:
            data = r.json()
            terms = []
            for term in data['results']['bindings']:
                word = term['term']['value']
                defi = ''
                if 'userdef' in term.keys():
                    defi = term['userdef']['value']
                elif 'otherdef' in term.keys():
                    defi = term['otherdef']['value']
                terms.append(Definition(word, defi))
            terms.append(Definition("hello", "world"))
            return terms
        except ValueError:
            print('Bad json data')
            print(r.content)
            return [Definition('error', 'error')]
    else:
        print(r)
        return [Definition('error', 'error')]


def delete_context(context):
    pass

def run_statements(statments, context, user):
    pass
