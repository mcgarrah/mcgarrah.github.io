require 'yaml'
require 'date'

tags_map = {}
issues = []

Dir.glob("_posts/*.{md,markdown}").each do |file|
  content = File.read(file)
  if content =~ /\A(---\s*\n.*?\n---)/m
    raw_yaml = $1
    if raw_yaml =~ /tags:\s*\[(.*?)\]/
      inside = $1
      if inside =~ /[^,\s]+,[^,\s]+/
        issues << "#{file}: Missing space after comma in tag list: [#{inside}]"
      end
    end
    
    begin
      data = YAML.safe_load(raw_yaml, permitted_classes: [Date, Time])
      tags = Array(data["tags"]).compact
      tags.each do |tag|
        str_tag = tag.to_s
        cleaned = str_tag.strip
        if str_tag != cleaned
          issues << "#{file}: Tag has extra whitespace: #{str_tag.inspect}"
        end
        
        slug = cleaned.downcase.gsub(" ", "-")
        tags_map[slug] ||= {}
        tags_map[slug][str_tag] ||= []
        tags_map[slug][str_tag] << file
      end
    rescue => e
      issues << "#{file}: YAML Parsing Error - #{e.message}"
    end
  end
end

puts "=== FRONT MATTER ISSUES ==="
if issues.empty?
  puts "No formatting syntax issues found."
else
  issues.each { |i| puts "  - #{i}" }
end

puts "\n=== TAG CASING / SLUG COLLISIONS ==="
collisions = 0
tags_map.each do |slug, variants|
  if variants.keys.size > 1
    collisions += 1
    puts "Slug conflict for [#{slug}]:"
    variants.each do |variant, files|
      puts "   - Variant \"#{variant}\" in: #{files.join(", ")}"
    end
  end
end

puts "No tag slug collisions found." if collisions == 0
