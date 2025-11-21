import json

class Agent2Tool:
    @staticmethod
    def filter_by_owner(full_json_data: dict, owner_name: str) -> str:
        """
        Filters the JSON output from Agent 1 to only include items 
        owned by the specified user.
        """
        mappings = full_json_data.get("mappings", [])
        
        # Case insensitive filtering
        filtered = [
            m for m in mappings 
            if m.get("data_owner", "").strip().lower() == owner_name.strip().lower()
        ]
        
        if not filtered:
            return "No data found for this owner."

        return json.dumps(filtered, indent=2)

    @staticmethod
    def format_er_prompt(filtered_data_str: str, owner_name: str) -> str:
        return f"""
        You are a Data Modeler specializing in Entity Relationship Diagrams (ERD).

        Context:
        We have a list of Banking Elements that have been categorized under Domains.
        The Data Owner is: {owner_name}.

        Data:
        {filtered_data_str}

        Task:
        Create an Entity Relationship model for this data.
        Treat 'mapped_domain' as a Parent Entity and 'element_name' as a Child Attribute or Entity belonging to that Domain.

        Output Requirements:
        Return a JSON object with exactly two keys:
        1. "mermaid_code": Valid Mermaid.js syntax for an ER Diagram. Use `erDiagram`.
           - Example: Domain ||--o{{ Element : contains
        2. "system_json": A simplified JSON structure for external systems listing Domains and their contained Elements.
        """