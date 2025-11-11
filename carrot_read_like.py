from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.action_chains import ActionChains
import time


class CarrotProfileReader:
    """당근마켓 관심목록 읽기 전용 봇"""
    
    def __init__(self):
        """초기화"""
        self.desired_caps = {
            "platformName": "Android",
            "appium:deviceName": "R3CN20HAC4A",
            "appium:automationName": "UiAutomator2",
            "appium:appPackage": "com.towneers.www",
            "appium:appActivity": ".launcher.LauncherActivity",
            "appium:noReset": True,
            "appium:newCommandTimeout": 0,
            "appium:autoGrantPermissions": True,
        }
        
        self.options = UiAutomator2Options().load_capabilities(self.desired_caps)
        self.driver = None

    def start_driver(self):
        """Appium driver 시작/재시작"""
        try:
            if self.driver:
                print("Appium 세션 재시작 중...")
                self.driver.quit()
        except:
            pass
        
        time.sleep(2)
        self.driver = webdriver.Remote(command_executor="http://127.0.0.1:4723", options=self.options)
        print("Appium session 시작/재시작 완료")

    def get_screen_size(self):
        """화면 크기 가져오기"""
        try:
            return self.driver.get_window_size()
        except:
            return {"width": 1080, "height": 2340}

    def scroll_down(self, start_ratio=0.75, end_ratio=0.25):
        """화면을 아래로 스크롤 (75% → 25%)"""
        try:
            screen_size_value = self.get_screen_size()
            width_value = screen_size_value["width"]
            height_value = screen_size_value["height"]
            
            start_x_value = width_value // 2
            start_y_value = int(height_value * start_ratio)
            end_x_value = width_value // 2
            end_y_value = int(height_value * end_ratio)
            
            print(f"아래로 스크롤: ({start_x_value}, {start_y_value}) → ({end_x_value}, {end_y_value})")
            
            actions = ActionChains(self.driver)
            actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
            actions.w3c_actions.pointer_action.move_to_location(start_x_value, start_y_value)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.move_to_location(end_x_value, end_y_value)
            actions.w3c_actions.pointer_action.release()
            actions.perform()
            
            time.sleep(1)
            print("아래로 스크롤 완료")
            
        except Exception as e:
            print(f"아래로 스크롤 중 오류: {e}")

    def extract_titles_from_textviews(self):
        """XPath로 TextView들에서 text 속성 추출"""
        try:
            # 1. 동일한 depth의 모든 element들을 받아오기 (WebDriverWait 사용)
            wait = WebDriverWait(self.driver, 10)
            elements = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//android.view.View[@resource-id='root']/android.view.View/android.view.View/android.view.View[2]/android.view.View/android.view.View")
                )
            )
            print(f"발견된 element 개수: {len(elements)}")  # 디버깅용
            titles = []
            
            for element in elements:
                try:
                    # TextView 개수 확인 (2개 이하면 중단)
                    textviews = element.find_elements(By.XPATH, ".//android.widget.TextView")

                    # 2. 해당 element 바로 하위의 첫번째 TextView에서 텍스트 불러오기
                    text = textviews[0].get_attribute("text")
                    
                    if text == "관심 있을 만한 ":
                        if textviews[1].get_attribute("text") == " 상품":
                            print("'관심 있을 만한' 섹션의 '상품' 발견 - 검색 중단")
                            titles.append(False)  # 종료 신호로 False 추가
                            break

                    if text and text.strip():
                        text = text.strip()
                        # 3. titles에 추가
                        titles.append(text)
                        print(f"제목 발견: {text}")
                except:
                    # 해당 element에 TextView가 없으면 건너뛰기
                    continue
        
            return titles
            
        except Exception as e:
            print(f"TextView에서 제목 추출 실패: {e}")
            return []

    def get_liked_posts_from_profile(self):
        """프로필로 이동하여 관심목록의 모든 게시물 제목 수집"""
        try:
            print("프로필 화면으로 이동 중...")
            
            # 1. 네비게이션 바 5번째 아이템 클릭 (프로필)
            nav_element_value = self.driver.find_element(
                By.XPATH, 
                "(//android.widget.ImageView[@resource-id=\"com.towneers.www:id/navigation_bar_item_icon_view\"])[5]"
            )
            nav_element_value.click()
            time.sleep(2)
            print("프로필 화면으로 이동 완료")

            self.scroll_down(start_ratio=0.3, end_ratio=0.2)
            
            # 2. 관심목록 섹션 클릭
            interest_section_value = self.driver.find_element(
                By.XPATH, 
                "//android.widget.TextView[@text='관심목록']"
            )
            interest_section_value.click()
            print("관심목록 섹션 클릭 완료")
            time.sleep(5) 

            
            # 3. 관심목록에서 모든 아이템 제목 수집
            collected_titles_value = []
            
            while True:
                # 현재 화면에서 제목 추출
                print("현재 화면에서 제목 추출 중...")
                current_titles = self.extract_titles_from_textviews()
                if len(collected_titles_value) == 0:
                    pass
                else:
                    current_titles.pop(0)
                
                # 마지막 값이 False면 중단 신호
                if current_titles and current_titles[-1] is False:
                    # 마지막 False 제거
                    current_titles.pop()
                    # 나머지 제목들 추가
                    new_titles_found = 0
                    for title in current_titles:
                        if title not in collected_titles_value:
                            collected_titles_value.append(title)
                            new_titles_found += 1
                    print(f"마지막으로 새로 발견된 제목: {new_titles_found}개")
                    print("'관심 있을 만한' 섹션 도달 - 관심목록 수집 종료")
                    break
                
                # 새로운 제목들만 추가
                new_titles_found = 0
                for title in current_titles:
                    if title not in collected_titles_value:
                        collected_titles_value.append(title)
                        new_titles_found += 1
                
                print(f"새로 발견된 제목: {new_titles_found}개")
                print(f"전체 수집된 제목: {len(collected_titles_value)}개")
                
                # 스크롤하여 더 많은 항목 로드
                print("다음 항목을 위해 아래로 스크롤...")
                self.scroll_down(start_ratio=0.6, end_ratio=0.2)
                time.sleep(2)
        
            return collected_titles_value
            
        except Exception as e:
            print(f"프로필 확인 중 오류: {e}")
            return []

    def print_liked_list(self, liked_list):
        """관심목록 출력"""
        print(f"\n=== 관심목록 결과 ===")
        print(f"총 관심목록 개수: {len(liked_list)}")
        print(f"관심목록 항목들:")
        
        if liked_list:
            for i, title in enumerate(liked_list, 1):
                print(f"  {i}. {title}")
        else:
            print("  (관심목록이 비어있습니다)")

    def run(self):
        """메인 실행 함수 - 관심목록만 가져오기"""
        try:
            self.start_driver()
            
            # 관심목록에서 모든 게시물 수집
            print("관심목록 수집을 시작합니다...")
            liked_list = self.get_liked_posts_from_profile()
            
            # 결과 출력
            self.print_liked_list(liked_list)
            
            return liked_list

        except Exception as e:
            print(f"실행 중 오류 발생: {e}")
            return []

        finally:
            print("종료 중...")
            try:
                if self.driver:
                    self.driver.quit()
            except:
                pass


def main():
    """메인 함수"""
    reader = CarrotProfileReader()
    liked_list = reader.run()
    
    # 전역 변수에 결과 저장
    globals()['liked_list_from_profile'] = liked_list
    
    print(f"\n수집 완료! 총 {len(liked_list)}개의 관심목록 항목을 찾았습니다.")
    
    return liked_list


if __name__ == "__main__":
    main()