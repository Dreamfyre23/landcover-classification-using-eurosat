from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = json.dumps({
            "status": "success",
            "predictions": [
                {"patch": "0,0", "class": "AnnualCrop"},
                # ... (your other data)
            ],
            "class_distribution": {
                "AnnualCrop": 0.9934,
                "Highway": 0.0066
            }
        }).encode()
        self.wfile.write(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on port {port}")  # Verify in logs
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
