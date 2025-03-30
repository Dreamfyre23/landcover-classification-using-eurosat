from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        print("Received POST request")  # Visible in your terminal
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = json.dumps({
            "status": "success",
            "predictions": [{"patch": "0,0", "class": "AnnualCrop"}],
            "class_distribution": {"AnnualCrop": 0.9934, "Highway": 0.0066}
        })
        self.wfile.write(response.encode())

if __name__ == "__main__":
    port = 8080  # Test on the same port Cloud Run uses
    print(f"🔥 Server running at http://localhost:{port}")
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()
