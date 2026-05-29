from workspaces.modules import deleteWorkspace

workspace_name = input("Enter the slug of the workspace: ")
status = deleteWorkspace(workspace_name)

if status:
    print("Workspace deleted successfully:")
else:    
    print("Failed to delete workspace.")
