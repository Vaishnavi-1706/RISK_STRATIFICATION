#!/usr/bin/env python3
"""
Generate PDFs for All Existing Patients
This script generates PDF reports for all patients in the index.csv file
"""

import pandas as pd
from pdf_generator import pdf_generator

def main():
    print("📄 Generating PDF Reports for All Patients")
    print("=" * 50)
    
    try:
        # Generate PDFs for all patients
        generated_count = pdf_generator.generate_pdfs_for_all_patients()
        
        print(f"\n🎉 PDF Generation Complete!")
        print(f"✅ Generated {generated_count} PDF reports")
        
        # List all PDF files
        pdf_files = pdf_generator.list_all_pdfs()
        print(f"📁 Total PDF files in temp folder: {len(pdf_files)}")
        
        if pdf_files:
            print("\n📋 Generated PDF Files:")
            for pdf_file in pdf_files:
                print(f"  - {pdf_file}")
        
        print(f"\n📂 PDF files are stored in: {pdf_generator.temp_folder}/")
        
    except Exception as e:
        print(f"❌ Error generating PDFs: {e}")

if __name__ == "__main__":
    main()
