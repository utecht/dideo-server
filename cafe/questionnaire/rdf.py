import requests
from questionnaire.models import *
from rdflib import Graph, BNode, URIRef, Literal, Namespace

graph = Graph()
print("RDF Graph ready")

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

def get_uri(text, prefixes, bnodes):
    split = text.split(':')
    if len(split) > 1:
        # we have a prefix
        if split[0] == '_':
            # we have a blank node

            # check to see if it already exists
            if split[1] in bnodes.keys():
                return bnodes[split[1]]
            else:
                # if not create it
                b = BNode(split[1])
                bnodes[split[1]] = b
                return b
        else:
            if split[0] in prefixes.keys():
                return prefixes[split[0]][split[1]]
            else:
                print('No prefix found: {}'.format(split))
                return None
    else:
        return text



    pass

def get_triples(answer, prefixes, bnodes):
    ret = []
    q_type = answer.question.q_type
    if q_type == 'bool':
        if answer.yesno:
            for statement in Statement.objects.filter(question=answer.question):
                s = get_uri(statement.subject, prefixes, bnodes)
                p = get_uri(statement.predicate, prefixes, bnodes)
                o = get_uri(statement.obj, prefixes, bnodes)
                ret.append((s, p, o))
    elif q_type == 'combo':
        if answer.text:
            for statement in Statement.objects.filter(question=answer.question):
                if statement.choice is not None:
                    if str(statement.choice) == str(answer.text):
                        s = get_uri(statement.subject, prefixes, bnodes)
                        p = get_uri(statement.predicate, prefixes, bnodes)
                        o = get_uri(statement.obj, prefixes, bnodes)
                        ret.append((s, p, o))
                else:
                    s = get_uri(statement.subject, prefixes, bnodes)
                    p = get_uri(statement.predicate, prefixes, bnodes)
                    o = get_uri(statement.obj, prefixes, bnodes)
                    ret.append((s, p, o))
    elif q_type == 'drugs':
        if answer.text:
            chebi = Chebi.objects.get(name=answer.text)
            chebi_text = "obo:CHEBI_{}".format(chebi.accession.split(':')[1])
            survey = '_:study'
            drug_product = 'obo:DRON_00000005'
            rdf_type = 'rdf:type'
            bearer_of = 'obo:RO_0000053'
            specified_input = 'obo:OBI_0000293'
            object_role = 'obo:DIDEO_00000012'
            precip_role = 'obo:DIDEO_00000013'
            s = get_uri(survey, prefixes, bnodes)
            p = get_uri(specified_input, prefixes, bnodes)
            o = get_uri(chebi_text, prefixes, bnodes)
            ret.append((s, p, o))
            s = get_uri(chebi_text, prefixes, bnodes)
            p = get_uri(rdf_type, prefixes, bnodes)
            o = get_uri(drug_product, prefixes, bnodes)
            ret.append((s, p, o))
            print(answer.yesno)
            if answer.yesno is not None:
                if answer.yesno:
                    s = get_uri(chebi_text, prefixes, bnodes)
                    p = get_uri(bearer_of, prefixes, bnodes)
                    o = get_uri(object_role, prefixes, bnodes)
                    ret.append((s, p, o))
                else:
                    s = get_uri(chebi_text, prefixes, bnodes)
                    p = get_uri(bearer_of, prefixes, bnodes)
                    o = get_uri(precip_role, prefixes, bnodes)
                    ret.append((s, p, o))

    elif q_type == 'int' or q_type == 'text':
        for statement in Statement.objects.filter(question=answer.question):
            if statement.value:
                s = get_uri(statement.subject, prefixes, bnodes)
                p = get_uri(statement.predicate, prefixes, bnodes)
                if q_type == 'int':
                    o = Literal(answer.integer)
                else:
                    o = Literal(answer.text)
                ret.append((s, p, o))
            else:
                s = get_uri(statement.subject, prefixes, bnodes)
                p = get_uri(statement.predicate, prefixes, bnodes)
                o = get_uri(statement.obj, prefixes, bnodes)
                ret.append((s, p, o))
        

    return ret
        

def rdf_from_survey(survey):
    # first clear graph
    g = Graph()
    bnodes = {}

    # next load prefixes
    prefixes = {}
    for prefix in RDFPrefix.objects.all():
        prefixes[prefix.short] = Namespace(prefix.full)

    # Generate triples for answers
    for answer in Answer.objects.filter(survey=survey):
        for triple in get_triples(answer, prefixes, bnodes):
            g.add(triple)

    return g.serialize()
