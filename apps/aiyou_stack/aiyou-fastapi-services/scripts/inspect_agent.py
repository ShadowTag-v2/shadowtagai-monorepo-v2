import inspect

from google.adk.agents import LlmAgent

print("Methods in LlmAgent:")
for name, obj in inspect.getmembers(LlmAgent):
    if inspect.isfunction(obj) or inspect.ismethod(obj):
        print(name)
