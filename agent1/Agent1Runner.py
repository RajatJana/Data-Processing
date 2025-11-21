# agent1/Agent1Runner.py
import csv
import io
import json
from typing import Dict, Any, List
from collections import defaultdict
from .Agent1 import Agent1

class Agent1Runner:
    def __init__(self):
        self.agent = Agent1()
        self.chunk_size = 160  # Safe for gemini-2.5-flash

    def _parse_csv(self, content: bytes) -> List[Dict[str, str]]:
        text = content.decode("utf-8", errors="ignore")
        return list(csv.DictReader(io.StringIO(text)))

    def _build_domain_lookup(self, domains: List[dict]) -> Dict[str, dict]:
        lookup = {}
        for d in domains:
            name = d['Service Domain'].strip()
            lookup[name] = {
                "domain_name": name,
                "data_owner": d['Data Owner name'].strip(),
                "definition": d['Service Domain Defination'].strip(),
                "subdomains_raw": [s.strip() for s in d['Subdomain'].strip().split(",") if s.strip()]
            }
        return lookup

    def _categorize_chunk(self, domain_lookup: dict, elements_chunk: List[dict]) -> List[dict]:
        domain_list = "\n".join([
            f"- {name} (Owner: {info['data_owner']})"
            for name, info in domain_lookup.items()
        ])

        elements_text = "\n".join([
            f"{i+1}. \"{e['Name'].strip()}\" → {e['Comment'].strip()}"
            for i, e in enumerate(elements_chunk)
        ])

        prompt = f"""You are a Senior Banking Data Architect.

AVAILABLE DOMAINS (use EXACT names):
{domain_list}

ELEMENTS TO CATEGORIZE:
{elements_text}

For each element, return ONLY this JSON structure (one object per element):
{{
  "element_name": "Exact Name",
  "element_definition": "Full Comment",
  "mapped_domain": "Exact Domain Name from list above",
  "suggested_subdomain": "Best matching subdomain or empty string"
}}

Return a valid JSON array ONLY. No explanations.
"""

        response = self.agent.model.generate_content(prompt)
        raw = response.text.strip()
        if raw.startswith("```json"): raw = raw[7:]
        if raw.endswith("```"): raw = raw[:-3:]
        raw = raw.strip()

        try:
            return json.loads(raw)
        except:
            # Fallback repair
            if raw.count('{') > raw.count('}'):
                raw += ']}'
            return json.loads(raw)

    def run(self, file1_bytes: bytes, file2_bytes: bytes) -> Dict[str, Any]:
        domains = self._parse_csv(file1_bytes)
        elements = self._parse_csv(file2_bytes)

        domain_lookup = self._build_domain_lookup(domains)

        flat_mappings = []
        for i in range(0, len(elements), self.chunk_size):
            chunk = elements[i:i + self.chunk_size]
            chunk_results = self._categorize_chunk(domain_lookup, chunk)
            flat_mappings.extend(chunk_results)

        # === BUILD HIERARCHICAL STRUCTURE ===
        hierarchy = defaultdict(lambda: defaultdict(list))

        for item in flat_mappings:
            domain = item["mapped_domain"]
            subdomain = item["suggested_subdomain"] or "General"
            hierarchy[domain][subdomain].append({
                "name": item["element_name"],
                "description": item["element_definition"]
            })

        # Convert to final format
        service_domains = []
        for domain_name, subdomains_dict in hierarchy.items():
            domain_info = domain_lookup.get(domain_name, {
                "data_owner": "Unknown",
                "definition": "Definition not found"
            })

            subdomains_list = []
            raw_subdomains = domain_info["subdomains_raw"]

            # Match suggested subdomains to official ones, fallback to "General"
            used_subdomains = set()
            for suggested, elements_list in subdomains_dict.items():
                matched = False
                for official in raw_subdomains:
                    if suggested.lower() in official.lower() or official.lower() in suggested.lower():
                        subdomains_list.append({
                            "subdomain_name": official,
                            "elements": elements_list
                        })
                        used_subdomains.add(official)
                        matched = True
                        break
                if not matched:
                    subdomains_list.append({
                        "subdomain_name": suggested,
                        "elements": elements_list
                    })

            # Add any missing official subdomains
            for official in raw_subdomains:
                if official not in used_subdomains:
                    subdomains_list.append({
                        "subdomain_name": official,
                        "elements": []
                    })

            service_domains.append({
                "domain_name": domain_name,
                "data_owner": domain_info["data_owner"],
                "definition": domain_info["definition"],
                "subdomains": subdomains_list
            })

        final_output = {
            "banking_elements_categorization": {
                "service_domains": service_domains
            }
        }

        # Markdown summary
        markdown = "# Banking Elements Categorization (Hierarchical)\n\n"
        for domain in service_domains:
            markdown += f"## {domain['domain_name']} ({domain['data_owner']})\n"
            markdown += f"*{domain['definition']}*\n\n"
            for sd in domain["subdomains"]:
                count = len(sd["elements"])
                markdown += f"### {sd['subdomain_name']} ({count} elements)\n"
                for el in sd["elements"][:10]:  # Limit preview
                    markdown += f"- **{el['name']}**: {el['description'][:100]}...\n"
                if count > 10:
                    markdown += f"... and {count-10} more\n"
                markdown += "\n"
        
        markdown += f"\n**Total Domains:** {len(service_domains)} | **Total Elements Mapped:** {len(flat_mappings)}"

        return {
            "json_data": final_output,
            "markdown_content": markdown,
            "total_elements": len(elements),
            "mapped_count": len(flat_mappings),
            "status": "success",
            "format": "hierarchical_v2"
        }