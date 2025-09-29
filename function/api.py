import requests

# 发送get请求
def get_request(base_url,params):
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
    except Exception as e:
        print("Error fetching data:", e)
        data = []
    print("response:", response.text)
    return data


# 发送post请求
def post_request(base_url,params):
    try:
        response = requests.post(base_url, json=params)
        data = response.json()
    except Exception as e:
        print("Error fetching data:", e)
        data = []
    print("response:", response.text)
    return data