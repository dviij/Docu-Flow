import os
import random
from PIL import Image, ImageDraw

# ==========================================
# ⚙️ GENERATOR SETUP
# ==========================================
def setup_generator():
    print("\n" + "="*50)
    print("🧪 SUPER-GENERATOR (12 FILES)")
    print("="*50)
    while True:
        target_path = input("👉 Enter the path to generate files in: ").strip().replace('"', '').replace("'", "")
        if os.path.exists(target_path) and os.path.isdir(target_path): return target_path
        print("❌ Invalid folder!")

TARGET_FOLDER = setup_generator()

def save_file(name, content):
    with open(os.path.join(TARGET_FOLDER, name), "w") as f: f.write(content)
    print(f"📄 Created: {name}")

# ==========================================
# 📄 TEMPLATES
# ==========================================

def create_invoices():
    # 1. AWS Bill
    save_file("scan_aws_bill.txt", """
    INVOICE #9921
    Vendor: Amazon Web Services
    Date: 2025-12-01
    Total Amount: $450.00
    Description: EC2 Instances
    """)
    # 2. Local Plumber
    save_file("handwritten_invoice.txt", """
    RECEIPT
    From: Joe's Plumbing
    Date: 2025-11-20
    Fixing leak: $120.00
    Parts: $30.00
    Total: $150.00
    PAID CASH
    """)

def create_medical():
    save_file("lab_report_blood.txt", """
    MEDICAL REPORT
    Patient: John Doe
    Date: 2025-10-15
    Test: CBC Blood Count
    Result: Normal
    Doctor: Dr. Smith
    """)

def create_resumes():
    save_file("resume_rahul_python.txt", """
    RESUME
    Name: Rahul Sharma
    Role: Senior Python Developer
    Skills: Django, AI, SQL
    Experience: 5 Years at TechCorp
    """)
    save_file("cv_priya_designer.txt", """
    CURRICULUM VITAE
    Name: Priya Verma
    Role: UI/UX Designer
    Portfolio: behance.net/priya
    """)

def create_bank_stmts():
    save_file("stmt_hdfc_dec.txt", """
    HDFC BANK STATEMENT
    Account: 5010023000
    Period: Dec 2025
    Opening Balance: 50,000 INR
    Closing Balance: 45,000 INR
    """)

def create_images():
    # Dummy Receipt Image
    img = Image.new('RGB', (300, 500), color='white')
    d = ImageDraw.Draw(img)
    d.text((50,50), "STARBUCKS\nTotal: $12.50\nDate: 2025-12-01", fill='black')
    img.save(os.path.join(TARGET_FOLDER, "photo_receipt_coffee.jpg"))
    print(f"🖼️ Created: photo_receipt_coffee.jpg")

    # Dummy ID Card
    img2 = Image.new('RGB', (400, 250), color='lightblue')
    d2 = ImageDraw.Draw(img2)
    d2.text((20,20), "CORPORATE ID\nName: Alice Cooper\nID: 9921", fill='black')
    img2.save(os.path.join(TARGET_FOLDER, "id_card_alice.png"))
    print(f"🖼️ Created: id_card_alice.png")

if __name__ == "__main__":
    print(f"\n🚀 Generating test data in: {TARGET_FOLDER}...\n")
    create_invoices()
    create_medical()
    create_resumes()
    create_bank_stmts()
    create_images()
    print("\n✅ Generation Complete!")