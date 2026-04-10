import pkgutil

import google.adk

print("Submodules in google.adk:")
for importer, modname, ispkg in pkgutil.iter_modules(google.adk.__path__):
    print(modname)
