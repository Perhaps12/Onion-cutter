import requests

def test_backend_generate(prompt="Hello from backend!"):
    url = "http://127.0.0.1:8000/generate"
    data = {"prompt": prompt}
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        result = response.json()
        
        if "output" in result:
            print("Generated text:", result["output"])
        else:
            print("Error in response:", result)
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)

if __name__ == "__main__":
    test_backend_generate("Once upon a time in a land far away")
