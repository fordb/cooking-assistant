#!/usr/bin/env python3
"""
API Documentation Generator for Cooking Assistant

Generates HTML API documentation from docstrings using pdoc3.
Run this script to build fresh API documentation in the docs/api/ directory.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    """Generate API documentation using pdoc3."""
    
    # Check if pdoc3 is installed
    try:
        import pdoc
    except ImportError:
        print("ERROR: pdoc3 is not installed. Run: pip install pdoc3")
        sys.exit(1)
    
    # Project root directory
    project_root = Path(__file__).parent
    
    # Documentation output directory
    docs_dir = project_root / "docs" / "api"
    
    # Create docs directory if it doesn't exist
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Clean existing documentation
    if docs_dir.exists():
        shutil.rmtree(docs_dir)
        docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Source directory
    src_dir = project_root / "src"
    
    print("🔧 Generating API documentation...")
    print(f"📂 Source directory: {src_dir}")
    print(f"📄 Output directory: {docs_dir}")
    
    # Build pdoc command
    cmd = [
        sys.executable, "-m", "pdoc",
        "--html",                    # Generate HTML output
        "--output-dir", str(docs_dir),  # Output directory
        "--force",                   # Overwrite existing files
        "--config", "show_source_code=False",  # Don't show source code
        str(src_dir)                 # Source directory to document
    ]
    
    try:
        # Run pdoc
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Documentation generated successfully!")
            
            # Move src directory up one level for cleaner URLs
            src_docs = docs_dir / "src"
            if src_docs.exists():
                # Move all contents from src/ to api/
                for item in src_docs.iterdir():
                    target = docs_dir / item.name
                    if target.exists():
                        shutil.rmtree(target)
                    shutil.move(str(item), str(target))
                # Remove empty src directory
                src_docs.rmdir()
            
            print(f"📖 Documentation available at: {docs_dir / 'index.html'}")
            print(f"🌐 Open in browser: file://{docs_dir.absolute() / 'index.html'}")
            
            # Create an index page if needed
            create_index_page(docs_dir)
            
        else:
            print("❌ Error generating documentation:")
            print(result.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error running pdoc: {e}")
        sys.exit(1)

def create_index_page(docs_dir: Path):
    """Create a main index page for the API documentation."""
    
    index_content = """<!DOCTYPE html>
<html>
<head>
    <title>Cooking Assistant - API Documentation</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        .module-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
        .module-card { border: 1px solid #ddd; border-radius: 8px; padding: 20px; background: #f8f9fa; }
        .module-card h3 { margin-top: 0; color: #2980b9; }
        .module-card a { text-decoration: none; color: #2980b9; font-weight: 500; }
        .module-card a:hover { text-decoration: underline; }
        .description { color: #666; font-size: 14px; margin: 10px 0; }
        .back-link { background: #3498db; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; display: inline-block; margin-bottom: 20px; }
        .back-link:hover { background: #2980b9; }
    </style>
</head>
<body>
    <a href="../" class="back-link">← Back to Project</a>
    
    <h1>🧑‍🍳 Cooking Assistant - API Documentation</h1>
    
    <p>Welcome to the API documentation for the Cooking Assistant project. This documentation is automatically generated from the source code docstrings.</p>
    
    <h2>📦 Core Modules</h2>
    <div class="module-grid">
        <div class="module-card">
            <h3><a href="core/index.html">Core</a></h3>
            <p class="description">Main cooking assistant interface, conversation memory, and query classification</p>
        </div>
        
        <div class="module-card">
            <h3><a href="prompting/index.html">Prompting</a></h3>
            <p class="description">Advanced prompting system with meta-prompting, templates, and examples</p>
        </div>
        
        <div class="module-card">
            <h3><a href="recipes/index.html">Recipes</a></h3>
            <p class="description">Recipe models, validation, and safety checking</p>
        </div>
        
        <div class="module-card">
            <h3><a href="vector/index.html">Vector</a></h3>
            <p class="description">Vector database operations, semantic search, and RAG functionality</p>
        </div>
        
        <div class="module-card">
            <h3><a href="common/index.html">Common</a></h3>
            <p class="description">Shared configuration, exceptions, and utilities</p>
        </div>
    </div>
    
    <h2>🔍 Key Features</h2>
    <ul>
        <li><strong>Vector Database</strong>: Semantic search with Chroma DB and OpenAI embeddings</li>
        <li><strong>Advanced Prompting</strong>: Meta-prompting with strategy selection and conversation memory</li>
        <li><strong>Recipe Generation</strong>: Multi-template recipe generation with validation</li>
        <li><strong>Search Capabilities</strong>: Dense, sparse, and hybrid search with filtering</li>
        <li><strong>Production Ready</strong>: Comprehensive testing, logging, and error handling</li>
    </ul>
    
    <h2>📚 Documentation</h2>
    <p>This API documentation covers all public functions, classes, and methods in the Cooking Assistant codebase. Each module includes detailed docstrings following PEP 257 conventions.</p>
    
    <p><strong>Last generated:</strong> """ + f"{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" + """</p>
</body>
</html>"""
    
    index_path = docs_dir / "index.html"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"📝 Created main index page: {index_path}")

if __name__ == "__main__":
    main()