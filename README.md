# BulkUserGroupUpdates
Python script to add or remove users to Webex Groups in bulk. 
  1. This script is designed to add or remove users to a Webex group with CSV file with user emails as input.
  2. An auth token containing the identity:groups_rw is required. Searching and viewing members of a group requires an auth token with a scope of identity:groups_read
  3. Please find the https://developer.webex.com/docs/api/getting-started to generate an access token. 
  4. Tested with Python version 3.11.4. Please refer to requirements.txt for the modules.
  
# Usage
  1. Install python 3.11.4
  2. The script leverage requests and csv modules.
  3. The scripts requires three inputs. Access token, Group ID and name of the CSV file.

# Add Users to Group
python3 BulkUsersGroupUpdateAdd.py

# Remove Users from Group
python3 BulkUsersGroupUpdateRemove.py
