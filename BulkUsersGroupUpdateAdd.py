import requests
import csv
import chardet

def get_user_ids(access_token, email_list):
    base_url = "https://webexapis.com/v1"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    matched_user_ids = {}
    unmatched_emails = []  # Create a list to store unmatched email addresses
    
    print("\n######## Begin User ID Retrieval ########\n")
    for email in email_list:
        url = f"{base_url}/people?email={email}"
        response = requests.get(url, headers=headers)
        response_json = response.json()

        if response.status_code == 200 and response_json.get("items"):
            # If there are items in the response, it means the email was matched
            matched_user_ids[email] = response_json["items"][0]["id"]
        elif response.status_code == 204:
            print(f"User with email '{email}' not found.")
            unmatched_emails.append(email)
        elif response.status_code == 201:
            print(f"User with email '{email}' has been created.")
            matched_user_ids[email] = response_json["id"]
        elif response.status_code == 202:
            print(f"User with email '{email}' update has been accepted for processing.")
            matched_user_ids[email] = response_json["id"]
        else:
            print(f"Failed to retrieve user id with email '{email}'. Status code: {response.status_code}\n")
            unmatched_emails.append(email)

    if unmatched_emails:
        unmatched_emails_count = len(unmatched_emails)
        print(f"Total unmatched email addresses: {unmatched_emails_count}")

    print("######## End User ID Retrieval ########")
    return matched_user_ids

def update_group_with_user_ids(access_token, group_id, user_ids):
    base_url = "https://webexapis.com/v1"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    url = f"{base_url}/groups/{group_id}"
    
    # Create the payload with the updated format
    members = [{"id": user_id, "operation": "add"} for user_id in user_ids.values()]

    successful_emails = []
    failed_emails = []
    
    print("######## Begin Group Membership Update ########\n")
    print(f"Group ID: {group_id}")
    for count, (email, user_id) in enumerate(user_ids.items(), 1):
        response = requests.patch(url, headers=headers, json={"members": [{"id": user_id, "operation": "add"}]})
        items = response.json().get("items")
        if response.status_code in (200, 201, 204):
            print(f"{count}, user_id: {user_id}, email: {email} - Successfully updated.")
            successful_emails.append(email)
        else:
            print(f"{count}, user_id: {user_id}, email: {email} - Failed to update. Status code: {response.status_code}")
            failed_emails.append(email)
    
    successful_count = len(successful_emails)
    failed_count = len(failed_emails)

    print(f"Total number of users successfully added to {group_id}: {successful_count}\n")
    print(f"Total number of users failed to be added to {group_id}: {failed_count}\n")

    for email in failed_emails:
        print(email)
    print("######## End Group Membership Update ########\n")

def main():
    access_token = input("Enter Access Token: ")
    group_id = input("Enter Group ID: ")
    csv_file = input("Enter the CSV file name with user emails: ")

    # Read user emails from the CSV file
    user_emails = []
    with open(csv_file, "r", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        print("CSV Headers:", reader.fieldnames)  # Print the header names to verify
        for row in reader:
            user_emails.append(row["users"])  # Access email addresses using the header "users"
            #print("Read email:", row["users"])  # Print the email being read from CSV

    # Get user IDs
    user_ids = get_user_ids(access_token, user_emails)
    if user_ids is None:
        return

    # Filter out user IDs for users in the CSV file
    filtered_user_ids = {email: user_ids[email] for email in user_emails if email in user_ids}

    # Update the group with the user IDs
    update_group_with_user_ids(access_token, group_id, filtered_user_ids)

if __name__ == "__main__":
    main()
