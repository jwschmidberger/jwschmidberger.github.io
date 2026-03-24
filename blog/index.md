---
layout: single
title: Writing
permalink: /blog/
nav_order: 4
author_profile: true
classes: wide
---

# Blog

{% if site.posts.size == 0 %}
No posts yet—check back soon.
{% endif %}

{% for post in site.posts %}
## [{{ post.title }}]({{ post.url | relative_url }})
<small>{{ post.date | date: "%B %-d, %Y" }}</small>

{{ post.excerpt | strip_html | truncate: 200 }}

[Read more →]({{ post.url | relative_url }})
{% unless forloop.last %}
---
{% endunless %}
{% endfor %}
