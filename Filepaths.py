import platform

# Get the current platform
current_platform = platform.system()

# Define the file paths based on the platform
if current_platform == "Darwin":  # macOS
    events_file = "events.json"
    events_backup_file = "events_backup.json"
    users_file = "users.json"
    tags_file = "tags.json"
    feedback_file = "feedback.txt"
    likes_file = "likes.json"


elif current_platform == "Linux":  # Linux server
    events_file = "/database/events.json"
    events_backup_file = "/database/events_backup.json"
    users_file = "/database/users.json"
    tags_file = "/database/tags.json"
    feedback_file = "/database/feedback.txt"
    likes_file = "/database/likes.json"


else:
    raise Exception("Unsupported platform")