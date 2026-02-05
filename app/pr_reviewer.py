# Updated code for app/pr_reviewer.py

# Your existing imports...

# Existing code...

# Here's a hypothetical section where we make changes to handle file_commentable
if isinstance(file_commentable, dict):
    file_commentable = list(file_commentable.keys())

# Ensure min/max logic
if file_commentable:
    line_range = (min(file_commentable), max(file_commentable))
else:
    line_range = (0, 0)  # or another appropriate default

# Rest of your existing code...
