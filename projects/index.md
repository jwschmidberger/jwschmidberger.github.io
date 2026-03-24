---
layout: single
permalink: /projects/
nav_order: 2
author_profile: true
classes: wide
---

{% assign items = site.projects | sort: "title" %}
{% for project in items %}
## [{{ project.title }}]({{ project.url | relative_url }})
{{ project.summary | default: project.excerpt | strip_html }}

{% if project.tech %}
**Tech:** {{ project.tech | array_to_sentence_string }}
{% endif %}

{% if project.links %}
**Links:**
{% for link in project.links %}
- [{{ link.label }}]({{ link.url }})
{% endfor %}
{% endif %}

{% unless forloop.last %}---{% endunless %}
{% endfor %}
