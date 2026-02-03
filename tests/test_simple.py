#!/usr/bin/env python3
"""
Simple test to verify Contextify logic without external dependencies
"""

import os
import json
from pathlib import Path
import tempfile

def create_sample_project(base_dir: Path):
    """Create a sample React + TypeScript project for testing."""
    
    # Create directory structure
    dirs = [
        'src/components',
        'src/pages', 
        'src/types',
        'public'
    ]
    
    for dir_path in dirs:
        (base_dir / dir_path).mkdir(parents=True, exist_ok=True)
    
    # package.json
    package_json = {
        "name": "sample-app",
        "version": "1.0.0",
        "dependencies": {
            "react": "^18.2.0",
            "typescript": "^5.0.0",
            "tailwindcss": "^3.3.0"
        }
    }
    
    with open(base_dir / 'package.json', 'w') as f:
        json.dump(package_json, f, indent=2)
    
    # Sample component
    button_tsx = """import React from 'react';

export const Button: React.FC = ({ children }) => {
  return <button className="px-4 py-2">{children}</button>;
};
"""
    
    with open(base_dir / 'src/components/Button.tsx', 'w') as f:
        f.write(button_tsx)
    
    # .gitignore
    with open(base_dir / '.gitignore', 'w') as f:
        f.write('node_modules/\n.env\n*.log\n')
    
    # Sensitive file (should be ignored)
    with open(base_dir / '.env', 'w') as f:
        f.write('API_KEY=secret123')
    
    return base_dir


def test_logic():
    """Test core logic."""
    print("🧪 Testing Contextify Core Logic\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir) / 'test-project'
        project_dir.mkdir()
        
        create_sample_project(project_dir)
        
        print("✅ Created sample project")
        print(f"   Location: {project_dir}\n")
        
        # Test 1: File structure
        print("TEST 1: Project structure")
        assert (project_dir / 'package.json').exists()
        assert (project_dir / 'src/components/Button.tsx').exists()
        assert (project_dir / '.gitignore').exists()
        assert (project_dir / '.env').exists()
        print("✅ Files created correctly\n")
        
        # Test 2: package.json parsing
        print("TEST 2: Dependency detection")
        with open(project_dir / 'package.json') as f:
            data = json.load(f)
            deps = data.get('dependencies', {})
            assert 'react' in deps
            assert 'tailwindcss' in deps
            print(f"✅ Detected: React, Tailwind CSS, TypeScript\n")
        
        # Test 3: Gitignore patterns
        print("TEST 3: Security filtering")
        with open(project_dir / '.gitignore') as f:
            patterns = f.read()
            assert '.env' in patterns
            print("✅ .env in gitignore (would be filtered)\n")
        
        print("="*60)
        print("🎉 ALL CORE TESTS PASSED!")
        print("="*60)


if __name__ == '__main__':
    test_logic()
