"""
Main Locust load testing file
Simulates realistic user behavior patterns
"""

import random
from datetime import datetime

from locust import HttpUser, between, events, task


class ShadowTag-v2User(HttpUser):
    """
    Simulates a user interacting with the ShadowTag-v2 FastAPI Services
    """

    # Wait time between tasks (simulates user think time)
    wait_time = between(1, 3)

    def on_start(self):
        """Called when a simulated user starts"""
        self.user_id = None
        self.task_ids = []
        self.headers = {"Content-Type": "application/json"}

    @task(5)
    def health_check(self):
        """Check application health"""
        with self.client.get("/health/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @task(3)
    def ping(self):
        """Quick ping endpoint"""
        self.client.get("/health/ping")

    @task(2)
    def get_metrics(self):
        """Get system metrics"""
        self.client.get("/health/metrics")

    @task(10)
    def create_user(self):
        """Create a new user"""
        username = f"user_{random.randint(1, 1000000)}"
        email = f"{username}@example.com"

        payload = {
            "username": username,
            "email": email,
            "full_name": f"Test User {username}",
            "password": "[VAPORIZED_PWD]",
            "role": random.choice(["user", "admin", "guest"]),
        }

        with self.client.post(
            "/users/", json=payload, headers=self.headers, catch_response=True
        ) as response:
            if response.status_code == 201:
                self.user_id = response.json()["id"]
                response.success()
            elif response.status_code == 400:
                # User might already exist, that's okay
                response.success()
            else:
                response.failure(f"Failed to create user: {response.status_code}")

    @task(15)
    def list_users(self):
        """List users with pagination"""
        skip = random.randint(0, 100)
        limit = random.randint(10, 50)
        self.client.get(f"/users/?skip={skip}&limit={limit}")

    @task(8)
    def get_user(self):
        """Get a specific user"""
        if self.user_id:
            self.client.get(f"/users/{self.user_id}")
        else:
            # Try a random user ID
            user_id = random.randint(1, 100)
            self.client.get(f"/users/{user_id}", name="/users/[id]")

    @task(12)
    def create_task(self):
        """Create a new task"""
        if not self.user_id:
            self.user_id = random.randint(1, 100)

        payload = {
            "title": f"Task {random.randint(1, 10000)}",
            "description": "This is a test task for load testing",
            "status": random.choice(["pending", "in_progress", "completed", "failed"]),
            "priority": random.randint(1, 5),
            "user_id": self.user_id,
        }

        with self.client.post(
            "/tasks/", json=payload, headers=self.headers, catch_response=True
        ) as response:
            if response.status_code == 201:
                self.task_ids.append(response.json()["id"])
                response.success()
            elif response.status_code == 404:
                # User not found, create one
                response.success()
            else:
                response.failure(f"Failed to create task: {response.status_code}")

    @task(20)
    def list_tasks(self):
        """List tasks with filters"""
        params = {}
        if random.random() > 0.5:
            params["status"] = random.choice(["pending", "in_progress", "completed", "failed"])
        if random.random() > 0.5:
            params["priority"] = random.randint(1, 5)

        params["skip"] = random.randint(0, 100)
        params["limit"] = random.randint(10, 50)

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        self.client.get(f"/tasks/?{query_string}")

    @task(7)
    def get_task(self):
        """Get a specific task"""
        if self.task_ids:
            task_id = random.choice(self.task_ids)
            self.client.get(f"/tasks/{task_id}")
        else:
            task_id = random.randint(1, 100)
            self.client.get(f"/tasks/{task_id}", name="/tasks/[id]")

    @task(5)
    def update_task_status(self):
        """Update task status"""
        if self.task_ids:
            task_id = random.choice(self.task_ids)
            new_status = random.choice(["pending", "in_progress", "completed", "failed"])
            self.client.patch(f"/tasks/{task_id}/status", params={"new_status": new_status})

    @task(10)
    def get_data(self):
        """Get sample data"""
        item_id = random.randint(1, 1000)
        self.client.get(f"/api/data/{item_id}")

    @task(3)
    def compute(self):
        """CPU-intensive endpoint"""
        iterations = random.randint(100, 1000)
        self.client.post("/api/compute", json={"iterations": iterations})


class QuickLoadUser(HttpUser):
    """
    Quick load test user - only hits lightweight endpoints
    """

    wait_time = between(0.5, 1.5)

    @task(10)
    def ping(self):
        self.client.get("/health/ping")

    @task(5)
    def health_check(self):
        self.client.get("/health/")

    @task(3)
    def get_data(self):
        item_id = random.randint(1, 1000)
        self.client.get(f"/api/data/{item_id}")


class StressTestUser(HttpUser):
    """
    Stress test user - focuses on heavy operations
    """

    wait_time = between(0.1, 0.5)

    @task(10)
    def compute(self):
        iterations = random.randint(5000, 10000)
        self.client.post("/api/compute", json={"iterations": iterations})

    @task(5)
    def create_user(self):
        username = f"stress_user_{random.randint(1, 1000000)}"
        payload = {
            "username": username,
            "email": f"{username}@example.com",
            "full_name": f"Stress User {username}",
            "password": "[VAPORIZED_PWD]",
            "role": "user",
        }
        self.client.post("/users/", json=payload)

    @task(8)
    def create_task(self):
        payload = {
            "title": f"Stress Task {random.randint(1, 10000)}",
            "description": "Stress test task",
            "status": "pending",
            "priority": random.randint(1, 5),
            "user_id": random.randint(1, 100),
        }
        self.client.post("/tasks/", json=payload)


# Event handlers for metrics collection
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when the test starts"""
    print(f"🚀 Load test starting at {datetime.now()}")
    print(f"Target host: {environment.host}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when the test stops"""
    print(f"🏁 Load test completed at {datetime.now()}")

    # Print summary statistics
    stats = environment.stats
    print("\n" + "=" * 80)
    print("LOAD TEST SUMMARY")
    print("=" * 80)
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Failed requests: {stats.total.num_failures}")
    print(f"Success rate: {(1 - stats.total.fail_ratio) * 100:.2f}%")
    print(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    print(f"Min response time: {stats.total.min_response_time:.2f}ms")
    print(f"Max response time: {stats.total.max_response_time:.2f}ms")
    print(f"Requests per second: {stats.total.total_rps:.2f}")
    print("=" * 80)


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Called for every request"""
    # Detect breaking points (response time > 5000ms or exceptions)
    if response_time > 5000 or exception:
        print("⚠️  Potential breaking point detected!")
        print(f"   Endpoint: {name}")
        print(f"   Response time: {response_time}ms")
        if exception:
            print(f"   Exception: {exception}")
