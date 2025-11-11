from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.action_chains import ActionChains
import time
from typing import Dict, List, Tuple, Optional


class CarrotLikeBot:
    """당근마켓 좋아요 자동화 봇"""
    
    # XPath 상수들
    COMPOSE_VIEW_BASE = '//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View'
    POST_LIST_XPATH = '//androidx.recyclerview.widget.RecyclerView[@resource-id="com.towneers.www:id/feedRecyclerView"]/android.view.ViewGroup[@content-desc]'
    TOAST_SUCCESS_XPATH = "//*[contains(@text, '관심목록에 추가했어요')]"
    DETAIL_BUTTON_TEXT = "자세히 보기"
    
    # 타이밍 상수들
    DEFAULT_TIMEOUT = 5
    TOAST_TIMEOUT = 2
    SCROLL_DELAY = 1
    PAGE_LOAD_DELAY = 2
    
    def __init__(self, device_name: str = "R3CN20HAC4A"):
        """초기화"""
        self.device_name = device_name
        self.driver = None
        self.stats = {
            'liked_posts_titles': [],
            'liked_posts_count': 0,
            'failed_posts': []
        }
        self._setup_capabilities()

    def _setup_capabilities(self) -> None:
        """Appium capabilities 설정"""
        self.desired_caps = {
            "platformName": "Android",
            "appium:deviceName": self.device_name,
            "appium:automationName": "UiAutomator2",
            "appium:appPackage": "com.towneers.www",
            "appium:appActivity": ".launcher.LauncherActivity",
            "appium:noReset": True,
            "appium:dontStopAppOnReset": False,
            "appium:newCommandTimeout": 0,
            "appium:commandTimeouts": 600000,
            "appium:keepAliveTimeout": 0,
            "appium:autoGrantPermissions": True,
            "appium:sessionOverride": True,
            "appium:clearSystemFiles": False,
            "appium:enforceAppInstall": False,
        }
        self.options = UiAutomator2Options().load_capabilities(self.desired_caps)

    def start_driver(self) -> None:
        """Appium driver 시작/재시작"""
        try:
            if self.driver:
                print("Appium 세션 재시작 중...")
                self.driver.quit()
        except:
            pass
        
        time.sleep(self.PAGE_LOAD_DELAY)
        self.driver = webdriver.Remote(command_executor="http://127.0.0.1:4723", options=self.options)
        print("Appium session 시작/재시작 완료")

    def get_screen_size(self) -> Dict[str, int]:
        """화면 크기 가져오기"""
        try:
            return self.driver.get_window_size()
        except:
            return {"width": 1080, "height": 2340}

    def _perform_scroll(self, start_ratio: float, end_ratio: float, direction: str) -> None:
        """스크롤 수행 공통 로직"""
        try:
            screen_size_value = self.get_screen_size()
            width_value = screen_size_value["width"]
            height_value = screen_size_value["height"]
            
            start_x_value = width_value // 2
            start_y_value = int(height_value * start_ratio)
            end_x_value = width_value // 2
            end_y_value = int(height_value * end_ratio)
            
            print(f"{direction} 스크롤: ({start_x_value}, {start_y_value}) → ({end_x_value}, {end_y_value})")
            
            actions = ActionChains(self.driver)
            actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
            actions.w3c_actions.pointer_action.move_to_location(start_x_value, start_y_value)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.move_to_location(end_x_value, end_y_value)
            actions.w3c_actions.pointer_action.release()
            actions.perform()
            
            time.sleep(self.SCROLL_DELAY)
            print(f"{direction} 스크롤 완료")
            
        except Exception as e:
            print(f"{direction} 스크롤 중 오류: {e}")

    def scroll_down(self, start_ratio: float = 0.75, end_ratio: float = 0.25) -> None:
        """화면을 아래로 스크롤 (75% → 25%)"""
        self._perform_scroll(start_ratio, end_ratio, "아래로")

    def scroll_up(self, start_ratio: float = 0.25, end_ratio: float = 0.75) -> None:
        """화면을 위로 스크롤 (25% → 75%)"""
        self._perform_scroll(start_ratio, end_ratio, "위로")

    def safe_find_elements(self, by: By, value: str, retries: int = 2) -> List:
        """Instrumentation crash 복구 로직이 포함된 find_elements 래퍼"""
        for attempt in range(retries + 1):
            try:
                return self.driver.find_elements(by, value)
            except WebDriverException as e:
                if "instrumentation process is not running" in str(e):
                    print(f"UiAutomator2 crash 감지 — 세션 재시작 시도 ({attempt+1}/{retries})")
                    self.start_driver()
                else:
                    raise
        raise RuntimeError("❌ 세션 복구 실패: instrumentation 재시작 불가")

    def safe_click(self, xpath_value: str) -> None:
        """특정 XPath 클릭 시도 (instrumentation crash 감지 및 복구 포함)"""
        try:
            element_value = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, xpath_value))
            )
            element_value.click()
        except WebDriverException as e:
            if "instrumentation process is not running" in str(e):
                print("UiAutomator2 crash 감지 — 세션 재시작 중...")
                self.start_driver()
                element_value = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT * 2).until(
                    EC.presence_of_element_located((By.XPATH, xpath_value))
                )
                element_value.click()
            else:
                raise

    def _get_title_xpath(self, base_xpath_value: str) -> str:
        """제목 XPath 결정 로직"""
        view3_xpath_value = f'{base_xpath_value}/android.view.View[3]/*'
        view3_elements_value = self.driver.find_elements(By.XPATH, view3_xpath_value)
        
        if len(view3_elements_value) == 1:
            return view3_xpath_value
        else:
            return f'({base_xpath_value}/android.view.View[4]/*)[1]'

    def get_post_title(self, index: int) -> str:
        """게시물 제목 가져오기"""
        base_xpath_value = f'{self.COMPOSE_VIEW_BASE}/android.view.View[1]'
        
        try:
            title_xpath_value = self._get_title_xpath(base_xpath_value)
            title_element_value = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, title_xpath_value))
            )
            return title_element_value.get_attribute("text") or f"제목 불명 #{index+1}"
            
        except Exception as e:
            print(f"제목 추출 실패: {e}")
            try:
                fallback_xpath_value = f'({base_xpath_value}/android.view.View[4]/*)[1]'
                title_element_value = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, fallback_xpath_value))
                )
                title_text_value = title_element_value.get_attribute("text")
                print(f"폴백으로 추출된 제목: {title_text_value}")
                return title_text_value or f"제목 불명 #{index+1}"
            except:
                return f"제목 불명 #{index+1}"

    def _detect_detail_button(self) -> bool:
        """자세히 보기 버튼 감지"""
        try:
            detail_elements_value = self.driver.find_elements(By.XPATH, ".//android.widget.TextView")
            return any(element.get_attribute("text") == self.DETAIL_BUTTON_TEXT 
                      for element in detail_elements_value)
        except:
            return False

    def _get_like_button_xpath(self) -> str:
        """좋아요 버튼 XPath 결정"""
        if self._detect_detail_button():
            return f'{self.COMPOSE_VIEW_BASE}/android.view.View[5]/android.view.View[1]'
        else:
            return f'{self.COMPOSE_VIEW_BASE}/android.view.View[4]/android.view.View[1]'

    def _check_toast_message(self) -> bool:
        """토스트 메시지 확인"""
        try:
            WebDriverWait(self.driver, self.TOAST_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, self.TOAST_SUCCESS_XPATH))
            )
            return True
        except:
            return False

    def click_like_button(self) -> bool:
        """좋아요 버튼 클릭 및 관심 추가 확인"""
        like_xpath_value = self._get_like_button_xpath()
        
        # 첫 번째 클릭
        self.safe_click(like_xpath_value)
        
        if self._check_toast_message():
            print("관심 추가 성공 감지됨")
            return True
        
        print("관심 추가 문구 감지 실패 — 재시도 중...")
        
        # 재시도
        try:
            print("관심 추가를 위해 다시 클릭...")
            self.safe_click(like_xpath_value)
            time.sleep(1)
            
            if self._check_toast_message():
                print("재클릭으로 관심 추가 성공")
                return False  # 이미 있던 것을 다시 추가한 경우
            else:
                print("재클릭 후에도 관심 추가 문구 감지 실패")
                return False
        except:
            print("재클릭 실패")
            return False

    def process_post(self, post_element, index: int) -> None:
        """개별 게시물 처리"""
        try:
            print(f"\n--- 게시물 {index+1} 처리 중 ---")
            post_element.click()
            time.sleep(self.PAGE_LOAD_DELAY)
            
            post_title_value = self.get_post_title(index)
            
            # 제목에서 "거래완료"나 "예약중" 텍스트 제거
            if "거래완료" in post_title_value:
                post_title_value = post_title_value.replace("거래완료", "").strip()
                print(f"'거래완료' 텍스트 제거됨")
            if "예약중" in post_title_value:
                post_title_value = post_title_value.replace("예약중", "").strip()
                print(f"'예약중' 텍스트 제거됨")
            
            print(f"게시물 제목: {post_title_value}")
            
            try:
                is_new_like_value = self.click_like_button()
                
                if is_new_like_value:
                    self.stats['liked_posts_count'] += 1
                    self.stats['liked_posts_titles'].append(post_title_value)
                    print(f"새로운 관심 추가 성공! (총 {self.stats['liked_posts_count']}개)")
                else:
                    print(f"관심 상태 유지됨 (카운트 안함)")
                
            except Exception as like_error:
                self.stats['failed_posts'].append(post_title_value)
                print(f"관심 추가 실패: {post_title_value} - {like_error}")
            
            self.driver.back()
            time.sleep(self.PAGE_LOAD_DELAY)
            
        except Exception as post_error:
            print(f"게시물 {index+1} 처리 중 오류: {post_error}")
            try:
                self.driver.back()
                time.sleep(self.PAGE_LOAD_DELAY)
            except:
                pass

    def _get_posts_elements(self) -> List:
        """현재 화면의 게시물 요소들 가져오기"""
        return self.safe_find_elements(By.XPATH, self.POST_LIST_XPATH)

    def _handle_scroll_if_needed(self, current_index_value: int, post_pages_value: List, enable_scroll: bool) -> Tuple[bool, int, List]:
        """스크롤이 필요한 경우 처리"""
        if current_index_value >= len(post_pages_value):
            if enable_scroll:
                print(f"더 많은 게시물을 보기 위해 페이지 갱신")
                self.scroll_up()
                time.sleep(self.PAGE_LOAD_DELAY)
                current_index_value = 0
                
                post_pages_value = self._get_posts_elements()
                
                if current_index_value >= len(post_pages_value):
                    print("더 이상 로드할 게시물이 없습니다.")
                    return False, current_index_value, post_pages_value
            else:
                print("스크롤이 비활성화되어 있어 더 이상 진행할 수 없습니다.")
                return False, current_index_value, post_pages_value
        
        return True, current_index_value, post_pages_value

    def print_results(self) -> None:
        """결과 출력"""
        print(f"\n=== 좋아요 처리 결과 ===")
        print(f"성공한 좋아요 개수: {self.stats['liked_posts_count']}")
        print(f"좋아요한 게시글 제목:")
        for i, title in enumerate(self.stats['liked_posts_titles'], 1):
            print(f"  {i}. {title}")

        if self.stats['failed_posts']:
            print(f"실패한 게시글: {len(self.stats['failed_posts'])}개")
            for i, title in enumerate(self.stats['failed_posts'], 1):
                print(f"  {i}. {title}")

    def get_results(self) -> Dict:
        """결과 데이터 반환"""
        return {
            'liked_count': self.stats['liked_posts_count'],
            'liked_titles': self.stats['liked_posts_titles'],
            'failed_posts': self.stats['failed_posts']
        }

    def run(self, max_posts: int = 10, enable_scroll: bool = True) -> Dict:
        """메인 실행 함수"""
        try:
            self.start_driver()
            
            processed_count_value = 0
            current_index_value = 0
            
            while self.stats['liked_posts_count'] < max_posts:
                post_pages_value = self._get_posts_elements()
                print(f"\n=== 게시물들 처리 시작 ===")

                can_continue, current_index_value, post_pages_value = self._handle_scroll_if_needed(
                    current_index_value, post_pages_value, enable_scroll
                )
                
                if not can_continue:
                    break
                
                if current_index_value < len(post_pages_value):
                    self.process_post(post_pages_value[current_index_value], processed_count_value)
                    processed_count_value += 1
                    current_index_value += 1

            self.print_results()
            return self.get_results()

        except Exception as e:
            print(f"실행 중 오류 발생: {e}")
            return self.get_results()

        finally:
            print("종료 중...")
            try:
                if self.driver:
                    self.driver.quit()
            except:
                pass


def main():
    """메인 함수"""
    bot = CarrotLikeBot()
    results = bot.run(max_posts=10, enable_scroll=True)
    
    # 전역 변수에 결과 저장 (기존 코드와 호환성)
    globals().update({
        'final_liked_count': results['liked_count'],
        'final_liked_titles': results['liked_titles'],
        'final_failed_posts': results['failed_posts']
    })
    
    print(f"\n처리 완료! 총 {results['liked_count']}개 게시글에 좋아요를 눌렀습니다.")


if __name__ == "__main__":
    main()