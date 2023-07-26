import requests
import csv
import chardet
import time

def get_user_ids(access_token, email_list):
    base_url = "https://webexapis.com/v1"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    matched_user_ids = {}
    unmatched_emails = []  # Create a list to store unmatched email addresses

    print("\n######## Begin User ID Retrieval ########\n")
    processed_count = 0
    total_emails = len(email_list)
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
        elif response.status_code == 429:
            wait_time = int(response.headers.get("Retry-After", "10"))  # Default to 10 seconds if Retry-After header is not present
            print(f"Rate limit exceeded. Waiting for {wait_time} seconds...")
            start_time = time.time()
            time.sleep(wait_time)
            end_time = time.time()
            print(f"Waited for {end_time - start_time} seconds before retrying.")
            # Retry the request after waiting for the specified seconds
            response = requests.get(url, headers=headers)
            response_json = response.json()
            if response.status_code == 200 and response_json.get("items"):
                matched_user_ids[email] = response_json["items"][0]["id"]
            else:
                print(f"Failed to retrieve user id with email '{email}' even after retry. Status code: {response.status_code}\n")
                unmatched_emails.append(email)
        else:
            print(f"Failed to retrieve user id with email '{email}'. Status code: {response.status_code}\n")
            unmatched_emails.append(email)

        processed_count += 1
        if processed_count % 10 == 0:  # Print an update after every 10 emails processed
            print(f"Processed {processed_count}/{total_emails} users")

        # Add a delay of 0.2 seconds between requests to avoid reaching rate limits too quickly
        time.sleep(0.2)

    if matched_user_ids:
        matched_emails_count = len(matched_user_ids)
        print(f"\nTotal matched email addresses: {matched_emails_count}")

    if unmatched_emails:
        unmatched_emails_count = len(unmatched_emails)
        print(f"\nTotal unmatched email addresses: {unmatched_emails_count}")

    print("######## End User ID Retrieval ########\n")
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
        response = requests.patch(url, headers=headers, json={"members": [{"id": user_id, "operation": "delete"}]})
        items = response.json().get("members")
        if response.status_code in (200, 201, 204):
            if response.status_code == 200:
                print(f"{count}, user_id: {user_id}, email: {email} - Successfully removed.")
                successful_emails.append(email)
            elif response.status_code == 201:
                print(f"{count}, user_id: {user_id}, email: {email} - User has been removed.")
                successful_emails.append(email)
            elif response.status_code == 202:
                print(f"{count}, user_id: {user_id}, email: {email} - Remove Request has been accepted for processing.")
                successful_emails.append(email)
            elif response.status_code == 204:
                print(f"{count}, user_id: {user_id}, email: {email} - Successful remove request without body content.")
                successful_emails.append(email)
            else:
                print(f"{count}, user_id: {user_id}, email: {email} - Failed to remove. Empty response.\n")
                failed_emails.append(email)
        elif response.status_code == 429:
            wait_time = int(response.headers["Retry-After"])
            print(f"Rate limit exceeded. Waiting for {wait_time} seconds...")
            start_time = time.time()
            time.sleep(wait_time)
            end_time = time.time()
            print(f"Waited for {end_time - start_time} seconds before retrying.")
            # Retry the request after waiting for the specified seconds
            response = requests.patch(url, headers=headers, json={"members": [{"id": user_id, "operation": "add"}]})
            items = response.json().get("items")
            if response.status_code in (200, 201, 204) and items:
                print(f"{count}, user_id: {user_id}, email: {email} - Successfully removed.")
                successful_emails.append(email)
            else:
                print(f"{count}, user_id: {user_id}, email: {email} - Failed to remove even after retry. Status code: {response.status_code}\n")
                failed_emails.append(email)
        else:
            print(f"{count}, user_id: {user_id}, email: {email} - Failed to remove. Status code: {response.status_code}\n")
            failed_emails.append(email)

        # Add a delay of 0.2 seconds between requests to avoid reaching rate limits too quickly
        time.sleep(0.2)

    successful_count = len(successful_emails)
    failed_count = len(failed_emails)

    print(f"\nTotal number of users successfully removed from {group_id}: {successful_count}\n")
    print(f"Total number of users failed to be removed from {group_id}: {failed_count}\n")

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
            print("Read email:", row["users"])  # Print the email being read from CSV

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
