import json
import re
import time

import requests
from PySide6.QtCore import QThread, Signal
from bs4 import BeautifulSoup

from utils import clean_cell_value



class DetailFetchThread(QThread):
    result_signal = Signal(dict)  # 크롤링 결과
    image_signal = Signal(dict)   # 이미지 정보
    log_signal = Signal(str)


    def __init__(self, detail_link, index, total_length, is_etc_only, etc_values):
        super().__init__()
        self.detail_link = detail_link
        self.index = index
        self.total_length = total_length
        self.is_etc_only = is_etc_only
        self.etc_values = etc_values

    def run(self):
        try:
            self.log_signal.emit(f"🔎 크롤링 시작: {self.index + 1}/{self.total_length}")
            response = requests.get(self.detail_link)
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'html.parser')
            time.sleep(1)

            data = {}

            price = soup.select_one(".sprinkles_fontSize_300_base__1byufe8uy.sprinkles_fontSize_400_small__1byufe8v3.sprinkles_fontSize_500_medium__1byufe8v8.sprinkles_fontWeight_bold__1byufe81z.sprinkles_lineHeight_heading\.medium_base__1byufe8vi.sprinkles_lineHeight_heading\.large_small__1byufe8vn.sprinkles_lineHeight_heading\.xlarge_medium__1byufe8vs").text.replace('판매중', '').strip()
            data['가격'] = clean_cell_value(price)

            seller_name = soup.select_one("._144m93ve._144m93vf._144m93vk._144m93vm._144m93vq").text.strip()
            if seller_name is None:
                seller_name = soup.select_one("._1mr23zje._1mr23zjf._1mr23zjk._1mr23zjm._1mr23zjq").text.strip()
            seller_name = clean_cell_value(seller_name)
            if soup.select_one("._1mr23zjd.h4it890") is None:
                seller_name = seller_name + " / 공인중개사"
            else:
                seller_name = seller_name + " / 개인"
            data['판매자 이름'] = seller_name

            detail_table = soup.select(
                ".sprinkles_display_flex_base__1byufe82i.sprinkles_alignItems_center_base__1byufe8si.sprinkles_gap_1_base__1byufe8qe.sprinkles_flexGrow_1_base__1byufe8u2"
            )
            for table in detail_table:
                dt = table.select_one("dt")
                dd = table.select_one("dd")
                if dt and dd:
                    key = clean_cell_value(dt.text.strip())
                    div = dd.select_one("div")
                    value = div.text.strip() if div else dd.text.strip()

                    if (
                            self.is_etc_only
                            and key == "건축물 용도"
                            and value not in self.etc_values
                    ):
                        continue

                    data[key] = clean_cell_value(value)

            if (
                    self.is_etc_only
                    and "토지" in self.etc_values
                    and "건축물 용도" not in data
            ):
                data['건축물 용도'] = '토지'

            contents = soup.select_one(".sprinkles_fontSize_200_base__1byufe8uu.sprinkles_fontWeight_regular__1byufe81x.sprinkles_lineHeight_body\\.medium_base__1byufe8w6.sprinkles_color_neutral__1byufe81._12k38uc8")
            if contents is None:
                contents = soup.select_one(".sprinkles_fontSize_200_base__1byufe8uu.sprinkles_fontWeight_regular__1byufe81x.sprinkles_lineHeight_body\\.medium_base__1byufe8w6.sprinkles_color_neutral__1byufe81._135xx788")

            if contents:
                data["내용"] = clean_cell_value(contents.text.strip())

            address = soup.select_one(".sprinkles_display_flex_base__1byufe82i.sprinkles_gap_2_base__1byufe8qi.sprinkles_alignItems_flexStart_base__1byufe8se.sprinkles_marginTop_1_base__1byufe8hy")
            if address:
                data["주소"] = clean_cell_value(address.text[:-2].strip())

            data["상세페이지 링크"] = self.detail_link

            # 이미지 처리
            images = soup.select("._7rso270.sprinkles_width_full_base__1byufe84q.sprinkles_height_full_base__1byufe86u.sprinkles_cursor_default__1byufe81n._7rso271")
            for idx, img in enumerate(images):
                src = img.attrs['src']
                if "주소" in data:
                    file_name = f'{data["주소"]}_{idx + 1}.jpg'
                    self.image_signal.emit({'file_name': file_name, 'image_src': src})

            self.result_signal.emit(data)
            #print(f"✅ DetailFetchThread 끝: {self.detail_link}")
            self.log_signal.emit(f"✅ 크롤링 완료: {self.detail_link}")

        except Exception as e:
            print(f"❌ Error while processing {self.detail_link}: {e}")
