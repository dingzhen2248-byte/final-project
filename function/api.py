import requests

# send get request
def get_request(base_url,params):
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
    except Exception as e:
        print("Error fetching data:", e)
        data = []
    print("response:", response.text)
    return data


# send post request
def post_request(base_url,params):
    try:
        response = requests.post(base_url, json=params)
        data = response.json()
    except Exception as e:
        print("Error fetching data:", e)
        data = []
    print("response:", response.text)
    return data