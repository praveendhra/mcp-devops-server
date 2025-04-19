"""Cloud cost analysis tools for MCP server."""
import json
import subprocess
from datetime import datetime, timedelta


def aws_cost_by_service(days: int = 30, profile: str = "default") -> dict:
    """Get AWS costs broken down by service."""
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    cmd = [
        "aws", "ce", "get-cost-and-usage",
        "--profile", profile,
        "--time-period", f"Start={start},End={end}",
        "--granularity", "MONTHLY",
        "--metrics", "BlendedCost",
        "--group-by", "Type=DIMENSION,Key=SERVICE",
        "--output", "json"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}

    data = json.loads(result.stdout)
    services = []
    for period in data.get("ResultsByTime", []):
        for group in period.get("Groups", []):
            cost = float(group["Metrics"]["BlendedCost"]["Amount"])
            if cost > 0.01:
                services.append({
                    "service": group["Keys"][0],
                    "cost": round(cost, 2)
                })

    services.sort(key=lambda x: x["cost"], reverse=True)
    total = sum(s["cost"] for s in services)
    return {"period": f"{start} to {end}", "total": round(total, 2), "services": services[:20]}


def aws_cost_forecast(days: int = 30, profile: str = "default") -> dict:
    """Get AWS cost forecast."""
    start = datetime.now().strftime("%Y-%m-%d")
    end = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

    cmd = [
        "aws", "ce", "get-cost-forecast",
        "--profile", profile,
        "--time-period", f"Start={start},End={end}",
        "--granularity", "MONTHLY",
        "--metric", "BLENDED_COST",
        "--output", "json"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}

    data = json.loads(result.stdout)
    return {
        "forecast_period": f"{start} to {end}",
        "total_forecast": data.get("Total", {}).get("Amount"),
        "unit": data.get("Total", {}).get("Unit")
    }
