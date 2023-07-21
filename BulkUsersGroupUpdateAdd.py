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
    members = [{"id": user_id, "operation": "add"} for user_id in user_ids.values()]
    payload = {"members": members}
    
    response = requests.patch(url, headers=headers, json=payload)
    if response.status_code == 200:
        successful_count = len(user_ids)
        print(f"Group {group_id} updated successfully with {successful_count} users.")
    else:
        failed_count = len(user_ids)
        print(f"Failed to update group {group_id}. Status code: {response.status_code}")
        print(f"{successful_count} users were successfully updated.")
        print(f"{failed_count} users failed to update.")

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
