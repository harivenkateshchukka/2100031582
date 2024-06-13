import requests
from django.http import JsonResponse
from threading import Lock

WINDOW_SIZE = 10
TIMEOUT = 0.5  # 500 ms
lock = Lock()

AUTHORIZATION_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzE4MjY1Mzk3LCJpYXQiOjE3MTgyNjUwOTcsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6IjA4YmIzOTlmLTQyMWUtNDZiZC05MjRhLWM5MWViYWQ0MjQ4ZiIsInN1YiI6IjIxMDAwMzE1ODJjc2VoQGdtYWlsLmNvbSJ9LCJjb21wYW55TmFtZSI6IktMIFVOSVZFUlNJVFkiLCJjbGllbnRJRCI6IjA4YmIzOTlmLTQyMWUtNDZiZC05MjRhLWM5MWViYWQ0MjQ4ZiIsImNsaWVudFNlY3JldCI6InV6d25PV2piWnNqV3V3cGgiLCJvd25lck5hbWUiOiJDSFVLS0EgSEFSSSBWRU5LQVRFU0giLCJvd25lckVtYWlsIjoiMjEwMDAzMTU4MmNzZWhAZ21haWwuY29tIiwicm9sbE5vIjoiMjEwMDAzMTU4MiJ9.alva_4F57pHeNzgvwiWqJGle8q2Y-SNxi5uSbCJKDwQ"
class NumberWindow:
    def __init__(self, size):
        self.size = size
        self.numbers = []

    def add(self, numbers):
        with lock:
            for number in numbers:
                if number not in self.numbers:
                    if len(self.numbers) >= self.size:
                        self.numbers.pop(0)
                    self.numbers.append(number)

    def average(self):
        if not self.numbers:
            return 0
        return sum(self.numbers) / len(self.numbers)

    def state(self):
        return self.numbers

windows = {
    'p': NumberWindow(WINDOW_SIZE),
    'f': NumberWindow(WINDOW_SIZE),
    'e': NumberWindow(WINDOW_SIZE),
    'r': NumberWindow(WINDOW_SIZE),
}

def fetch_numbers(numberid):
    urls = {
        'p': 'http://20.244.56.144/test/primes',
        'f': 'http://20.244.56.144/test/fibo',
        'e': 'http://20.244.56.144/test/even',
        'r': 'http://20.244.56.144/test/random',
    }
    headers = {
        'Authorization': f'Bearer {AUTHORIZATION_TOKEN}',
    }
    print(f"Fetching numbers from URL: {urls[numberid]} with headers: {headers}")
    try:
        response = requests.get(urls[numberid], headers=headers, timeout=TIMEOUT)
        print(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            json_response = response.json()
            print(f"Response JSON: {json_response}")
            return json_response.get('numbers', [])
        else:
            print(f"Failed to fetch numbers, status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"RequestException: {e}")
    return []

def get_numbers(request, numberid):
    if numberid not in windows:
        return JsonResponse({'error': 'Invalid number ID'}, status=400)

    print(f"Processing request for number ID: {numberid}")
    numbers = fetch_numbers(numberid)
    prev_state = windows[numberid].state().copy()
    windows[numberid].add(numbers)
    curr_state = windows[numberid].state().copy()
    avg = windows[numberid].average()

    print(f"Previous state: {prev_state}")
    print(f"Current state: {curr_state}")
    print(f"Average: {avg}")

    return JsonResponse({
        'numbers': numbers,
        'windowPrevState': prev_state,
        'windowCurrState': curr_state,
        'avg': avg,
    })
