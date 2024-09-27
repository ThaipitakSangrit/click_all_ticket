import subprocess
import ntplib
from datetime import datetime, timedelta
import re
from time import ctime, sleep
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui

# กำหนดเส้นทางไปยัง Microsoft Edge
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# กำหนดพอร์ตสำหรับการดีบักระยะไกล
remote_debugging_port = "9222"

# กำหนดไดเรกทอรีข้อมูลผู้ใช้
user_data_dir = r"C:\EdgeUserData"

# กำหนด URL ที่จะเปิด
url = "https://www.allticket.com"

# ฟังก์ชันสำหรับเปิดเบราว์เซอร์
def open_browser():
    command = [
        edge_path,
        f"--remote-debugging-port={remote_debugging_port}",
        f"--user-data-dir={user_data_dir}",
        url
    ]
    subprocess.Popen(command)

# ฟังก์ชันสำหรับเปิดเว็บเพจ
def open_web():
    # สร้างตัวเลือกสำหรับ Edge
    options = Options()
    options.debugger_address = f"localhost:{remote_debugging_port}"

    global driver
    # Initialize Edge WebDriver with executable path
    driver = webdriver.Edge(options=options)
            
    print("Open Web")
    driver.get(url)

# ฟังก์ชันสำหรับเลือกตั๋ว
def choose_ticket(driver):
    try:
        # ticket path [change ticket]
        button_xpath = '/html/body/app-root/app-home/main/section[2]/div/div[3]/app-card-ticket/div/div/div[5]/div/button' #
        # button_xpath = '/html/body/app-root/app-home/main/section[2]/div/div[1]/app-card-ticket/div/div/div[4]/div/button'
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, button_xpath)))

        # Click the button BuyNow First Page
        button = driver.find_element(By.XPATH, button_xpath)
        button.click()

        # รอจนกว่าข้อความจะปรากฏ
        text_xpath = '/html/body/app-root/app-event-info/div/div[2]/div[2]/div/div[2]/div[2]/div/div[2]/span'
        element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, text_xpath)))

        # ดึงข้อความจากองค์ประกอบ
        text = element.text
        
        # ใช้ Regular Expression เพื่อแยกเวลา
        times = re.findall(r'\d{2}:\d{2}', text)

        # ตรวจสอบว่าเรามีเวลาทั้งหมดที่เราต้องการ
        if times:
            first_time = times[0]
            global start_click_time
            start_click_time = first_time + ":00"  # เติม :00 ที่ท้าย

            # แปลงสตริงเวลาเป็น datetime object
            time_format = "%H:%M:%S"
            time_obj = datetime.strptime(start_click_time, time_format)

            # ลบ 2 วินาที
            F5_time_obj = time_obj - timedelta(seconds=2)

            # แปลง datetime object กลับเป็นสตริง
            global F5_click_time
            F5_click_time = F5_time_obj.strftime(time_format)
            print("F5 time : ", F5_click_time)
            print("Start click time : ", start_click_time)
    except Exception as e:
        print(f"Error in choose_ticket: {e}")

# ฟังก์ชันเพื่อดึงเวลา NTP
def get_ntp_time():
    client = ntplib.NTPClient()
    retries = 5
    for _ in range(retries):
        try:
            response = client.request('time.google.com', timeout=5)
            return ctime(response.tx_time)
        except ntplib.NTPException as e:
            print(f"Error fetching NTP time: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        sleep(1)  # Wait before retrying
    raise Exception("Failed to fetch NTP time after several attempts")

# ฟังก์ชันเพื่อเริ่มทำงาน
def start_buy():

    # Click the button BuyNow Second Page
    button_xpath = '/html/body/app-root/app-event-info/div/div[2]/div[2]/div/div[5]/div/button'
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
    button = driver.find_element(By.XPATH, button_xpath)
    button.click()

    # Check the consent checkbox
    consent_xpath = '/html/body/app-root/app-consent-buy/div/div[2]/div/div'
    consent = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, consent_xpath)))
    consent.click()

    # Find the "Confirm" button
    confirm_button_xpath = "//*[contains(text(), 'Confirm')]"
    confirm_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, confirm_button_xpath)))
    confirm_button.click()

def select_seat_area():

    zone = "A1"
    row = "M"
    seat = 5

    # รอให้ <map> โหลดขึ้นมา
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'map')))

    # ค้นหา <area> ที่มี data-zone ตรงกับค่าใน zone
    area_element = driver.find_element(By.XPATH, f'//area[@data-zone="{zone}"]')

    # คลิกที่ <area>
    area_element.click()
    print(f"คลิกที่ <area> ที่มี data-zone = {zone} สำเร็จ")

    # รอจนกว่า <tr> ทั้งหมดใน <tbody> จะโหลดขึ้นมา
    tr_elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tbody tr.seat-rotate.ng-star-inserted')))

    # สร้างลิสต์เพื่อเก็บกลุ่มของ <tr>
    tr_groups = []
    group_name = None

    # สำหรับแต่ละ <tr>
    for tr in tr_elements:
        # หา <td> ที่มีคลาส "td.header-row.row-end" ใน <tr>
        end_td_elements = tr.find_elements(By.CSS_SELECTOR, 'td.header-row.row-end')

        seat_td_elements = tr.find_elements(By.CSS_SELECTOR, 'td.ng-star-inserted')

        # หากพบ <td> ที่ตรงตามเงื่อนไข
        if end_td_elements:
            # ตั้งชื่อกลุ่มตามค่าข้างใน <td> = A
            group_name = end_td_elements[0].text.strip()  # ดึงข้อความจาก <td>

            # เพิ่มกลุ่ม <tr> ลงในลิสต์หลัก = [A,tr]
            tr_groups.append((group_name, seat_td_elements))

            # เริ่มกลุ่มใหม่
            seat_td_elements = []

    list_td = []
    for i ,(name, group) in enumerate(tr_groups):
        if name == row:  # ตรงกับแถว
            for td in group:
                list_td.append(td)
                if len(list_td) == int(seat):
                    # หา <td> ที่ถูกต้องสำหรับที่นั่ง
                    target_td = list_td[int(seat)-1]  # ลบ 1 เพราะ seat เริ่มนับจาก 1

                     # ค้นหา <div> ภายใน <td>
                    div_elements = target_td.find_element(By.TAG_NAME, 'div')

                    # ค้นหา <svg> ภายใน <div>
                    svg_elements = div_elements.find_elements(By.TAG_NAME, 'svg')
                    
                    for svg in svg_elements:
                        svg.click()
                            
def select_unseat_area():
    # รอให้ <map> โหลดขึ้นมา
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'map')))

    area_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'area')))
    area_element.click()

# ฟังก์ชันหลักสำหรับการทำงาน
def main():
    try:
        open_browser()
        open_web()
        choose_ticket(driver)

        while True:
            current_time = get_ntp_time()
            print(f"Current NTP time: {current_time}")
            sleep(0.5)
            if current_time.split()[3] == "16:25:58":
                print("Press F5")
                pyautogui.press('f5')  # กดปุ่ม F5 เพื่อรีหน้าเว็บ
                sleep(1)
                start_buy()
                select_seat_area()
                # select_unseat_area()

    except KeyboardInterrupt:
        print("Process interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
if __name__ == "__main__":
    main()