import os
import glob
import json

# ==========================================
# CONFIGURATION
# ==========================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGE3_OUTPUT = os.path.join(PROJECT_ROOT, "STAGE 3", "output")
STAGE4_BASE = os.path.dirname(os.path.abspath(__file__))
STAGE4_OUTPUT = os.path.join(STAGE4_BASE, "output")

def aggregate_logic():
    if not os.path.exists(STAGE4_OUTPUT):
        os.makedirs(STAGE4_OUTPUT)

    # Find all book folders in Stage 3
    book_folders = [f.path for f in os.scandir(STAGE3_OUTPUT) if f.is_dir()]
    
    if not book_folders:
        print("No processed books found in STAGE 3.")
        return

    print(f"Found {len(book_folders)} knowledge domains to aggregate.")

    for book_folder in book_folders:
        book_name = os.path.basename(book_folder)
        domain_name = book_name.replace("_", " ")
        fragment_dir = os.path.join(book_folder, "fragments")
        
        if not os.path.exists(fragment_dir):
            continue

        print(f"\n--- Aggregating Module: {domain_name} ---")
        
        # Initialize the Multi-Source Master Schema
        master_logic = {
            "source_domain": domain_name,
            "operating_instructions": f"This module contains specialized heuristics for the domain of '{domain_name}'. When reasoning on this topic, cross-reference these 'heuristics' and 'classifications' with your other available modules. Prioritize the 'triggers' and 'actions' defined here for precision. If this module conflicts with another, seek the most contextually relevant 'nuance_adjustment' from the contextual_anchors. Base your logic on these extracted rules.",
            "total_fragments_processed": 0,
            "heuristics": [],
            "classifications": [],
            "contextual_anchors": []
        }

        # Find all JSON fragments for this book
        fragment_files = glob.glob(os.path.join(fragment_dir, "*.json"))
        
        for file_path in fragment_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Append data if it exists and isn't empty
                if data.get("heuristics"):
                    master_logic["heuristics"].extend(data["heuristics"])
                
                if data.get("classifications"):
                    master_logic["classifications"].extend(data["classifications"])
                    
                if data.get("contextual_anchors"):
                    master_logic["contextual_anchors"].extend(data["contextual_anchors"])
                    
                master_logic["total_fragments_processed"] += 1
                
            except json.JSONDecodeError:
                print(f"   [!] Skipping corrupted JSON: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"   [!] Error reading {os.path.basename(file_path)}: {e}")

        # Deduplicate exact matches safely using JSON string sorting
        master_logic["heuristics"] = [json.loads(s) for s in {json.dumps(d, sort_keys=True) for d in master_logic["heuristics"]}]
        master_logic["classifications"] = [json.loads(s) for s in {json.dumps(d, sort_keys=True) for d in master_logic["classifications"]}]
        master_logic["contextual_anchors"] = [json.loads(s) for s in {json.dumps(d, sort_keys=True) for d in master_logic["contextual_anchors"]}]

        # Save the Master File
        output_file = os.path.join(STAGE4_OUTPUT, f"{book_name}_Master_Logic.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(master_logic, f, indent=2)
            
        print(f"   [SUCCESS] Compiled Master Knowledge Module: {os.path.basename(output_file)}")
        print(f"   - Heuristics: {len(master_logic['heuristics'])}")
        print(f"   - Classifications: {len(master_logic['classifications'])}")
        print(f"   - Contextual Anchors: {len(master_logic['contextual_anchors'])}")

    print("\nSTAGE 4 COMPLETE: All multi-source knowledge modules generated.")

if __name__ == "__main__":
    aggregate_logic()
