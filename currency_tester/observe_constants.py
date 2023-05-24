from datetime import timedelta

timeframes = {
    '1m': timedelta(minutes=1),
    '3m': timedelta(minutes=3),
    '5m': timedelta(minutes=5),
    '15m': timedelta(minutes=15),
    '30m': timedelta(minutes=30),
    '1h': timedelta(hours=1),
    '2h': timedelta(hours=2),
    '4h': timedelta(hours=4),
    '6h': timedelta(hours=6),
    '8h': timedelta(hours=8),
    '12h': timedelta(hours=12),
    '1d': timedelta(days=1),
    '3d': timedelta(days=3),
    '1w': timedelta(days=7)
}