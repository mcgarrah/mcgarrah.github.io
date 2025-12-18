---
title: "Creating a Resume Post Type in Jekyll: Alternative to Full Site Integration"
layout: post
categories: [web-development, jekyll]
tags: [jekyll, resume, post-types, collections, data-driven-content]
excerpt: "Exploring how to create a specialized 'Resume' post type within Jekyll to display professional information as structured content, offering a lightweight alternative to full site merger."
published: false
---

Rather than merging two complete Jekyll sites, what if we could create a specialized "Resume" post type within the main blog? This approach would allow displaying professional information as structured content while maintaining the blog's existing architecture and functionality.

<!-- excerpt-end -->

## Concept Overview

The idea is to extend Jekyll's post system to support a new content type that:
- Uses structured data instead of traditional markdown content
- Renders with specialized layouts optimized for professional information
- Integrates seamlessly with existing blog navigation and SEO
- Maintains print-friendly formatting options

## Implementation Approaches

### Approach 1: Custom Post Layout with Data Files

**Structure**:
```
_posts/2025-01-03-michael-mcgarrah-resume.md
_data/resume/
├── personal.yml
├── experience.yml
├── education.yml
└── skills.yml
```

**Post Front Matter**:
```yaml
---
title: "Michael McGarrah - Resume"
layout: resume
categories: [resume]
tags: [professional, cv, experience]
resume_data: true
print_friendly: true
canonical_url: "/resume/"
---
```

**Minimal Post Content**:
```markdown
This is my professional resume, updated {{ site.time | date: "%B %Y" }}.

For a PDF version, [download here](/assets/pdf/resume.pdf).
```

### Approach 2: Jekyll Collections for Resume Sections

**Configuration** (`_config.yml`):
```yaml
collections:
  resume_sections:
    output: false
    
resume:
  enabled: true
  permalink: /resume/
```

**Collection Structure**:
```
_resume_sections/
├── 01-profile.md
├── 02-experience.md
├── 03-education.md
└── 04-skills.md
```

**Resume Post**:
```yaml
---
title: "Professional Resume"
layout: resume
type: resume
sections: true
---
```

### Approach 3: Data-Driven Resume Post (Recommended)

**Single Resume Post** (`_posts/2025-01-03-resume.md`):
```yaml
---
title: "Michael McGarrah - Professional Resume"
layout: resume
categories: [professional]
tags: [resume, cv, experience, skills]
type: resume
last_updated: 2025-01-03
print_url: /resume/print/
pdf_url: /assets/pdf/resume.pdf
---

Professional summary and contact information.
```

**Data Structure** (`_data/resume.yml`):
```yaml
personal:
  name: "Michael McGarrah"
  title: "Data Scientist / Cloud Architect"
  email: "mcgarrah@gmail.com"
  phone: "919 807-1057"
  website: "mcgarrah.org"
  
experience:
  - role: "Lead Principal Engineer"
    company: "Envestnet, Inc."
    period: "Oct 2021 - Present"
    location: "Remote"
    highlights:
      - "Building large scale cloud platforms"
      - "AWS & Kubernetes implementations"
      
education:
  - degree: "Masters of Science in Computer Science"
    school: "Georgia Institute of Technology"
    period: "2014 - 2019"
    gpa: "3.63"
```

## Custom Resume Layout

**Layout File** (`_layouts/resume.html`):
```html
---
layout: default
---

<article class="resume-post">
  <header class="resume-header">
    <h1>{{ page.title }}</h1>
    <div class="resume-meta">
      <span class="last-updated">Updated: {{ page.last_updated | date: "%B %d, %Y" }}</span>
      {% if page.pdf_url %}
        <a href="{{ page.pdf_url }}" class="pdf-download">Download PDF</a>
      {% endif %}
    </div>
  </header>

  <div class="resume-content">
    {{ content }}
    
    {% comment %}
    {% include resume/personal.html %}
    {% include resume/experience.html %}
    {% include resume/education.html %}
    {% include resume/skills.html %}
    {% endcomment %}
  </div>
</article>
```

## Modular Resume Components

**Personal Section** (`_includes/resume/personal.html`):
```html
<section class="resume-section personal">
  <div class="contact-info">
    <h2>{{ site.data.resume.personal.name }}</h2>
    <p class="title">{{ site.data.resume.personal.title }}</p>
    <ul class="contact-details">
      <li>{{ site.data.resume.personal.email }}</li>
      <li>{{ site.data.resume.personal.phone }}</li>
      <li>{{ site.data.resume.personal.website }}</li>
    </ul>
  </div>
</section>
```

**Experience Section** (`_includes/resume/experience.html`):
```html
<section class="resume-section experience">
  <h2>Professional Experience</h2>
  {% for job in site.data.resume.experience %}
    <div class="job">
      <h3>{{ job.role }}</h3>
      <div class="job-meta">
        <span class="company">{{ job.company }}</span>
        <span class="period">{{ job.period }}</span>
      </div>
      <ul class="highlights">
        {% for highlight in job.highlights %}
          <li>{{ highlight }}</li>
        {% endfor %}
      </ul>
    </div>
  {% endfor %}
</section>
```

## Styling Integration

**Resume-Specific Styles** (`_sass/resume.sass`):
```scss
.resume-post {
  .resume-header {
    border-bottom: 2px solid #333;
    margin-bottom: 2rem;
    
    .resume-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 1rem;
    }
  }
  
  .resume-section {
    margin-bottom: 2rem;
    
    h2 {
      border-bottom: 1px solid #ddd;
      padding-bottom: 0.5rem;
    }
  }
  
  .job {
    margin-bottom: 1.5rem;
    
    .job-meta {
      display: flex;
      justify-content: space-between;
      font-style: italic;
      color: #666;
    }
  }
}

// Print styles
@media print {
  .resume-post {
    .resume-header .pdf-download {
      display: none;
    }
  }
}
```

## Implementation Complexity

### Low Complexity ✅
- **Single resume post with data files**
- **Basic custom layout**
- **Simple styling integration**
- **Estimated effort**: 4-6 hours

### Medium Complexity
- **Print optimization**
- **PDF generation integration**
- **Advanced styling and responsive design**
- **Estimated effort**: 8-12 hours

### High Complexity
- **Multiple resume versions (different audiences)**
- **Dynamic section toggling**
- **Advanced print layouts**
- **Estimated effort**: 16-20 hours

## Benefits of This Approach

### 1. **Minimal Disruption**
- No changes to existing blog functionality
- Maintains current theme and navigation
- Single additional post and layout

### 2. **SEO Integration**
- Resume appears in blog archives and feeds
- Proper meta tags and structured data
- Canonical URL management

### 3. **Content Management**
- Version controlled resume updates
- Easy to maintain and update
- Consistent with blog workflow

### 4. **Flexibility**
- Can create multiple resume versions
- Easy to add new sections or modify layout
- Print-friendly options

## Navigation Integration

**Updated Navigation** (`_config.yml`):
```yaml
navigation:
  - {file: "index.html", icon: blog}
  - {file: "archive.html", icon: list}
  - {file: "tags.html", title: Tags, icon: tags}
  - {file: "categories.html", title: Categories, icon: th-list}
  - {file: "search.html", title: Search, icon: search}
  - {title: Resume, url: "/resume/", icon: user}  # Links to resume post
  - {file: "README.md", icon: user}
```

## URL Structure Options

### Option 1: Date-Based (Standard Jekyll)
```
/michael-mcgarrah-resume/
```

### Option 2: Custom Permalink
```yaml
# In post front matter
permalink: /resume/
```

### Option 3: Category-Based
```yaml
# In _config.yml
permalink: /:categories/:title/
# Results in: /professional/michael-mcgarrah-resume/
```

## Advanced Features

### 1. **Multiple Resume Versions**
```
_posts/
├── 2025-01-03-resume-technical.md
├── 2025-01-03-resume-executive.md
└── 2025-01-03-resume-academic.md
```

### 2. **Dynamic Content Filtering**
```yaml
# In post front matter
resume_focus: technical
show_sections: [experience, skills, education]
hide_sections: [publications]
```

### 3. **Print Page Generation**
```yaml
# Additional layout for print
layout: resume-print
print_optimized: true
```

## Implementation Steps

### Phase 1: Basic Implementation
1. Create resume data file (`_data/resume.yml`)
2. Create resume post with custom layout
3. Add basic styling
4. Test rendering and navigation

### Phase 2: Enhancement
1. Add print optimization
2. Integrate with existing navigation
3. Add PDF download functionality
4. Implement responsive design

### Phase 3: Advanced Features
1. Multiple resume versions
2. Dynamic section filtering
3. Advanced print layouts
4. SEO optimization

## Comparison with Full Site Merger

| Aspect | Resume Post Type | Full Site Merger |
|--------|------------------|------------------|
| **Complexity** | Low-Medium | High |
| **Development Time** | 4-12 hours | 40-80 hours |
| **Maintenance** | Minimal | Significant |
| **Functionality** | Core features | Full features |
| **Risk** | Low | High |
| **SEO Integration** | Excellent | Complex |

## Conclusion

Creating a "Resume" post type offers a **pragmatic middle ground** between maintaining separate sites and full integration. This approach:

- **Preserves** existing blog functionality
- **Adds** professional content display capability  
- **Maintains** SEO benefits of unified site
- **Requires** minimal development effort
- **Provides** flexibility for future enhancements

The data-driven approach with custom layouts provides the professional presentation needed while leveraging Jekyll's existing post system and maintaining the blog's architecture integrity.

## Next Steps

1. **Prototype** basic resume post with sample data
2. **Design** custom layout matching blog theme
3. **Implement** print-friendly styling
4. **Test** across devices and browsers
5. **Deploy** and gather feedback

This approach offers **80% of the benefits** of full site integration with **20% of the complexity** - making it an ideal solution for displaying professional information within the existing blog framework.

---

*This implementation strategy provides a clean, maintainable way to add resume functionality without the architectural complexity of merging two complete Jekyll sites.*