# app.py
import streamlit as st
import requests
import json
import pandas as pd

# ========================= CONFIG =========================
API_URL = "http://localhost:8000"
TIMEOUT = 600

st.set_page_config(page_title="Banking Data Architecture AI", layout="wide", initial_sidebar_state="expanded")
st.title("Banking Data Architecture AI Orchestrator")
st.markdown("**Agent 1** → Hierarchical Domain Categorization  |  **Agent 2** → ER Diagram per Owner")

# ========================= SIDEBAR =========================
st.sidebar.header("Backend Status")
try:
    health = requests.get(f"{API_URL}/", timeout=10)
    st.sidebar.success("API Running ✅")
except:
    st.sidebar.error("API Offline — Run `uvicorn main:app --reload`")

if "agent1_result" not in st.session_state:
    st.session_state.agent1_result = None

tab1, tab2 = st.tabs(["Agent 1: Hierarchical Categorization", "Agent 2: ER Modeler"])

# ========================= AGENT 1 =========================
with tab1:
    st.header("Agent 1: Map Elements → Domains & Subdomains (Hierarchical)")

    col1, col2 = st.columns(2)
    with col1:
        file1 = st.file_uploader("Reference Domains (File1.csv)", type="csv")
    with col2:
        file2 = st.file_uploader("Banking Elements (File2.csv)", type="csv")

    if st.button("Run Agent 1 – Generate Hierarchy", type="primary", use_container_width=True):
        if not file1 or not file2:
            st.error("Please upload both files.")
        else:
            files = {"file1": ("File1.csv", file1.getvalue(), "text/csv"),
                     "file2": ("File2.csv", file2.getvalue(), "text/csv")}
            with st.spinner("Gemini 2.5 Flash is building hierarchical structure..."):
                try:
                    resp = requests.post(f"{API_URL}/agent1/categorize", files=files, timeout=TIMEOUT)
                    resp.raise_for_status()
                    data = resp.json()
                    if "json_data" in data:
                        st.session_state.agent1_result = data
                        domains = data["json_data"]["banking_elements_categorization"]["service_domains"]
                        total_elements = sum(len(el["elements"]) for d in domains for sd in d["subdomains"] for el in sd["elements"])
                        st.success(f"Hierarchical mapping complete! {len(domains)} domains • {total_elements} elements")
                        st.balloons()
                    else:
                        st.error("Invalid response")
                        st.json(data)
                except Exception as e:
                    st.error(f"Error: {e}")

    # ========================= DISPLAY HIERARCHY =========================
    if st.session_state.agent1_result:
        result = st.session_state.agent1_result
        categorization = result["json_data"]["banking_elements_categorization"]
        domains = categorization["service_domains"]

        st.divider()
        st.subheader("Hierarchical Banking Elements Catalog")

        # Global search
        search_term = st.text_input("Search across all elements, descriptions, domains...", "")

        total_elements = 0
        for domain in domains:
            domain_elements = sum(len(sd["elements"]) for sd in domain["subdomains"])
            total_elements += domain_elements

            # Filter domain if search term
            domain_elements_list = []
            for sd in domain["subdomains"]:
                filtered_elements = sd["elements"]
                if search_term:
                    filtered_elements = [
                        el for el in sd["elements"]
                        if search_term.lower() in el["name"].lower() or
                           search_term.lower() in el["description"].lower()
                    ]
                domain_elements_list.extend(filtered_elements)

            if search_term and not domain_elements_list:
                continue

            with st.expander(f"**{domain['domain_name']}** — {domain['data_owner']} ({domain_elements} elements)", expanded=True):
                st.caption(domain["definition"])

                for sd in domain["subdomains"]:
                    elements = sd["elements"]
                    if search_term:
                        elements = [
                            el for el in elements
                            if search_term.lower() in el["name"].lower() or
                               search_term.lower() in el["description"].lower()
                        ]
                    if not elements:
                        continue

                    with st.container():
                        st.write(f"**{sd['subdomain_name']}** ({len(elements)} elements)")
                        cols = st.columns(3)
                        for idx, el in enumerate(elements):
                            with cols[idx % 3]:
                                with st.container(border=True):
                                    st.write(f"**{el['name']}**")
                                    st.caption(el['description'][:300] + ("..." if len(el['description']) > 300 else ""))

        # Export
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(
                "Download Full Hierarchical JSON",
                data=json.dumps(result["json_data"], indent=2, ensure_ascii=False),
                file_name="banking_elements_hierarchical.json",
                mime="application/json"
            )
        with col_d2:
            # Flatten for CSV export
            flat_rows = []
            for domain in domains:
                for sd in domain["subdomains"]:
                    for el in sd["elements"]:
                        flat_rows.append({
                            "Domain": domain["domain_name"],
                            "Owner": domain["data_owner"],
                            "Subdomain": sd["subdomain_name"],
                            "Element": el["name"],
                            "Description": el["description"]
                        })
            df_flat = pd.DataFrame(flat_rows)
            st.download_button(
                "Download as CSV (Flat)",
                data=df_flat.to_csv(index=False),
                file_name="banking_elements_flat.csv",
                mime="text/csv"
            )

        with st.expander("View Raw Markdown Summary"):
            st.markdown(result.get("markdown_content", ""))

# ========================= AGENT 2 =========================
with tab2:
    st.header("Agent 2: Generate Mermaid ER Diagram per Owner")
    if not st.session_state.agent1_result:
        st.info("Run Agent 1 first.")
    else:
        domains = st.session_state.agent1_result["json_data"]["banking_elements_categorization"]["service_domains"]
        owners = sorted({d["data_owner"] for d in domains})
        selected_owner = st.selectbox("Select Data Owner", owners)

        if st.button("Generate ER Diagram", type="primary"):
            payload = {
                "categorized_data": st.session_state.agent1_result["json_data"],
                "owner_name": selected_owner
            }
            with st.spinner(f"Generating ER diagram for {selected_owner}..."):
                try:
                    resp = requests.post(f"{API_URL}/agent2/generate-er", json=payload, timeout=180)
                    resp.raise_for_status()
                    output = resp.json()
                    if "mermaid_code" in output:
                        st.success("ER Diagram Ready!")
                        st.code(output["mermaid_code"], language="mermaid")
                        st.mermaid(output["mermaid_code"], height=800)
                    else:
                        st.error("Failed")
                        st.json(output)
                except Exception as e:
                    st.error(f"Error: {e}")