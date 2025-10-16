from typing import List, Iterable
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

NAVER_HOME = 'https://www.naver.com'
NAVER_LOGIN = 'https://nid.naver.com/nidlogin.login'

TOP_N = 40


def uniq_keep_order(items: Iterable[str]) -> List[str]:
    seen = set()
    out = []
    for s in items:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def print_content_list(title: str, items: List[str]) -> None:
    print(f'\n[{title}]')
    if not items:
        print('데이터가 없습니다.')
        return
    for i, t in enumerate(items[:TOP_N], 1):
        print(f'{i}. {t}')


def smooth_scroll(driver, steps: int = 4, pause: float = 0.4) -> None:
    """아래로 천천히 스크롤하여 지연 로딩을 유도"""
    height = driver.execute_script('return document.body.scrollHeight || 0')
    for i in range(1, steps + 1):
        y = int(height * i / steps)
        driver.execute_script(f'window.scrollTo(0, {y});')
        time.sleep(pause)
    driver.execute_script('window.scrollTo(0, 0);')
    time.sleep(0.4)


def collect_targets_first(driver) -> List[str]:
    """자주 보이는 메인 블록에서 우선 수집"""
    target_selectors = [
        '#NM_FAVORITE a',                        # 즐겨찾기/바로가기
        '#shortcutArea a',                      # 바로가기 버튼들
        '#NM_THEME_BANNER a',                   # 테마 배너
        '#NM_NEWSSTAND_DEFAULT_THUMB a',        # 뉴스스탠드 썸네일
        '#NM_NEWSSTAND_HEADER a',               # 뉴스스탠드 탭
        '#NM_LEFT_NAV a',                       # 좌측 내비(있을 때)
        'a[href^="https://mail.naver.com"]',
        'a[href^="https://section.blog.naver.com"]',
        'a[href^="https://section.cafe.naver.com"]',
        'a[href^="https://section.news.naver.com"]',
        'a[href^="https://shopping.naver.com"]',
    ]
    texts: List[str] = []
    for sel in target_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, sel)
            for el in elements:
                if el.is_displayed():
                    t = el.text.strip()
                    if t:
                        texts.append(t)
        except Exception:
            continue
    return uniq_keep_order(texts)


def collect_any_visible_links(driver) -> List[str]:
    """폴백: 화면에 보이는 모든 a 태그 텍스트 수집"""
    anchors = driver.find_elements(By.CSS_SELECTOR, 'a')
    texts = []
    for a in anchors:
        try:
            if a.is_displayed():
                t = a.text.strip()
                if t and not t.startswith('#'):
                    texts.append(t)
        except Exception:
            continue
    return uniq_keep_order(texts)


def collect_page_contents(driver) -> List[str]:
    """타깃 → 폴백 순으로 수집하고 비어 있으면 스크롤 후 재시도"""
    texts = collect_targets_first(driver)
    if not texts:
        texts = collect_any_visible_links(driver)
    if not texts:
        smooth_scroll(driver)
        texts = collect_targets_first(driver)
        if not texts:
            texts = collect_any_visible_links(driver)
    return texts


def switch_into_login_iframe_if_any(driver, wait) -> None:
    """로그인 입력 iframe이 있으면 진입"""
    driver.switch_to.default_content()
    for sel in ['iframe#account', 'iframe#ssoLoginIframe']:
        try:
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, sel)))
            return
        except TimeoutException:
            driver.switch_to.default_content()
    # 없으면 본문 그대로 진행


def find_login_fields(driver, wait):
    """다양한 로그인 필드 id 대응"""
    switch_into_login_iframe_if_any(driver, wait)
    id_candidates = ['id', 'loginId']
    pw_candidates = ['pw', 'loginPw']

    id_box = pw_box = None
    for cid in id_candidates:
        try:
            id_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'input#{cid}')))
            break
        except TimeoutException:
            continue
    for cpw in pw_candidates:
        try:
            pw_box = driver.find_element(By.CSS_SELECTOR, f'input#{cpw}')
            break
        except NoSuchElementException:
            continue
    if not id_box or not pw_box:
        raise RuntimeError('로그인 입력 필드를 찾지 못했습니다.')
    return id_box, pw_box


def main():
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)

    try:
        driver.get(NAVER_HOME)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        pre = collect_page_contents(driver)
        print_content_list('로그인 전 콘텐츠', pre)

        driver.get(NAVER_LOGIN)
        user_id = input('네이버 ID를 입력하세요: ')
        user_pw = input('네이버 비밀번호를 입력하세요: ')

        id_box, pw_box = find_login_fields(driver, wait)
        id_box.clear(); id_box.send_keys(user_id)
        pw_box.clear(); pw_box.send_keys(user_pw)

        print('\n브라우저에서 캡차/추가 인증을 직접 완료하고 "로그인" 버튼을 클릭하세요.')
        input('로그인이 끝났으면 콘솔에서 Enter를 눌러 계속합니다... ')

        driver.switch_to.default_content()
        time.sleep(2)

        driver.get(NAVER_HOME)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        smooth_scroll(driver)
        post = collect_page_contents(driver)
        print_content_list('로그인 후 콘텐츠', post)

        only_after = [x for x in post if x not in pre]
        print_content_list('로그인 후에만 보이는 콘텐츠', only_after)

    finally:
        time.sleep(1)
        driver.quit()


if __name__ == '__main__':
    main()
