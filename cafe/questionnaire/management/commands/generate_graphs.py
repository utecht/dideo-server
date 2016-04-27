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
                    for statement in statements:
                        f.write(self.parse(statement))
                    f.write("}")

    def parse(self, statement):
        return '"{}" -> "{}" [label="{}"]\n'.format(
                                            statement.subject,
                                            statement.obj,
                                            statement.predicate)
