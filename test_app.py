import unittest
from app import app, init_db
import sqlite3


class TaskManagerHTMLTests(unittest.TestCase):
    def setUp(self):
        """Настраиваем тестовое окружение."""
        self.app = app.test_client()
        self.app.testing = True  # Включаем режим тестирования
        init_db()  # Создаем базу данных и таблицы

        # Очищаем таблицу задач перед тестами
        with sqlite3.connect("tasks.db") as conn:
            conn.execute("DELETE FROM tasks")

    def test_add_task(self):
        response = self.app.post("/add", data={"description": "Test Task"})
        self.assertEqual(response.status_code, 302)
        response = self.app.get("/")
        self.assertIn(b"Test Task", response.data)

    def test_list_tasks(self):
        self.app.post("/add", data={"description": "Task 1"})
        self.app.post("/add", data={"description": "Task 2"})
        response = self.app.get("/")
        self.assertIn(b"Task 1", response.data)
        self.assertIn(b"Task 2", response.data)

    def test_complete_task(self):
        self.app.post("/add", data={"description": "Test Task"})
        with sqlite3.connect("tasks.db") as conn:
            task_id = conn.execute("SELECT id FROM tasks WHERE description = 'Test Task'").fetchone()[0]
        self.app.get(f"/complete/{task_id}")
        response = self.app.get("/")
        self.assertIn(b"class=\"completed\"", response.data)  # Ищем класс `completed` в HTML

    def test_delete_task(self):
        self.app.post("/add", data={"description": "Test Task"})
        with sqlite3.connect("tasks.db") as conn:
            task_id = conn.execute("SELECT id FROM tasks WHERE description = 'Test Task'").fetchone()[0]
        self.app.get(f"/delete/{task_id}")
        response = self.app.get("/")
        self.assertNotIn(b"Test Task", response.data)

    def test_add_task_without_description(self):
        response = self.app.post("/add", data={"description": ""})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(b"class=\"task\"", response.data)


if __name__ == "__main__":
    unittest.main()
