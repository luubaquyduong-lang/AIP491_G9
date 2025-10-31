import re, json, os
p = os.path.join('Data','raw','vnexpress','vnexpress_data.txt')
with open(p, 'r', encoding='utf-8') as f:
    text = f.read()
# Tìm các cụm 'Giới thiệu về X.' hoặc 'Giới thiệu về X,'
matches = re.findall(r"Giới thiệu về ([^\n\.,]+)[\.,]", text)
seen = set()
unique = []
for m in matches:
    name = m.strip()
    if name and name not in seen:
        seen.add(name)
        unique.append(name)
print(json.dumps(unique, ensure_ascii=False, indent=2))
