from ray import serve
import ray

@serve.deployment
class HealthCheck:
    async def __call__(self, request):
        """Health Check: devuelve el estado de la aplicación."""
        return {"status": "ok"}

app = HealthCheck.bind()
