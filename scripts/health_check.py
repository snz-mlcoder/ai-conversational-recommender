import requests
from catalog_builder.config import BASE_URL, USER_AGENT

def run():
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(BASE_URL, headers=headers, timeout=20)
    print("Status code:", r.status_code)
    print("Content length:", len(r.text))

if __name__ == "__main__":
    run()
