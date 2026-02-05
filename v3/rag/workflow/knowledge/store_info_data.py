STORE_INFO = {
    "name": "Horecamart",
    "email": "info@horecamart.it",
    "phone": "3515161696",
    "address": {
        "company": "Traversari",
        "street": "Via Riccardo Lombardi 14",
        "city": "Marcon (VE)",
        "zip": "30020",
        "country": "Italia",
    },
    "shipping": {
        "couriers": ["Poste Italiane SDA", "DHL"],
        "handling_time_days": 7,
        "delivery_time_days": "2–3 giorni lavorativi",
        "peak_notice": "Nel periodo novembre–dicembre i tempi possono allungarsi",
        "free_shipping_threshold": 100,
        "tracking": True,
    },
    "returns": {
        "return_window_days": 14,
        "refund_window_days": 14,
        "return_shipping_paid_by": "cliente",
        "damaged_notice_hours": 48,
    },
    "payments": {
        "secure": True,
        "ssl": True,
        "payment_deadline_days": 3,
    },
    "discounts": {
        "volume_discount_percent": 10,
        "coupons_stackable": True,
    },
}

'''این فایل LLM نیست
📌 بعداً می‌تونه از DB / CMS پر بشه
📌 handler و prompt فقط از این می‌خونن'''