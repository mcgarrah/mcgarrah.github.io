---
title: "Contact"
permalink: /contact/
layout: page
---

## Get in Touch

I'm always interested in connecting with fellow technologists, researchers, and homelab enthusiasts.

### Contact Information

{% for item in site.external %}
  {% if item.icon == 'envelope' %}
**Email:** [{{ item.url | remove: 'mailto:' }}]({{ item.url }})
  {% endif %}
{% endfor %}

### Professional Networks

{% for item in site.external %}
  {% if item.icon == 'linkedin' or item.icon == 'github' or item.icon == 'gitlab' or item.icon == 'stack-overflow' %}
- **{{ item.title }}:** [{{ item.url | remove: 'https://' | remove: 'http://' }}]({{ item.url }})
  {% endif %}
{% endfor %}

### Academic & Research

{% for item in site.external %}
  {% if item.icon == 'orcid' or item.icon == 'graduation-cap' or item.icon == 'researchgate' %}
- **{{ item.title }}:** [{{ item.url | remove: 'https://' | remove: 'http://' }}]({{ item.url }})
  {% endif %}
{% endfor %}

### Other

{% for item in site.external %}
  {% if item.icon == 'discord' or item.icon == 'file' or item.icon == 'rss' %}
- **{{ item.title }}:** [{{ item.url | remove: 'https://' | remove: 'http://' }}]({{ item.url }})
  {% endif %}
{% endfor %}

### About This Blog

This blog covers technical topics including:

- Homelab infrastructure (Proxmox, Ceph, Kubernetes)
- Machine learning and AI research
- Networking and virtualization
- Software development and automation

For more information, see the [About](/about/) page.

### Privacy

Your privacy is important. See our [Privacy Policy](/privacy/) for details on how we handle data.
