import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_user_info():
    info_path = "./user.info"
    with open(info_path, "r") as f:
        info = f.read()
    user_name, user_passwd = "", ""
    info = info.split("\n")
    for ln in info:
        if "user" in ln:
            user_name = ln.split(':')[-1].strip()
        if "passwd" in ln:
            user_passwd = ln.split(':')[-1].strip()

    return {"user": user_name, "passwd": user_passwd}


def check_relc_status():
    previous_msg = 'Registration: [Opens on the 3rd of May 2021, Monday - 9am DELAYED (to be advised by CEA)]'
    driver_path = '/Users/yunfan/Documents/Scraping/chromedriver'
    relc_url = "https://www.relc.org.sg/professional-qualifications/skills/cea-res"
    chromeOptions = Options()
    chromeOptions.headless = True
    wd = webdriver.Chrome(executable_path=driver_path, options=chromeOptions)
    # print("Current session is {}".format(wd.session_id))
    wd.get(relc_url)
    xpath = "/html/body/div[2]/main/div/div[1]/div/div/div/div[2]/section/div/div/div/div[1]/div[2]/div/ul[1]"
    try:
        status = wd.find_element_by_xpath(xpath)
        body = status.text
    except:
        print("cannot find element")
    wd.close()
    wd.quit()

    # construct email
    if body != previous_msg:
        # s = smtplib.SMTP ('smtp.gmail.com', 587)
        s = smtplib.SMTP(host='smtp-mail.outlook.com', port=587)
        # tls port is 587
        s.starttls()
        user_info = get_user_info()
        s.login(user_info["user_name"], user_info["user_passwd"])
        msg = MIMEMultipart()       # create a message
        msg['From'] = user_info["user_name"]
        msg['To'] = "yunfan.zhang23@gmail.com"
        msg['Subject'] = "Status From RELC Res Web"
        print(body)
        msg.attach(MIMEText(body, 'plain'))
        s.send_message(msg)
        print('E-mail is sent')
    else:
        print('No Update yet...')


if __name__ == '__main__':
    check_relc_status()
