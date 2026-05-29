from chats.modules import deleteThread

workspace_slug = input("Enter workspace slug: ")
thread_name = input("Enter thread name to be deleted: ")
thread_details = deleteThread(workspace_slug, thread_name)

if thread_details:
    print(f"Thread deleted successfully.")
else:
    print("Failed to delete thread.")