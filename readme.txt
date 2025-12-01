# 📂 Docu-Flow: The Autonomous Enterprise Clerk

### 🏆 Kaggle AI Agents Capstone Project | Track: **Enterprise Agents**

**Docu-Flow** is an intelligent, multi-modal "Watchdog Agent" that autonomously monitors file directories, classifies documents (using Vision & Text analysis), extracts key business data, and organizes files into a structured archive. It transforms chaotic "Downloads" folders into searchable, audit-ready enterprise repositories without human intervention.

-----

## 🚨 The Problem

In every business, administrative teams waste countless hours manually processing incoming files. Invoices, contracts, resumes, and receipts arrive with useless names like `scan_001.pdf` or `WhatsApp_Image_29.jpeg`.

  * **Manual Effort:** Opening every file to see what it is.
  * **Data Loss:** Important financial data remains trapped in PDFs/Images.
  * **Disorganization:** Files are lost in a sea of unclassified folders.

## 💡 The Solution

**Docu-Flow** acts as an always-on back-office clerk. It utilizes **Google Gemini 1.5 Flash** to:

1.  **Watch:** Detect new files the moment they land.
2.  **Read:** Analyze text docs AND images (receipts/ID cards).
3.  **Think:** Classify the document type and generate a standardized filename (e.g., `Invoice_AWS_2025-12-01`).
4.  **Act:** Move the file to the correct department folder.
5.  **Remember:** Log every action and extract financial data (Vendor, Amount) into a CSV report.

-----

## ⚙️ Architecture & Design

This project implements a **Sequential Multi-Agent Architecture** following **SOLID principles**:

| Component | Responsibility (SRP) |
| :--- | :--- |
| **WatcherHandler** | The "Trigger". Uses `watchdog` to listen for file system events in real-time. |
| **DocumentAnalyst** | The "Brain". Uses **Gemini 1.5 Flash** to classify documents and extract JSON metadata. Handles API rate limits with exponential backoff. |
| **Librarian** | The "Hands". Handles safe file operations, collision detection (duplicate names), and directory management. |
| **AuditService** | The "Memory". Maintains `Audit_Log.csv` for observability and `Financial_Report.csv` for data extraction. |

-----

## 🚀 Installation & Setup

### 1\. Prerequisites

  * Python 3.9+
  * A Google Gemini API Key

### 2\. Install Dependencies

```bash
pip install google-generativeai watchdog pillow
```

### 3\. Configure API Key

Open `main.py` and paste your API key in the configuration section:

```python
API_KEY = "YOUR_GEMINI_API_KEY_HERE"
```

-----

## 🖥️ How to Use

### Step 1: Start the Agent (`main.py`)

Run the main agent script. It features an interactive setup wizard.

```bash
python main.py
```

  * **Input:** Enter the path of the folder you want to watch (e.g., `D:\My_Inbox`).
  * **Output:** Enter where you want the sorted files to go.
  * *The agent is now live and waiting for files.*

### Step 2: Generate Test Data (`grn.py`)

To test the system without manually finding files, open a **second terminal** and run the generator.

```bash
python grn.py
```

  * Enter the **same path** you provided in Step 1.
  * The script will instantly generate 10+ diverse files (Invoices, Resumes, NDAs, and Receipt Images).

### Step 3: Watch the Magic

Switch back to the Agent terminal. You will see it:

1.  Detect the new files.
2.  Analyze them (reading images via Vision, text via LLM).
3.  Move them to folders like `INVOICE`, `RESUME`, `CONTRACT`.
4.  Log the extracted expense data to `Financial_Report.csv`.

-----

## 🧠 Key Features (Course Concepts Applied)

  * **Multi-Modal Tools:** The agent seamlessly switches between text analysis and **Gemini Vision** depending on the file type (processing `.jpg` receipts vs `.txt` contracts).
  * **Observability:** Every action is logged to `Master_Log.csv`. Financial data is extracted to `Expense_Report.csv`, turning unstructured data into structured insights.
  * **Robust Error Handling:**
      * **Rate Limits:** Implements retry logic with sleep timers for `429 Resource Exhausted` errors.
      * **File Locking:** Uses `io.BytesIO` to load images into memory, preventing Windows `WinError 32` file lock crashes.
      * **Model Auto-Discovery:** Dynamically finds the best available Gemini model for the user's API key.
  * **Prototype to Production:** The code is modular, uses Type Hinting, logging, and separates configuration from logic.

-----

## 📊 Example Output

**Input File:** `scan_aws_bill.txt`

> **Content:** "Vendor: Amazon Web Services, Amount: $450.00, Date: 2025-12-01"

**Agent Action:**

1.  **Classifies** as `INVOICE`.
2.  **Renames** to `Invoice_AmazonWebServices_2025-12-01.txt`.
3.  **Moves** to `/Organized/INVOICE`.
4.  **Logs** `$450.00` to the CSV Expense Report.

-----

## 📜 License

This project is open-source under the MIT License. Created for the Kaggle AI Agents Intensive 2025.