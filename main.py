import os
import time
import shutil
import json
import csv
import io
import sys
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import google.generativeai as genai
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import PIL.Image

# ==========================================
# ⚙️ GLOBAL CONFIGURATION
# ==========================================
# 🔴 PASTE YOUR API KEY HERE
API_KEY = "AIzaSyBgMtNnqQCiCu7plY46FjcjPv5sAzTnzxw"

# Configure Logging to Console
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("DocuFlow")

genai.configure(api_key=API_KEY)

# ==========================================
# 🛠️ UTILITY: SYSTEM SETUP
# ==========================================
class SystemConfig:
    def __init__(self):
        self.source_dir: Path = Path(".")
        self.dest_dir: Path = Path(".")
        self.log_file: Path = Path(".")
        self.expense_file: Path = Path(".")

    def setup_interactive(self):
        print("\n" + "█"*60)
        print("   📂 DOCU-FLOW ENTERPRISE | AUTOMATION AGENT")
        print("█"*60 + "\n")
        
        # 1. Get Source Directory
        while True:
            raw_input = input("📥 INPUT SOURCE (Full Path): ").strip().replace('"', '').replace("'", "")
            path = Path(raw_input)
            if path.exists() and path.is_dir():
                self.source_dir = path
                break
            print("   ❌ Invalid path. Please try again.")

        # 2. Get Destination Root
        print(f"\n   (Press Enter to create output inside Source folder)")
        raw_output = input("out OUTPUT ROOT (Full Path): ").strip().replace('"', '').replace("'", "")
        
        root_dest = Path(raw_output) if raw_output else self.source_dir
        
        # Create Timestamped Session Folder
        session_id = datetime.now().strftime("%Y-%m-%d_%H-%M")
        self.dest_dir = root_dest / f"Organized_Batch_{session_id}"
        self.dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup CSV Logs
        self.log_file = self.dest_dir / "Audit_Log.csv"
        self.expense_file = self.dest_dir / "Financial_Report.csv"
        
        print("\n" + "-"*60)
        print(f"✅ Watching:  {self.source_dir}")
        print(f"✅ Target:    {self.dest_dir}")
        print("-"*60 + "\n")

# ==========================================
# 🧠 SERVICE: AI MODEL MANAGER
# ==========================================
class ModelService:
    @staticmethod
    def get_client() -> genai.GenerativeModel:
        logger.info("🔄 Initializing AI Engine...")
        try:
            available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            # Strict Priority List (Stable Only)
            priorities = [
                'models/gemini-1.5-flash',
                'models/gemini-1.5-flash-001',
                'models/gemini-1.5-flash-latest',
                'models/gemini-pro'
            ]
            
            for p in priorities:
                if p in available:
                    logger.info(f"   ⚡ Connected to: {p}")
                    return genai.GenerativeModel(p)
            
            # Fallback to any non-experimental model
            for m in available:
                if 'exp' not in m and 'preview' not in m:
                    return genai.GenerativeModel(m)
                    
        except Exception as e:
            logger.error(f"   ❌ Connection Failed: {e}")
        
        return genai.GenerativeModel('gemini-1.5-flash')

# ==========================================
# 📊 SERVICE: AUDIT LOGGER
# ==========================================
class AuditService:
    def __init__(self, config: SystemConfig):
        self.config = config
        self._init_csv(self.config.log_file, ["Time", "Original", "Category", "New Name", "Status"])
        self._init_csv(self.config.expense_file, ["Date", "Vendor", "Amount", "Category", "File"])

    def _init_csv(self, path: Path, headers: list):
        if not path.exists():
            try:
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    csv.writer(f).writerow(headers)
            except Exception as e:
                logger.error(f"   ❌ CSV Init Error: {e}")

    def log_event(self, original, category, new_name, status="OK"):
        self._write_row(self.config.log_file, [
            datetime.now().strftime("%H:%M:%S"), original, category, new_name, status
        ])

    def log_finance(self, data: dict, filename: str):
        if data.get('is_expense') or data.get('amount'):
            self._write_row(self.config.expense_file, [
                data.get('date', 'N/A'),
                data.get('vendor', 'Unknown'),
                data.get('amount', '0.00'),
                data.get('category', 'Expense'),
                filename
            ])
            print(f"   💰 FINANCES LOGGED: {data.get('vendor')} | ${data.get('amount')}")

    def _write_row(self, path: Path, row: list):
        try:
            with open(path, 'a', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(row)
        except: pass

# ==========================================
# 🕵️ SERVICE: DOCUMENT ANALYST
# ==========================================
class DocumentAnalyst:
    def __init__(self, model):
        self.model = model

    def _extract_json(self, text: str) -> Optional[dict]:
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            payload = match.group() if match else text
            return json.loads(payload)
        except: return None

    def analyze(self, file_path: Path) -> dict:
        ext = file_path.suffix.lower()
        
        prompt = """
        ROLE: Enterprise Document Processor.
        TASK:
        1. Classify file into: [INVOICE, RESUME, CONTRACT, ID_CARD, BANK_STMT, OTHER].
        2. Create a clean filename (Format: 'Category_Entity_Date').
        3. If financial, set 'is_expense': true and extract Vendor, Amount, Date.
        
        OUTPUT JSON ONLY:
        {"category": "INVOICE", "new_filename": "Invoice_AWS_2025", "is_expense": true, "vendor": "AWS", "amount": "100", "date": "2025-01-01"}
        """

        # Retry Logic for Rate Limits (429)
        for attempt in range(3):
            try:
                if ext in ['.jpg', '.jpeg', '.png', '.webp']:
                    with open(file_path, "rb") as f:
                        img = PIL.Image.open(io.BytesIO(f.read()))
                    response = self.model.generate_content([prompt, img])
                else:
                    with open(file_path, 'r', errors='ignore') as f:
                        text = f.read(4000)
                    response = self.model.generate_content([prompt, f"CONTENT:\n{text}"])

                data = self._extract_json(response.text)
                if data: return data
                
            except Exception as e:
                if "429" in str(e):
                    wait = (attempt + 1) * 15
                    logger.warning(f"   ⚠️ Rate Limit Hit. Pausing {wait}s...")
                    time.sleep(wait)
                else:
                    logger.error(f"   ❌ Analysis Error: {e}")
                    return {"category": "ERROR", "new_filename": "Processing_Failed"}

        return {"category": "UNSORTED", "new_filename": "Unknown_Doc"}

# ==========================================
# 🗄️ SERVICE: LIBRARIAN (WORKER)
# ==========================================
class Librarian:
    def __init__(self, config: SystemConfig, analyst: DocumentAnalyst, auditor: AuditService):
        self.config = config
        self.analyst = analyst
        self.auditor = auditor
        self.counter = 0

    def process_file(self, file_path: Path):
        # Validation
        if not file_path.is_file(): return
        if file_path.parent == self.config.dest_dir: return # Don't process output
        if file_path.suffix in ['.tmp', '.crdownload', '.py', '.csv']: return

        self.counter += 1
        print(f"\n[{self.counter}] ⏳ Analyzing: {file_path.name}...")

        # 1. AI Analysis
        meta = self.analyst.analyze(file_path)
        
        # 2. Determine Paths
        category = meta.get('category', 'OTHER').upper().replace(" ", "_")
        raw_name = meta.get('new_filename', 'Doc')
        
        # Sanitize Filename
        clean_name = "".join([c for c in raw_name if c.isalnum() or c in (' ', '_', '-')]).strip()
        new_filename = f"{clean_name}{file_path.suffix}"
        
        # 3. Log Financials
        self.auditor.log_finance(meta, new_filename)

        # 4. Move File
        dest_folder = self.config.dest_dir / category
        dest_folder.mkdir(exist_ok=True)
        final_path = dest_folder / new_filename

        # Handle Duplicates
        uniq = 1
        while final_path.exists():
            final_path = dest_folder / f"{clean_name}_{uniq}{file_path.suffix}"
            uniq += 1

        self._safe_move(file_path, final_path, category)
        
        # Rate Limit Cool-down
        time.sleep(4) 

    def _safe_move(self, src: Path, dest: Path, category: str):
        for _ in range(3):
            try:
                shutil.move(str(src), str(dest))
                print(f"   ✅ MOVED TO: {category} | NAME: {dest.name}")
                self.auditor.log_event(src.name, category, dest.name, "Success")
                return
            except PermissionError:
                time.sleep(1)
            except Exception as e:
                print(f"   ❌ Move Failed: {e}")
                return

# ==========================================
# 📡 WATCHDOG HANDLER
# ==========================================
class WatchHandler(FileSystemEventHandler):
    def __init__(self, librarian: Librarian):
        self.librarian = librarian
        self.last_event = 0

    def on_created(self, event):
        if not event.is_directory:
            # Debounce events
            if time.time() - self.last_event < 1: return
            self.last_event = time.time()
            
            time.sleep(2) # Buffer for file write completion
            self.librarian.process_file(Path(event.src_path))

# ==========================================
# 🚀 MAIN ENTRY POINT
# ==========================================
if __name__ == "__main__":
    # 1. Setup
    config = SystemConfig()
    config.setup_interactive()
    
    # 2. Initialize Services
    ai_model = ModelService.get_client()
    analyst = DocumentAnalyst(ai_model)
    auditor = AuditService(config)
    librarian = Librarian(config, analyst, auditor)

    # 3. Process Existing Files
    print("🔎 Scanning source for existing files...")
    existing = [p for p in config.source_dir.iterdir() if p.is_file()]
    valid_existing = [p for p in existing if p.suffix not in ['.py', '.csv']]

    if valid_existing:
        print(f"⚡ Found {len(valid_existing)} files. Processing batch...")
        for file_p in valid_existing:
            librarian.process_file(file_p)
    else:
        print("⚡ Folder is empty.")

    # 4. Start Live Watch
    print(f"\n🚀 Live Watchdog Active at: {config.source_dir}")
    print("   (Press Ctrl+C to stop)")
    print("-" * 60)
    
    observer = Observer()
    observer.schedule(WatchHandler(librarian), str(config.source_dir), recursive=False)
    observer.start()
    
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Docu-Flow Stopped.")
    observer.join()