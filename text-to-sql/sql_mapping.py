sql_mapping_list = [
    {
        "Question": "List all sites which have domain installed",
        "SQL": "SELECT id, name, domain FROM app.sites WHERE domain_type_to_install IS NOT NULL and domain_ssl_activated_on IS NULL"
    },
    {
        "Question": "List all sites which have set up Stripe",
        "SQL": "SELECT id, name, domain FROM app.sites s INNER JOIN app.site_subscriptions sub ON s.id = sub.site_id WHERE (stripe_bacs_pay_method_id IS NOT NULL OR stripe_sepa_pay_method_id IS NOT NULL) AND status = 'A' and stripe_cust_id IS NOT NULL"
    },
    {
        "Question": "List all sites which have domain not yet installed",
        "SQL": "SELECT id, name, domain FROM app.sites WHERE domain_type_to_install IS NULL AND domain_ssl_activated_on IS NOT NULL"
    }
]