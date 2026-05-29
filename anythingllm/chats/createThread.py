from chats.modules import createThreads

workspace_slug = input("Enter workspace slug: ")
thread_name = input("Enter thread name: ")
thread_details = createThreads(workspace_slug, thread_name)

if thread_details:
    print(f"Thread created successfully: {thread_details}")
else:
    print("Failed to create thread.")