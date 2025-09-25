import re
import sys
import json
import requests
from bs4 import BeautifulSoup


def fetch_weather_info(city='Seoul'):
    try:
        url = f'http://wttr.in/{city}?format=3'
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        weather_text = response.text.strip()
        
        if ':' in weather_text:
            parts = weather_text.split(':')
            city_name = parts[0].strip()
            weather_data = parts[1].strip()
            
            temp_match = re.search(r'([+-]?\d+)°C', weather_data)
            temperature = temp_match.group(0) if temp_match else 'N/A'
            
            weather_icon = weather_data.split()[0] if weather_data.split() else '🌤️'
            
            weather_info = {
                'city': city_name,
                'temperature': temperature,
                'description': weather_icon
            }
        else:
            weather_info = {
                'city': city,
                'temperature': 'N/A',
                'description': '🌤️'
            }
        
        return weather_info
        
    except requests.RequestException as e:
        print(f'날씨 데이터를 가져오는 중 오류가 발생했습니다: {e}')
        print('프로그램을 종료합니다.')
        sys.exit(1)
    except Exception as e:
        print(f'날씨 정보 처리 중 오류가 발생했습니다: {e}')
        print('프로그램을 종료합니다.')
        sys.exit(1)


def fetch_kbs_news():
    url = 'http://news.kbs.co.kr/news/pc/main/main.html'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 링크가 있는 모든 텍스트 중에서 뉴스 제목 추출
        links = soup.find_all('a')
        news_headlines = []
        
        for link in links:
            text = link.get_text().strip()
            
            # 시간 형식으로 시작하는 항목 필터링 (예: "06:00", "07:00" 등)
            time_pattern = r'^\d{1,2}:\d{2}'
            
            # 뉴스 제목으로 보이는 조건들
            if (text and len(text) > 10 and len(text) < 100 and 
                not text.startswith('http') and 
                not re.match(time_pattern, text) and  # 시간 형식 필터링 추가
                not text in ['더보기', 'ON AIR', 'English', '재난포털', '제보'] and
                any(keyword in text for keyword in ['…', '·', ':', '(', ')', '경제', '사회', '정치', '국제'])):
                news_headlines.append(text)
        
        # 중복 제거 (순서 유지)
        unique_headlines = list(dict.fromkeys(news_headlines))
        
        return unique_headlines
        
    except requests.RequestException as e:
        print(f'뉴스 데이터를 가져오는 중 오류가 발생했습니다: {e}')
        print('프로그램을 종료합니다.')
        sys.exit(1)
    except Exception as e:
        print(f'예상치 못한 오류가 발생했습니다: {e}')
        print('프로그램을 종료합니다.')
        sys.exit(1)


def fetch_kospi_stocks():
    """
    네이버 금융에서 코스피 상장 주식 5개의 주가 정보를 가져옵니다.
    
    Returns:
        list: 주식 정보 리스트
    """
    try:
        # 네이버 금융 코스피 시가총액 상위 페이지
        url = 'https://finance.naver.com/sise/sise_market_sum.nhn?sosok=0'
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        stocks = []
        
        # 주식 테이블에서 상위 5개 주식 정보 추출
        table = soup.find('table', class_='type_2')
        if table:
            rows = table.find_all('tr')[2:7]  # 헤더와 첫 번째 행 제외하고 5개 행
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    # 주식명 (2번째 셀)
                    name_cell = cells[1].find('a')
                    if name_cell:
                        stock_name = name_cell.get_text().strip()
                        
                        # 현재가 (3번째 셀)
                        price_cell = cells[2]
                        current_price = price_cell.get_text().strip()
                        
                        # 등락률 (5번째 셀)
                        change_cell = cells[4]
                        change_rate = change_cell.get_text().strip()
                        
                        stocks.append({
                            'name': stock_name,
                            'price': current_price,
                            'change': change_rate
                        })
        
        return stocks[:5]  # 최대 5개만 반환
        
    except requests.RequestException as e:
        print(f'주식 데이터를 가져오는 중 오류가 발생했습니다: {e}')
        print('프로그램을 종료합니다.')
        sys.exit(1)
    except Exception as e:
        print(f'주식 정보 처리 중 오류가 발생했습니다: {e}')
        print('프로그램을 종료합니다.')
        sys.exit(1)


def display_weather(weather_info):
    print('=== 오늘의 날씨 ===')
    print(f'도시: {weather_info["city"]}')
    print(f'온도: {weather_info["temperature"]}')
    print(f'날씨: {weather_info["description"]}')
    print()


def display_headlines(headlines):
    """
    헤드라인 리스트를 화면에 출력합니다.
    
    Args:
        headlines (list): 출력할 헤드라인 리스트
    """
    if not headlines:
        print('헤드라인을 찾을 수 없습니다.')
        return
    
    print('=== KBS 뉴스 헤드라인 ===')
    for i, headline in enumerate(headlines, 1):
        print(f'{i}. {headline}')


def display_stocks(stocks):
    if not stocks:
        print('주식 정보를 찾을 수 없습니다.')
        return
    
    print('=== 코스피 거래량 상위 5개 ===')
    for i, stock in enumerate(stocks, 1):
        print(f'{i}. {stock["name"]}: {stock["price"]} ({stock["change"]})')


if __name__ == '__main__':
    print('오늘의 날씨, 뉴스, 주식 정보를 가져오는 중...')
    print()
    
    # 날씨 정보 가져오기
    weather_info = fetch_weather_info('Seoul')
    display_weather(weather_info)
    
    # 뉴스 헤드라인 가져오기
    headlines = fetch_kbs_news()
    display_headlines(headlines)
    print()
    
    # 코스피 주식 정보 가져오기
    stocks = fetch_kospi_stocks()
    display_stocks(stocks)