from chats.modules import queryThreads

workspace_slug = input("Enter workspace slug: ")
thread_name = input("Enter thread name: ")
answer = queryThreads(workspace_slug, thread_name, "What is AnythingLLM?")

if answer:
    print(answer)
else:
    print("Failed to answer the question.")