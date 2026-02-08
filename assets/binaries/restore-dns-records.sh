#!/bin/bash
# DNS Restore Script for Porkbun
# Restores DNS records from backup files to Porkbun using their API

# Check for required commands
if ! command -v curl &> /dev/null; then
    echo "ERROR: 'curl' command not found"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "ERROR: 'jq' command not found"
    echo "Install with: apt-get install jq (Debian/Ubuntu) or dnf install jq (RHEL/Fedora)"
    exit 1
fi

# Porkbun API credentials - SET THESE BEFORE RUNNING
PORKBUN_API_KEY="${PORKBUN_API_KEY:-}"
PORKBUN_SECRET_KEY="${PORKBUN_SECRET_KEY:-}"

if [[ -z "$PORKBUN_API_KEY" || -z "$PORKBUN_SECRET_KEY" ]]; then
    echo "ERROR: Porkbun API credentials not set"
    echo ""
    echo "Set credentials as environment variables:"
    echo "  export PORKBUN_API_KEY='your_api_key'"
    echo "  export PORKBUN_SECRET_KEY='your_secret_key'"
    echo ""
    echo "Get API keys from: https://porkbun.com/account/api"
    exit 1
fi

# Check for backup directory argument
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <backup-directory>"
    echo ""
    echo "Example: $0 dns-backups-20260215-120000"
    exit 1
fi

BACKUP_DIR="$1"

if [[ ! -d "$BACKUP_DIR" ]]; then
    echo "ERROR: Backup directory not found: $BACKUP_DIR"
    exit 1
fi

API_URL="https://porkbun.com/api/json/v3/dns/create"

echo "DNS Restore started at $(date)"
echo "Backup directory: $BACKUP_DIR"
echo "================================"
echo ""

# Function to create DNS record via Porkbun API
create_record() {
    local domain=$1
    local name=$2
    local type=$3
    local content=$4
    local ttl=${5:-600}
    local priority=${6:-}
    
    # Build JSON payload
    local json_data=$(jq -n \
        --arg apikey "$PORKBUN_API_KEY" \
        --arg secretapikey "$PORKBUN_SECRET_KEY" \
        --arg name "$name" \
        --arg type "$type" \
        --arg content "$content" \
        --arg ttl "$ttl" \
        --arg prio "$priority" \
        '{apikey: $apikey, secretapikey: $secretapikey, name: $name, type: $type, content: $content, ttl: $ttl} + if $prio != "" then {prio: $prio} else {} end')
    
    response=$(curl -s -X POST "${API_URL}/${domain}" \
        -H "Content-Type: application/json" \
        -d "$json_data")
    
    status=$(echo "$response" | jq -r '.status // "error"')
    
    if [[ "$status" == "SUCCESS" ]]; then
        echo "  ✓ Created: $type $name -> $content"
        return 0
    else
        message=$(echo "$response" | jq -r '.message // "Unknown error"')
        echo "  ✗ Failed: $type $name -> $content ($message)"
        return 1
    fi
}

# Process each backup file
for backup_file in "$BACKUP_DIR"/*.txt; do
    if [[ ! -f "$backup_file" ]]; then
        continue
    fi
    
    domain=$(basename "$backup_file" .txt)
    echo "Processing: $domain"
    echo "---"
    
    # Parse backup file and create records
    while IFS= read -r line; do
        # Skip empty lines, comments, and section headers
        [[ -z "$line" || "$line" =~ ^[[:space:]]*$ || "$line" =~ ^\[ || "$line" =~ ^DNS || "$line" =~ ^Backup || "$line" =~ ^=== ]] && continue
        
        # Parse dig output format: name TTL class type content
        if [[ "$line" =~ ^([^[:space:]]+)[[:space:]]+([0-9]+)[[:space:]]+IN[[:space:]]+([A-Z]+)[[:space:]]+(.+)$ ]]; then
            record_name="${BASH_REMATCH[1]}"
            ttl="${BASH_REMATCH[2]}"
            record_type="${BASH_REMATCH[3]}"
            record_content="${BASH_REMATCH[4]}"
            
            # Extract subdomain from FQDN
            subdomain="${record_name%.${domain}.}"
            [[ "$subdomain" == "$domain" ]] && subdomain=""
            
            # Skip NS and SOA records (managed by Porkbun)
            [[ "$record_type" == "NS" || "$record_type" == "SOA" ]] && continue
            
            # Handle MX records (extract priority)
            priority=""
            if [[ "$record_type" == "MX" ]]; then
                priority=$(echo "$record_content" | awk '{print $1}')
                record_content=$(echo "$record_content" | awk '{print $2}')
            fi
            
            # Create the record
            create_record "$domain" "$subdomain" "$record_type" "$record_content" "$ttl" "$priority"
        fi
    done < "$backup_file"
    
    echo ""
done

echo "================================"
echo "Restore complete at $(date)"
echo ""
echo "Verify records at: https://porkbun.com/account/domainsSpeedy"
