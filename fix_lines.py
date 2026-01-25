#!/usr/bin/env python3

with open('frontend/web/src/pages/MajorDetailPage.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix problematic lines by replacing them entirely
problematic_pattern = '{item.year && `${item.year年：`}{item.title}'
fixed_line = '                          {item.year && `${item.year年：`}{item.title}\n'

for i, line in enumerate(lines):
    if problematic_pattern in line:
        lines[i] = fixed_line

with open('frontend/web/src/pages/MajorDetailPage.tsx', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Fixed problematic lines")