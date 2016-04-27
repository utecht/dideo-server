from django.core.management.base import BaseCommand, CommandError
from questionnaire.models import *

class Command(BaseCommand):
    help = 'Generate Graphviz graph files in graphs/'

    def add_arguments(self, parser):
        parser.add_argument('question_id', nargs='*', type=int)

    def handle(self, *args, **options):
        questions = Question.objects.all()
        if options['question_id']:
            questions = Question.objects.filter(pk__in=options['question_id'])
        for question in questions:
            statements = Statement.objects.filter(question=question)
            if statements:
                with open("graphs/{}.dot".format(question.id), "w") as f:
                    f.write("digraph g { node [shape=rectangle];\n")
                    f.write("graph [splines=true, nodesep=.5, ranksep=0, overlap=false];\n")
                    for statement in statements:
                        f.write(self.parse(statement))
                    f.write("}")

    def humanize(self, statement, question):
        predicates = {
                'obo:BFO_0000053': 'is_bearer_of',
                'obo:BFO_0000051': 'has_part',
                'obo:RO_0000052': 'inheres_in',
                'obo:RO_0000056': 'participates_in',
                'obo:IAO_0000136': 'is_about',
                'obo:BFO_0000050': 'part_of',
                'obo:RO_0002350': 'member_of',
                'obo:RO_0000059': 'concretizes',
                'obo:BFO_0000055': 'realizes',
                }
        for key in predicates:
            statement = statement.replace(key, predicates[key])
        return statement


    def parse(self, statement):
        subject = self.humanize(statement.subject, statement.question)
        obj = self.humanize(statement.obj, statement.question)
        predicate = self.humanize(statement.predicate, statement.question)
        return '"{}" -> "{}" [label="{}"]\n'.format(
                                            subject,
                                            obj,
                                            predicate)
