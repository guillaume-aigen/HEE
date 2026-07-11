import os
import glob
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

# ==========================================
# CONFIGURATION
# ==========================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGE1_OUTPUT = os.path.join(PROJECT_ROOT, "STAGE 1", "output")
STAGE2_BASE = os.path.dirname(os.path.abspath(__file__))
STAGE2_OUTPUT = os.path.join(STAGE2_BASE, "output")

# We use a larger max chunk size because Qwen 32B has a large context window
MAX_CHUNK_SIZE = 12000   
CHUNK_OVERLAP = 1000 

def process_all_markdowns():
    if not os.path.exists(STAGE2_OUTPUT):
        os.makedirs(STAGE2_OUTPUT)

    search_pattern = os.path.join(STAGE1_OUTPUT, "**", "*.md")
    md_files = glob.glob(search_pattern, recursive=True)

    print(f"Found {len(md_files)} Markdown files to slice.")

    # 1. Define the Markdown Header Splitter
    # This ensures logic isn't split across major section boundaries
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

    # 2. Define the fallback Character Splitter
    # If a single chapter is absurdly long (over 12k chars), this will split it safely
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=MAX_CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    for md_path in md_files:
        book_folder_name = os.path.basename(os.path.dirname(md_path))
        print(f"\n--- Slicing: {book_folder_name} ---")

        book_chunk_dir = os.path.join(STAGE2_OUTPUT, book_folder_name, "chunks")
        if not os.path.exists(book_chunk_dir):
            os.makedirs(book_chunk_dir)

        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Step A: Split by Markdown Headers
        md_splits = markdown_splitter.split_text(content)
        
        # Step B: Ensure no split is too large for the context window
        final_chunks = char_splitter.split_documents(md_splits)
        
        total_chunks = len(final_chunks)
        print(f"   [+] Generated {total_chunks} semantic logic-bites.")

        # Save Chunks
        for i, chunk in enumerate(final_chunks):
            chunk_num = i + 1
            chunk_filename = f"chunk_{chunk_num:03d}.md"
            output_path = os.path.join(book_chunk_dir, chunk_filename)
            
            # Reconstruct context from the metadata dictionary
            context_str = " > ".join([f"{k}: {v}" for k, v in chunk.metadata.items()])
            
            header = f"--- HEE CHUNK {chunk_num}/{total_chunks} | BOOK: {book_folder_name} ---\n"
            header += f"--- CONTEXT: {context_str} ---\n\n"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(header + chunk.page_content)

    print("\n\nSTAGE 2 COMPLETE: All books are now logic-bites ready for Stage 3.")

if __name__ == "__main__":
    process_all_markdowns()
