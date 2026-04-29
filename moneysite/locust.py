from locust import HttpUser, constant, constant_throughput, task


class APIUser(HttpUser):
    host = "http://127.0.0.1:8000"
    wait_time = constant_throughput(0.2)

    def on_start(self):
        # Сначала получаем CSRF-токен
        self.client.get("/users/login/")
        csrftoken = self.client.cookies.get("csrftoken")

        # Логинимся через email (у тебя EmailAuthBackend)
        self.client.post("/users/login/", data={
            "username": "boris",
            "password": "borik2002",
            "csrfmiddlewaretoken": csrftoken,
        }, headers={
            "Referer": "http://127.0.0.1:8000/users/login/"
        })
    @task
    def get_categories(self):
        self.client.get("/api/category/spending/")
