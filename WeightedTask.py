import sys


class WeightedTask:
    def __init__(self, task_id, weight):
        self.id = task_id
        self.weight = int(weight)

    def to_string(self):
        return "task id:{id}\ntask weight: {weight}".format(id=self.id, weight=self.weight)

    def __eq__(self, other):
        return self.id == other.task_id

    def __add__(self, other):
        try:
            if self.id != other.id:
                raise ValueError
            return self.weight + other.weight
        except ValueError:
            msg = "Cannot add weight from different tasks"
            sys.stdout.write("\n{}".format(msg))
            exit(1)
