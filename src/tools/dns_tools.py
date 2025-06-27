"""DNS management and debugging tools for MCP server."""
import json
import subprocess
import socket


def dns_lookup(domain: str, record_type: str = "A") -> dict:
    """Perform DNS lookup for a domain."""
    try:
        cmd = ["dig", "+short", domain, record_type]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        records = [r.strip() for r in result.stdout.strip().split("\n") if r.strip()]
        return {"domain": domain, "type": record_type, "records": records}
    except subprocess.TimeoutExpired:
        return {"error": f"DNS lookup timed out for {domain}"}
    except Exception as e:
        return {"error": str(e)}


def dns_trace(domain: str) -> dict:
    """Trace DNS resolution path."""
    cmd = ["dig", "+trace", domain]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        return {"error": result.stderr}
    return {"domain": domain, "trace": result.stdout}


def check_ssl_certificate(domain: str, port: int = 443) -> dict:
    """Check SSL certificate details for a domain."""
    cmd = [
        "openssl", "s_client", "-connect", f"{domain}:{port}",
        "-servername", domain, "-brief"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10,
                           input="")
    if result.returncode != 0 and not result.stderr:
        return {"error": "Could not connect"}

    # Parse certificate info
    cert_cmd = [
        "openssl", "s_client", "-connect", f"{domain}:{port}",
        "-servername", domain
    ]
    cert_result = subprocess.run(cert_cmd, capture_output=True, text=True,
                                timeout=10, input="")

    info_cmd = ["openssl", "x509", "-noout", "-subject", "-issuer",
                "-dates", "-ext", "subjectAltName"]
    info_result = subprocess.run(info_cmd, input=cert_result.stdout,
                                capture_output=True, text=True)

    return {"domain": domain, "port": port, "certificate_info": info_result.stdout}


def check_endpoints(endpoints: list) -> dict:
    """Check health of multiple endpoints."""
    results = []
    for ep in endpoints:
        try:
            cmd = ["curl", "-s", "-o", "/dev/null", "-w",
                   "%{http_code}|%{time_total}|%{ssl_verify_result}",
                   "-m", "10", ep]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            parts = result.stdout.split("|")
            results.append({
                "endpoint": ep,
                "status_code": int(parts[0]) if parts[0].isdigit() else 0,
                "response_time_s": float(parts[1]) if len(parts) > 1 else None,
                "ssl_ok": parts[2] == "0" if len(parts) > 2 else None
            })
        except Exception as e:
            results.append({"endpoint": ep, "error": str(e)})

    healthy = sum(1 for r in results if r.get("status_code", 0) in (200, 201, 204))
    return {"total": len(results), "healthy": healthy, "results": results}
