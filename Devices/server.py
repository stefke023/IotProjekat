from http.server import HTTPServer, SimpleHTTPRequestHandler

def main():
    server_address = ('', 8000)  
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    httpd.serve_forever()

if __name__ == "__main__": 
    main()