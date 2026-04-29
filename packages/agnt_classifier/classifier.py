"""
XML Classifier Side-Query
Porting Anthropic's XML classification logic to AGNT QueryEngine.
"""
import re
from typing import Dict, Optional

class XMLClassifier:
    """
    Side-query router that uses XML tag semantics to classify user intent 
    and route to specialized sub-agents.
    """
    def __init__(self):
        self.routing_table = {
            "search": "osint_agent",
            "refactor": "coder_agent",
            "test": "qa_agent",
            "sql": "db_architect"
        }

    def extract_xml_tags(self, query: str) -> list:
        # Anthropic standard: <query_type>search</query_type>
        pattern = r"<([a-z_]+)>(.*?)</\1>"
        return re.findall(pattern, query)

    def classify(self, query: str) -> str:
        """
        Extracts XML tags and returns the recommended sub-agent route.
        Defaults to 'general_agent' if no specialized routing is found.
        """
        tags = self.extract_xml_tags(query)
        for tag_name, tag_value in tags:
            if tag_name == "intent" and tag_value in self.routing_table:
                return self.routing_table[tag_value]
            elif tag_name in self.routing_table:
                return self.routing_table[tag_name]
                
        return "general_agent"

    def strip_xml(self, query: str) -> str:
        """
        Removes the classification XML before passing to the execution agent.
        """
        return re.sub(r"<[a-z_]+>.*?</[a-z_]+>", "", query).strip()
