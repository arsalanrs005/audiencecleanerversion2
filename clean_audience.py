#!/usr/bin/env python3
"""
Audience Cleaner - Processes large CSV files from Audience Lab
Transforms the input CSV to a cleaned format with selected columns and cleaned data.
Handles files of any size by processing in chunks.
"""

import csv
import re
import sys
from pathlib import Path


def clean_phone(phone_str):
    """Extract and clean the first phone number from a string."""
    if not phone_str or phone_str.strip() == '':
        return ''
    
    # Split by comma and get first phone
    phones = phone_str.split(',')
    if not phones:
        return ''
    
    first_phone = phones[0].strip()
    
    # Remove +, spaces, and other non-digit characters except the number itself
    # Keep only digits
    cleaned = re.sub(r'[^\d]', '', first_phone)
    
    # Remove leading "1" for US phone numbers (11 digits -> 10 digits)
    if len(cleaned) == 11 and cleaned.startswith('1'):
        cleaned = cleaned[1:]
    
    return cleaned


def extract_first_email(email_str):
    """Extract the first email from a comma-separated list."""
    if not email_str or email_str.strip() == '':
        return ''
    
    emails = email_str.split(',')
    if not emails:
        return ''
    
    return emails[0].strip()


def clean_income_range(income_str):
    """Replace commas with spaces in income range strings."""
    if not income_str or income_str.strip() == '':
        return ''
    
    return income_str.replace(',', ' ')


def get_primary_phone(row):
    """Get primary phone from DIRECT_NUMBER, MOBILE_PHONE, or PERSONAL_PHONE."""
    # Try DIRECT_NUMBER first
    if row.get('DIRECT_NUMBER'):
        phone = clean_phone(row['DIRECT_NUMBER'])
        if phone:
            return phone
    
    # Try MOBILE_PHONE
    if row.get('MOBILE_PHONE'):
        phone = clean_phone(row['MOBILE_PHONE'])
        if phone:
            return phone
    
    # Try PERSONAL_PHONE
    if row.get('PERSONAL_PHONE'):
        phone = clean_phone(row['PERSONAL_PHONE'])
        if phone:
            return phone
    
    return ''


def get_primary_email(row):
    """Get primary email from BUSINESS_EMAIL or first from PERSONAL_EMAILS."""
    # Try BUSINESS_EMAIL first
    if row.get('BUSINESS_EMAIL') and row['BUSINESS_EMAIL'].strip():
        business_email = row['BUSINESS_EMAIL'].strip()
        # Extract first email if it contains multiple emails
        return extract_first_email(business_email)
    
    # Try PERSONAL_EMAILS
    if row.get('PERSONAL_EMAILS'):
        email = extract_first_email(row['PERSONAL_EMAILS'])
        if email:
            return email
    
    return ''


def process_csv(input_file, output_file):
    """Process the CSV file and create cleaned output."""
    
    print(f"Reading input file: {input_file}")
    print(f"Writing output file: {output_file}")
    
    # Output columns in the correct order
    output_columns = [
        'FIRST_NAME', 'LAST_NAME', 'PRIMARY_PHONE', 'PRIMARY_EMAIL',
        'Personal_Phone', 'Mobile_Phone', 'Valid_Phone', 'UUID',
        'PERSONAL_CITY', 'PERSONAL_STATE', 'AGE_RANGE', 'CHILDREN',
        'GENDER', 'HOMEOWNER', 'MARRIED', 'NET_WORTH', 'INCOME_RANGE',
        'LINKEDIN_URL'
    ]
    
    rows_processed = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8', errors='replace') as infile:
            # Detect delimiter
            sample = infile.read(1024)
            infile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(infile, delimiter=delimiter)
            
            with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=output_columns)
                writer.writeheader()
                
                for row in reader:
                    # Get primary phone
                    primary_phone = get_primary_phone(row)
                    
                    # Get personal and mobile phones
                    personal_phone = clean_phone(row.get('PERSONAL_PHONE', ''))
                    mobile_phone = clean_phone(row.get('MOBILE_PHONE', ''))
                    
                    # Get primary email
                    primary_email = get_primary_email(row)
                    
                    # Clean income ranges
                    net_worth = clean_income_range(row.get('NET_WORTH', ''))
                    income_range = clean_income_range(row.get('INCOME_RANGE', ''))
                    
                    # Get LinkedIn URL (try common column name variations)
                    linkedin_url = (row.get('LINKEDIN_URL', '') or 
                                   row.get('LinkedIn_URL', '') or 
                                   row.get('LINKEDIN', '') or 
                                   row.get('LinkedIn', '') or 
                                   row.get('linkedin_url', '') or '').strip()
                    
                    # Build output row
                    output_row = {
                        'FIRST_NAME': row.get('FIRST_NAME', ''),
                        'LAST_NAME': row.get('LAST_NAME', ''),
                        'PRIMARY_PHONE': primary_phone,
                        'PRIMARY_EMAIL': primary_email,
                        'Personal_Phone': personal_phone,
                        'Mobile_Phone': mobile_phone,
                        'Valid_Phone': primary_phone,  # Same as primary phone
                        'UUID': row.get('UUID', ''),
                        'PERSONAL_CITY': row.get('PERSONAL_CITY', ''),
                        'PERSONAL_STATE': row.get('PERSONAL_STATE', ''),
                        'AGE_RANGE': row.get('AGE_RANGE', ''),
                        'CHILDREN': row.get('CHILDREN', ''),
                        'GENDER': row.get('GENDER', ''),
                        'HOMEOWNER': row.get('HOMEOWNER', ''),
                        'MARRIED': row.get('MARRIED', ''),
                        'NET_WORTH': net_worth,
                        'INCOME_RANGE': income_range,
                        'LINKEDIN_URL': linkedin_url
                    }
                    
                    writer.writerow(output_row)
                    rows_processed += 1
                    
                    # Progress indicator for large files
                    if rows_processed % 10000 == 0:
                        print(f"Processed {rows_processed:,} rows...", end='\r')
        
        print(f"\n✓ Successfully processed {rows_processed:,} rows")
        print(f"✓ Output saved to: {output_file}")
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help', 'help']:
        print("Audience Cleaner - Clean and transform Audience Lab CSV files")
        print("=" * 60)
        print("\nUsage:")
        print("  clean-audience <input_file.csv> [output_file.csv]")
        print("\nExamples:")
        print("  clean-audience test2.csv")
        print("  clean-audience test2.csv cleaned_output.csv")
        print("  clean-audience ~/Downloads/large_file.csv")
        print("\nOptions:")
        print("  -h, --help    Show this help message")
        print("\nFor more information, see README.md")
        sys.exit(0)
    
    input_file = sys.argv[1]
    
    # Generate output filename if not provided
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        input_path = Path(input_file)
        output_file = str(input_path.parent / f"cleaned_{input_path.stem}.csv")
    
    # Check if input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)
    
    process_csv(input_file, output_file)


if __name__ == '__main__':
    main()

