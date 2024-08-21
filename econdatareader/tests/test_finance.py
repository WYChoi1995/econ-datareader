from econdatareader.finance import FinanceDownloader

downloader = FinanceDownloader()
downloader.download_data('CRYPTO_SPOT_BINANCE', ['BTCUSDT'], '1m', 202407240000, 202408050000)
