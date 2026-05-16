CREATE SCHEMA IF NOT EXISTS fraud_demo OPTIONS(location="US");

LOAD DATA OVERWRITE fraud_demo.customers FROM FILES ( format = 'CSV', uris = ['gs://sample-data-and-media/fraud-demo-data/customers.csv'], skip_leading_rows = 1 );
LOAD DATA OVERWRITE fraud_demo.emails FROM FILES ( format = 'CSV', uris = ['gs://sample-data-and-media/fraud-demo-data/emails.csv'], skip_leading_rows = 1 );
LOAD DATA OVERWRITE fraud_demo.phones FROM FILES ( format = 'CSV', uris = ['gs://sample-data-and-media/fraud-demo-data/phones.csv'], skip_leading_rows = 1 );
LOAD DATA OVERWRITE fraud_demo.addresses FROM FILES ( format = 'CSV', uris = ['gs://sample-data-and-media/fraud-demo-data/addresses.csv'], skip_leading_rows = 1 );
LOAD DATA OVERWRITE fraud_demo.customer_emails FROM FILES ( format = 'CSV', uris = ['gs://sample-data-and-media/fraud-demo-data/customer_emails.csv'], skip_leading_rows = 1 );
LOAD DATA OVERWRITE fraud_demo.customer_phones FROM FILES ( format = 'CSV', uris = ['gs://sample-data-and-media/fraud-demo-data/customer_phones.csv'], skip_leading_rows = 1 );
LOAD DATA OVERWRITE fraud_demo.customer_addresses FROM FILES ( format = 'CSV', uris = ['gs://sample-data-and-media/fraud-demo-data/customer_addresses.csv'], skip_leading_rows = 1 );
LOAD DATA OVERWRITE fraud_demo.orders FROM FILES ( format = 'CSV', uris = ['gs://sample-data-and-media/fraud-demo-data/orders.csv'], skip_leading_rows = 1 );

CREATE OR REPLACE PROPERTY GRAPH fraud_demo.FraudDemo
NODE TABLES(
  fraud_demo.customers KEY(account_id) LABEL Customer PROPERTIES( account_id, name),
  fraud_demo.emails KEY(email) LABEL Email PROPERTIES( email, email_type),
  fraud_demo.phones KEY(phone_number) LABEL Phone PROPERTIES( phone_number, phone_type),
  fraud_demo.addresses KEY(address) LABEL Address PROPERTIES( address, address_type)
)
EDGE TABLES(
  fraud_demo.customer_emails KEY(account_id, email)
    SOURCE KEY(account_id) REFERENCES customers(account_id)
    DESTINATION KEY(email) REFERENCES emails(email)
    LABEL OwnsEmail PROPERTIES( account_id, email, last_updated_ts),
  fraud_demo.customer_phones KEY(account_id, phone_number)
    SOURCE KEY(account_id) REFERENCES customers(account_id)
    DESTINATION KEY(phone_number) REFERENCES phones(phone_number)
    LABEL OwnsPhone PROPERTIES( account_id, phone_number, last_updated_ts),
  fraud_demo.customer_addresses KEY(account_id, address)
    SOURCE KEY(account_id) REFERENCES customers(account_id)
    DESTINATION KEY(address) REFERENCES addresses(address)
    LABEL LinkedToAddress PROPERTIES( account_id, address, last_updated_ts)
);
