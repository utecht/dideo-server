from django.core.management.base import BaseCommand, CommandError
from questionnaire.models import *

class Command(BaseCommand):
    help = 'Generate Graphviz graph files in graphs/'

    def handle(self, *args, **options):
        self.stdout.write('{} statements'.format(len(Statement.objects.all())))
        for question in Question.objects.all():
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
