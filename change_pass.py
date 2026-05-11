from backend.db_manager import update_user_credentials

# EDIT THESE TWO LINES:
NEW_USER = input("Enter new username: ")
NEW_PASS = input("Enter new password: ")

if __name__ == "__main__":
    confirm = input(f"Change login to '{NEW_USER}'? (y/n): ")
    if confirm.lower() == 'y':
        update_user_credentials(NEW_USER, NEW_PASS)
    else:
        print("Cancelled.")