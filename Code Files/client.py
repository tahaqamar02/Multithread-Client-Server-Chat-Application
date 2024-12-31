import requests

BASE_URL = "http://127.0.0.1:5000"

def register_user():
    username = input("Enter username: ")
    password = input("Enter password: ")
    response = requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
    print(response.json())

def login_user():
    username = input("Enter username: ")
    password = input("Enter password: ")
    response = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
    if response.status_code == 200:
        user_id = response.json()['user_id']
        print("Login successful")
        return user_id
    else:
        print("Login failed")
        return None

def send_message(user_id):
    receiver_id = int(input("Enter receiver ID: "))
    message = input("Enter your message: ")
    response = requests.post(f"{BASE_URL}/send_message", json={"sender_id": user_id, "receiver_id": receiver_id, "message": message})
    print(response.json())

def get_messages(user_id):
    response = requests.get(f"{BASE_URL}/get_messages", params={"user_id": user_id})
    messages = response.json().get('messages', [])
    print("Messages:")
    for msg in messages:
        print(f"From {msg['sender_id']}: {msg['message']}")

if __name__ == "__main__":
    print("1. Register\n2. Login\n")
    choice = int(input("Enter choice: "))
    if choice == 1:
        register_user()
    elif choice == 2:
        user_id = login_user()
        if user_id:
            while True:
                print("\n1. Send Message\n2. Get Messages\n3. Exit")
                action = int(input("Enter action: "))
                if action == 1:
                    send_message(user_id)
                elif action == 2:
                    get_messages(user_id)
                elif action == 3:
                    break
