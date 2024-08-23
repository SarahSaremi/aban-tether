ORDER_STATUS_PENDING = 'pending'
ORDER_STATUS_PROCESSED = 'processed'
ORDER_STATUS_FAILED = 'failed'

ORDER_STATUS_CHOICES = (
    (ORDER_STATUS_PENDING, 'Pending'),
    (ORDER_STATUS_PROCESSED, 'Processed'),
    (ORDER_STATUS_FAILED, 'Failed'),
)

# Crypto can be a separate model instead of being hardcoded.
CRYPTO_ABAN = 'aban'
CRYPTO_TETHER = 'tether'
CRYPTO_CHOICES = (
    (CRYPTO_ABAN, 'Aban'),
    (CRYPTO_TETHER, 'Tether'),
)

