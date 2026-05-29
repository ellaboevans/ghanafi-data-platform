from faker import Faker
from datetime import date, timedelta, datetime
from pathlib import Path
import random
import sys

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


import logging
logger = logging.getLogger(__name__)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import CONFIG


fake = Faker()

user = CONFIG["database"]["user"]
password = CONFIG["database"]["password"]
host = CONFIG["database"]["host"]
dbname = CONFIG["database"]["dbname"]
port = CONFIG["database"]["port"]

engine = create_engine(
    f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"
)

# Ghana-specific names
gh_full_names = [
    "Evans Elabo", "Kwame Mensah", "Ama Boateng", "Kofi Asare", "Abena Osei",
    "Yaw Frimpong", "Akua Serwaa", "Kojo Appiah", "Efua Nyarko", "Nana Adjei",
    "Esi Owusu", "Kwesi Agyeman", "Afia Darko", "Kwaku Ansah", "Adwoa Amponsah",
    "Selorm Agbeko", "Dzifa Mensah", "Fiifi Quansah", "Maame Gyamfi", "Kojo Baah",
    "Akosua Sarpong", "Yaw Boakye", "Abigail Tetteh", "Prince Addo", "Linda Aidoo",
    "Emmanuel Nartey", "Mavis Donkor", "Samuel Antwi", "Grace Asiedu", "Daniel Opoku",
    "Patricia Arthur", "Isaac Bediako", "Priscilla Dapaah", "Joseph Annan",
    "Comfort Yeboah", "Francis Kumah", "Theresa Ababio", "Michael Teye",
    "Gifty Boadu", "Richard Ofori", "Bernice Awuah", "Stephen Agyei",
    "Doreen Amankwah", "Peter Koomson", "Cynthia Agyapong", "Ernestina Larbi",
    "David Danso", "Felicia Konadu", "George Amoako", "Beatrice Tawiah"
]

ghana_regions = [
    "Ahafo",
    "Ashanti",
    "Bono",
    "Bono East",
    "Central",
    "Eastern",
    "Greater Accra",
    "North East",
    "Northern",
    "Oti",
    "Savannah",
    "Upper East",
    "Upper West",
    "Volta",
    "Western",
    "Western North"
]

occupations = [
    "Trader",
    "Student",
    "Farmer",
    "Teacher",
    "Nurse",
    "Driver",
    "Civil Servant",
    "Mobile Money Agent",
    "Shop Owner",
    "Hairdresser",
    "Mechanic",
    "Banker",
    "Security Officer",
    "Seamstress",
    "Unemployed",
    "Software Developer"
]

def random_date(start_year, end_year):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta_days = (end - start).days
    return start + timedelta(days=random.randint(0, delta_days))


def weighted_choice(options):
    values = list(options.keys())
    weights = list(options.values())
    return random.choices(values, weights=weights, k=1)[0]


def generate_ghana_phone(existing_numbers):
    """
    Generates unique fake Ghana phone numbers in +233 format.
    Example: +233241234567
    """
    prefixes = ["24", "54", "55", "59", "20", "50", "27", "57"]

    while True:
        prefix = random.choice(prefixes)
        number = fake.random_number(digits=7, fix_len=True)
        mobile_number = f"+233{prefix}{number}"

        if mobile_number not in existing_numbers:
            existing_numbers.add(mobile_number)
            return mobile_number


def get_network_operator(mobile_number):
    """
    Extracts the two-digit Ghana mobile prefix after +233.
    Example: +233541234567 -> 54
    """
    prefix = mobile_number[4:6]

    if prefix in ["24", "54", "55", "59"]:
        return "MTN"
    elif prefix in ["20", "50"]:
        return "Telecel"
    elif prefix in ["27", "57"]:
        return "AirtelTigo"
    else:
        return "Unknown"


def generate_ghana_card_number(existing_cards):
    """
    Generates unique fake Ghana Card numbers.
    Example: GHA-123456789-1
    """
    while True:
        number = random.randint(100000000, 999999999)
        suffix = random.randint(0, 9)
        ghana_card_number = f"GHA-{number}-{suffix}"

        if ghana_card_number not in existing_cards:
            existing_cards.add(ghana_card_number)
            return ghana_card_number


def generate_residential_address():
    areas = [
        "East Legon", "Madina", "Adenta", "Osu", "Dansoman",
        "Asokwa", "Bantama", "Tafo", "Koforidua", "Cape Coast",
        "Takoradi", "Tamale", "Bolgatanga", "Ho", "Sunyani",
        "Wa", "Techiman", "Dambai", "Goaso", "Sefwi Wiawso"
    ]

    streets = [
        "High Street",
        "Market Road",
        "Station Road",
        "Hospital Road",
        "School Lane",
        "Ring Road",
        "Independence Avenue",
        "Mission Street"
    ]

    house_number = random.randint(1, 999)

    return f"House No. {house_number}, {random.choice(streets)}, {random.choice(areas)}"


def get_limits_for_kyc_level(kyc_level):
    if kyc_level == "basic":
        return 1000.00, 6000.00

    if kyc_level == "standard":
        return 5000.00, 30000.00

    if kyc_level == "enhanced":
        return 20000.00, 100000.00

    return 1000.00, 6000.00


def generate_customers(n=1000):
    customers = []

    existing_numbers = set()
    existing_cards = set()

    gender_weights = {
        "Male": 0.49,
        "Female": 0.49,
        "Other": 0.02
    }

    kyc_status_weights = {
        "verified": 0.82,
        "pending": 0.13,
        "rejected": 0.05
    }

    wallet_status_weights = {
        "active": 0.78,
        "dormant": 0.13,
        "suspended": 0.06,
        "closed": 0.03
    }

    risk_rating_weights = {
        "low": 0.58,
        "medium": 0.30,
        "high": 0.10,
        "critical": 0.02
    }

    kyc_level_weights = {
        "basic": 0.20,
        "standard": 0.35,
        "enhanced": 0.45
    }

    fraud_flag_weights = {
        0: 0.96,
        1: 0.04
    }
    
    region_weights = {
    "Greater Accra": 0.25,  # most populous
    "Ashanti":       0.20,
    "Central":       0.07,
    "Eastern":       0.07,
    "Western":       0.06,
    "Northern":      0.06,
    "Volta":         0.05,
    "Bono":          0.04,
    "Upper East":    0.04,
    "Upper West":    0.03,
    "Western North": 0.03,
    "Ahafo":         0.02,
    "Bono East":     0.02,
    "Savannah":      0.02,
    "North East":    0.02,
    "Oti":           0.02,
}

    for i in range(1, n + 1):
        mobile_number = generate_ghana_phone(existing_numbers)
        network_operator = get_network_operator(mobile_number)

        kyc_level = weighted_choice(kyc_level_weights)
        daily_limit, monthly_limit = get_limits_for_kyc_level(kyc_level)

        customer = {
            "customer_id": f"CUS{i:06d}",
            "full_name": fake.random_element(gh_full_names),
            "mobile_number": mobile_number,
            "network_operator": network_operator,
            "date_of_birth": random_date(1960, 2007).isoformat(),
            "gender": weighted_choice(gender_weights),
            "ghana_card_number": generate_ghana_card_number(existing_cards),
            "residential_address": generate_residential_address(),
            "region": weighted_choice(region_weights),
            "occupation": fake.random_element(occupations),
            "wallet_status": weighted_choice(wallet_status_weights),
            "kyc_level": kyc_level,
            "kyc_status": weighted_choice(kyc_status_weights),
            "registration_date": random_date(2018, 2025).isoformat(),
            "daily_limit": daily_limit,
            "monthly_limit": monthly_limit,
            "wallet_balance": round(random.uniform(0, daily_limit), 2),
            "risk_rating": weighted_choice(risk_rating_weights),
            "fraud_flag": weighted_choice(fraud_flag_weights),
            "last_transaction_date": None
        }

        customers.append(customer)

    fake.unique.clear()
    return customers


def random_datetime_last_12_months():
    end = datetime.now()
    start = end - timedelta(days=365)
    delta_seconds = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, delta_seconds))

def add_random_days(base_datetime, min_days=1, max_days=30):
    return base_datetime + timedelta(days=random.randint(min_days, max_days))


def random_future_seconds(base_time, min_seconds=1, max_seconds=60):
    return base_time + timedelta(seconds=random.randint(min_seconds, max_seconds))


def get_amount_for_product_line(product_line):
    if product_line == "mobile_money":
        return round(random.uniform(1, 5000), 2)

    if product_line == "bill_payments":
        return round(random.uniform(10, 500), 2)

    if product_line == "micro_loans":
        return round(random.uniform(500, 5000), 2)

    return round(random.uniform(1, 500), 2)


def get_transaction_type(product_line):
    if product_line == "mobile_money":
        return random.choice(["send_money", "cash_in", "cash_out", "merchant_payment"])

    if product_line == "bill_payments":
        return random.choice(["utility_payment", "tv_subscription", "school_fees", "insurance_payment"])

    if product_line == "micro_loans":
        return "loan_disbursement"

    return "general_transaction"


def get_fee_amount(product_line, amount):
    if product_line == "mobile_money":
        return round(min(amount * random.uniform(0.005, 0.015), 50), 2)

    if product_line == "bill_payments":
        return round(random.uniform(0, 5), 2)

    if product_line == "micro_loans":
        return 0.00

    return 0.00


def get_tax_amount(product_line, amount):
    if product_line == "mobile_money":
        return round(amount * random.uniform(0, 0.01), 2)

    return 0.00


def generate_fake_msisdn():
    prefixes = ["24", "54", "55", "59", "20", "50", "27", "57"]
    return f"+233{random.choice(prefixes)}{random.randint(1000000, 9999999)}"


def get_provider_from_msisdn(msisdn):
    prefix = msisdn[4:6]

    if prefix in ["24", "54", "55", "59"]:
        return "MTN"
    elif prefix in ["20", "50"]:
        return "Telecel"
    elif prefix in ["27", "57"]:
        return "AirtelTigo"
    else:
        return "Unknown"


def get_biller_details():
    billers = [
        {
            "biller_id": "ECG",
            "biller_name": "Electricity Company of Ghana",
            "bill_category": "utilities"
        },
        {
            "biller_id": "GWCL",
            "biller_name": "Ghana Water Company Limited",
            "bill_category": "utilities"
        },
        {
            "biller_id": "DSTV",
            "biller_name": "DStv Ghana",
            "bill_category": "tv_subscription"
        },
        {
            "biller_id": "GOTV",
            "biller_name": "GOtv Ghana",
            "bill_category": "tv_subscription"
        },
        {
            "biller_id": "SCHOOLPAY",
            "biller_name": "School Fees Payment",
            "bill_category": "school_fees"
        }
    ]

    return random.choice(billers)


def generate_transactions(n=10000):
    transactions = []

    customer_df = pd.read_sql(
        "SELECT customer_id, full_name, mobile_number, network_operator FROM customers",
        engine
    )

    if customer_df.empty:
        raise ValueError("No customers found in database. Insert customers before generating transactions.")

    customers = customer_df.to_dict("records")

    transaction_status_weights = {
        "success": 0.85,
        "failed": 0.10,
        "pending": 0.04,
        "reversed": 0.01
    }

    product_line_weights = {
        "mobile_money": 0.70,
        "bill_payments": 0.20,
        "micro_loans": 0.10
    }

    channels = ["USSD", "Mobile App", "Agent", "Web"]
    providers = ["MTN", "Telecel", "AirtelTigo"]

    for i in range(1, n + 1):
        customer = random.choice(customers)

        product_line = weighted_choice(product_line_weights)
        transaction_type = get_transaction_type(product_line)
        amount = get_amount_for_product_line(product_line)
        fee_amount = get_fee_amount(product_line, amount)
        tax_amount = get_tax_amount(product_line, amount)

        if transaction_type == "loan_disbursement":
            total_debit_amount = amount
        else:
            total_debit_amount = round(amount + fee_amount + tax_amount, 2)

        status = weighted_choice(transaction_status_weights)

        created_at = random_datetime_last_12_months()
        initiated_at = random_future_seconds(created_at, 1, 20)
        processed_at = random_future_seconds(initiated_at, 1, 40)

        if status in ["success", "failed", "reversed"]:
            completed_at = random_future_seconds(processed_at, 1, 60)
        else:
            completed_at = None

        if status == "reversed":
            reversed_at = random_future_seconds(completed_at, 60, 86400)
        else:
            reversed_at = None

        updated_at = reversed_at or completed_at or processed_at

        if status == "success":
            status_reason = None
        elif status == "failed":
            status_reason = random.choice([
                "insufficient_balance",
                "network_timeout",
                "invalid_recipient",
                "provider_declined"
            ])
        elif status == "pending":
            status_reason = "awaiting_provider_confirmation"
        else:
            status_reason = "customer_reversal_or_provider_reversal"

        sender_msisdn = None
        receiver_msisdn = None
        receiver_name = None
        sender_wallet_provider = None
        receiver_wallet_provider = None

        biller_id = None
        biller_name = None
        bill_category = None
        account_number = None
        meter_number = None
        customer_bill_name = None
        invoice_number = None
        token = None
        biller_response_code = None
        biller_response_message = None

        agent_id = None
        agent_location = None

        if product_line == "mobile_money":
            sender_msisdn = customer["mobile_number"]
            receiver_msisdn = generate_fake_msisdn()
            receiver_name = fake.random_element(gh_full_names)
            sender_wallet_provider = customer["network_operator"]
            receiver_wallet_provider = get_provider_from_msisdn(receiver_msisdn)

            if transaction_type in ["cash_in", "cash_out"]:
                agent_id = f"AGT{random.randint(1, 99999):05d}"
                agent_location = random.choice([
                    "Madina, Accra",
                    "Kejetia, Kumasi",
                    "Market Circle, Takoradi",
                    "Tamale Central",
                    "Ho Central",
                    "Cape Coast"
                ])

        elif product_line == "bill_payments":
            biller = get_biller_details()
            biller_id = biller["biller_id"]
            biller_name = biller["biller_name"]
            bill_category = biller["bill_category"]
            account_number = f"ACC{random.randint(10000000, 99999999)}"
            customer_bill_name = customer["full_name"]
            invoice_number = f"INV{random.randint(100000, 999999)}"
            biller_response_code = "00" if status == "success" else "99"
            biller_response_message = "Approved" if status == "success" else "Failed"

            if biller_id == "ECG":
                meter_number = f"MTR{random.randint(100000000, 999999999)}"
                token = f"{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"

        elif product_line == "micro_loans":
            sender_msisdn = "GhanaFi"
            receiver_msisdn = customer["mobile_number"]
            receiver_name = customer["full_name"]
            receiver_wallet_provider = customer["network_operator"]

        transaction = {
            "transaction_id": f"TXN{i:08d}",
            "customer_id": customer["customer_id"],
            "wallet_id": f"WAL{random.randint(1, 500):05d}",

            "product_line": product_line,
            "transaction_type": transaction_type,
            "channel": random.choice(channels),
            "provider": random.choice(providers),

            "amount": amount,
            "fee_amount": fee_amount,
            "tax_amount": tax_amount,
            "total_debit_amount": total_debit_amount,
            "currency": "GHS",

            "status": status,
            "status_reason": status_reason,
            "reference": f"REF-{fake.uuid4()}",
            "external_reference": f"EXT-{fake.uuid4()}",
            "narration": f"{transaction_type.replace('_', ' ').title()} via {product_line}",

            "sender_msisdn": sender_msisdn,
            "receiver_msisdn": receiver_msisdn,
            "receiver_name": receiver_name,
            "sender_wallet_provider": sender_wallet_provider,
            "receiver_wallet_provider": receiver_wallet_provider,

            "biller_id": biller_id,
            "biller_name": biller_name,
            "bill_category": bill_category,
            "account_number": account_number,
            "meter_number": meter_number,
            "customer_bill_name": customer_bill_name,
            "invoice_number": invoice_number,
            "token": token,
            "biller_response_code": biller_response_code,
            "biller_response_message": biller_response_message,

            "agent_id": agent_id,
            "agent_location": agent_location,

            "created_at": created_at,
            "initiated_at": initiated_at,
            "processed_at": processed_at,
            "completed_at": completed_at,
            "reversed_at": reversed_at,
            "updated_at": updated_at
        }

        transactions.append(transaction)

    return transactions

def update_customer_last_transaction_dates(engine):
    print("Updating customers.last_transaction_date...")

    update_sql = text("""
        UPDATE customers c
        JOIN (
            SELECT
                customer_id,
                MAX(created_at) AS latest_transaction_date
            FROM transactions
            GROUP BY customer_id
        ) t
            ON c.customer_id = t.customer_id
        SET c.last_transaction_date = t.latest_transaction_date
    """)

    try:
        with engine.begin() as conn:
            result = conn.execute(update_sql)

        print("customers.last_transaction_date updated successfully.")
        print(f"Rows affected: {result.rowcount}")
        return True

    except SQLAlchemyError as e:
        print("Failed to update customers.last_transaction_date.")
        print(f"Error type: {type(e).__name__}")
        print(f"Error: {e}")
        return False

def generate_loans(n=500):
    loans = []

    customer_df = pd.read_sql(
        """
        SELECT customer_id, wallet_balance, risk_rating
        FROM customers
        """,
        engine
    )

    if customer_df.empty:
        raise ValueError("No customers found. Insert customers before generating loans.")

    customers = customer_df.to_dict("records")

    disbursement_txn_df = pd.read_sql(
        """
        SELECT transaction_id, customer_id, amount, created_at
        FROM transactions
        WHERE product_line = 'micro_loans'
          AND status = 'success'
        """,
        engine
    )

    disbursement_transactions = disbursement_txn_df.to_dict("records")

    loan_status_weights = {
        "disbursed": 0.45,
        "closed": 0.22,
        "approved": 0.10,
        "pending": 0.08,
        "rejected": 0.05,
        "defaulted": 0.10
    }

    purposes = [
        "Business",
        "School fees",
        "Medical expenses",
        "Household needs",
        "Emergency",
        "Inventory purchase",
        "Transport",
        "Rent",
        "Utility payment"
    ]

    providers = [
        "GhanaFi Micro Loans",
        "QwikLoan",
        "XpressLoan",
        "MomoAdvance"
    ]

    channels = ["USSD", "Mobile App", "Agent"]

    repayment_sources = [
        "MOMO_WALLET",
        "AUTO_DEBIT",
        "AGENT_CASH",
        "BANK_TRANSFER"
    ]

    risk_grade_map = {
        "low": "A",
        "medium": "B",
        "high": "C",
        "critical": "D"
    }

    used_disbursement_ids = set()

    for i in range(1, n + 1):
        linked_disbursement = None

        # Link some loans to real micro_loan transactions where available.
        # 60% of loans try to use an existing transaction_id.
        if disbursement_transactions and random.random() < 0.60:
            available_txns = [
                txn for txn in disbursement_transactions
                if txn["transaction_id"] not in used_disbursement_ids
            ]

            if available_txns:
                linked_disbursement = random.choice(available_txns)
                used_disbursement_ids.add(linked_disbursement["transaction_id"])

        if linked_disbursement:
            customer_id = linked_disbursement["customer_id"]
            principal_amount = round(float(linked_disbursement["amount"]), 2)
            created_at = linked_disbursement["created_at"]

            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)
        else:
            customer = random.choice(customers)
            customer_id = customer["customer_id"]
            principal_amount = round(random.uniform(500, 5000), 2)
            created_at = random_datetime_last_12_months()

        customer_match = customer_df[customer_df["customer_id"] == customer_id]

        if not customer_match.empty:
            risk_rating = customer_match.iloc[0]["risk_rating"]
        else:
            risk_rating = random.choice(["low", "medium", "high", "critical"])

        loan_status = weighted_choice(loan_status_weights)

        interest_rate = round(random.uniform(3.5, 12.5), 4)
        interest_rate_type = "flat"
        interest_amount = round(principal_amount * (interest_rate / 100), 2)
        processing_fee = round(principal_amount * random.uniform(0.005, 0.02), 2)

        tenure_days = random.choice([14, 30, 60, 90])
        installment_count = random.choice([1, 2, 3])
        repayment_frequency = "one_time" if installment_count == 1 else random.choice(["weekly", "monthly"])

        applied_at = created_at
        approved_at = None
        disbursed_at = None
        closed_at = None

        approval_reason = None
        rejection_reason = None

        if loan_status == "pending":
            repayment_status = "on_track"
            approved_at = None
            disbursed_at = None
            approval_reason = None
            rejection_reason = None

            amount_disbursed = 0.00
            penalty_amount = 0.00
            total_repayable_amount = round(principal_amount + interest_amount + processing_fee, 2)
            amount_repaid = 0.00
            outstanding_balance = total_repayable_amount

        elif loan_status == "rejected":
            repayment_status = "on_track"
            approved_at = add_random_days(applied_at, 0, 1)
            disbursed_at = None
            approval_reason = None
            rejection_reason = random.choice([
                "low_credit_score",
                "high_risk_profile",
                "failed_kyc_validation",
                "existing_unpaid_loan"
            ])

            amount_disbursed = 0.00
            penalty_amount = 0.00
            total_repayable_amount = 0.00
            amount_repaid = 0.00
            outstanding_balance = 0.00

        else:
            approved_at = add_random_days(applied_at, 0, 1)
            disbursed_at = add_random_days(approved_at, 0, 1)
            approval_reason = "eligible_customer"
            rejection_reason = None

            amount_disbursed = principal_amount
            due_date = (disbursed_at + timedelta(days=tenure_days)).date()

            if loan_status == "closed":
                repayment_status = "completed"
                penalty_amount = 0.00
                total_repayable_amount = round(principal_amount + interest_amount + processing_fee, 2)
                amount_repaid = total_repayable_amount
                outstanding_balance = 0.00
                closed_at = add_random_days(disbursed_at, tenure_days, tenure_days + 20)

            elif loan_status == "defaulted":
                repayment_status = "defaulted"
                days_past_due_value = random.randint(31, 180)
                penalty_amount = round(principal_amount * random.uniform(0.03, 0.15), 2)
                total_repayable_amount = round(
                    principal_amount + interest_amount + processing_fee + penalty_amount,
                    2
                )
                amount_repaid = round(random.uniform(0, total_repayable_amount * 0.40), 2)
                outstanding_balance = round(total_repayable_amount - amount_repaid, 2)

            elif loan_status == "disbursed":
                today = datetime.now().date()
                total_repayable_amount = round(principal_amount + interest_amount + processing_fee, 2)

                if due_date < today and random.random() < 0.35:
                    repayment_status = "late"
                    days_past_due_value = (today - due_date).days
                    penalty_amount = round(principal_amount * random.uniform(0.01, 0.05), 2)
                    total_repayable_amount = round(total_repayable_amount + penalty_amount, 2)
                    amount_repaid = round(random.uniform(0, total_repayable_amount * 0.70), 2)
                    outstanding_balance = round(total_repayable_amount - amount_repaid, 2)

                else:
                    repayment_status = "on_track"
                    penalty_amount = 0.00
                    amount_repaid = round(random.uniform(0, total_repayable_amount * 0.60), 2)
                    outstanding_balance = round(total_repayable_amount - amount_repaid, 2)

            elif loan_status == "approved":
                repayment_status = "on_track"
                penalty_amount = 0.00
                total_repayable_amount = round(principal_amount + interest_amount + processing_fee, 2)
                amount_repaid = 0.00
                outstanding_balance = total_repayable_amount

        # Ensure due_date exists for all rows because your table requires it.
        if loan_status in ["pending", "rejected"]:
            due_date = (created_at + timedelta(days=tenure_days)).date()

        if repayment_status == "late":
            days_past_due = random.randint(1, 60)
            missed_payments_count = random.randint(1, 3)
        elif repayment_status == "defaulted":
            days_past_due = random.randint(61, 180)
            missed_payments_count = random.randint(2, 6)
        else:
            days_past_due = 0
            missed_payments_count = 0

        if amount_repaid > 0:
            last_repayment_date = fake.date_between(
                start_date=created_at.date(),
                end_date=datetime.now().date()
            )
            last_repayment_amount = round(min(amount_repaid, random.uniform(50, 1000)), 2)
        else:
            last_repayment_date = None
            last_repayment_amount = None

        if repayment_status in ["completed", "defaulted"]:
            next_repayment_date = None
            next_repayment_amount = None
        else:
            next_repayment_date = due_date
            next_repayment_amount = round(outstanding_balance, 2)

        if closed_at:
            updated_at = closed_at
        else:
            updated_at = datetime.now()

        if risk_rating == "low":
            credit_score = random.randint(700, 850)
        elif risk_rating == "medium":
            credit_score = random.randint(600, 699)
        elif risk_rating == "high":
            credit_score = random.randint(500, 599)
        else:
            credit_score = random.randint(300, 499)

        previous_loans_count = random.randint(0, 8)
        previous_defaults_count = 0

        if risk_rating in ["high", "critical"]:
            previous_defaults_count = random.randint(0, 3)

        loan_limit_at_application = round(random.uniform(principal_amount, 10000), 2)

        loan = {
            "loan_id": f"LN{i:08d}",
            "customer_id": customer_id,
            "wallet_id": f"WAL{random.randint(1, 500):05d}",
            "application_id": f"APP{i:08d}",

            "loan_product": "momo_micro_loan",
            "provider": random.choice(providers),
            "channel": random.choice(channels),

            "principal_amount": principal_amount,
            "interest_rate": interest_rate,
            "interest_rate_type": interest_rate_type,
            "interest_amount": interest_amount,
            "processing_fee": processing_fee,
            "penalty_amount": penalty_amount,

            "total_repayable_amount": total_repayable_amount,
            "amount_disbursed": amount_disbursed,
            "amount_repaid": amount_repaid,
            "outstanding_balance": outstanding_balance,
            "currency": "GHS",

            "loan_status": loan_status,
            "repayment_status": repayment_status,
            "purpose": random.choice(purposes),
            "tenure_days": tenure_days,
            "installment_count": installment_count,
            "repayment_frequency": repayment_frequency,

            "next_repayment_date": next_repayment_date,
            "next_repayment_amount": next_repayment_amount,
            "last_repayment_date": last_repayment_date,
            "last_repayment_amount": last_repayment_amount,
            "days_past_due": days_past_due,
            "missed_payments_count": missed_payments_count,

            "auto_debit_enabled": weighted_choice({
                1: 0.70,
                0: 0.30
            }),
            "auto_debit_attempts": random.randint(0, 5),
            "repayment_source": random.choice(repayment_sources),

            "credit_score": credit_score,
            "risk_grade": risk_grade_map.get(risk_rating, "B"),
            "loan_limit_at_application": loan_limit_at_application,
            "previous_loans_count": previous_loans_count,
            "previous_defaults_count": previous_defaults_count,

            "disbursement_transaction_id": (
                linked_disbursement["transaction_id"]
                if linked_disbursement
                else None
            ),
            "latest_repayment_transaction_id": None,

            "approval_reason": approval_reason,
            "rejection_reason": rejection_reason,

            "created_at": created_at,
            "applied_at": applied_at,
            "approved_at": approved_at,
            "disbursed_at": disbursed_at,
            "due_date": due_date,
            "closed_at": closed_at,
            "updated_at": updated_at
        }

        loans.append(loan)

    return loans
   
def insert_dataframe_in_chunks(df, table_name, engine, chunk_size=1000):
    total_rows = len(df)
    inserted_rows = 0

    print(f"Starting insert into `{table_name}`...")
    print(f"Total rows: {total_rows}")
    print(f"Chunk size: {chunk_size}")

    for start in range(0, total_rows, chunk_size):
        end = min(start + chunk_size, total_rows)
        chunk = df.iloc[start:end]

        try:
            chunk.to_sql(
                table_name,
                engine,
                if_exists="append",
                index=False
            )

            inserted_rows += len(chunk)
            print(f"Inserted rows {start + 1}-{end} ({inserted_rows}/{total_rows})")

        except SQLAlchemyError as e:
            print(f"\nFailed inserting rows {start + 1}-{end}")
            print(f"Error type: {type(e).__name__}")
            print(f"Error: {e}")
            print("\nFailed chunk columns:")
            print(chunk.columns.tolist())
            print("\nFailed chunk preview:")
            print(chunk.head())
            return False

        except Exception as e:
            print(f"\nUnexpected error inserting rows {start + 1}-{end}")
            print(f"Error type: {type(e).__name__}")
            print(f"Error: {e}")
            print("\nFailed chunk preview:")
            print(chunk.head())
            return False

    print(f"Successfully inserted {inserted_rows}/{total_rows} rows into `{table_name}`.")
    return True


if __name__ == "__main__":
    try:
        print("Generating loans...")
        loans = generate_loans(500)
        loans_df = pd.DataFrame(loans)

        print("Generated loans DataFrame.")
        print(f"Shape: {loans_df.shape}")
        print("Columns:")
        print(loans_df.columns.tolist())

        print("\nSample rows:")
        print(loans_df.head())

        success = insert_dataframe_in_chunks(
            df=loans_df,
            table_name="loans",
            engine=engine,
            chunk_size=100
        )

        if success:
            print("Loan generation and insert completed successfully.")
        else:
            print("Loan insert failed. Fix the issue above and rerun.")

    except Exception as e:
        print("Fatal error in loan generation script.")
        print(f"Error type: {type(e).__name__}")
        print(f"Error: {e}")