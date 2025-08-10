from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
# 파일 상단 import
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

class ResultLogger:
    def __init__(self):
        self.rows: List[Dict[str, Any]] = []

    def add(self, tc_name: str, status: bool, note: str = ""):
        self.rows.append({
            "TC": tc_name,
            "Status": "PASS" if status else "FAIL",
            "Note": note
        })

    def export_excel(self, filepath: str):
        df = pd.DataFrame(self.rows)

        total = len(df)
        pass_df = df[df["Status"] == "PASS"].copy()
        fail_df = df[df["Status"] == "FAIL"].copy()

        # 요약표
        summary = pd.DataFrame([
            {"Metric": "Total", "Count": total},
            {"Metric": "Pass",  "Count": len(pass_df)},
            {"Metric": "Fail",  "Count": len(fail_df)},
        ])

        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
            summary.to_excel(writer, index=False, sheet_name="Summary")
            df.to_excel(writer, index=False, sheet_name="All Results")
            pass_df.to_excel(writer, index=False, sheet_name="Pass List")
            fail_df.to_excel(writer, index=False, sheet_name="Fail List")


# ===== 설정 =====
APPIUM_URL = "http://localhost:4723/wd/hub"
UDID = "R54R303BFTA"  # adb devices에서 확인
APP_PACKAGE = "net.skyscanner.android.main"
APP_ACTIVITY = "net.skyscanner.shell.ui.activity.SplashActivity"
# ================

# 드라이버 생성
def make_driver():
    opts = UiAutomator2Options()
    opts.udid = UDID
    opts.platform_name = "Android"
    opts.app_package = APP_PACKAGE
    opts.app_activity = APP_ACTIVITY
    driver = webdriver.Remote(APPIUM_URL, options=opts)
    driver.implicitly_wait(2)
    return driver

# OS 레벨 좌표 탭(안 먹는 화면에도 강함)
def tap_os(driver, x, y):
    driver.execute_script("mobile: shell", {
        "command": "input",
        "args": ["tap", str(x), str(y)]
    })

# TC1: 앱 실행 확인
def tc1(driver) -> bool:
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (AppiumBy.ID, "net.skyscanner.android.main:id/privacy_policy_container")
            )
        )
        return True
    except:
        return False

# TC2: 로그인 확인
def tc2(driver) -> bool:
    ok = True
    try:
        time.sleep(2)
        driver.find_element(AppiumBy.ID, "net.skyscanner.android.main:id/privacy_policy_accept_button").click()
        print("  1) 쿠키정책: 모두수락 클릭")
    except:
        print("  1) 쿠키정책: 없음/클릭 스킵")

    try:
        time.sleep(2)
        driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().className("android.widget.TextView").text("Google")'
        ).click()
        print("  2) 로그인 화면: Google 클릭")
    except:
        print("  2) 로그인 화면: Google 클릭 실패")
        ok = False

    try:
        time.sleep(2)
        driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().className("android.widget.TextView").text("개인정보 처리방침에 따른 개인정보 수집 및 이용에 동의합니다.")'
        ).click()
        driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().className("android.widget.TextView").text("본인은 만 16세 이상이며 서비스약관에 동의합니다.")'
        ).click()
        driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().className("android.widget.Button")'
        ).click()
        print("  3) 이용약관: 동의 완료")
    except:
        print("  3) 이용약관: 화면 없음/스킵")

    try:
        time.sleep(3)
        tap_os(driver, 441, 1499)  # 구글 계정 좌표 탭
        print("  4) 계정 버튼 탭")
    except:
        print("  4) 계정 버튼 탭 실패")
        ok = False

    # 로그인 완료 검증
    try:
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located(
                (AppiumBy.ID, "net.skyscanner.android.main:id/login_finished_title")
                
            )
            
        )
        print(" 판정) 로그인되셨습니다! 문구 출력")
        return ok and True
    except:
        return False


# TC3: 메인메뉴 확인
def tc3(driver) -> bool:
    try:
        time.sleep(2)
        driver.find_element(AppiumBy.ID, "net.skyscanner.android.main:id/onboarding_marketing_optin_secondary_button").click()
        print("  1) 다음에 할께요 클릭")
    except:
        print("  1) 다음에 할께요 실패")

    try:
        # 항공권 확인
        flight_el = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (AppiumBy.ID, "net.skyscanner.android.main:id/home_flights_text")
            )
        )
        flight_ok = (flight_el.text.strip() == "항공권")
        print(f"  판정1) 항공권 텍스트 확인: {'PASS' if flight_ok else f'FAIL (실제: {flight_el.text})'}")

        # 호텔 확인
        hotel_el = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (AppiumBy.ID, "net.skyscanner.android.main:id/home_hotels_text")
            )
        )
        hotel_ok = (hotel_el.text.strip() == "호텔")
        print(f"  판정2) 호텔 텍스트 확인: {'PASS' if hotel_ok else f'FAIL (실제: {hotel_el.text})'}")

        # 렌터카 확인
        car_el = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (AppiumBy.ID, "net.skyscanner.android.main:id/home_carhire_text")
            )
        )
        car_ok = (car_el.text.strip() == "렌터카")
        print(f"  판정3) 렌터카 텍스트 확인: {'PASS' if car_ok else f'FAIL (실제: {car_el.text})'}")

        # 세 개 다 맞아야 PASS
        return flight_ok and hotel_ok and car_ok

    except Exception as e:
        print("  [TC3] 요소 찾기 실패:", e)
        return False

def tc4(driver) -> bool:
    """Drops 버튼 클릭 후 'Drops 시작하기' 노출 확인"""
    try:
        # Drops 버튼 클릭
        drops_btn = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                AppiumBy.XPATH,
                '//android.widget.TextView[@resource-id="net.skyscanner.android.main:id/navigation_bar_item_small_label_view" and @text="Drops"]'
            ))
        )
        drops_btn.click()
        print("[TC4] Drops 버튼 클릭 : PASS")
    except Exception as e:
        print("[TC4] Drops 버튼 클릭 : FAIL")
        print("  ↳ 에러:", e)
        return False

    # 'Drops 시작하기' 문구 노출 판정
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                AppiumBy.XPATH,
                '//android.widget.TextView[@text="Drops 시작하기"]'
            ))
        )
        print(" 판정) 'Drops 시작하기' 노출 : PASS")
        return True
    except Exception as e:
        print(" 판정) 'Drops 시작하기' 노출 : FAIL")
        print("  ↳ 에러:", e)
        return False


def tc5(driver) -> bool:
    # Drops 닫기 클릭
    drops_btn = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((
            AppiumBy.XPATH,'//android.widget.ImageView[@content-desc="닫기"]'
            )))
    drops_btn.click()
    
    """위시리스트 버튼 클릭 후 '위시리스트' 노출 확인"""
    try:
        # 위시리스트 버튼 클릭
        drops_btn = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                AppiumBy.XPATH,
                '//android.widget.TextView[@resource-id="net.skyscanner.android.main:id/navigation_bar_item_small_label_view" and @text="위시리스트"]'
            ))
        )
        drops_btn.click()
        print("[TC5] 위시리스트 버튼 클릭 완료")

        # 클릭 후 'Drops 자세히 알아보기' 노출 확인
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                AppiumBy.XPATH,
                '(//android.widget.TextView[@text="위시리스트"])[1]'
            ))
        )
        print("판정) '위시리스트' 노출 확인 : PASS")
        return True

    except Exception as e:
        print("판정) '위시리스트' 노출 실패 : FAIL")
        print("↳ 에러:", e)
        return False
    

def tc6(driver) -> bool:
    """검색 → 항공권 → 출발/도착 지정 → 검색 → 결과 8개 판정"""
    ok = True
    wait = WebDriverWait(driver, 10)

    try:
        # 1) 하단탭 '검색'
        el = wait.until(EC.element_to_be_clickable((
            AppiumBy.XPATH,
            '//android.widget.TextView[@resource-id="net.skyscanner.android.main:id/navigation_bar_item_small_label_view" and @text="검색"]'
        )))
        el.click(); print("  1) 검색 클릭")
    except Exception as e:
        print("  1) 검색 실패:", e); ok = False

    try:
        # 2) 메인 카드 '항공권'
        el = wait.until(EC.element_to_be_clickable((
            AppiumBy.XPATH, "//android.widget.ImageView[@content-desc='항공권']"
        )))
        el.click(); print("  2) 항공권 클릭")
    except Exception as e:
        print("  2) 항공권 실패:", e); ok = False

    try:
        # 2) 메인 카드 '항공권'
        el = wait.until(EC.element_to_be_clickable((
            AppiumBy.XPATH, "//android.widget.TextView[@text='닫기']"
        )))
        el.click(); print("  3) 닫기 클릭")
    except Exception as e:
        print("  3) 닫기 실패:", e); ok = False

    try:
        # 3) 출발지
        el = wait.until(EC.element_to_be_clickable((
            AppiumBy.XPATH,
            '//android.widget.TextView[@resource-id="net.skyscanner.android.main:id/placeText" and contains(@text, "출발지")]'
        )))
        el.click(); print("  4) 출발지 클릭")
    except Exception as e:
        print("  4) 출발지 실패:", e); ok = False

    try:
        # 4) 인천(ICN)
        el = wait.until(EC.element_to_be_clickable((
            AppiumBy.XPATH,
            '//android.widget.TextView[contains(@text, "인천") and contains(@text, "ICN")]'
        )))
        el.click(); print("  5) 인천(ICN) 클릭")
    except Exception as e:
        print("  5) 인천(ICN) 실패:", e); ok = False

    try:
        # 5) 도착지
        el = wait.until(EC.element_to_be_clickable((
            AppiumBy.XPATH,
            '//android.widget.TextView[@resource-id="net.skyscanner.android.main:id/placeText" and contains(@text, "도착지")]'
        )))
        el.click(); print("  6) 도착지 클릭")
    except Exception as e:
        print("  6) 도착지 실패:", e); ok = False

    try:
        # 6) 방콕(모두)
        el = wait.until(EC.element_to_be_clickable((
            AppiumBy.XPATH,
            '//android.widget.TextView[contains(@text, "방콕")]'
        )))
        el.click(); print("  7) 방콕 클릭")
    except Exception as e:
        print("  7) 방콕 실패:", e); ok = False

    try:
        # 7) 검색 버튼
        el = wait.until(EC.element_to_be_clickable((
            AppiumBy.ID, "net.skyscanner.android.main:id/searchButton"
        )))
        el.click(); print("  8) 검색 버튼 클릭")
    except Exception as e:
        print("  8) 검색 버튼 실패:", e); ok = False

    # ===== 결과 판정: itineraryCard 8개인지 확인 =====
    try:
        time.sleep(2)  # 로딩 대기
        elements = driver.find_elements(
            AppiumBy.XPATH,
            '//androidx.compose.ui.platform.ComposeView[@resource-id="net.skyscanner.android.main:id/itineraryCard"][1]//android.view.View'
        )
        count = len(elements)
        print(f"[TC6] 발견된 View 개수: {count}")

        if count == 8:
            print("✅ PASS - 8개 발견")
            return True
        else:
            print(f"❌ FAIL - 기대: 8개, 실제: {count}")
            return False
    except Exception as e:
        print("❌ FAIL - 요소 탐색 실패")
        print("   ↳ 에러:", e)
        return False
    
def main():
    driver = make_driver()
    logger = ResultLogger()
    try:
        test_cases = [
            ("TC1 앱 실행 확인", tc1),
            ("TC2 로그인 확인", tc2),
            ("TC3 메인 문구 확인", tc3),
            ("TC4 Drops 확인", tc4),
            ("TC5 위시리스트 확인", tc5),  
            ("TC6 상단 메뉴- 항공권 확인", tc6),  
        ]

        for tc_name, tc_fn in test_cases:
            print(f"\n====== {tc_name} 시작 ======")
            result = False
            note = ""
            try:
                result = tc_fn(driver)
            except Exception as e:
                result = False
                note = f"Exception: {e}"
            print(f"결과: {'✅ PASS' if result else '❌ FAIL'}")
            logger.add(tc_name, result, note)

    finally:
        driver.quit()
        print("\n드라이버 종료")

        # 엑셀 저장
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = f"tc_results_{ts}.xlsx"
        logger.export_excel(out_path)

        # 콘솔에 PASS 리스트 출력
        pass_list = [row["TC"] for row in logger.rows if row["Status"] == "PASS"]
        fail_list = [row["TC"] for row in logger.rows if row["Status"] == "FAIL"]

        print(f"\n[📊 테스트 요약]")
        print(f"총 {len(logger.rows)}건 / PASS: {len(pass_list)}건 / FAIL: {len(fail_list)}건")
        print(f"✅ PASS 리스트: {', '.join(pass_list) if pass_list else '없음'}")
        print(f"❌ FAIL 리스트: {', '.join(fail_list) if fail_list else '없음'}")

        print(f"\n엑셀 저장 완료: {out_path}")


if __name__ == "__main__":
    main()