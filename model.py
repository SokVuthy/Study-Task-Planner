from datetime import datetime

class Task:
    def __init__(self, task_id, title, subject, due_date, status="pending"):
        self.task_id= task_id
        self.title= title
        self.subject= subject
        self.due_date= due_date
        self.status= status

    def to_dict(self):
        return {
            "task_id" : self.task_id,
            "title": self.title,
            "subject": self.subject,
            "due_date": self.due_date,
            "status": self.status,
        
        }
class TaskManager:
    def __init__(self):
        self.task= {}

    def add_task(self, task):
        self.task[task.task_id]= task

    def get_task(self, task_id):
        return self.task.get(task_id)

    def delete_task(self, task_id):
        if task_id in self.task:
            del self.task[task_id]
            return True                     # if success
        
        return False                        # if not found = false

    def get_summary(self):                  #summarize statistic

        total= len(self.task)

        completed = sum(1 for t in self.task.values() if t.status.lower=="completed")

        pending = total - completed

        overdue= 0
        
        today= datetime.today().strftime('%Y-%m-%d')

        for t in self.task.values():
            if t.status.lower() == "pending" and t.due_date < today:            # if status still pending and due date is older than today --> overdue 
                overdue+= 1

        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "overdue": overdue
        }