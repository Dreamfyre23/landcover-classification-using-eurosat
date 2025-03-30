from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):  # New method for browser access
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Send POST requests to this endpoint (use curl/Postman).")
        
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = json.dumps({
            "status": "success",
            "predictions": [
                {"patch": "0,0", "class": "AnnualCrop"},
                {"patch": "0,64", "class": "AnnualCrop"},
                {"patch": "0,128", "class": "AnnualCrop"},
                {"patch": "0,192", "class": "AnnualCrop"},
                {"patch": "0,256", "class": "AnnualCrop"},
                {"patch": "0,320", "class": "AnnualCrop"},
                {"patch": "0,384", "class": "AnnualCrop"},
                {"patch": "0,448", "class": "AnnualCrop"},
                {"patch": "0,512", "class": "AnnualCrop"},
                {"patch": "0,576", "class": "AnnualCrop"}
            ],
            "class_distribution": {
                "AnnualCrop": 0.9934,
                "Highway": 0.0066
            }
        }).encode()
        self.wfile.write(response)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f'Starting server on port {port}...')
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()
