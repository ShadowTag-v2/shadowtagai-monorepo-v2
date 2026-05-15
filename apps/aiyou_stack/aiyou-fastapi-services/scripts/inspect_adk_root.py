import pkgutil

import google.adk

print("Submodules in google.adk:")
for _importer, modname, _ispkg in pkgutil.iter_modules(google.adk.__path__):
    print(modname)
