class ToolSearchTool:
    def __init__(self, full_registry):
        self.registry = full_registry # Dict of name -> schema

    def get_deferred_manifest(self):
        return {"deferred_tools_available": list(self.registry.keys())}

    def search(self, query: str):
        return {name: schema for name, schema in self.registry.items() 
                if query.lower() in name.lower() or query.lower() in schema.get('description', '').lower()}
