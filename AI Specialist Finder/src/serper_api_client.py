import http.client
import json

class SerperAPIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.conn = http.client.HTTPSConnection("google.serper.dev")

    def search(self, query: str) -> dict:
        payload = json.dumps({
            "q": query
        })
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        self.conn.request("POST", "/search", payload, headers)
        res = self.conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))

if __name__ == "__main__":
    api_key = "2fb50306700da371c6a4d46b28d6045830fa7781"
    client = SerperAPIClient(api_key)
    result = client.search("apple inc")
    print(json.dumps(result, indent=2))
