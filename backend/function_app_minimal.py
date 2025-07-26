import azure.functions as func
import json

# Create a minimal function app for testing
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="test", methods=["GET"])
def test_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Simple test endpoint to verify function app is working"""
    return func.HttpResponse(
        json.dumps({"status": "ok", "message": "Function app is working!"}),
        status_code=200,
        headers={"Content-Type": "application/json"}
    )

@app.route(route="health", methods=["GET"])
def health_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Minimal health check"""
    return func.HttpResponse(
        json.dumps({"status": "healthy", "timestamp": "2025-07-25"}),
        status_code=200,
        headers={"Content-Type": "application/json"}
    )
