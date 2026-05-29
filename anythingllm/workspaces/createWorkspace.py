from workspaces.modules import createWorkspace

workspace_name = input("Enter the name of the workspace: ")
details = createWorkspace(workspace_name)

if details:
    print(f"Workspace created successfully: {details}")
else:
    print("Failed to create workspace.")