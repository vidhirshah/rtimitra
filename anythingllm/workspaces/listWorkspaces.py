from workspaces.modules import listWorkspaces

workspaces = listWorkspaces()
if workspaces is not None:
    print("Workspaces:")
    for workspace in workspaces:
        print(f"ID: {workspace['id']}, Name: {workspace['name']}, Slug: {workspace['slug']}")
else:
    print("Failed to retrieve workspaces.")