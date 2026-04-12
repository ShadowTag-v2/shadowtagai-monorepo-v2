import inspect

import google.adk.runners

print("Members of google.adk.runners:")
for name, obj in inspect.getmembers(google.adk.runners):
    if inspect.isclass(obj):
        print(f"Class: {name}")
