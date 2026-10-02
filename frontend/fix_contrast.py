import os, re

d = r'd:\B Tech academic docs and study material\Term II ABHAY BHISE\Predictive Analytics\PA LAB\PA LAB PROJECT\AQI PREDICTION VERSION 2\frontend\src'
for root, _, files in os.walk(d):
    for f in files:
        if f.endswith('.jsx'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8') as file:
                content = file.read()
            
            def replacer(match):
                class_str = match.group(1)
                
                if 'dark:text-' not in class_str:
                    class_str = re.sub(r'\btext-slate-900\b', r'text-slate-900 dark:text-white', class_str)
                    class_str = re.sub(r'\btext-slate-800\b', r'text-slate-800 dark:text-slate-200', class_str)
                    class_str = re.sub(r'\btext-slate-700\b', r'text-slate-700 dark:text-slate-300', class_str)
                    class_str = re.sub(r'\btext-slate-600\b', r'text-slate-600 dark:text-slate-400', class_str)
                    class_str = re.sub(r'\btext-slate-500\b', r'text-slate-500 dark:text-slate-400', class_str)
                
                return match.group(0).replace(match.group(1), class_str)
                
            new_content = re.sub(r'(?:className|class)="([^"]*)"', replacer, content)
            new_content = re.sub(r'(?:className|class)=\{`([^`]*)`\}', replacer, new_content)
            
            # Additional fallback: Just direct replace if they are naked text-slate-800 etc without being caught
            # But the above should catch them inside className="" or className={``}
            
            if new_content != content:
                with open(p, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f'Updated {f}')

