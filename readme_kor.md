# Econ DataReader

<div align="right">

[![Pypi Package Ver.](https://img.shields.io/pypi/v/econ-datareader.svg)](https://pypi.org/project/econ-datareader/)
[![License](https://img.shields.io/pypi/l/ansicolortags.svg)](https://img.shields.io/pypi/l/ansicolortags.svg)

<div align="left">

**Econ DataReader** 는 한국은행, FRED (미국 연방준비제도 경제 데이터), 국내외 금융상품 시세 데이터, 암호화폐 시세 데이터 등 다양한 출처에서 경제 및 금융 데이터를 쉽게 가져올 수 있도록 설계된 Python 라이브러리입니다. 이 도구는 데이터 수집을 간소화하고 데이터 과학 워크플로우에 쉽게 통합할 수 있습니다.

## 주요 기능

- 다음과 같은 다양한 출처에서 경제 데이터를 가져올 수 있습니다:
    - Trad-Fi 시세데이터 (주식, 채권 등)
    - 암호화폐: 업비트(Upbit) 현물, 바이낸스 (Binance) 현/선물 시세 데이터
    - FRED
    - 한국은행 (Bank Of Korea)

 ## 설치

econ-datareader는 pip를 통해 간단하게 설치할 수 있습니다.

```bash
pip install econ-datareader
```

## 사용법
아래는 econ-datareader의 사용 예시입니다.

### Trad-Fi and Cryptocurrency
```python
from econdatareader.finance import FinanceDownloader

downloader = FinanceDownloader()
data = downloader.download_data('CRYPTO_SPOT_BINANCE', ['BTCUSDT', 'ETHUSDT'], '1m', 202407240000, 202408050000)
```
`download_data` 메서드의 인수는 아래와 같이 입력합니다.
  - 데이터구분: `KOREA_STOCK`, `GLOBAL_FINANCE`, `CRYPTO_SPOT_BINANCE`, `CRYPTO_FUTURES_BINANCE`, `CRYPTO_SPOT_UPBIT` 중 1개 입력
  - 티커: `['티커명1', '티커명2']` 형식으로 입력
  - 시간간격: `1m`, `1h`, `1d`, `1M` 등의 문자열 형식으로 입력
  - 시작시간: `YYYYMMddHHmm` 형식으로 입력 (`int` 자료형)
  - 종료시간: 시작시간과 동일

데이터 호출은 아래와 같이 합니다. 위의 예시에서 ETHUSDT 데이터를 불러오고 싶을 경우
```python
eth_data = data['ETHUSDT']
```
`KOREA_STOCK`의 경우 일중 데이터는 실행시점 기준 7영업일까지만 다운로드 할 수 있으며, `GLOBAL_FINANCE`의 경우 분 단위 일중 데이터는 최대 30일까지 시간 단위 일중 데이터는 730일까지만 다운로드 할 수 있습니다.

### FRED
```python
from econdatareader.fred import FredDownloader

downloader = FredDownloader(api_key='your_api_key')
id_table = downloader.search_series_by_keyword('core consumer price index')
data = downloader.download_data(['Code1', 'Code2'], '2011-01-01', '2024-08-01')
```
FRED 데이터를 다운로드하기 위해서는 FRED에서 API_KEY를 발급받아야 합니다. 아래 링크에서 회원가입 후 API_KEY를 발급받으세요.
  - https://fred.stlouisfed.org/
  
`search_series_by_keyword` 메서드의 인수는 아래와 같이 입력합니다.
  - keyword: `str` 자료형으로 입력, 예를 들어 Core CPI의 id를 알고싶은 경우 `core consumer price index` 등으로 입력.

`download_data` 메서드의 인수는 아래와 같이 입력합니다.
  - 데이터 id: `['Code1', 'Code2']`와 같이 입력
  - 시작시간: `YYYY-mm-dd` 형식으로 입력 (`str` 자료형)
  - 종료시간: 시작시간과 동일

데이터가 가지는 고유 id는 FRED에서 키워드 검색을 통해 찾을 수 있습니다. 예를 들어 일 단위 달러인덱스의 id는 `DTWEXBGS`입니다.

데이터 호출은 아래와 같이 합니다. 위의 예시에서 달러 인덱스 데이터를 불러오고 싶을 경우
```python
dollar_index_data = data['DTWEXBGS']
```


### 한국은행 (BOK)
```python
from econdatareader.bok import BokDownloader

downloader = BokDownloader(api_key='your_api_key')
id_table = downloader.search_stat_code_by_keyword('소비자물가')
data = downloader.download_data([('StatCode1', 'A', '2013', '2024', 'ItemCode1'), 
('StatCode2', 'Q', '2015Q1', '2024Q2', 'ItemCode2'),
('StatCode3', 'M', '201501', '202407' 'ItemCode3'),
('Statcode4', 'D', '20110101', '20240101', 'ItemCode4')])
```
한국은행 경제통계시스템 데이터를 다운로드하기 위해서는 아래 링크에서 회원가입 후 API_KEY를 발급받으세요.
 - https://ecos.bok.or.kr/api/#/

`search_stat_code_by_keyword` 메서드의 인수는 아래와 같이 입력합니다.
  - keyword: `str` 자료형으로 입력, 예를 들어 소비자물가지수의 STAT_CODE를 알고싶은 경우 `소비자물가지수`로 입력.

`download_data` 메서드의 인수는 아래와 같이 입력합니다.
  - `(데이터 id, 시간간격, 시작시간, 종료시간, 데이터 서브 id)` 순으로 입력 (위 코드 예시 참조)
  - 시간간격은 `D`, `M`, `Q`, `A` 중 1가지를 선택
  - 시작시간 및 종료시간
    -  `D`의 경우 `YYYYMMDD` 형식으로 입력
    -  `M`의 경우 `YYYYMM` 형식으로 입력
    -  `Q`의 경우 `YYYYQd` 형식으로 입력 (`d=1,2,3,4`)
    -  `A`의 경우 `YYYY` 형식으로 입력
 - 데이터 id 및 데이터 서브 id는 한국은행 경제통계시스템을 참조하면 됨.


데이터 호출은 아래와 같이 합니다. 위의 예시에서 `Statcode1`의 데이터를 불러오고 싶을 경우
```python
stat1_data = data['StatCode1-ItemCode1'] 
```


## 라이센스
이 프로젝트는 MIT 라이선스에 따라 라이선스가 부여됩니다. 자세한 내용은 LICENSE 파일을 참조하십시오.

## 문의
질문이나 제안이 있으시면 `wydanielchoi@gmail.com`으로 연락해 주세요.
