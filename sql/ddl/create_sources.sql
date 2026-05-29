CREATE DATABASE IF NOT EXISTS ghanafi_db;

USE ghanafi_db;

CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    mobile_number VARCHAR(20) NOT NULL,
    network_operator VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender  VARCHAR(10) CHECK (gender IN ('Male', 'Female', 'Other')),
    ghana_card_number VARCHAR(20) NOT NULL,
    residential_address VARCHAR(255) NOT NULL,
    region VARCHAR(50) NOT NULL,
    occupation VARCHAR(100) NOT NULL,
    wallet_status VARCHAR(50) CHECK (wallet_status IN ('active', 'dormant', 'suspended', 'closed')) ,
    kyc_level VARCHAR(50) NOT NULL,
    kyc_status VARCHAR(50) CHECK (kyc_status IN ('pending', 'verified', 'rejected')),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    daily_limit DECIMAL(10, 2) NOT NULL,
    monthly_limit DECIMAL(10, 2) NOT NULL,
    wallet_balance DECIMAL(10, 2) NOT NULL,
    risk_rating VARCHAR(50) CHECK (risk_rating IN ('low', 'medium', 'high', 'critical')),
    fraud_flag BOOLEAN NOT NULL,
    last_transaction_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions(
    transaction_id VARCHAR(50) PRIMARY KEY,

    customer_id VARCHAR(50) NOT NULL,
    wallet_id VARCHAR(50),

    product_line VARCHAR(50) CHECK (product_line IN ('mobile_money', 'bill_payments', 'micro_loans')),
    transaction_type VARCHAR(50) NOT NULL,
    channel VARCHAR(30),
    provider VARCHAR(50),

    amount DECIMAL(18, 2) NOT NULL,
    fee_amount DECIMAL(18, 2) DEFAULT 0.00,
    tax_amount DECIMAL(18, 2) DEFAULT 0.00,
    total_debit_amount DECIMAL(18, 2) NOT NULL,
    currency CHAR(3) CHECK (currency IN ('GHS', 'USD', 'EUR')),

    status VARCHAR(30) CHECK (status IN ('success', 'failed', 'pending', 'reversed')),
    status_reason TEXT,

    reference VARCHAR(100),
    external_reference VARCHAR(100),
    narration TEXT,

    sender_msisdn VARCHAR(20),
    receiver_msisdn VARCHAR(20),
    receiver_name VARCHAR(150),
    sender_wallet_provider VARCHAR(50),
    receiver_wallet_provider VARCHAR(50),

    biller_id VARCHAR(50),
    biller_name VARCHAR(150),
    bill_category VARCHAR(50),
    account_number VARCHAR(100),
    meter_number VARCHAR(100),
    customer_bill_name VARCHAR(150),
    invoice_number VARCHAR(100),
    token TEXT,
    biller_response_code VARCHAR(20),
    biller_response_message TEXT,

    agent_id VARCHAR(50),
    agent_location VARCHAR(150),

    created_at TIMESTAMP NOT NULL,
    initiated_at TIMESTAMP,
    processed_at TIMESTAMP,
    completed_at TIMESTAMP,
    reversed_at TIMESTAMP,
    updated_at TIMESTAMP NOT NULL,

    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE loans (
    loan_id VARCHAR(50) PRIMARY KEY,

    customer_id VARCHAR(50) NOT NULL,
    wallet_id VARCHAR(50),
    application_id VARCHAR(50),

    loan_product VARCHAR(50) NOT NULL,
    provider VARCHAR(100),
    channel VARCHAR(30),

    principal_amount DECIMAL(18, 2) NOT NULL,
    interest_rate DECIMAL(7, 4) NOT NULL,
    interest_rate_type VARCHAR(30),
    interest_amount DECIMAL(18, 2) DEFAULT 0.00,
    processing_fee DECIMAL(18, 2) DEFAULT 0.00,
    penalty_amount DECIMAL(18, 2) DEFAULT 0.00,

    total_repayable_amount DECIMAL(18, 2) NOT NULL,
    amount_disbursed DECIMAL(18, 2) NOT NULL,
    amount_repaid DECIMAL(18, 2) DEFAULT 0.00,
    outstanding_balance DECIMAL(18, 2) NOT NULL,
    currency CHAR(3) DEFAULT 'GHS',

    loan_status VARCHAR(30) CHECK (loan_status IN ('pending', 'approved', 'disbursed', 'closed', 'rejected', 'defaulted')),
    repayment_status VARCHAR(30) CHECK (repayment_status IN ('on_track', 'late', 'defaulted', 'completed')),

    purpose VARCHAR(100),
    tenure_days INT,
    installment_count INT DEFAULT 1,
    repayment_frequency VARCHAR(30),

    next_repayment_date DATE,
    next_repayment_amount DECIMAL(18, 2),
    last_repayment_date DATE,
    last_repayment_amount DECIMAL(18, 2),
    days_past_due INT DEFAULT 0,
    missed_payments_count INT DEFAULT 0,

    auto_debit_enabled BOOLEAN DEFAULT FALSE,
    auto_debit_attempts INT DEFAULT 0,
    repayment_source VARCHAR(50),

    credit_score INT,
    risk_grade VARCHAR(20),
    loan_limit_at_application DECIMAL(18, 2),
    previous_loans_count INT DEFAULT 0,
    previous_defaults_count INT DEFAULT 0,

    disbursement_transaction_id VARCHAR(50),
    latest_repayment_transaction_id VARCHAR(50),

    approval_reason TEXT,
    rejection_reason TEXT,

    created_at TIMESTAMP NOT NULL,
    applied_at TIMESTAMP,
    approved_at TIMESTAMP,
    disbursed_at TIMESTAMP,
    due_date DATE NOT NULL,
    closed_at TIMESTAMP,
    updated_at TIMESTAMP NOT NULL,

    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (disbursement_transaction_id) REFERENCES transactions(transaction_id),
    FOREIGN KEY (latest_repayment_transaction_id) REFERENCES transactions(transaction_id)
);


CREATE TABLE app_events (
    event_id VARCHAR(50) PRIMARY KEY,

    customer_id VARCHAR(50) NOT NULL,
    session_id VARCHAR(100),
    device_id VARCHAR(100),

    event_name VARCHAR(100) NOT NULL,
    event_category VARCHAR(50),
    event_source VARCHAR(50) DEFAULT 'MOBILE_APP',
    screen_name VARCHAR(100),
    flow_name VARCHAR(100),

    product_line VARCHAR(50),
    transaction_id VARCHAR(50),
    loan_id VARCHAR(50),

    amount DECIMAL(18, 2),
    currency CHAR(3) DEFAULT 'GHS',

    recipient_msisdn VARCHAR(20),
    biller_id VARCHAR(50),
    merchant_id VARCHAR(50),
    reference VARCHAR(100),

    event_status VARCHAR(30),
    failure_reason TEXT,

    ip_address VARCHAR(45),
    location_city VARCHAR(100),
    location_region VARCHAR(100),
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),

    app_version VARCHAR(30),
    os_name VARCHAR(30),
    os_version VARCHAR(30),

    event_timestamp TIMESTAMP NOT NULL,
    ingested_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL,

    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
    FOREIGN KEY (loan_id) REFERENCES loans(loan_id)
);