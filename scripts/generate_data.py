"""
generate_data.py
Generates synthetic business document training data.
Output: data/business_docs.csv — 200 samples per category, 800 total.

Categories: Invoice, Contract, Report, Email
"""

import random
import csv
import os

random.seed(42)  # reproducible — same data every run

# ── Word pools ────────────────────────────────────────────────────────────────

COMPANIES = [
    "Brightstone Ltd", "Nexora Inc", "DataBridge LLC", "Pinnacle Solutions",
    "Vertex Corp", "Clearwave Technologies", "Ironside Consulting", "BluePeak Group",
    "Solaris Partners", "Crestfield Enterprises", "Quantum Dynamics", "Redwood Advisory",
    "Atlas Systems", "Meridian Global", "Halcyon Ventures", "Cobalt Digital",
    "Sterling Financial", "Apex Innovations", "Harbor Group", "Titan Services"
]

PEOPLE = [
    "James Anderson", "Sarah Mitchell", "David Chen", "Emily Carter",
    "Michael Torres", "Rachel Lee", "William Scott", "Jessica Patel",
    "Robert Kim", "Amanda Johnson", "Christopher Nguyen", "Laura Bennett",
    "Daniel Rivera", "Olivia Thompson", "Matthew Harris", "Sophia Williams"
]

SERVICES = [
    "software development", "consulting services", "marketing campaign",
    "legal advisory", "IT infrastructure", "data analysis", "graphic design",
    "financial audit", "project management", "cloud migration",
    "cybersecurity assessment", "training and development", "HR consulting",
    "content creation", "logistics management"
]

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

YEARS = ["2024", "2025", "2026"]
DEPARTMENTS = ["Finance", "Operations", "Marketing", "Sales", "Engineering", "HR", "Legal"]
QUARTERS = ["Q1", "Q2", "Q3", "Q4"]


def rand_company():    return random.choice(COMPANIES)
def rand_person():     return random.choice(PEOPLE)
def rand_service():    return random.choice(SERVICES)
def rand_amount():     return f"${random.randint(500, 50000):,}"
def rand_date():       return f"{random.randint(1,28)} {random.choice(MONTHS)} {random.choice(YEARS)}"
def rand_inv_num():    return f"INV-{random.randint(1000, 9999)}"
def rand_days():       return str(random.choice([7, 14, 21, 30, 45, 60]))
def rand_dept():       return random.choice(DEPARTMENTS)
def rand_quarter():    return random.choice(QUARTERS)
def rand_year():       return random.choice(YEARS)
def rand_pct():        return f"{random.randint(2, 35)}%"
def rand_large_amt():  return f"${random.randint(100000, 5000000):,}"


# ── Invoice templates ─────────────────────────────────────────────────────────

INVOICE_TEMPLATES = [
    "{inv} from {co1}. Date: {date}. Bill to: {co2}. Service: {svc}. Amount due: {amt}. Payment terms: net {days} days. Please remit payment to the address on file.",
    "Tax Invoice — {inv}. Issued by {co1} to {co2}. Description: {svc}. Total amount: {amt}. Due date: {date}. Late payments incur a 2% monthly fee.",
    "{co1} — Invoice {inv}. Dear {co2}, please find attached our invoice for {svc} rendered during {date}. Total payable: {amt} within {days} days.",
    "INVOICE {inv} | From: {co1} | To: {co2} | For: {svc} | Amount: {amt} | Due: {date} | Payment method: bank transfer or cheque.",
    "Billing statement from {co1}. Invoice number: {inv}. Client: {co2}. Professional services: {svc}. Subtotal: {amt}. Tax included. Payment due within {days} days of {date}.",
    "This invoice {inv} is issued by {co1} for services provided to {co2}. Service rendered: {svc}. Invoice date: {date}. Amount outstanding: {amt}. Kindly process at your earliest convenience.",
    "{co1} requests payment of {amt} from {co2} for {svc}. Reference: {inv}. Payment due by {date}. Bank details enclosed. Thank you for your business.",
    "Final invoice — {inv}. Provider: {co1}. Recipient: {co2}. Engagement: {svc}. Total fees: {amt}. Please settle by {date} to avoid late charges.",
    "BILL TO: {co2} | FROM: {co1} | INV#: {inv} | DATE: {date} | DESCRIPTION: {svc} | AMOUNT DUE: {amt} | TERMS: Net {days}.",
    "Invoice issued by {co1}. Invoice no: {inv}. Billing period ending {date}. Services: {svc} for {co2}. Total due: {amt}. Payment within {days} business days required.",
]


def make_invoice():
    t = random.choice(INVOICE_TEMPLATES)
    return t.format(
        inv=rand_inv_num(), co1=rand_company(), co2=rand_company(),
        svc=rand_service(), amt=rand_amount(), date=rand_date(), days=rand_days()
    )


# ── Contract templates ────────────────────────────────────────────────────────

CONTRACT_TEMPLATES = [
    "This agreement is entered into between {co1} and {co2} on {date}. The contractor agrees to provide {svc} for a period of {days} months. Both parties agree to the terms and conditions outlined herein.",
    "SERVICE AGREEMENT — {co1} (Service Provider) and {co2} (Client) hereby agree: 1. Scope of work: {svc}. 2. Commencement date: {date}. 3. Either party may terminate with 30 days written notice.",
    "This contract between {co1} and {co2} is effective as of {date}. {co1} shall deliver {svc} in accordance with the attached statement of work. Payment terms are as specified in Schedule A.",
    "MEMORANDUM OF UNDERSTANDING between {co1} and {co2}. Purpose: {svc}. This MOU is non-binding but represents the intent of both parties to collaborate from {date} onwards.",
    "Non-Disclosure Agreement: {co1} and {co2} agree to keep all confidential information related to {svc} strictly private. This agreement is effective {date} and remains in force for {days} years.",
    "Master Services Agreement — {co1} engages {co2} to perform {svc}. Deliverables, timelines, and compensation are defined in the accompanying Statement of Work dated {date}. Governing law: applicable jurisdiction.",
    "This binding contract is made on {date} between {co1} (hereafter 'the Company') and {co2} (hereafter 'the Vendor'). The Vendor will provide {svc}. Total contract value: {amt}. Penalties for breach apply.",
    "CONSULTING AGREEMENT: {co2} retains {co1} as an independent contractor for {svc} effective {date}. The consultant shall invoice monthly. Intellectual property created remains property of {co2}.",
    "Partnership Agreement between {co1} and {co2} dated {date}. Both parties agree to jointly deliver {svc} and share revenues equally. This agreement supersedes all prior oral or written agreements.",
    "Software License Agreement — {co1} grants {co2} a non-exclusive, non-transferable license to use the {svc} platform from {date}. Annual fee: {amt}. Unauthorised redistribution is strictly prohibited.",
]


def make_contract():
    t = random.choice(CONTRACT_TEMPLATES)
    return t.format(
        co1=rand_company(), co2=rand_company(), svc=rand_service(),
        date=rand_date(), days=random.randint(1, 24), amt=rand_amount()
    )


# ── Report templates ──────────────────────────────────────────────────────────

REPORT_TEMPLATES = [
    "{quarter} {year} {dept} Report — {co1}. Revenue increased by {pct} compared to the previous quarter. Operating costs totalled {amt}. Key highlight: successful rollout of {svc}. Outlook remains positive.",
    "Monthly Performance Report — {dept} Department, {co1}. Reporting period: {date}. Budget utilisation: {pct} of allocated {amt}. Ongoing initiatives include {svc}. No critical issues to report.",
    "EXECUTIVE SUMMARY — {year} Annual Report, {co1}. Total revenue: {amt}. Net profit margin: {pct}. The {dept} division outperformed targets. Strategic focus for next year: expansion of {svc}.",
    "Internal Audit Report — {co1} {dept}. Audit period: {quarter} {year}. Findings: financial controls are adequate. Expenditure on {svc}: {amt}. Recommendation: review vendor contracts by {date}.",
    "{co1} Quarterly Business Review — {quarter} {year}. Prepared by {dept}. Headcount grew by {pct}. Total spend: {amt}. Investment in {svc} continues to yield measurable returns.",
    "Risk Assessment Report — {co1}. Date: {date}. Department: {dept}. Three key risks identified in {svc} operations. Mitigation budget approved: {amt}. Risk exposure reduced by {pct} year-on-year.",
    "Financial Performance Summary — {co1} — {quarter} {year}. Gross profit: {amt}. Year-over-year growth: {pct}. The {dept} team exceeded KPIs. Continued investment in {svc} recommended.",
    "Project Status Report — {co1}. Project: {svc}. Reporting period: {date}. Budget consumed: {amt} of total allocation. Timeline: on track. {dept} team capacity at {pct} utilisation.",
    "{year} Market Analysis Report — {co1}. Sector: {dept}. Market share increased by {pct}. Competitive landscape remains challenging. Revenue from {svc}: {amt}. Full report available on request.",
    "Board Report — {co1} — {date}. Prepared by: {dept} division. Key metrics: revenue {amt}, growth {pct}. Major decisions this period: investment in {svc} approved. Next review: {quarter} {year}.",
]


def make_report():
    t = random.choice(REPORT_TEMPLATES)
    return t.format(
        co1=rand_company(), dept=rand_dept(), quarter=rand_quarter(),
        year=rand_year(), date=rand_date(), amt=rand_large_amt(),
        pct=rand_pct(), svc=rand_service()
    )


# ── Email templates ───────────────────────────────────────────────────────────

EMAIL_TEMPLATES = [
    "Hi {p2}, I wanted to follow up on our conversation about {svc}. Could you please confirm availability for a call this week? I'm flexible on timing. Best regards, {p1}.",
    "Dear {p2}, thank you for meeting with us yesterday. As discussed, we will proceed with {svc}. Please review the attached proposal and let us know your thoughts. Kind regards, {p1} — {co1}.",
    "Hello {p2}, just a quick note to check in on the {svc} project. We're on track for the {date} deadline but will need your sign-off by end of week. Thanks, {p1}.",
    "Hi team, please be advised that the {svc} meeting originally scheduled for {date} has been moved. New details to follow. Apologies for any inconvenience. Regards, {p1}, {dept}.",
    "Dear {p2}, I hope this email finds you well. I'm reaching out on behalf of {co1} regarding {svc}. We believe there's a strong opportunity to collaborate. Would you be open to a brief call? {p1}.",
    "Hi {p2}, following up on the proposal sent last week. We haven't heard back yet and wanted to ensure it reached you. Please don't hesitate to reach out with any questions. Cheers, {p1} — {co1}.",
    "Good morning {p2}, your request for {svc} has been received and assigned to our {dept} team. Expected completion by {date}. We'll keep you updated throughout. Best, {p1}.",
    "Hi {p2}, as per our earlier discussion, please find the {svc} documentation attached. Let me know if revisions are needed before {date}. Always happy to help. Warm regards, {p1}, {co1}.",
    "Dear {p2}, this is a reminder that the {svc} deadline is approaching on {date}. Please ensure all required materials are submitted to the {dept} team. Thank you. {p1}.",
    "Hey {p2}, quick update — the {dept} team has completed the initial phase of {svc}. Everything looks good so far. Will send a full summary by {date}. Let me know if you have questions. {p1}.",
]


def make_email():
    t = random.choice(EMAIL_TEMPLATES)
    return t.format(
        p1=rand_person(), p2=rand_person(), co1=rand_company(),
        svc=rand_service(), date=rand_date(), dept=rand_dept()
    )


# ── Main generator ────────────────────────────────────────────────────────────

def generate_dataset(samples_per_class=200):
    generators = {
        "Invoice":  make_invoice,
        "Contract": make_contract,
        "Report":   make_report,
        "Email":    make_email,
    }

    rows = []
    for label, fn in generators.items():
        for _ in range(samples_per_class):
            rows.append({"text": fn(), "label": label})

    # Shuffle so classes aren't all grouped together
    random.shuffle(rows)
    return rows


def save_csv(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    output_path = os.path.join(os.path.dirname(__file__), "../data/business_docs.csv")
    output_path = os.path.normpath(output_path)

    print("Generating dataset...")
    rows = generate_dataset(samples_per_class=200)
    save_csv(rows, output_path)

    # Summary
    from collections import Counter
    counts = Counter(r["label"] for r in rows)
    print(f"Saved {len(rows)} samples to {output_path}")
    print()
    for label, count in sorted(counts.items()):
        print(f"  {label:<12} {count} samples")
    print()
    print("Sample from each category:")
    seen = set()
    for row in rows:
        if row["label"] not in seen:
            print(f"\n[{row['label']}]\n{row['text']}")
            seen.add(row["label"])
        if len(seen) == 4:
            break
