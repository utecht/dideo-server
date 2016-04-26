from django.core.management.base import BaseCommand, CommandError
from questionnaire.models import *

class Command(BaseCommand):
    help = 'Generate Graphviz graph files in graphs/'

    def handle(self, *args, **options):
        self.stdout.write('{} statements'.format(len(Statement.objects.all())))
        with open("graphs/super.dot", "w") as f:
            f.write("digraph g { node [shape=rectangle];\n")
            for statement in Statement.objects.all():
                f.write(self.parse(statement))
            f.write("}")

    def parse(self, statement):
        subject = statement.subject
        obj = statement.obj
        predicate = statement.predicate
        if "_:" in subject:
            subject = subject.replace("_:", "{}:".format(statement.question.id))
        if "_:" in predicate:
            predicate = predicate.replace("_:", "{}:".format(statement.question.id))
        if "_:" in obj:
            obj = obj.replace("_:", "{}:".format(statement.question.id))
        return '"{}" -> "{}" [label="{}"]\n'.format(
                                            subject,
                                            obj,
                                            predicate)
