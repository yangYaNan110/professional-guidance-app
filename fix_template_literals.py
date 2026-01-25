#!/usr/bin/env python3

with open('frontend/web/src/pages/MajorDetailPage.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix broken template literals
import re

# Pattern to match broken template literals like `{item.year年:``}{item.title}`
pattern = r'({item\.year.*?年:)``({item\.title})'
fixed_content = re.sub(pattern, r'\1`\2', content)

# Also fix any remaining character encoding issues
fixed_content = fixed_content.replace('\xef\xbc\x9a', '：')

with open('frontend/web/src/pages/MajorDetailPage.tsx', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("Fixed template literal issues")