from locust import HttpUser, constant, constant_throughput, tag, task


class APIUser(HttpUser):
    host = "http://127.0.0.1:8003"
    wait_time = constant_throughput(0.2)

    def on_start(self):
        self.client.cookies.set("sessionid", "nfb7ppymvviwimz51dgnxjmcf07hl2u1")
        self.client.cookies.set("csrftoken", "o7tqr16lvvOJudwMpniUbFYDYGG2Xz7O")

    @tag('get') 
    @task
    def get_categories(self):
        self.client.get("/api/category/spending/")

    @tag("use_case")
    @task
    def use_case(self):
        self.client.get("/api/category/spending/")
        self.client.get("/api/category")