import requests
import csv

def get_user_ids(access_token):
    base_url = "https://webexapis.com/v1"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    url = f"{base_url}/people"
    response = requests.get(url, headers=headers)
    response_json = response.json()
    if response.status_code == 200:
        user_ids = {user["emails"][0]: user["id"] for user in response_json["items"]}
        return user_ids
    else:
        print(f"Failed to retrieve user list. Status code: {response.status_code}")
        return None

def update_group_with_user_ids(access_token, group_id, user_ids):
    base_url = "https://webexapis.com/v1"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    url = f"{base_url}/groups/{group_id}"
    
    # Create the payload with the updated format
    members = [{"id": user_id, "operation": "delete"} for user_id in user_ids.values()]
    
    for count, user_id in enumerate(user_ids.values(), 1):
        response = requests.patch(url, headers=headers, json={"members": [{"id": user_id, "operation": "add"}]})
    if response.status_code == 200:
        print(f"{count}, user_id {user_id} - Successfully removed.")
    else:
        print(f"{count}, user_id {user_id} - Failed to remove. Status code: {response.status_code}")

    successful_count = sum(1 for _ in user_ids)
    failed_count = len(user_ids) - successful_count

    print(f"\nGroup {group_id} update summary:")
    print(f"Successfully removed {successful_count} users.")
    print(f"Failed to remove {failed_count} users.")


def main():
    access_token = input("Enter Access Token: ")
    group_id = input("Enter Group ID: ")
    csv_file = input("Enter the CSV file name with user emails: ")

    # Read user emails from the CSV file
    user_emails = []
    with open(csv_file, "r") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            user_emails.append(row[0])

    # Get user IDs
    user_ids = get_user_ids(access_token)
    if user_ids is None:
        return

    # Filter out user IDs for users in the CSV file
    filtered_user_ids = {email: user_ids[email] for email in user_emails if email in user_ids}

    # Update the group with the user IDs
    update_group_with_user_ids(access_token, group_id, filtered_user_ids)

if __name__ == "__main__":
    main()
