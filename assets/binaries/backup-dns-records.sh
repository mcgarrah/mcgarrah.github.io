#!/bin/bash
# DNS Backup Script for SquareSpace Domain Migration
# Backs up all DNS records before transfer to Porkbun

# Check if dig command is available
if ! command -v dig &> /dev/null; then
    echo "ERROR: 'dig' command not found"
    echo "Install with: apt-get install dnsutils (Debian/Ubuntu) or dnf install bind-utils (RHEL/Fedora)"
    exit 1
fi

DOMAINS=(
    # Already migrated to Porkbun (commented out):
    # "mathomancer.com"
    # "mathomancy.com"
    # "brainyzone.com"
    # "brainyzone.org"
    # "cshensley.com"
    # "brainyz.one"
    # "brainyzone.app"
    # "brainyzone.net"
    # "brainyzone.us"
    
    # Still at SquareSpace (active):
    "mcgarware.com"
    "phonemes.org"
    "darkmagic.org"
    "mcgarrah.dev"
    "mcgarrah.org"
    "mcgarrah.us"
    "mcgarrah.app"
)

RECORD_TYPES=("A" "AAAA" "CNAME" "MX" "TXT" "NS" "SOA" "SRV")
BACKUP_DIR="dns-backups-$(date +%Y%m%d-%H%M%S)"

mkdir -p "$BACKUP_DIR"

echo "DNS Backup started at $(date)"
echo "Backup directory: $BACKUP_DIR"
echo "================================"

for domain in "${DOMAINS[@]}"; do
    echo "Backing up: $domain"
    output_file="$BACKUP_DIR/${domain}.txt"
    
    echo "DNS Records for $domain" > "$output_file"
    echo "Backup Date: $(date)" >> "$output_file"
    echo "========================================" >> "$output_file"
    echo "" >> "$output_file"
    
    for type in "${RECORD_TYPES[@]}"; do
        echo "[$type Records]" >> "$output_file"
        dig @8.8.8.8 "$domain" "$type" +noall +answer >> "$output_file" 2>&1
        echo "" >> "$output_file"
    done
    
    # Also check www subdomain
    echo "[WWW Subdomain]" >> "$output_file"
    dig @8.8.8.8 "www.$domain" A +noall +answer >> "$output_file" 2>&1
    echo "" >> "$output_file"
    
    echo "✓ Saved to $output_file"
done

echo "================================"
echo "Backup complete!"
echo "Files saved in: $BACKUP_DIR"
echo ""
echo "To view a domain's records:"
echo "  cat $BACKUP_DIR/mcgarrah.org.txt"
