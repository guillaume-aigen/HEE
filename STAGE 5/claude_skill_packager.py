import os
import shutil
import json

# ==========================================
# CONFIGURATION
# ==========================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGE4_OUTPUT = os.path.join(PROJECT_ROOT, "STAGE 4", "output")
STAGE5_BASE = os.path.dirname(os.path.abspath(__file__))

def build_claude_skill():
    print("==========================================")
    print(" STAGE 5: CLAUDE UNIFIED SKILL PACKAGER")
    print("==========================================\n")

    # 1. Verify Stage 4 data exists
    if not os.path.exists(STAGE4_OUTPUT):
        print("[!] Error: Stage 4 output folder not found.")
        return

    json_files = [f for f in os.listdir(STAGE4_OUTPUT) if f.endswith('.json')]
    
    if not json_files:
        print("[!] No Master Logic JSON files found in Stage 4. Run Stage 4 first.")
        return

    print(f"[*] Found {len(json_files)} Knowledge Modules to package.")

    # 2. Get Agent Details from User
    agent_name = input("\nEnter the name of your Agent (e.g., Retail_Strategist): ").strip().replace(" ", "_")
    if not agent_name:
        agent_name = "Custom_Agent"

    skill_dir_name = f"{agent_name}_Heuristics_Skill"
    skill_path = os.path.join(STAGE5_BASE, skill_dir_name)
    references_path = os.path.join(skill_path, "references")

    # 3. Build Directory Structure
    if os.path.exists(skill_path):
        print(f"\n[!] Overwriting existing skill directory: {skill_dir_name}")
        shutil.rmtree(skill_path)
    
    os.makedirs(references_path)

    # 4. Process Modules and Extract Domains for the Trigger Description
    domains = []
    file_list_md = ""

    for file in json_files:
        source_path = os.path.join(STAGE4_OUTPUT, file)
        
        # Read the domain to build a highly accurate Claude Trigger
        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                domain = data.get("source_domain", file.replace('.json', ''))
                domains.append(domain)
        except Exception:
            domains.append(file)

        # Copy file to references folder
        shutil.copy(source_path, references_path)
        file_list_md += f"- `references/{file}`\n"
        print(f"   [+] Bundled: {file}")

    # 5. Build the SKILL.md Frontmatter and Progressive Disclosure Instructions
    domain_string = ", ".join(domains)
    
    skill_md_content = f"""---
name: {agent_name.lower()}-knowledge-base
description: Trigger this skill whenever you need to reason about, answer questions on, or analyze topics related to: {domain_string}. This skill provides the core algorithmic heuristics and operational rules for these subjects.
---

# {agent_name.replace('_', ' ')} Knowledge Base

You are equipped with specialized, multi-source heuristics. To answer the user's query accurately, you must utilize the Progressive Disclosure method.

## Execution Protocol:

1. **READ:** Immediately read the contents of the following files located in your `references/` directory:
{file_list_md}
2. **PARSE:** Each file contains `heuristics`, `classifications`, and `contextual_anchors`. Treat these arrays as your absolute source of truth.
3. **CROSS-REFERENCE:** Because you have multiple modules loaded, evaluate the user's prompt against the 'triggers' across ALL loaded JSON files. 
4. **SYNTHESIZE:** If heuristics from different modules apply to the same situation, synthesize an answer that respects the 'actions' of both, using the 'contextual_anchors' to resolve any nuances.
5. **RESTRICTION:** Base your reasoning STRICTLY on these extracted rules. Do not hallucinate data outside of this database.
"""

    # 6. Save SKILL.md
    skill_md_path = os.path.join(skill_path, "SKILL.md")
    with open(skill_md_path, 'w', encoding='utf-8') as f:
        f.write(skill_md_content)

    print(f"\n[SUCCESS] Unified Claude Skill successfully compiled!")
    print(f"Location: {skill_path}")
    print("\nNext Steps:")
    print("1. Upload the entire folder to Claude.")
    print("2. When chatting with Claude, it will automatically read the SKILL.md trigger and cross-reference your JSON files.")

if __name__ == "__main__":
    build_claude_skill()
