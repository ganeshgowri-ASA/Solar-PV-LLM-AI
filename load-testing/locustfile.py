"""
Locust Load Testing Configuration for Solar PV LLM AI
Simulates realistic user traffic patterns
"""

from locust import HttpUser, task, between, SequentialTaskSet
import random
import json


class UserBehavior(SequentialTaskSet):
    """Sequential task set simulating realistic user behavior"""

    def on_start(self):
        """Setup tasks - runs once when a user starts"""
        self.system_id = None

    @task
    def health_check(self):
        """Check system health"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @task
    def list_solar_systems(self):
        """List all solar PV systems"""
        with self.client.get("/api/v1/solar-pv/systems", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    self.system_id = data[0]['id']
                response.success()
            else:
                response.failure(f"List systems failed: {response.status_code}")

    @task
    def get_system_details(self):
        """Get details of a specific system"""
        if self.system_id:
            with self.client.get(
                f"/api/v1/solar-pv/systems/{self.system_id}",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    response.success()
                elif response.status_code == 404:
                    response.failure("System not found")
                else:
                    response.failure(f"Get system failed: {response.status_code}")

    @task
    def ml_prediction(self):
        """Make ML prediction"""
        payload = {
            "features": {
                "temperature": random.uniform(20, 35),
                "irradiance": random.uniform(500, 1000),
                "humidity": random.uniform(40, 80),
            },
            "model_name": "solar_efficiency_predictor"
        }

        with self.client.post(
            "/api/v1/ml/predict",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Prediction failed: {response.status_code}")

    @task
    def rag_query(self):
        """Ask RAG question"""
        questions = [
            "What is the optimal angle for solar panels?",
            "How does temperature affect solar panel efficiency?",
            "What are the best practices for solar PV maintenance?",
            "How to calculate solar panel output?",
        ]

        payload = {
            "question": random.choice(questions),
            "max_sources": 5,
            "audience_level": random.choice(["beginner", "intermediate", "expert"])
        }

        with self.client.post(
            "/api/v1/rag/query",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"RAG query failed: {response.status_code}")


class SolarPVUser(HttpUser):
    """Simulated user for Solar PV LLM AI"""

    tasks = [UserBehavior]
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks
    host = "http://localhost:8000"


class AdminUser(HttpUser):
    """Simulated admin user with different access patterns"""

    wait_time = between(2, 8)

    @task(5)
    def view_metrics(self):
        """View system metrics"""
        self.client.get("/metrics")

    @task(3)
    def list_training_jobs(self):
        """List training jobs"""
        self.client.get("/api/v1/training/jobs")

    @task(2)
    def view_models(self):
        """View available models"""
        self.client.get("/api/v1/ml/models")

    @task(1)
    def create_training_job(self):
        """Create a new training job"""
        payload = {
            "model_name": "test_model",
            "training_data_path": "/data/training.csv",
            "hyperparameters": {
                "learning_rate": 0.001,
                "batch_size": 32,
            },
            "incremental": True
        }

        self.client.post("/api/v1/training/jobs", json=payload)


# Run with:
# locust -f locustfile.py --host=http://localhost:8000
# or
# locust -f locustfile.py --host=https://api.your-domain.com --users=100 --spawn-rate=10 --run-time=5m
