from datetime import datetime

DATE_FORMAT = "%Y-%m-%d"
STATUS_PENDING = "pending"
STATUS_COMPLETED = "completed"
VALID_STATUSES = (STATUS_PENDING, STATUS_COMPLETED)
NO_NUMBER = 10**9

def today_string():
    return datetime.today().strftime(DATE_FORMAT)


def parse_date(text):
    try:
        return datetime.strptime(text.strip(), DATE_FORMAT).strftime(DATE_FORMAT)
    except ValueError:
        return None


def id_number(task_id):
    digits = "".join(ch for ch in str(task_id) if ch.isdigit())
    return int(digits) if digits else NO_NUMBER


def make_task_id(number):
    return f"T{number:03d}"


# ==========================TASK==================

class Task:
    def __init__(self, task_id, title, subject, due_date, status=STATUS_PENDING):
        self.task_id = str(task_id)
        self.title = str(title)
        self.subject = str(subject)
        self.due_date = str(due_date)

        status = str(status).lower()
        self.status = status if status in VALID_STATUSES else STATUS_PENDING

    def is_completed(self):
        return self.status == STATUS_COMPLETED

    def is_overdue(self, today=None):
        today = today or today_string()
        return (not self.is_completed()) and self.due_date < today

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "title": self.title,
            "subject": self.subject,
            "due_date": self.due_date,
            "status": self.status,
        }


# ====================TASK MANAGER=================

class TaskManager:
    def __init__(self):
        self.task = {}

    # ============(add / find / delete)========

    def add_task(self, task):
        self.task[task.task_id] = task

    def create_task(self, title, subject, due_date):
        task = Task(self.next_id(), title, subject, due_date)
        self.add_task(task)
        return task

    def get_task(self, task_id):
        return self.task.get(task_id)

    def delete_task(self, task_id):
        if task_id in self.task:
            del self.task[task_id]
            self.renumber_tasks()
            return True

        return False

    # ===============(ids and ordering)====================
    def next_id(self):
        numbers = [id_number(tid) for tid in self.task if id_number(tid) != NO_NUMBER]
        return make_task_id(max(numbers) + 1 if numbers else 1)

    def get_sorted_tasks(self):
        return sorted(self.task.values(), key=lambda t: (id_number(t.task_id), t.task_id))

    def renumber_tasks(self):               # (SORTING)
        ordered = self.get_sorted_tasks()
        self.task = {}

        for number, task in enumerate(ordered, start=1):
            task.task_id = make_task_id(number)
            self.task[task.task_id] = task

    # ================(search and filter)=============
    def search_by_subject(self, subject):
        subject = subject.strip().lower()
        return [t for t in self.get_sorted_tasks() if subject in t.subject.lower()]
    
    def filter_tasks(self, status=None, text=""):
        text = text.strip().lower()
        results = []

        for task in self.get_sorted_tasks():
            if status and task.status != status:
                continue
            if text and not (
                text in task.title.lower()
                or text in task.subject.lower()
                or text in task.task_id.lower()
            ):
                continue
            results.append(task)

        return results

    def get_upcoming(self, limit=5):
        pending = [t for t in self.task.values() if not t.is_completed()]
        return sorted(pending, key=lambda t: t.due_date)[:limit]

    # =================(summary)==============
    def get_summary(self):
        tasks = list(self.task.values())
        today = today_string()

        total = len(tasks)
        completed = sum(1 for t in tasks if t.is_completed())
        overdue = sum(1 for t in tasks if t.is_overdue(today))

        return {
            "total": total,
            "completed": completed,
            "pending": total - completed,
            "overdue": overdue,
        }