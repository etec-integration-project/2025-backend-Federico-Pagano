import json
from datetime import datetime
from jinja2 import Template
import os
import glob

def load_data():
    """Load project data from various sources"""
    data = {
        'issues': [],
        'milestones': [],
        'api_endpoints': []
    }
    
    # Load issues if available
    if os.path.exists('data/issues.json'):
        with open('data/issues.json', 'r') as f:
            data['issues'] = json.load(f)
            
    # Load milestones if available
    if os.path.exists('data/milestones.json'):
        with open('data/milestones.json', 'r') as f:
            data['milestones'] = json.load(f)
            
    # Scan for API endpoints in the codebase
    for file in glob.glob('app/**/*.py', recursive=True):
        if 'routes' in file or 'views' in file:
            with open(file, 'r') as f:
                content = f.read()
                # Simple endpoint detection - can be enhanced
                if '@app.route' in content or '@bp.route' in content:
                    data['api_endpoints'].append({
                        'file': file,
                        'endpoints': extract_endpoints(content)
                    })
    
    return data

def extract_endpoints(content):
    """Extract API endpoints from file content"""
    endpoints = []
    lines = content.split('\n')
    for line in lines:
        if '@app.route' in line or '@bp.route' in line:
            # Basic endpoint extraction - can be enhanced
            endpoint = line.split('(')[1].split(')')[0].strip('"\'')
            method = 'GET'  # Default method
            if 'methods=' in line:
                method = line.split('methods=')[1].split(']')[0].strip('[').strip("'")
            endpoints.append({
                'path': endpoint,
                'method': method
            })
    return endpoints

def generate_docs():
    data = load_data()
    
    # Template para la documentación
    template_str = """---
layout: default
title: Documentación Detallada
---

# Documentación Detallada del Proyecto

_Última actualización: {{ current_date }}_

## API Endpoints

{% for file_data in api_endpoints %}
### {{ file_data.file }}
{% for endpoint in file_data.endpoints %}
- **{{ endpoint.method }}** {{ endpoint.path }}
{% endfor %}
{% endfor %}

## Resumen de Milestones

| Milestone | Estado | Fecha Límite |
|-----------|--------|--------------|
{% for milestone in milestones %}
| {{ milestone.title }} | {{ milestone.state }} | {{ milestone.due_on if milestone.due_on else 'No definida' }} |
{% endfor %}

## Issues Activos

{% for issue in issues if issue.state == 'open' %}
### #{{ issue.number }}: {{ issue.title }}
**Estado:** {{ issue.state }}
**Creado:** {{ issue.created_at }}
{% if issue.milestone %}**Milestone:** {{ issue.milestone }}{% endif %}
{% if issue.labels %}**Labels:** {{ issue.labels|join(', ') }}{% endif %}

{{ issue.body }}

---
{% endfor %}

## Issues Cerrados

{% for issue in issues if issue.state == 'closed' %}
### #{{ issue.number }}: {{ issue.title }}
**Estado:** {{ issue.state }}
**Creado:** {{ issue.created_at }}
**Cerrado:** {{ issue.closed_at }}
{% if issue.milestone %}**Milestone:** {{ issue.milestone }}{% endif %}
{% if issue.labels %}**Labels:** {{ issue.labels|join(', ') }}{% endif %}

{{ issue.body }}

---
{% endfor %}
"""
    
    template = Template(template_str)
    doc_content = template.render(
        current_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        **data
    )
    
    # Ensure docs directory exists
    os.makedirs('docs', exist_ok=True)
    
    # Guardar la documentación
    with open('docs/project-documentation.md', 'w') as f:
        f.write(doc_content)

if __name__ == '__main__':
    generate_docs() 