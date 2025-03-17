import requests
import random
import datetime
import emoji
import os
import re
import time
import json
import telebot
import mysql.connector
from telebot import types
from colorama import init, Fore, Style

API_KEY = '7914109458:AAFWgoFEF-mb_ovOX5OAN131NSCA1ekrduA'
bot = telebot.TeleBot(API_KEY, parse_mode=None)
admin_ids = [7491211987]
def la_admin(user_id):
  return user_id in admin_ids

# Khởi tạo colorama
init()

# Khai báo biến toàn cục
db_conn = None
db_cursor = None


# Hàm để kết nối đến cơ sở dữ liệu
def connect_to_database():
  global db_conn
  try:
    if not db_conn:
      db_conn = mysql.connector.connect(host="103.97.126.29",
user="zgjgagoa_taivp",
password="WQgQgdfk389mY4BB2PXn",
database="zgjgagoa_taivp")
    return db_conn, db_conn.cursor()
  except mysql.connector.Error as e:
    print(f"Lỗi khi kết nối đến cơ sở dữ liệu: {e}")
    return None, None


# Hàm để thực hiện truy vấn SELECT
def execute_select_query(query, params=None):
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return None

  try:
    db_cursor.execute(query, params)
    result = db_cursor.fetchall()
    return result
  except mysql.connector.Error as e:
    print(f"Lỗi khi thực hiện truy vấn SELECT: {e}")
    return None


# Hàm để thực hiện truy vấn INSERT, UPDATE hoặc DELETE
def execute_non_select_query(query, params=None):
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return False

  try:
    db_cursor.execute(query, params)
    db_conn.commit()
    return True
  except mysql.connector.Error as e:
    print(f"Lỗi khi thực hiện truy vấn INSERT, UPDATE hoặc DELETE: {e}")
    return False


# Gọi hàm kết nối đến cơ sở dữ liệu
db_conn, db_cursor = connect_to_database()

# Kiểm tra xem kết nối đã thành công hay chưa
if db_conn and db_cursor:
  print(Fore.GREEN + "Kết nối đến cơ sở dữ liệu thành công!" + Style.RESET_ALL)
else:
  print("Không thể kết nối đến cơ sở dữ liệu.")


# Hàm để đóng kết nối đến cơ sở dữ liệu
def close_database_connection():
  global db_conn
  try:
    if db_conn:
      db_conn.close()
      db_conn = None
      print(Fore.YELLOW + "Đã đóng kết nối đến cơ sở dữ liệu." +
            Style.RESET_ALL)
  except mysql.connector.Error as e:
    print(f"Lỗi khi đóng kết nối đến cơ sở dữ liệu: {e}")


#trạng thái .....
user_state = {}
# trạng thái game tai xiu
user_state_tx = {}
#trạng thái game chẵn lẻ
user_state_cl = {}
#trạng thái game tài xỉu 2
user_state_tx2 = {}
#trạng thái game chẵn lẻ 2
user_state_cl2 = {}
# trạng thái game 1 phần 3
user_state_phanba = {}
# trạng thái game đoán số
user_state_doan = {}
# trạng thái game bầu cua
user_state_bc = {}
# trạng thái tạo code
user_state_cd = {}
# trạng thái setsodu
user_state_sd = {}
# Dùng từ điển để lưu số dư của người dùng
user_balance = {}
# Khởi tạo từ điển để lưu số tiền cược của từng người dùng
user_bet_amount = {}

###HÀM LƯU ALL LỊCH SỬ CHƠI#####


def save_to_alichsuchoi(telegram_id, ket_qua, cuoc, so_tien_cuoc,
                        so_tien_thang, loai_game, thoi_gian):
  try:
    db_conn, db_cursor = connect_to_database()

    # Truy vấn để chèn dữ liệu vào bảng alichsuchoi
    query = "INSERT INTO alichsuchoi (telegram_id, ket_qua, cuoc, so_tien_cuoc, so_tien_thang, loai_game, thoi_gian) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    params = (telegram_id, ket_qua, cuoc, so_tien_cuoc, so_tien_thang,
              loai_game, thoi_gian)
    db_cursor.execute(query, params)

    # Lưu thay đổi vào cơ sở dữ liệu
    db_conn.commit()

    # Đóng con trỏ cơ sở dữ liệu
    db_cursor.close()

    # In ra thông báo nếu lưu thành công
    print("Đã cập nhật all lịch sử chơi mới!")
  except mysql.connector.Error as e:
    print(f"Lỗi khi lưu all lịch sử chơi: {e}")


############Hàm lưu thống kê tài xỉu#####################
def get_or_create_thongketx():
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return None

  try:
    # Thực hiện truy vấn SELECT để lấy bản ghi duy nhất từ bảng thongketx
    query = "SELECT * FROM thongketx"
    db_cursor.execute(query)
    result = db_cursor.fetchone()

    if result:
      # Nếu đã có bản ghi, trả về thông tin
      return {
          "tong_tien_cuoc": result[0],
          "tong_tien_da_tra": result[1],
          "so_lan_cuoc_tai": result[2],
          "so_lan_cuoc_xiu": result[3]
      }
    else:
      # Nếu chưa có bản ghi, tạo bản ghi mới với các giá trị ban đầu là 0
      query = "INSERT INTO thongketx (tong_tien_cuoc, tong_tien_da_tra, so_lan_cuoc_tai, so_lan_cuoc_xiu) VALUES (0, 0, 0, 0)"
      db_cursor.execute(query)
      db_conn.commit()
      return {
          "tong_tien_cuoc": 0,
          "tong_tien_da_tra": 0,
          "so_lan_cuoc_tai": 0,
          "so_lan_cuoc_xiu": 0
      }

  except mysql.connector.Error as e:
    print(
        f"Lỗi khi thực hiện truy vấn SELECT hoặc INSERT vào bảng thongketx: {e}"
    )
    return None


def update_thongketx(tien_cuoc, tien_tra, loai_cuoc):
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return

  try:
    # Lấy thông tin thongketx hiện tại
    thongke_info = get_or_create_thongketx()

    if loai_cuoc == "tai":
      # Cập nhật tổng tiền cược, tổng tiền trả, số lần cược tài
      thongke_info["tong_tien_cuoc"] += tien_cuoc
      thongke_info["tong_tien_da_tra"] += tien_tra
      thongke_info["so_lan_cuoc_tai"] += 1
    elif loai_cuoc == "xiu":
      # Cập nhật tổng tiền cược, tổng tiền trả, số lần cược xỉu
      thongke_info["tong_tien_cuoc"] += tien_cuoc
      thongke_info["tong_tien_da_tra"] += tien_tra
      thongke_info["so_lan_cuoc_xiu"] += 1

    # Cập nhật thông tin vào bảng thongketx
    query = "UPDATE thongketx SET tong_tien_cuoc=%s, tong_tien_da_tra=%s, so_lan_cuoc_tai=%s, so_lan_cuoc_xiu=%s"
    db_cursor.execute(
        query,
        (thongke_info["tong_tien_cuoc"], thongke_info["tong_tien_da_tra"],
         thongke_info["so_lan_cuoc_tai"], thongke_info["so_lan_cuoc_xiu"]))
    db_conn.commit()

  except mysql.connector.Error as e:
    print(f"Lỗi khi cập nhật thông tin vào bảng thongketx: {e}")


#############Hàm lưu thống kê chẵn lẻ##############


def get_or_create_thongkecl():
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return None

  try:
    # Thực hiện truy vấn SELECT để lấy bản ghi duy nhất từ bảng thongkecl
    query = "SELECT * FROM thongkecl"
    db_cursor.execute(query)
    result = db_cursor.fetchone()

    if result:
      # Nếu đã có bản ghi, trả về thông tin
      return {
          "tong_tien_cuoc": result[0],
          "tong_tien_da_tra": result[1],
          "so_lan_cuoc_chan": result[2],
          "so_lan_cuoc_le": result[3]
      }
    else:
      # Nếu chưa có bản ghi, tạo bản ghi mới với các giá trị ban đầu là 0
      query = "INSERT INTO thongkecl (tong_tien_cuoc, tong_tien_da_tra, so_lan_cuoc_chan, so_lan_cuoc_le) VALUES (0, 0, 0, 0)"
      db_cursor.execute(query)
      db_conn.commit()
      return {
          "tong_tien_cuoc": 0,
          "tong_tien_da_tra": 0,
          "so_lan_cuoc_chan": 0,
          "so_lan_cuoc_le": 0
      }

  except mysql.connector.Error as e:
    print(
        f"Lỗi khi thực hiện truy vấn SELECT hoặc INSERT vào bảng thongkecl: {e}"
    )
    return None


def update_thongkecl(tien_cuoc, tien_tra, loai_cuoc):
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return

  try:
    # Lấy thông tin thongkecl hiện tại
    thongke_info = get_or_create_thongkecl()

    if loai_cuoc == "chan":
      # Cập nhật tổng tiền cược, tổng tiền trả, số lần cược chẵn
      thongke_info["tong_tien_cuoc"] += tien_cuoc
      thongke_info["tong_tien_da_tra"] += tien_tra
      thongke_info["so_lan_cuoc_chan"] += 1
    elif loai_cuoc == "le":
      # Cập nhật tổng tiền cược, tổng tiền trả, số lần cược lẻ
      thongke_info["tong_tien_cuoc"] += tien_cuoc
      thongke_info["tong_tien_da_tra"] += tien_tra
      thongke_info["so_lan_cuoc_le"] += 1

    # Cập nhật thông tin vào bảng thongkecl
    query = "UPDATE thongkecl SET tong_tien_cuoc=%s, tong_tien_da_tra=%s, so_lan_cuoc_chan=%s, so_lan_cuoc_le=%s"
    db_cursor.execute(
        query,
        (thongke_info["tong_tien_cuoc"], thongke_info["tong_tien_da_tra"],
         thongke_info["so_lan_cuoc_chan"], thongke_info["so_lan_cuoc_le"]))
    db_conn.commit()

  except mysql.connector.Error as e:
    print(f"Lỗi khi cập nhật thông tin vào bảng thongkecl: {e}")


###############Hàm lưu thống kê tài xỉu 2############################3


def get_or_create_thongketx2():
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return None

  try:
    # Thực hiện truy vấn SELECT để lấy bản ghi duy nhất từ bảng thongketx2
    query = "SELECT * FROM thongketx2"
    db_cursor.execute(query)
    result = db_cursor.fetchone()

    if result:
      # Nếu đã có bản ghi, trả về thông tin
      return {
          "tong_tien_cuoc": result[0],
          "tong_tien_da_tra": result[1],
          "so_lan_cuoc_tai2": result[2],
          "so_lan_cuoc_xiu2": result[3]
      }
    else:
      # Nếu chưa có bản ghi, tạo bản ghi mới với các giá trị ban đầu là 0
      query = "INSERT INTO thongketx2 (tong_tien_cuoc, tong_tien_da_tra, so_lan_cuoc_tai2, so_lan_cuoc_xiu2) VALUES (0, 0, 0, 0)"
      db_cursor.execute(query)
      db_conn.commit()
      return {
          "tong_tien_cuoc": 0,
          "tong_tien_da_tra": 0,
          "so_lan_cuoc_tai2": 0,
          "so_lan_cuoc_xiu2": 0
      }

  except mysql.connector.Error as e:
    print(
        f"Lỗi khi thực hiện truy vấn SELECT hoặc INSERT vào bảng thongketx2: {e}"
    )
    return None


def update_thongketx2(tien_cuoc, tien_tra, so_lan_cuoc_tai, so_lan_cuoc_xiu):
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return

  try:
    # Lấy thông tin thongketx2 hiện tại
    thongke_info = get_or_create_thongketx2()

    # Cập nhật tổng tiền cược, tổng tiền đã trả, số lần cược Tài và Xỉu
    thongke_info["tong_tien_cuoc"] += tien_cuoc
    thongke_info["tong_tien_da_tra"] += tien_tra
    thongke_info["so_lan_cuoc_tai2"] += so_lan_cuoc_tai
    thongke_info["so_lan_cuoc_xiu2"] += so_lan_cuoc_xiu

    # Cập nhật thông tin vào bảng thongketx2
    query = "UPDATE thongketx2 SET tong_tien_cuoc=%s, tong_tien_da_tra=%s, so_lan_cuoc_tai2=%s, so_lan_cuoc_xiu2=%s"
    db_cursor.execute(
        query,
        (thongke_info["tong_tien_cuoc"], thongke_info["tong_tien_da_tra"],
         thongke_info["so_lan_cuoc_tai2"], thongke_info["so_lan_cuoc_xiu2"]))
    db_conn.commit()

  except mysql.connector.Error as e:
    print(f"Lỗi khi cập nhật thông tin vào bảng thongketx2: {e}")


####################HÀM LƯU THỐNG KÊ CHẴN LẺ 2###########333333333


def get_or_create_thongkecl2():
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return None

  try:
    # Thực hiện truy vấn SELECT để lấy bản ghi duy nhất từ bảng thongkecl2
    query = "SELECT * FROM thongkecl2"
    db_cursor.execute(query)
    result = db_cursor.fetchone()

    if result:
      # Nếu đã có bản ghi, trả về thông tin
      return {
          "tong_tien_cuoc": result[0],
          "tong_tien_da_tra": result[1],
          "so_lan_cuoc_chan2": result[2],
          "so_lan_cuoc_le2": result[3]
      }
    else:
      # Nếu chưa có bản ghi, tạo bản ghi mới với các giá trị ban đầu là 0
      query = "INSERT INTO thongkecl2 (tong_tien_cuoc, tong_tien_da_tra, so_lan_cuoc_chan2, so_lan_cuoc_le2) VALUES (0, 0, 0, 0)"
      db_cursor.execute(query)
      db_conn.commit()
      return {
          "tong_tien_cuoc": 0,
          "tong_tien_da_tra": 0,
          "so_lan_cuoc_chan2": 0,
          "so_lan_cuoc_le2": 0
      }

  except mysql.connector.Error as e:
    print(
        f"Lỗi khi thực hiện truy vấn SELECT hoặc INSERT vào bảng thongkecl2: {e}"
    )
    return None


def update_thongkecl2(tien_cuoc, tien_tra, loai_cuoc):
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return

  try:
    # Lấy thông tin thongkecl2 hiện tại
    thongke_info = get_or_create_thongkecl2()

    if loai_cuoc == "chan2":
      # Cập nhật tổng tiền cược, tổng tiền trả, số lần cược chẵn
      thongke_info["tong_tien_cuoc"] += tien_cuoc
      thongke_info["tong_tien_da_tra"] += tien_tra
      thongke_info["so_lan_cuoc_chan2"] += 1
    elif loai_cuoc == "le2":
      # Cập nhật tổng tiền cược, tổng tiền trả, số lần cược lẻ
      thongke_info["tong_tien_cuoc"] += tien_cuoc
      thongke_info["tong_tien_da_tra"] += tien_tra
      thongke_info["so_lan_cuoc_le2"] += 1

    # Cập nhật thông tin vào bảng thongkecl2
    query = "UPDATE thongkecl2 SET tong_tien_cuoc=%s, tong_tien_da_tra=%s, so_lan_cuoc_chan2=%s, so_lan_cuoc_le2=%s"
    db_cursor.execute(
        query,
        (thongke_info["tong_tien_cuoc"], thongke_info["tong_tien_da_tra"],
         thongke_info["so_lan_cuoc_chan2"], thongke_info["so_lan_cuoc_le2"]))
    db_conn.commit()

  except mysql.connector.Error as e:
    print(f"Lỗi khi cập nhật thông tin vào bảng thongkecl2: {e}")


##############HÀM LƯU THỐN KÊ 1 PHẦN 3######################


# Hàm lấy thông tin từ bảng thongke1p3 hoặc tạo mới nếu chưa có
def get_or_create_thongke1p3():
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return None

  try:
    # Thực hiện truy vấn SELECT để lấy bản ghi duy nhất từ bảng thongke1p3
    query = "SELECT * FROM thongke1p3"
    db_cursor.execute(query)
    result = db_cursor.fetchone()

    if result:
      # Nếu đã có bản ghi, trả về thông tin
      return {
          "tong_tien_cuoc": result[0],
          "tong_tien_da_tra": result[1],
          "so_lan_cuoc_n0": result[2],
          "so_lan_cuoc_n1": result[3],
          "so_lan_cuoc_n2": result[4],
          "so_lan_cuoc_n3": result[5]
      }
    else:
      # Nếu chưa có bản ghi, tạo bản ghi mới với các giá trị ban đầu là 0
      query = "INSERT INTO thongke1p3 (tong_tien_cuoc, tong_tien_da_tra, so_lan_cuoc_n0, so_lan_cuoc_n1, so_lan_cuoc_n2, so_lan_cuoc_n3) VALUES (0, 0, 0, 0, 0, 0)"
      db_cursor.execute(query)
      db_conn.commit()
      return {
          "tong_tien_cuoc": 0,
          "tong_tien_da_tra": 0,
          "so_lan_cuoc_n0": 0,
          "so_lan_cuoc_n1": 0,
          "so_lan_cuoc_n2": 0,
          "so_lan_cuoc_n3": 0
      }

  except mysql.connector.Error as e:
    print(
        f"Lỗi khi thực hiện truy vấn SELECT hoặc INSERT vào bảng thongke1p3: {e}"
    )
    return None


# Hàm cập nhật thông tin vào bảng thongke1p3 sau mỗi ván chơi
def update_thongke1p3(tong_tien_cuoc, tong_tien_da_tra, so_lan_cuoc_n0,
                      so_lan_cuoc_n1, so_lan_cuoc_n2, so_lan_cuoc_n3):
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return

  try:
    # Lấy thông tin thongke1p3 hiện tại
    thongke_info = get_or_create_thongke1p3()

    # Cập nhật thông tin
    thongke_info["tong_tien_cuoc"] += tong_tien_cuoc
    thongke_info["tong_tien_da_tra"] += tong_tien_da_tra
    thongke_info["so_lan_cuoc_n0"] += so_lan_cuoc_n0
    thongke_info["so_lan_cuoc_n1"] += so_lan_cuoc_n1
    thongke_info["so_lan_cuoc_n2"] += so_lan_cuoc_n2
    thongke_info["so_lan_cuoc_n3"] += so_lan_cuoc_n3

    # Cập nhật thông tin vào bảng thongke1p3
    query = "UPDATE thongke1p3 SET tong_tien_cuoc=%s, tong_tien_da_tra=%s, so_lan_cuoc_n0=%s, so_lan_cuoc_n1=%s, so_lan_cuoc_n2=%s, so_lan_cuoc_n3=%s"
    db_cursor.execute(
        query,
        (thongke_info["tong_tien_cuoc"], thongke_info["tong_tien_da_tra"],
         thongke_info["so_lan_cuoc_n0"], thongke_info["so_lan_cuoc_n1"],
         thongke_info["so_lan_cuoc_n2"], thongke_info["so_lan_cuoc_n3"]))
    db_conn.commit()

  except mysql.connector.Error as e:
    print(f"Lỗi khi cập nhật thông tin vào bảng thongke1p3: {e}")
    return


################HÀM LƯU THỐNG KÊ ĐOÁN SỐ #################


# Hàm lấy thông tin từ bảng thongke1p3 hoặc tạo mới nếu chưa có
def get_or_create_thongkeds():
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return None

  try:
    # Thực hiện truy vấn SELECT để lấy bản ghi duy nhất từ bảng thongke1p3
    query = "SELECT * FROM thongkeds"
    db_cursor.execute(query)
    result = db_cursor.fetchone()

    if result:
      # Nếu đã có bản ghi, trả về thông tin
      return {
          "tong_tien_cuoc": result[0],
          "tong_tien_da_tra": result[1],
          "so_lan_cuoc_d0": result[2],
          "so_lan_cuoc_d1": result[3],
          "so_lan_cuoc_d2": result[4],
          "so_lan_cuoc_d3": result[5],
          "so_lan_cuoc_d4": result[6],
          "so_lan_cuoc_d5": result[7],
          "so_lan_cuoc_d6": result[8],
          "so_lan_cuoc_d7": result[9],
          "so_lan_cuoc_d8": result[10],
          "so_lan_cuoc_d9": result[11]
      }
    else:
      # Nếu chưa có bản ghi, tạo bản ghi mới với các giá trị ban đầu là 0
      query = "INSERT INTO thongkeds (tong_tien_cuoc, tong_tien_da_tra, so_lan_cuoc_d0, so_lan_cuoc_d1, so_lan_cuoc_d2, so_lan_cuoc_d3, so_lan_cuoc_d4, so_lan_cuoc_d5, so_lan_cuoc_d6, so_lan_cuoc_d7, so_lan_cuoc_d8, so_lan_cuoc_d9) VALUES (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)"
      db_cursor.execute(query)
      db_conn.commit()
      return {
          "tong_tien_cuoc": 0,
          "tong_tien_da_tra": 0,
          "so_lan_cuoc_d0": 0,
          "so_lan_cuoc_d1": 0,
          "so_lan_cuoc_d2": 0,
          "so_lan_cuoc_d3": 0,
          "so_lan_cuoc_d4": 0,
          "so_lan_cuoc_d5": 0,
          "so_lan_cuoc_d6": 0,
          "so_lan_cuoc_d7": 0,
          "so_lan_cuoc_d8": 0,
          "so_lan_cuoc_d9": 0
      }

  except mysql.connector.Error as e:
    print(
        f"Lỗi khi thực hiện truy vấn SELECT hoặc INSERT vào bảng thongkeds: {e}"
    )
    return None


# Hàm cập nhật thông tin vào bảng thongke1p3 sau mỗi ván chơi
def update_thongkeds(tong_tien_cuoc, tong_tien_da_tra, so_lan_cuoc_d0,
                     so_lan_cuoc_d1, so_lan_cuoc_d2, so_lan_cuoc_d3,
                     so_lan_cuoc_d4, so_lan_cuoc_d5, so_lan_cuoc_d6,
                     so_lan_cuoc_d7, so_lan_cuoc_d8, so_lan_cuoc_d9):
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return

  try:
    # Lấy thông tin thongke1p3 hiện tại
    thongke_info = get_or_create_thongkeds()

    # Cập nhật thông tin
    thongke_info["tong_tien_cuoc"] += tong_tien_cuoc
    thongke_info["tong_tien_da_tra"] += tong_tien_da_tra
    thongke_info["so_lan_cuoc_d0"] += so_lan_cuoc_d0
    thongke_info["so_lan_cuoc_d1"] += so_lan_cuoc_d1
    thongke_info["so_lan_cuoc_d2"] += so_lan_cuoc_d2
    thongke_info["so_lan_cuoc_d3"] += so_lan_cuoc_d3
    thongke_info["so_lan_cuoc_d4"] += so_lan_cuoc_d4
    thongke_info["so_lan_cuoc_d5"] += so_lan_cuoc_d5
    thongke_info["so_lan_cuoc_d6"] += so_lan_cuoc_d6
    thongke_info["so_lan_cuoc_d7"] += so_lan_cuoc_d7
    thongke_info["so_lan_cuoc_d8"] += so_lan_cuoc_d8
    thongke_info["so_lan_cuoc_d9"] += so_lan_cuoc_d9

    # Cập nhật thông tin vào bảng thongkeds
    query = "UPDATE thongkeds SET tong_tien_cuoc=%s, tong_tien_da_tra=%s, so_lan_cuoc_d0=%s, so_lan_cuoc_d1=%s, so_lan_cuoc_d2=%s, so_lan_cuoc_d3=%s, so_lan_cuoc_d4=%s, so_lan_cuoc_d5=%s, so_lan_cuoc_d6=%s, so_lan_cuoc_d7=%s, so_lan_cuoc_d8=%s, so_lan_cuoc_d9=%s"
    db_cursor.execute(
        query,
        (thongke_info["tong_tien_cuoc"], thongke_info["tong_tien_da_tra"],
         thongke_info["so_lan_cuoc_d0"], thongke_info["so_lan_cuoc_d1"],
         thongke_info["so_lan_cuoc_d2"], thongke_info["so_lan_cuoc_d3"],
         thongke_info["so_lan_cuoc_d4"], thongke_info["so_lan_cuoc_d5"],
         thongke_info["so_lan_cuoc_d6"], thongke_info["so_lan_cuoc_d7"],
         thongke_info["so_lan_cuoc_d8"], thongke_info["so_lan_cuoc_d9"]))
    db_conn.commit()

  except mysql.connector.Error as e:
    print(f"Lỗi khi cập nhật thông tin vào bảng thongkeds: {e}")
    return

##################HÀM LƯU THỐNG KÊ BẦU CUA#####################


# Hàm lấy thông tin từ bảng thongkebc hoặc tạo mới nếu chưa có
def get_or_create_thongkebc():
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return None

  try:
    # Thực hiện truy vấn SELECT để lấy bản ghi duy nhất từ bảng thongkebc
    query = "SELECT * FROM thongkebc"
    db_cursor.execute(query)
    result = db_cursor.fetchone()

    if result:
      # Nếu đã có bản ghi, trả về thông tin
      return {
          "tong_tien_cuoc": result[0],
          "tong_tien_da_tra": result[1],
          "so_lan_cuoc_khi": result[2],
          "so_lan_cuoc_ho": result[3],
          "so_lan_cuoc_tom": result[4],
          "so_lan_cuoc_cua": result[5],
          "so_lan_cuoc_ca": result[6],
          "so_lan_cuoc_ran": result[7]
      }
    else:
      # Nếu chưa có bản ghi, tạo bản ghi mới với các giá trị ban đầu là 0
      query = "INSERT INTO thongkebc (tong_tien_cuoc, tong_tien_da_tra, so_lan_cuoc_khi, so_lan_cuoc_ho, so_lan_cuoc_tom, so_lan_cuoc_cua, so_lan_cuoc_ca, so_lan_cuoc_ran) VALUES (0, 0, 0, 0, 0, 0, 0, 0)"
      db_cursor.execute(query)
      db_conn.commit()
      return {
          "tong_tien_cuoc": 0,
          "tong_tien_da_tra": 0,
          "so_lan_cuoc_khi": 0,
          "so_lan_cuoc_ho": 0,
          "so_lan_cuoc_tom": 0,
          "so_lan_cuoc_cua": 0,
          "so_lan_cuoc_ca": 0,
          "so_lan_cuoc_ran": 0
      }

  except mysql.connector.Error as e:
    print(
        f"Lỗi khi thực hiện truy vấn SELECT hoặc INSERT vào bảng thongkebc: {e}"
    )
    return None


# Hàm cập nhật thông tin vào bảng thongkebc
def update_thongkebc(tong_tien_cuoc, tong_tien_da_tra, animal_key):
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return

  try:
    query = f"UPDATE thongkebc SET tong_tien_cuoc = %s, tong_tien_da_tra = %s, {animal_key} = {animal_key} + 1"
    db_cursor.execute(query, (tong_tien_cuoc, tong_tien_da_tra))
    db_conn.commit()
  except mysql.connector.Error as e:
    print(f"Lỗi khi cập nhật dữ liệu vào bảng thongkebc: {e}")
  finally:
    db_cursor.close()


#################################################################

# ID của nhóm chat  thông báo kết quả
group_chat_id = -1001960838181


# Hàm gửi kết quả cho tất cả người chơi trong nhóm
def send_to_group(player_id, message):
  # Thêm ID của người chơi vào tin nhắn
  message_with_id = f"Người chơi Có id: ({player_id})\n" + message

  # URL API của Telegram để gửi tin nhắn đến nhóm chat
  url = f"https://api.telegram.org/bot6539528123:AAFQ_0g0xYJ2Jj3j91RAfLxYDCDVnNLVL1k/sendMessage"

  # Tham số để gửi tin nhắn
  data = {
      "chat_id": group_chat_id,
      "text": message_with_id,
  }

  # Gửi yêu cầu POST đến API của Telegram để gửi tin nhắn đến nhóm chat
  response = requests.post(url, data=data)

  # Kiểm tra xem yêu cầu có thành công hay không
  if response.status_code != 200:
    print("Gửi tin nhắn không thành công:", response.text)


###########################################################3


# Hàm xử lý game Tài/Xỉu
def calculate_tai_xiu(total_score):
  return "Tài" if 11 <= total_score <= 18 else "Xỉu"


# Hàm tính toán kết quả Chẵn Lẻ
def calculate_chan_le(last_digit):
  return "Chẵn" if int(last_digit) % 2 == 0 else "Lẻ"


# Hàm để kiểm tra xem người dùng có tồn tại trong CSDL hay không
def check_user_exists(user_id):
  query = "SELECT id FROM users WHERE telegram_id = %s"
  params = (user_id, )

  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    print("Không thể kết nối đến CSDL.")
    return False

  try:
    db_cursor.execute(query, params)
    result = db_cursor.fetchone()
    if result:
      return True
    return False
  except mysql.connector.Error as e:
    print(f"Lỗi khi kiểm tra người dùng tồn tại: {e}")
    return False


# Hàm lấy số dư của người dùng từ cơ sở dữ liệu
def load_balance(user_id):
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return 0.0

  try:
    query = "SELECT balance FROM users WHERE telegram_id = %s"
    params = (user_id, )
    db_cursor.execute(query, params)
    result = db_cursor.fetchone()
    if result:
      current_balance = float(result[0])
    else:
      current_balance = 0.0
    return current_balance

  except mysql.connector.Error as e:
    print(f"Lỗi khi lấy số dư của người dùng: {e}")
    return 0.0


# Hàm cập nhật số dư của người dùng sau mỗi ván chơi
def set_user_balance_amount(user_id, bet_amount, win_amount):
  current_balance = load_balance(user_id)
  new_balance = current_balance + bet_amount + win_amount
  return set_user_balance(user_id, new_balance)


###################################################################################################
# Hàm kiểm tra tổng số tiền cược của người chơi từ cơ sở dữ liệu
def check_total_bet_amount(user_id):
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return 0.0

  try:
    query = "SELECT total_bet_amount FROM tongcuoc WHERE telegram_id = %s"
    params = (user_id, )
    db_cursor.execute(query, params)
    result = db_cursor.fetchone()
    if result:
      total_bet_amount = float(result[0])
    else:
      total_bet_amount = 0.0
  except mysql.connector.Error as e:
    print("Lỗi truy vấn cơ sở dữ liệu:", e)
    total_bet_amount = 0.0
  finally:
    db_cursor.close()

  return total_bet_amount


# Hàm cập nhật tổng số tiền cược của người chơi sau mỗi ván chơi
def update_total_bet_amount(user_id, bet_amount, win_amount):
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return

  try:
    query = "SELECT total_bet_amount FROM tongcuoc WHERE telegram_id = %s"
    params = (user_id, )
    db_cursor.execute(query, params)
    result = db_cursor.fetchone()
    if result:
      current_total_bet = float(result[0])
    else:
      current_total_bet = 0.0

    new_total_bet = current_total_bet + bet_amount + win_amount
    if current_total_bet:
      query = "UPDATE tongcuoc SET total_bet_amount = %s WHERE telegram_id = %s"
      params = (new_total_bet, user_id)
    else:
      query = "INSERT INTO tongcuoc (telegram_id, total_bet_amount) VALUES (%s, %s)"
      params = (user_id, new_total_bet)

    db_cursor.execute(query, params)
    db_conn.commit()

  except mysql.connector.Error as e:
    print(f"Lỗi khi kiểm tra tổng tiền cược: {e}")
    return 0.0


# Hàm info
@bot.message_handler(commands=["info"])
def info_command(msg):
  user_id = msg.from_user.id
  total_bet_amount = check_total_bet_amount(user_id)
  formatted_total_bet = format_currency(total_bet_amount)

  result_text = f"┏━━━━━━━━━━━━━┓\n" \
                f"┣➤ ID : {user_id}\n" \
                f"┣➤ Tổng tiền cược: {formatted_total_bet}\n" \
                f"┗━━━━━━━━━━━━━┛"

  bot.reply_to(msg, result_text)


#####################################################################################################################
# Hàm check số dư của người dùng
@bot.message_handler(commands=["sd"])
def check_balance(msg):
  user_id = msg.from_user.id
  balance = load_balance(user_id)
  formatted_balance = "{:,.0f} đ".format(balance)

  result_text = f"┏━━━━━━━━━━━━━┓\n" \
                f"┣➤ Số dư của bạn: {formatted_balance}\n" \
                f"┗━━━━━━━━━━━━━┛"

  bot.reply_to(msg, result_text)


################################################################3
#lưu số dư của từng người
def save_balance(user_id, balance):
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return False

  try:
    query = "UPDATE users SET balance = %s WHERE telegram_id = %s"
    params = (balance, user_id)
    db_cursor.execute(query, params)
    db_conn.commit()
    return True

  except mysql.connector.Error as e:
    print(f"Lỗi khi lưu số dư của người dùng: {e}")
    return False


# Hàm cập nhật số dư của người dùng
def set_user_balance(user_id, new_balance):
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return False

  try:
    query = "UPDATE users SET balance = %s WHERE telegram_id = %s"
    params = (new_balance, user_id)
    db_cursor.execute(query, params)
    db_conn.commit()
    return True

  except mysql.connector.Error as e:
    print(f"Lỗi khi cập nhật số dư của người dùng: {e}")
    return False


# Hàm lấy số dư của user_id từ bảng users
def get_balance(user_id):
  query = "SELECT balance FROM users WHERE telegram_id = %s"
  params = (user_id, )
  db_cursor.execute(query, params)
  result = db_cursor.fetchone()
  if result:
    return result[0]
  return 0.0


# Hàm lưu lịch sử nạp tiền vào bảng lichsunap
def save_transaction_log(user_id, method, amount, note):
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return

  try:
    query = "INSERT INTO lichsunap (telegram_id, method, amount, note) VALUES (%s, %s, %s, %s)"
    params = (user_id, method, amount, note)
    db_cursor.execute(query, params)
    db_conn.commit()

  except mysql.connector.Error as e:
    print(f"Lỗi khi lưu lịch sử nạp tiền: {e}")
    return


# Hàm gửi thông báo cho bot chỉ định
def send_notification_to_target_bot(target_user_id, message):
  api_url = f"https://api.telegram.org/bot6514589047:AAFbyptAN1t_g-rU4mI5-MVEf_KUGKGs6-A/sendMessage"
  data = {"chat_id": target_user_id, "text": message, "parse_mode": "HTML"}
  response = requests.post(api_url, data=data)
  return response.json()


# Hàm xóa trạng thái tạm thời của người dùng sau khi hoàn thành việc nạp tiền
def clear_user_state(user_id):
  if user_id in user_state_sd:
    del user_state_sd[user_id]


# Hàm nạp tiền cho UID
@bot.message_handler(commands=["setsodu"])
def set_balance(msg):
  if msg.from_user.id == 7491211987:  # ID của người dùng quản trị
    bot.reply_to(msg, "Nhập user ID của thành viên:")
    user_state_sd[msg.from_user.id] = "set_user_id"
  else:
    bot.reply_to(msg, "Bạn không có quyền sử dụng lệnh này.")


@bot.message_handler(func=lambda message: message.from_user.id in user_state_sd
                     and user_state_sd[message.from_user.id] == "set_user_id")
def set_user_id(msg):
  try:
    user_id = int(msg.text)
    if not check_user_exists(user_id):
      bot.reply_to(msg, "UID không tồn tại trong hệ thống.")
      del user_state_sd[msg.from_user.id]
      return
    bot.reply_to(msg,
                 "Nhập số tiền muốn cộng hoặc trừ (ví dụ: +1000 hoặc -1000):")
    user_state_sd[msg.from_user.id] = (user_id, "set_balance_amount")
  except ValueError:
    bot.reply_to(msg, "Vui lòng nhập một user ID hợp lệ.")


@bot.message_handler(
    func=lambda message: message.from_user.id in user_state_sd and
    "set_balance_amount" in user_state_sd[message.from_user.id])
def set_user_balance_amount(msg):
  try:
    amount_str = msg.text
    if not (amount_str.startswith('+') or amount_str.startswith('-')):
      bot.reply_to(msg,
                   "Vui lòng nhập số tiền hợp lệ (ví dụ: +1000 hoặc -1000).")
      return

    balance_change = int(amount_str)
    user_id, _ = user_state_sd[msg.from_user.id]
    current_balance = load_balance(user_id)

    # Tính toán số dư mới sau khi cộng hoặc trừ
    new_balance = current_balance + balance_change

    # Thực hiện cập nhật số dư mới vào cơ sở dữ liệu
    set_user_balance(user_id, new_balance)

    # Lấy thông tin thời gian hiện tại
    current_time = datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")

    # Ghi chú cho lịch sử
    method = "NAP" if balance_change > 0 else "TRỪ TIỀN"
    amount = abs(balance_change)
    note = f"{method} - {amount:,} đ - ({current_time})"

    # Lưu lịch sử nạp tiền vào bảng lichsunap
    save_transaction_log(user_id, method, amount, note)

    # Gửi thông báo cho người dùng về việc thay đổi số dư
    formatted_balance = "{:,.0f} đ".format(new_balance)
    if balance_change > 0:
      message = f"✅ Nạp tiền thành công!!\n\n Thời gian : ({current_time})\n ➡️ Số tiền: {abs(balance_change):,} đồng\n➡️ Số dư hiện tại: {formatted_balance}\n\n/game để lấy danh sách game chơi và tỷ lệ thắng\n\nChúc bạn chơi game vui vẻ!!!"
    else:
      message = f"🚫 Bạn đã bị admin trừ tiền!!\n\n Thời gian : ({current_time})\n ➡️ Số tiền: {abs(balance_change):,} đồng\n➡️ Số dư hiện tại: {formatted_balance}\n\n/game để lấy danh sách game chơi và tỷ lệ thắng\n\nChúc bạn chơi game vui vẻ!!!"

    # Gửi thông báo đến bot chỉ định về việc thay đổi số dư
    if user_id != msg.from_user.id:
      send_notification_to_target_bot(user_id, message)

    # Gửi thông báo đến người dùng quản trị về việc thay đổi số dư thành công
    bot.reply_to(
        msg,
        f"Số dư của thành viên {user_id} đã được {'cộng' if balance_change > 0 else 'trừ'} {abs(balance_change):,} đồng.\nSố dư mới: {formatted_balance}"
    )

    # Xóa trạng thái tạm thời của người dùng sau khi hoàn thành việc nạp tiền
    clear_user_state(msg.from_user.id)

  except ValueError:
    bot.reply_to(msg, "Vui lòng nhập một số tiền hợp lệ.")


##########################lsnap
# Hàm lấy lịch sử nạp tiền từ bảng lichsunap
def load_transaction_history(user_id):
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return []

  try:
    query = "SELECT method, amount, time FROM lichsunap WHERE telegram_id = %s"
    params = (user_id, )
    db_cursor.execute(query, params)
    results = db_cursor.fetchall()

    transaction_history = []
    for result in results:
      method = result[0]
      amount = "{:,.0f} đ".format(result[1])
      time_str = result[2].strftime("%H:%M:%S - %d/%m/%Y")
      entry = f"{method} - {amount} - ({time_str})"
      transaction_history.append(entry)

    return transaction_history

  except mysql.connector.Error as e:
    print(f"Lỗi khi lấy lịch sử nạp tiền: {e}")
    return []


# Hàm lsnap
@bot.message_handler(commands=["lsnap"])
def check_transaction_history(msg):
  user_id = msg.from_user.id
  transaction_history = load_transaction_history(user_id)

  if transaction_history:
    formatted_history = "\n".join(transaction_history)
    bot.reply_to(
        msg, f"NẠP - CÁCH THỨC - SỐ TIỀN - THỜI GIAN\n\n{formatted_history}")
  else:
    bot.reply_to(msg, "Bạn chưa có lịch sử nạp tiền.")


########################################################
#CODE GAME TÀI XỈU DO HUYDEP ZAI VIẾT
@bot.message_handler(func=lambda message: message.text == "T")
def send_tai_xiu(msg):
  user_state_tx[msg.from_user.id] = "tai"  # Lưu trạng thái là tai
  # Hiển thị ô vuông để chọn số tiền cược
  markup = telebot.types.ReplyKeyboardMarkup(row_width=2,
                                             one_time_keyboard=True,
                                             resize_keyboard=True)
  markup.add("1000", "5000", "10000", "20000", "50000", "100000", "200000",
             "500000")
  bot.reply_to(msg,
               "Chọn nhanh tiền cược hoặc nhập số tiền tùy ý:",
               reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "X")
def send_xiu(msg):
  user_state_tx[msg.from_user.id] = "xiu"  # Lưu trạng thái là xiu
  # Hiển thị ô vuông để chọn số tiền cược
  markup = telebot.types.ReplyKeyboardMarkup(row_width=2,
                                             one_time_keyboard=True,
                                             resize_keyboard=True)
  markup.add("1000", "5000", "10000", "20000", "50000", "100000", "200000",
             "500000")
  bot.reply_to(msg,
               "Chọn nhanh tiền cược hoặc nhập số tiền tùy ý:",
               reply_markup=markup)


@bot.message_handler(func=lambda message: message.from_user.id in user_state_tx
                     and user_state_tx[message.from_user.id] in ["tai", "xiu"])
def bet_amount(msg):
  try:
    amount = int(msg.text)
    if amount <= 999:
      bot.reply_to(msg, "Số tiền cược phải lớn hơn hoặc = 1.000 đ.")
      return

    if amount >= 1000000:
      bot.reply_to(msg, "Số tiền được cược tối đa là 1.000.000 đ.")
      return

    # Kiểm tra số dư trước khi cược
    if not check_balance_before_play(msg.from_user.id, amount):
      bot.reply_to(
          msg,
          "Số dư của bạn không đủ để cược. Vui lòng nạp thêm tiền vào tài khoản."
      )
      return

    # Lưu trạng thái hiện tại của người chơi vào biến tạm thời
    current_state = user_state_tx[msg.from_user.id]

    # Trừ tiền cược ngay sau khi nhập số tiền
    balance = load_balance(msg.from_user.id)
    balance -= amount
    save_balance(msg.from_user.id, balance)

    # Tung 3 xúc xắc và tính tổng điểm
    result = [bot.send_dice(chat_id=msg.chat.id).dice.value for _ in range(3)]
    total_score = sum(result)

    # Lấy thông tin thời gian hiện tại
    current_time = datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")

    # Xác định kết quả Tài/Xỉu từ tổng điểm
    result_text = f"┏━━━━━━━━━━━━━┓\n" \
                  f"┣➤ {' - '.join(str(x) for x in result)}\n" \
                  f"┣➤ Tổng điểm: {total_score}\n" \
                  f"┣➤  ({current_time})\n" \
                  f"┣➤ Kết quả: {calculate_tai_xiu(total_score)}"
    #luu số tiền thua 0
    win_amount = 0

    if current_state == "tai":
      if calculate_tai_xiu(total_score) == "Tài":
        win_amount = int(amount * 1.9)
        result_text += f"\n┣➤ Bạn đã thắng! Với số tiền {win_amount:,} đ "
        balance += win_amount  # Cộng tiền thắng vào số dư mới
        update_total_bet_amount(msg.from_user.id, amount, win_amount)
      else:
        result_text += f"\n┣➤ Bạn đã thua! Số tiền  {amount:,} đ"

    elif current_state == "xiu":
      if calculate_tai_xiu(total_score) == "Xỉu":
        win_amount = int(amount * 1.9)
        result_text += f"\n┣➤ Bạn đã thắng! Với số tiền {win_amount:,} đ "
        balance += win_amount  # Cộng tiền thắng vào số dư mới
        update_total_bet_amount(
            msg.from_user.id, amount,
            win_amount)  # Cập nhật tổng số tiền cược sau ván chơi
      else:
        result_text += f"\n┣➤ Bạn đã thua! Số tiền  {amount:,} đ"

    # Cập nhật thông tin vào bảng thongketx
    update_thongketx(amount, win_amount, current_state)

    # Cập nhật số dư mới vào kết quả
    save_balance(msg.from_user.id, balance)
    formatted_balance = "{:,.0f} đ".format(load_balance(msg.from_user.id))
    result_text += f"\n┣➤ Số dư mới của bạn: {formatted_balance}"

    # Xoá trạng thái của người dùng sau khi cược thành công
    del user_state_tx[msg.from_user.id]

    result_text += "\n┗━━━━━━━━━━━━━┛"

    bot.send_message(chat_id=msg.chat.id, text=result_text)

    # Gọi hàm để lưu lịch sử chơi vào bảng alichsuchoi
    if win_amount == 0:
      save_to_alichsuchoi(msg.from_user.id, ' - '.join(str(x) for x in result),
                          current_state, amount, 0, "Tài Xỉu",
                          datetime.datetime.now())
    else:
      save_to_alichsuchoi(msg.from_user.id, ' - '.join(str(x) for x in result),
                          current_state, amount, win_amount, "Tài Xỉu",
                          datetime.datetime.now())

    # Gửi kết quả trò chơi cho tất cả người chơi trong nhóm thông báo
    send_to_group(msg.from_user.id, result_text)

  except ValueError:
    pass


#############mã timeticke chẵn lẻ#############


def check_balance_before_play(user_id, bet_amount):
  current_balance = load_balance(user_id)
  return current_balance >= bet_amount


def get_timeticks():
  # Lấy thời gian hiện tại
  current_time = int(time.time())

  # Chuyển đổi số giây thành số Timeticks
  timeticks = current_time * 1

  # Lấy 10 số cuối cùng của số Timeticks
  random_timeticks = str(timeticks)[-10:]

  return random_timeticks


#code game chẵn lẻ
@bot.message_handler(func=lambda message: message.text == "C")
def request_bet_amount_chan(msg):
  user_id = msg.from_user.id
  user_state_cl[
      user_id] = "chan"  # Lưu trạng thái lựa chọn của người dùng là "/chan"
  # Hiển thị ô vuông để chọn số tiền cược
  markup = telebot.types.ReplyKeyboardMarkup(row_width=2,
                                             one_time_keyboard=True,
                                             resize_keyboard=True)
  markup.add("1000", "5000", "10000", "20000", "50000", "100000", "200000",
             "500000")
  bot.reply_to(msg,
               "Chọn nhanh tiền cược hoặc nhập số tiền tùy ý:",
               reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "L")
def request_bet_amount_le(msg):
  user_id = msg.from_user.id
  user_state_cl[
      user_id] = "le"  # Lưu trạng thái lựa chọn của người dùng là "/le"
  # Hiển thị ô vuông để chọn số tiền cược
  markup = telebot.types.ReplyKeyboardMarkup(row_width=2,
                                             one_time_keyboard=True,
                                             resize_keyboard=True)
  markup.add("1000", "5000", "10000", "20000", "50000", "100000", "200000",
             "500000")
  bot.reply_to(msg,
               "Chọn nhanh tiền cược hoặc nhập số tiền tùy ý:",
               reply_markup=markup)


@bot.message_handler(func=lambda message: message.from_user.id in user_state_cl
                     and user_state_cl[message.from_user.id] in ["chan", "le"])
def bet_amount(msg):
  try:
    amount = int(msg.text)
    if amount <= 999:
      bot.reply_to(msg, "Số tiền cược phải lớn hơn hoặc = 1.000 đ.")
      return

    if amount >= 1000000:
      bot.reply_to(msg, "Số tiền được cược tối đa là 1.000.000 đ.")
      return

    # Lưu trạng thái hiện tại của người chơi vào biến tạm thời
    current_state = user_state_cl[msg.from_user.id]

    # Kiểm tra số dư trước khi cược
    if not check_balance_before_play(msg.from_user.id, amount):
      bot.reply_to(
          msg,
          "Số dư của bạn không đủ để cược. Vui lòng nạp thêm tiền vào tài khoản."
      )
      del user_state_cl[msg.from_user.id]
      return

    # Trừ tiền cược ngay sau khi nhập số tiền
    balance = load_balance(msg.from_user.id)
    balance -= amount
    save_balance(msg.from_user.id, balance)
    ####################RANDOM########################
    # Hàm để lấy mã Timeticks từ thời gian hiện tại

    random_timeticks = get_timeticks()
    #######################RANDOM#######################
    # Xác định kết quả chẵn/lẻ từ số cuối của số ngẫu nhiên
    result = calculate_chan_le(random_timeticks[-1])

    # Xác định kết quả cược của người chơi
    win = (current_state == "chan"
           and result == "Chẵn") or (current_state == "le" and result == "Lẻ")
    if win:
      win_amount = int(amount * 1.95)
      balance += win_amount  # Cộng tiền thắng vào số dư mới
      update_total_bet_amount(
          msg.from_user.id, amount,
          win_amount)  # Cập nhật tổng số tiền cược sau ván chơi
    else:
      update_total_bet_amount(msg.from_user.id, amount,
                              0)  # Cập nhật tổng số tiền cược sau ván chơi

    # Cập nhật số dư mới vào kết quả
    save_balance(msg.from_user.id, balance)
    formatted_balance = "{:,.0f} đ".format(load_balance(msg.from_user.id))

    # Lấy thông tin thời gian hiện tại
    current_time = datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")

    # Gửi kết quả trò chơi
    result_text = f"┏━━━━━━━━━━━━━┓\n" \
                  f"┣➤ Timeticks : {random_timeticks}\n" \
                  f"┣➤ Bạn đã : {'Thắng' if win else 'Thua'}" \
                  f"{' (' + str(win_amount) + ' đ)' if win else ''}\n" \
                  f"┣➤ ({current_time})\n" \
                  f"┣➤ Số dư mới của bạn: {formatted_balance}\n" \
                      # Xoá trạng thái của người dùng sau khi cược thành công

    del user_state_cl[msg.from_user.id]

    result_text += "┗━━━━━━━━━━━━━┛"

    bot.send_message(chat_id=msg.chat.id, text=result_text)

    # Gọi hàm để lưu lịch sử chơi vào bảng alichsuchoi
    loai_game = "Chẵn Lẻ" if current_state == "chan" else "Chẵn Lẻ"
    save_to_alichsuchoi(msg.from_user.id, random_timeticks, current_state,
                        amount, win_amount if win else 0, loai_game,
                        datetime.datetime.now())

    #nếu thua lưu thống kê =0
    win_amount = 0

    # Cập nhật thông tin vào bảng thongke
    update_thongkecl(amount, win_amount, current_state)

    # Gửi kết quả trò chơi cho tất cả người chơi trong nhóm thông báo
    send_to_group(msg.from_user.id, result_text)

  except ValueError:
    pass


#code tài xỉu v2
###code game tai xiu v2
# Hàm kiểm tra xúc xắc và tính kết quả Tài/Xỉu
def check_dice_result(dice_value):
  if dice_value in [1, 3, 5]:
    return "Tài"
  elif dice_value in [2, 4, 6]:
    return "Xỉu"
  else:
    return None


# Lệnh chơi Tài/Xỉu v2
@bot.message_handler(commands=["tai2", "xiu2"])
def request_bet_amount_tai_xiu(msg):
  user_id = msg.from_user.id
  user_state_tx2[user_id] = msg.text[
      1:]  # Lưu trạng thái lựa chọn của người dùng ("/tai2" hoặc "/xiu2")
  # Hiển thị ô vuông để chọn số tiền cược
  markup = telebot.types.ReplyKeyboardMarkup(row_width=2,
                                             one_time_keyboard=True,
                                             resize_keyboard=True)
  markup.add("1000", "5000", "10000", "20000", "50000", "100000", "200000",
             "500000")
  bot.reply_to(msg,
               "Chọn nhanh tiền cược hoặc nhập số tiền tùy ý:",
               reply_markup=markup)


@bot.message_handler(
    func=lambda message: message.from_user.id in user_state_tx2 and
    user_state_tx2[message.from_user.id] in ["tai2", "xiu2"])
def bet_amount_tai_xiu(msg):
  try:
    amount = int(msg.text)
    if amount <= 999:
      bot.reply_to(msg, "Số tiền cược phải lớn hơn hoặc = 1.000 đ.")
      return

    if amount >= 1000000:
      bot.reply_to(msg, "Số tiền được cược tối đa là 1.000.000 đ.")
      return

    # Kiểm tra số dư trước khi cược
    if not check_balance_before_play(msg.from_user.id, amount):
      bot.reply_to(
          msg,
          "Số dư của bạn không đủ để cược. Vui lòng nạp thêm tiền vào tài khoản."
      )
      del user_state_tx2[msg.from_user.id]
      return

    # Lưu trạng thái hiện tại của người chơi vào biến tạm thời
    current_state = user_state_tx2[msg.from_user.id]

    # Trừ tiền cược ngay sau khi nhập số tiền
    balance = load_balance(msg.from_user.id)
    balance -= amount
    save_balance(msg.from_user.id, balance)

    # Hiển thị ô vuông để gửi nhanh hình xúc xắc
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2,
                                               one_time_keyboard=True,
                                               resize_keyboard=False)
    markup.add("🎲")  # Add the dice emoji button to the keyboard
    bot.reply_to(
        msg,
        "Gửi nhanh hình xúc xắc (🎲) hoặc tự copy gửi để đưa ra kết quả",
        reply_markup=markup)

    # Xoá trạng thái lệnh của người dùng và lưu kết quả cược vào biến tạm thời
    del user_state_tx2[msg.from_user.id]
    user_state_tx2[msg.from_user.id] = (current_state, amount)

  except ValueError:
    pass


@bot.message_handler(
    content_types=["dice"],
    func=lambda message: message.from_user.id in user_state_tx2 and isinstance(
        user_state_tx2[message.from_user.id], tuple))
def process_dice_result(msg):
  try:
    result_dice = msg.dice.value

    # Kiểm tra kết quả xúc xắc và tính kết quả Tài/Xỉu từ kết quả xúc xắc
    current_state, amount = user_state_tx2[msg.from_user.id]
    tai_xiu_result = check_dice_result(result_dice)

    if tai_xiu_result is None:
      bot.reply_to(
          msg, "Kết quả xúc xắc không hợp lệ. Vui lòng gửi lại hình xúc xắc.")
      return

    # Xác định kết quả cược của người chơi
    win_amount = 0  # Đặt giá trị mặc định cho win_amount
    win = (current_state == "tai2"
           and tai_xiu_result == "Tài") or (current_state == "xiu2"
                                            and tai_xiu_result == "Xỉu")
    if win:
      win_amount = int(amount * 1.9)
      balance = load_balance(msg.from_user.id)
      balance += win_amount  # Cộng tiền thắng vào số dư mới
      update_total_bet_amount(msg.from_user.id, amount, win_amount)
      save_balance(msg.from_user.id, balance)

    # Lấy thông tin thời gian hiện tại
    current_time = datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")

    # Gửi kết quả trò chơi
    formatted_balance = "{:,.0f} đ".format(load_balance(msg.from_user.id))
    result_text = f"┏━━━━━━━━━━━━━┓\n" \
                  f"┣➤ Kết quả xúc xắc: {result_dice}\n" \
                  f"┣➤ Kết quả: {tai_xiu_result}\n" \
                  f"┣➤ Bạn đã : {'Thắng' if win else 'Thua'}" \
                  f"{' (' + str(win_amount) + ' đ)' if win else ''}\n" \
                  f"┣➤ ({current_time})\n" \
                  f"┣➤ Số dư mới của bạn: {formatted_balance}\n" \
                  f"┗━━━━━━━━━━━━━┛"

    bot.reply_to(msg, result_text)

    # Ghi kết quả vào cơ sở dữ liệu
    save_to_alichsuchoi(msg.from_user.id, result_dice, current_state, amount,
                        win_amount if win else 0, "Tài Xỉu 2",
                        datetime.datetime.now())

    # Cập nhật thông tin vào bảng thongketx2
    if win:
      update_thongketx2(amount, win_amount,
                        1 if current_state == "tai2" else 0,
                        1 if current_state == "xiu2" else 0)
    else:
      update_thongketx2(amount, 0, 1 if current_state == "tai2" else 0,
                        1 if current_state == "xiu2" else 0)

    send_to_group(msg.from_user.id, result_text)

  except ValueError:
    bot.reply_to(
        msg, "Kết quả xúc xắc không hợp lệ. Vui lòng gửi lại hình xúc xắc.")
    return

  # Xoá trạng thái của người dùng sau khi cược thành công
  del user_state_tx2[msg.from_user.id]


# code game chẵn lẻ  2


#code game chẵn lẻ v2
# Hàm tính toán kết quả Chẵn Lẻ từ 4 hình
def calculate_chan_le_v2(result_list, current_command):
  # Đếm số lượng hình 🔴 trong kết quả
  count_red = result_list.count(emoji.emojize(":red_circle:"))

  # Đếm số lượng hình ⚪️ trong kết quả
  count_white = result_list.count(emoji.emojize(":white_circle:"))

  # Xác định kết quả Chẵn hoặc Lẻ dựa trên lệnh người dùng đã chọn
  if (count_red == 2
      and count_white == 2) or count_red == 4 or count_white == 4:
    result = "Chẵn"
  else:
    result = "Lẻ"

  # Xác định kết quả cược của người chơi
  win = (current_command == "chan2"
         and result == "Chẵn") or (current_command == "le2" and result == "Lẻ")

  return result, win


# Handler khi người dùng chọn chơi /chan2 hoặc /le2
@bot.message_handler(commands=["chan2", "le2"])
def request_bet_amount_v2(msg):
  user_id = msg.from_user.id
  user_state_cl2[user_id] = {}
  user_state_cl2[user_id]["command"] = msg.text[
      1:]  # Lưu trạng thái lựa chọn của người dùng ("/chan2" hoặc "/le2")
  # Hiển thị ô vuông để chọn số tiền cược
  markup = telebot.types.ReplyKeyboardMarkup(row_width=2,
                                             one_time_keyboard=True,
                                             resize_keyboard=True)
  markup.add("1000", "5000", "10000", "20000", "50000", "100000", "200000",
             "500000")
  bot.reply_to(msg,
               "Chọn nhanh tiền cược hoặc nhập số tiền tùy ý:",
               reply_markup=markup)


@bot.message_handler(
    func=lambda message: message.from_user.id in user_state_cl2 and "command"
    in user_state_cl2[message.from_user.id] and user_state_cl2[
        message.from_user.id]["command"] in ["chan2", "le2"])
def bet_amount_v2(msg):
  try:
    amount = int(msg.text)
    if amount <= 999:
      bot.reply_to(msg, "Số tiền cược phải lớn hơn hoặc = 1.000 đ.")
      return

    if amount >= 1000000:
      bot.reply_to(msg, "Số tiền được cược tối đa là 1.000.000 đ.")
      return

    # Lưu trạng thái hiện tại của người chơi vào biến tạm thời
    current_command = user_state_cl2[msg.from_user.id]["command"]

    # Kiểm tra số dư trước khi cược
    user_id = msg.from_user.id
    if not check_balance_before_play(user_id, amount):
      bot.reply_to(
          msg,
          "Số dư của bạn không đủ để cược. Vui lòng nạp thêm tiền vào tài khoản."
      )
      del user_state_cl2[user_id]
      return

    # Trừ tiền cược ngay sau khi nhập số tiền
    balance = load_balance(user_id)
    balance -= amount
    save_balance(user_id, balance)

    # Khởi tạo win_amount với giá trị mặc định 0
    win_amount = 0

    # Danh sách 8 hình gồm 4 hình "🔴" và 4 hình "⚪️"
    hinh_list = [emoji.emojize(":red_circle:")
                 ] * 4 + [emoji.emojize(":white_circle:")] * 4

    # Chọn ngẫu nhiên 4 hình từ danh sách 8 hình
    result_list = random.sample(hinh_list, 4)
    result_text = "-".join(result_list)

    # Xác định kết quả Chẵn/Lẻ từ 4 hình
    result, win = calculate_chan_le_v2(result_list, current_command)

    if win:
      win_amount = int(amount * 1.9)
      balance += win_amount  # Cộng tiền thắng vào số dư mới
      update_total_bet_amount(
          user_id, amount,
          win_amount)  # Cập nhật tổng số tiền cược sau ván chơi
    else:
      update_total_bet_amount(user_id, amount,
                              0)  # Cập nhật tổng số tiền cược sau ván chơi

    # Cập nhật số dư mới vào kết quả
    save_balance(user_id, balance)
    formatted_balance = "{:,.0f} đ".format(load_balance(user_id))

    # Lấy thông tin thời gian hiện tại
    current_time = datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")

    # Gửi kết quả trò chơi
    result_text = f"┏━━━━━━━━━━━━━┓\n" \
                  f"┣➤ {'-'.join(result_list)}\n" \
                  f"┣➤ Kết quả: {result} \n" \
                  f"┣➤ Bạn đã : {'Thắng' if win else 'Thua'}" \
                  f"{' (' + str(win_amount) + ' đ)' if win else ''}\n" \
                  f"┣➤ ({current_time})\n" \
                  f"┣➤ Số dư mới của bạn: {formatted_balance}\n" \
                  f"┗━━━━━━━━━━━━━┛"

    bot.send_message(chat_id=msg.chat.id, text=result_text)

    # Lưu lịch sử chơi vào cơ sở dữ liệu
    save_to_alichsuchoi(msg.from_user.id, result, current_command, amount,
                        win_amount if win else 0, "Chẵn Lẻ 2",
                        datetime.datetime.now())

    # Gọi hàm update_thongkecl2 để cập nhật dữ liệu vào bảng thongkecl2
    update_thongkecl2(amount, win_amount if win else 0, current_command)

    send_to_group(user_id, result_text)

    del user_state_cl2[
        user_id]  # Xoá trạng thái của người dùng sau khi cược thành công
  except ValueError:
    pass


##code  game 1 phần 3
@bot.message_handler(
    func=lambda message: message.text in ["N0", "N1", "N2", "N3"])
def request_bet_amount_phanba(msg):
  user_id = msg.from_user.id
  user_state_phanba[
      user_id] = msg.text  # Lưu trạng thái lựa chọn của người dùng

  # Hiển thị ô vuông để chọn số tiền cược
  markup = telebot.types.ReplyKeyboardMarkup(row_width=2,
                                             one_time_keyboard=True,
                                             resize_keyboard=True)
  markup.add("1000", "5000", "10000", "20000", "50000", "100000", "200000",
             "500000")
  bot.reply_to(msg,
               "Chọn số tiền cược hoặc nhập số tiền tùy ý:",
               reply_markup=markup)


@bot.message_handler(
    func=lambda message: message.from_user.id in user_state_phanba)
def bet_amount_phanba(msg):
  try:
    amount = int(msg.text)
    if amount <= 999:
      bot.reply_to(msg, "Số tiền cược phải lớn hơn hoặc = 1.000 đ.")
      return

    if amount >= 1000000:
      bot.reply_to(msg, "Số tiền được cược tối đa là 1.000.000 đ.")
      return

    # Lưu trạng thái hiện tại của người chơi vào biến tạm thời
    current_state = user_state_phanba[msg.from_user.id]

    # Kiểm tra số dư trước khi cược
    if not check_balance_before_play(msg.from_user.id, amount):
      bot.reply_to(
          msg,
          "Số dư của bạn không đủ để cược. Vui lòng nạp thêm tiền vào tài khoản."
      )
      del user_state_phanba[msg.from_user.id]
      return

    # Trừ tiền cược ngay sau khi nhập số tiền
    balance = load_balance(msg.from_user.id)
    balance -= amount
    save_balance(msg.from_user.id, balance)

    # Tạo 10 số ngẫu nhiên từ 0 đến 9 và ghép thành chuỗi
    random_number_pa = ''.join(str(random.randint(0, 9)) for _ in range(10))

    win_amount = 0

    # Xác định kết quả theo lệnh được chọn
    win = False
    if current_state == "N0":
      if random_number_pa[-1:] == "0":
        win = True
        win_amount = int(amount * 5.0)
        balance += win_amount
        update_total_bet_amount(msg.from_user.id, amount, win_amount)
    elif current_state == "N1":
      if random_number_pa[-1:] in "123":
        win = True
        win_amount = int(amount * 3.0)
        balance += win_amount
        update_total_bet_amount(msg.from_user.id, amount, win_amount)
    elif current_state == "N2":
      if random_number_pa[-1:] in "456":
        win = True
        win_amount = int(amount * 3.0)
        balance += win_amount
        update_total_bet_amount(msg.from_user.id, amount, win_amount)
    elif current_state == "N3":
      if random_number_pa[-1:] in "789":
        win = True
        win_amount = int(amount * 3.0)
        balance += win_amount
        update_total_bet_amount(msg.from_user.id, amount, win_amount)

    # Cập nhật số dư mới vào kết quả
    save_balance(msg.from_user.id, balance)
    formatted_balance = "{:,.0f} đ".format(load_balance(msg.from_user.id))

    # Lấy thông tin thời gian hiện tại
    current_time = datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")

    # Gửi kết quả trò chơi
    result_text = f"┏━━━━━━━━━━━━━┓\n" \
                  f"┣➤ Timeticks : {random_number_pa}\n" \
                  f"┣➤ Kết quả: {'Thắng' if win else 'Thua'}" \
                  f"{' (' + str(win_amount) + ' đ)' if win else ''}\n" \
                  f"┣➤ ({current_time})\n" \
                  f"┣➤ Số dư mới của bạn: {formatted_balance}\n" \
                      # Xoá trạng thái của người dùng sau khi cược thành công

    del user_state_phanba[msg.from_user.id]

    result_text += "┗━━━━━━━━━━━━━┛"

    bot.send_message(chat_id=msg.chat.id, text=result_text)

    # Ghi kết quả vào cơ sở dữ liệu
    save_to_alichsuchoi(msg.from_user.id, random_number_pa, current_state,
                        amount, win_amount if win else 0, "1 phần 3",
                        datetime.datetime.now())

    # Cập nhật thông tin vào bảng thongke1p3
    update_thongke1p3(amount, win_amount, 1 if current_state == "N0" else 0,
                      1 if current_state == "N1" else 0,
                      1 if current_state == "N2" else 0,
                      1 if current_state == "N3" else 0)

    send_to_group(msg.from_user.id, result_text)
  except ValueError:
    pass


##code game đoán số


@bot.message_handler(
    func=lambda message: message.text in
    ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9"])
def request_bet_amount_doan(msg):
  user_id = msg.from_user.id
  user_state_doan[user_id] = msg.text  # Lưu trạng thái lựa chọn của người dùng

  # Hiển thị ô vuông để chọn số tiền cược
  markup = telebot.types.ReplyKeyboardMarkup(row_width=2,
                                             one_time_keyboard=True,
                                             resize_keyboard=True)
  markup.add("1000", "5000", "10000", "20000", "50000", "100000", "200000",
             "500000")
  bot.reply_to(msg,
               "Chọn số tiền cược hoặc nhập số tiền tùy ý:",
               reply_markup=markup)


@bot.message_handler(
    func=lambda message: message.from_user.id in user_state_doan)
def bet_amount_doan(msg):
  try:
    amount = int(msg.text)
    if amount <= 999:
      bot.reply_to(msg, "Số tiền cược phải lớn hơn hoặc = 1.000 đ.")
      return

    if amount >= 1000000:
      bot.reply_to(msg, "Số tiền được cược tối đa là 1.000.000 đ.")
      return

    # Lưu trạng thái hiện tại của người chơi vào biến tạm thời
    current_state = user_state_doan[msg.from_user.id]

    # Kiểm tra số dư trước khi cược
    if not check_balance_before_play(msg.from_user.id, amount):
      bot.reply_to(
          msg,
          "Số dư của bạn không đủ để cược. Vui lòng nạp thêm tiền vào tài khoản."
      )
      del user_state_doan[msg.from_user.id]
      return

    # Trừ tiền cược ngay sau khi nhập số tiền
    balance = load_balance(msg.from_user.id)
    balance -= amount
    save_balance(msg.from_user.id, balance)

    # Tạo số ngẫu nhiên từ 0 đến 9
    random_number_ds = random.randint(0, 9)

    win_amount = 0

    # Xác định kết quả theo lệnh được chọn
    win = False
    if current_state == "D0" and random_number_ds == 0:
      win = True
      win_amount = int(amount * 9.0)
      balance += win_amount
      update_total_bet_amount(msg.from_user.id, amount, win_amount)
    elif current_state == "D1" and random_number_ds == 1:
      win = True
      win_amount = int(amount * 9.0)
      balance += win_amount
      update_total_bet_amount(msg.from_user.id, amount, win_amount)
    elif current_state == "D2" and random_number_ds == 2:
      win = True
      win_amount = int(amount * 9.0)
      balance += win_amount
      update_total_bet_amount(msg.from_user.id, amount, win_amount)
    elif current_state == "D3" and random_number_ds == 3:
      win = True
      win_amount = int(amount * 9.0)
      balance += win_amount
      update_total_bet_amount(msg.from_user.id, amount, win_amount)
    elif current_state == "D4" and random_number_ds == 4:
      win = True
      win_amount = int(amount * 9.0)
      balance += win_amount
      update_total_bet_amount(msg.from_user.id, amount, win_amount)
    elif current_state == "D5" and random_number_ds == 5:
      win = True
      win_amount = int(amount * 9.0)
      balance += win_amount
      update_total_bet_amount(msg.from_user.id, amount, win_amount)
    elif current_state == "D6" and random_number_ds == 6:
      win = True
      win_amount = int(amount * 9.0)
      balance += win_amount
      update_total_bet_amount(msg.from_user.id, amount, win_amount)
    elif current_state == "D7" and random_number_ds == 7:
      win = True
      win_amount = int(amount * 9.0)
      balance += win_amount
      update_total_bet_amount(msg.from_user.id, amount, win_amount)
    elif current_state == "D8" and random_number_ds == 8:
      win = True
      win_amount = int(amount * 9.0)
      balance += win_amount
      update_total_bet_amount(msg.from_user.id, amount, win_amount)
    elif current_state == "D9" and random_number_ds == 9:
      win = True
      win_amount = int(amount * 9.0)
      balance += win_amount
      update_total_bet_amount(msg.from_user.id, amount, win_amount)

    # Cập nhật số dư mới vào kết quả
    save_balance(msg.from_user.id, balance)
    formatted_balance = "{:,.0f} đ".format(load_balance(msg.from_user.id))

    # Lấy thông tin thời gian hiện tại
    current_time = datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")

    # Gửi kết quả trò chơi
    result_text = f"┏━━━━━━━━━━━━━┓\n" \
                  f"┣➤ Timeticks : {random_number_ds}\n" \
                  f"┣➤ Kết quả: {'Thắng' if win else 'Thua'}" \
                  f"{' (' + str(win_amount) + ' đ)' if win else ''}\n" \
                  f"┣➤ ({current_time})\n" \
                  f"┣➤ Số dư mới của bạn: {formatted_balance}\n" \
                      # Xoá trạng thái của người dùng sau khi cược thành công

    del user_state_doan[msg.from_user.id]

    result_text += "┗━━━━━━━━━━━━━┛"

    bot.send_message(chat_id=msg.chat.id, text=result_text)

    # Ghi kết quả vào cơ sở dữ liệu
    save_to_alichsuchoi(msg.from_user.id, random_number_ds, current_state,
                        amount, win_amount if win else 0, "Đoán Số",
                        datetime.datetime.now())

    # Cập nhật thông tin vào bảng thongke1p3
    update_thongkeds(
        amount, win_amount, 1 if current_state == "D0" else 0,
        1 if current_state == "D1" else 0, 1 if current_state == "D2" else 0,
        1 if current_state == "D3" else 0, 1 if current_state == "D4" else 0,
        1 if current_state == "D5" else 0, 1 if current_state == "D6" else 0,
        1 if current_state == "D7" else 0, 1 if current_state == "D8" else 0,
        1 if current_state == "D9" else 0)

    send_to_group(msg.from_user.id, result_text)
  except ValueError:
    pass


#code game bầu cua
# Hàm tính toán kết quả Bầu Cua từ 3 con vật ngẫu nhiên
def calculate_bau_cua():
  random_animals = random.sample(list(animals.keys()), 3)
  result_text = "-".join([animals[animal] for animal in random_animals])
  return random_animals, result_text


# Hàm kiểm tra số dư trước khi cược
def check_balance_before_bet(user_id, amount):
  balance = load_balance(user_id)
  return balance >= amount


# Danh sách các con vật
animals = {
    "Khỉ": "🦧",
    "Hổ": "🦁",
    "Tôm": "🦐",
    "Cua": "🦀",
    "Cá": "🐋",
    "Rắn": "🐍"
}

animals_keys = {
    "Khỉ": "so_lan_cuoc_khi",
    "Hổ": "so_lan_cuoc_ho",
    "Tôm": "so_lan_cuoc_tom",
    "Cua": "so_lan_cuoc_cua",
    "Cá": "so_lan_cuoc_ca",
    "Rắn": "so_lan_cuoc_ran"
}


# Hàm xử lý lựa chọn con vật
def select_animal_callback(call):
  user_id = call.from_user.id
  selected_animal = call.data

  user_state_bc[user_id] = {"animal": selected_animal}
  # Hiển thị ô vuông để chọn số tiền cược
  markup = telebot.types.ReplyKeyboardMarkup(row_width=2,
                                             one_time_keyboard=True,
                                             resize_keyboard=True)
  markup.add("1000", "5000", "10000", "20000", "50000", "100000", "200000",
             "500000")
  bot.reply_to(call.message,
               "Chọn nhanh tiền cược hoặc nhập số tiền tùy ý:",
               reply_markup=markup)


# Lệnh chơi game bầu cua
@bot.message_handler(commands=["baucua"])
def play_bau_cua(msg):
  user_id = msg.from_user.id
  user_state_bc[user_id] = "baucua"

  # Hiển thị danh sách các con vật để chọn cược
  markup = types.InlineKeyboardMarkup(row_width=2)
  for animal, emoji in animals.items():
    button = types.InlineKeyboardButton(text=animal, callback_data=animal)
    markup.add(button)

  bot.reply_to(msg, "Chọn 1 trong 6 con vật để cược:", reply_markup=markup)


# Xử lý chọn con vật và yêu cầu nhập số tiền cược
@bot.callback_query_handler(
    func=lambda call: user_state_bc.get(call.from_user.id) == "baucua")
def bet_amount(call):
  user_id = call.from_user.id
  selected_animal = call.data

  if selected_animal not in animals:
    bot.answer_callback_query(call.id, "Vui lòng chọn đúng tên của con vật.")
    return

  user_state_bc[user_id] = {"animal": selected_animal}
  # Hiển thị ô vuông để chọn số tiền cược
  markup = telebot.types.ReplyKeyboardMarkup(row_width=2,
                                             one_time_keyboard=True,
                                             resize_keyboard=True)
  markup.add("1000", "5000", "10000", "20000", "50000", "100000", "200000",
             "500000")
  bot.reply_to(call.message,
               "Chọn nhanh tiền cược hoặc nhập số tiền tùy ý:",
               reply_markup=markup)


# Xử lý số tiền cược và thông báo kết quả
@bot.message_handler(func=lambda message: message.from_user.id in user_state_bc
                     and isinstance(user_state_bc[message.from_user.id], dict))
def process_bet_amount(msg):
  user_id = msg.from_user.id
  try:
    amount = int(msg.text)
    if amount <= 999:
      bot.reply_to(msg, "Số tiền cược phải lớn hơn hoặc = 1.000 đ.")
      return

    if amount >= 1000000:
      bot.reply_to(msg, "Số tiền được cược tối đa là 1.000.000 đ.")
      return

    # Kiểm tra số dư trước khi cược
    if not check_balance_before_bet(user_id, amount):
      bot.reply_to(
          msg,
          "Số dư của bạn không đủ để cược. Vui lòng nạp thêm tiền vào tài khoản."
      )
      del user_state_bc[user_id]
      return

    # Lưu trạng thái hiện tại của người chơi vào biến tạm thời menugame
    current_state = user_state_bc[msg.from_user.id]

    selected_animal = user_state_bc[user_id]["animal"]

    # Trừ tiền cược ngay sau khi nhập số tiền
    balance = load_balance(msg.from_user.id)
    balance -= amount
    save_balance(msg.from_user.id, balance)

    # Tính toán kết quả Bầu Cua
    random_animals, result_text = calculate_bau_cua()

    # Kiểm tra kết quả và xác định thắng/thua
    win = selected_animal in random_animals
    if win:
      win_amount = int(amount * 1.9)
      # Cộng tiền thưởng vào số dư mới
      balance += win_amount
      update_total_bet_amount(msg.from_user.id, amount, win_amount)
    else:
      win_amount = 0

    # Cập nhật số dư mới vào kết quả
    save_balance(msg.from_user.id, balance)

    formatted_balance = "{:,.0f} đ".format(load_balance(msg.from_user.id))

    # Lấy thông tin thời gian hiện tại
    current_time = datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")

    # Hiển thị kết quả trò chơi
    result_text = f"┏━━━━━━━━━━━━━┓\n" \
                  f"┣➤ {result_text}\n" \
                  f"┣➤ Kết quả: {'-'.join(random_animals)}\n" \
                  f"┣➤ Bạn cược: {selected_animal}\n" \
                  f"┣➤ Bạn đã : {'Thắng' if win else 'Thua'}" \
                  f"{' (' + str(win_amount) + ' đ)' if win else ''}\n" \
                  f"┣➤ ({current_time})\n" \
                  f"┣➤ Số dư mới của bạn: {formatted_balance}\n"

    result_text += "┗━━━━━━━━━━━━━┛"

    bot.send_message(chat_id=msg.chat.id, text=result_text)

    # Ghi kết quả vào cơ sở dữ liệu
    save_to_alichsuchoi(msg.from_user.id, '-'.join(random_animals),
                        selected_animal, amount, win_amount if win else 0,
                        "Bầu Cua", datetime.datetime.now())

    # Hàm lưu thống kê
    thongkebc = get_or_create_thongkebc()
    if thongkebc:
      tong_tien_cuoc = thongkebc['tong_tien_cuoc'] + amount
      tong_tien_da_tra = thongkebc[
          'tong_tien_da_tra'] + win_amount if win else thongkebc[
              'tong_tien_da_tra']
      update_thongkebc(tong_tien_cuoc, tong_tien_da_tra,
                       animals_keys[selected_animal])  # Updated line

    send_to_group(msg.from_user.id, result_text)
    # Xoá trạng thái của người dùng sau khi cược thành công
    del user_state_bc[msg.from_user.id]
  except ValueError:
    pass


###########################################################################################################
# Hàm xử lý khi người dùng gửi lệnh /start
@bot.message_handler(commands=["start"])
def start_handler(msg):
  try:
    # Lưu user_id và tên người dùng vào cơ sở dữ liệu users
    user_id = msg.from_user.id
    username = msg.from_user.username
    thoi_gian = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Kiểm tra xem kết nối CSDL đã tồn tại hay chưa
    global db_conn, db_cursor
    if not db_conn or not db_cursor:
      db_conn, db_cursor = connect_to_database()
      if not db_conn or not db_cursor:
        raise Exception("Không thể kết nối cơ sở dữ liệu")

    # Kiểm tra xem user_id đã tồn tại trong cơ sở dữ liệu hay chưa
    query = "SELECT id FROM users WHERE telegram_id = %s"
    params = (user_id, )
    db_cursor.execute(query, params)
    result = db_cursor.fetchone()

    if not result:  # Nếu user_id chưa tồn tại, thêm user_id, tên người dùng và thời gian vào cơ sở dữ liệu users
      query = "INSERT INTO users (telegram_id, username, thoi_gian) VALUES (%s, %s, %s)"
      params = (user_id, username, thoi_gian)
      db_cursor.execute(query, params)
      db_conn.commit()

  # Tạo thông báo chào mừng và hướng dẫn sử dụng bot
    welcome_message = "Chào mừng bạn đã đến với thiên đường giải trí Tele 333 👏👏👏\n\n" \
                      " Tham gia website để nhập gifcode mỗi ngày : http://cltx.ct.ws/ \n\n" \
                      "🍀 Tại đây, bạn có thể chơi rất nhiều game trực tiếp trên Telegram mà không cần cài đặt bất kỳ app nào 🍀\n\n" \
                      "👉 Cách chơi đơn giản, tiện lợi 🎁\n\n" \
                      "👉 Nạp rút nhanh chóng, đa dạng hình thức 💸\n\n" \
                      "👉 Tặng thưởng tiền khi giới thiệu người chơi mới 🤝\n\n" \
                      "👉 Đua top thật hăng, nhận quà cực căng 💍\n\n" \
                      "👉 An toàn, bảo mật tuyệt đối 🏆\n\n" \
                      "⚠️ Chú ý đề phòng lừa đảo ⚠️\n\n" \
                      "Bạn đã sẵn sàng bùng nổ chưa? 💣💣💣"

    # Tạo nút "Chiến thôi !!!!" dưới dòng thông báo
    chienthoi_button = telebot.types.InlineKeyboardButton(
        "👉 Chiến thôi !!!!", callback_data="chienthoi")
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(chienthoi_button)

    # Hiển thị thông báo chào mừng và nút "Chiến thôi !!!!" trên bàn phím ảo
    bot.send_message(msg.chat.id, welcome_message, reply_markup=keyboard)

  except Exception as e:
    print("Lỗi khi xử lý start:", e)
    # Xử lý lỗi theo ý muốn, ví dụ: thông báo cho người dùng hoặc ghi log lỗi


# Hàm đọc thông tin MOMO từ cơ sở dữ liệu
def read_momo_info():
  try:
    db_conn, db_cursor = connect_to_database()
    if not db_conn or not db_cursor:
      return None, None

    query = "SELECT phone_number, account_holder_name FROM momo"
    db_cursor.execute(query)
    result = db_cursor.fetchone()

    if result:
      phone_number, account_holder_name = result
      return phone_number, account_holder_name
    else:
      return None, None
  except Exception as e:
    print("Lỗi khi đọc thông tin MOMO:", e)
    return None, None


# Hàm đọc thông tin ngân hàng từ bảng nganhang
def read_bank_info():
  try:
    # Thực hiện truy vấn SELECT để lấy thông tin từ bảng nganhang
    query = "SELECT bank_name, account_number, account_holder_name FROM nganhang LIMIT 1"
    result = execute_select_query(query)

    if result:
      bank_name, account_number, account_holder_name = result[0]
      return bank_name, account_number, account_holder_name
    else:
      return None, None, None
  except Exception as e:
    print("Lỗi khi đọc thông tin ngân hàng:", e)
    return None, None, None


# Hàm nạp tiền
@bot.message_handler(commands=["nap"])
def handle_nap_command(msg):
  keyboard = types.InlineKeyboardMarkup()
  momo_button = types.InlineKeyboardButton("MOMO", callback_data="momo")
  bank_button = types.InlineKeyboardButton("BANK", callback_data="bank")
  keyboard.row(momo_button,
               bank_button)  # Hiển thị cả hai nút MOMO và BANK cùng một hàng
  bot.send_message(
      msg.chat.id,
      "⭕️ Vui lòng chọn phương thức nạp tiền bên dưới\n\n⭕️ Lưu ý: Nạp tối thiểu 20,000đ, Nội dung phải ghi chính xác",
      reply_markup=keyboard)


# Hàm xử lý sau khi nhấp vào nút "NẠP TIỀN"
@bot.callback_query_handler(func=lambda call: call.data == "nap")
def handle_nap_callback(call):
  handle_nap_command(call.message)


# Hàm xử lý sau khi nhấp vào nút MOMO
@bot.callback_query_handler(func=lambda call: call.data == "momo")
def handle_momo_callback(call):
  # Get user's Telegram UID
  user_id = call.from_user.id
  # Read MOMO information from the database
  phone_number, account_holder_name = read_momo_info()
  if phone_number and account_holder_name:
    momo_content = f"NAP {user_id}"
    message = f"➡️ Chuyển tiền đến số MOMO bên dưới:\n\n➡️ Số điện thoại: {phone_number}\n➡️ Tên người nhận: {account_holder_name}\nNội dung: {momo_content}\n\n⭕️ Vui lòng điền chính xác nội dung để hệ thống xử lý"
    bot.send_message(call.message.chat.id, message)
  else:
    bot.send_message(call.message.chat.id,
                     "Không thể đọc thông tin MOMO. Vui lòng thử lại sau.")

  # Close the database connection
  close_database_connection()

  # Reconnect to the database
  db_conn, db_cursor = connect_to_database()

  # Check if the reconnection is successful
  if db_conn and db_cursor:
    print(Fore.GREEN + "Kết nối lại đến cơ sở dữ liệu thành công!" +
          Style.RESET_ALL)
  else:
    print(Fore.RED + "Không thể kết nối lại đến cơ sở dữ liệu." +
          Style.RESET_ALL)


# Hàm xử lý sau khi nhấp vào nút BANK
@bot.callback_query_handler(func=lambda call: call.data == "bank")
def handle_bank_callback(call):
  # Get user's Telegram UID
  user_id = call.from_user.id
  # Read BANK information from the database
  bank_name, account_number, account_holder_name = read_bank_info()
  if bank_name and account_number and account_holder_name:
    bank_content = f"NAP {user_id}"
    bot.send_message(
        call.message.chat.id,
        f"""➡️ Chuyển tiền đến ngân hàng bên dưới:\n\n➡️ Ngân hàng: {bank_name}\n➡️ Số tài khoản: {account_number}\n➡️ Tên người nhận: {account_holder_name}\nNội dung: {bank_content}\n\n⭕️ Vui lòng điền chính xác nội dung để hệ thống xử lý"""
    )
  else:
    bot.send_message(
        call.message.chat.id,
        "Không thể đọc thông tin ngân hàng. Vui lòng thử lại sau.")

  # Close the database connection
  close_database_connection()

  # Reconnect to the database
  db_conn, db_cursor = connect_to_database()

  # Check if the reconnection is successful
  if db_conn and db_cursor:
    print(Fore.GREEN + "Kết nối lại đến cơ sở dữ liệu thành công!" +
          Style.RESET_ALL)
  else:
    print(Fore.RED + "Không thể kết nối lại đến cơ sở dữ liệu." +
          Style.RESET_ALL)


# Hàm xử lý khi người dùng nhấp vào nút "Nhập Gifcode"
@bot.callback_query_handler(func=lambda call: call.data == "cod")
def handle_gifcode_callback(call):
  bot.send_message(
      call.message.chat.id,
      "💝 Để nhập Giftcode, vui lòng thực hiện theo cú pháp sau:\n\n/code [dấu cách] mã giftcode\n\n➡️ Vd:   /code TELE333"
  )


# Hàm xử lý khi người dùng nhấp vào nút "Chuyển tiền"
@bot.callback_query_handler(func=lambda call: call.data == "c")
def handle_chuyen_tien_callback(call):
  bot.send_message(
      call.message.chat.id,
      "💸 Vui lòng thực hiện theo hướng dẫn sau:\n\n/ct [dấu cách] ID nhận tiền [dấu cách] Số tiền muốn chuyển [dấu cách] Nội dung\n\n➡️ Vd:   /ct 216789354 200000 Lì xì"
  )


# Hàm xử lý khi người dùng nhấp vào nút "ls nap"
@bot.callback_query_handler(func=lambda call: call.data == "lnap")
def handle_ls_nap_callback(call):
  bot.send_message(call.message.chat.id,
                   "VUI LÒNG ẤN VÀO ĐÂY ĐỂ XEM LS NẠP\n\n👉👉👉 /lsnap 👈👈👈")


# Hàm xử lý khi người dùng nhấp vào nút "ls rut"
@bot.callback_query_handler(func=lambda call: call.data == "lrut")
def handle_ls_rut_callback(call):
  bot.send_message(call.message.chat.id,
                   "VUI LÒNG ẤN VÀO ĐÂY ĐỂ XEM LS RÚT\n\n👉👉👉 /lsrut 👈👈👈")


# Hàm xử lý khi người dùng nhấp vào nút "ls rut"
@bot.callback_query_handler(func=lambda call: call.data == "tc")
def handle_ls_rut_callback(call):
  bot.send_message(call.message.chat.id,
                   "VUI LÒNG ẤN VÀO ĐÂY ĐỂ XEM TỔNG CƯỢC\n\n👉👉👉 /info 👈👈👈")


# Hàm xử lý sau khi nhấp vào nút "RÚT TIỀN"
@bot.callback_query_handler(func=lambda call: call.data == "rut")
def handle_rut_callback(call):
  keyboard = types.InlineKeyboardMarkup()
  momo2_button = types.InlineKeyboardButton("MOMO", callback_data="momo2")
  bank2_button = types.InlineKeyboardButton("BANK", callback_data="bank2")
  keyboard.row(momo2_button,
               bank2_button)  # Hiển thị cả hai nút MOMO và BANK cùng một hàng
  bot.send_message(call.message.chat.id,
                   "⭕️ Vui lòng chọn phương thức rút tiền",
                   reply_markup=keyboard)


# Hàm xử lý lệnh /rut
@bot.message_handler(commands=["rut"])
def rut_tien_command(msg):
  keyboard = types.InlineKeyboardMarkup()
  rut_button = types.InlineKeyboardButton("RÚT TIỀN", callback_data="rut")
  keyboard.add(rut_button)  # Hiển thị nút "RÚT TIỀN"
  bot.send_message(msg.chat.id,
                   "Để tiến hành rút tiền, vui lòng chọn 'RÚT TIỀN' dưới đây.",
                   reply_markup=keyboard)


# Hàm xử lý sau khi nhấp vào nút MOMO
@bot.callback_query_handler(func=lambda call: call.data == "momo2")
def handle_momo2_callback(call):
  bot.send_message(
      call.message.chat.id,
      f"""💸 Vui lòng thực hiện theo hướng dẫn sau:\n\n/rutmomo [dấu cách] SĐT [dấu cách] Số tiền muốn rút\n\n➡️ VD:   /rutmomo 0987112233 200000"""
  )


# Hàm xử lý sau khi nhấp vào nút BANK
@bot.callback_query_handler(func=lambda call: call.data == "bank2")
def handle_bank2_callback(call):
  bot.send_message(
      call.message.chat.id,
      f"""🏧 Vui lòng thực hiện theo hướng dẫn sau:\n\n👉 /rutbank [dấu cách] Số tiền muốn rút [dấu cách]  Mã ngân hàng [dấu cách] Số tài khoản [dấu cách] Tên chủ tài khoản\n👉 VD:  Muốn rút 100k đến TK số 01234567890 tại Ngân hàng Vietcombank. Thực hiện theo cú pháp sau:\n\n/rutbank 100000 VCB 01234567890 NGUYEN VAN A\n\n TÊN NGÂN HÀNG - MÃ NGÂN HÀNG\n📌 Vietcombank => VCB\n📌 BIDV => BIDV \n📌 Vietinbank => VTB\n📌 Techcombank => TCB\n📌 MB Bank => MBB \n📌 Agribank => AGR \n📌 TienPhong Bank => TPB\n📌 SHB bank => SHB\n📌 ACB => ACB \n📌 Maritime Bank => MSB\n📌 VIB => VIB\n📌 Sacombank => STB\n📌 VP Bank => VPB\n📌 SeaBank => SEAB\n📌 Shinhan bank Việt Nam => SHBVN\n📌 Eximbank => EIB \n📌 KienLong Bank => KLB \n📌 Dong A Bank => DAB \n📌 HD Bank => HDB \n📌 LienVietPostBank => LPB \n📌 VietBank => VBB\n📌 ABBANK => ABB \n📌 PG Bank => PGB\n📌 PVComBank => PVC\n📌 Bac A Bank => BAB \n📌 Sai Gon Commercial Bank => SCB\n📌 BanVietBank => VCCB \n📌 Saigonbank => SGB\n📌 Bao Viet Bank => BVB  \n📌 Orient Commercial Bank => OCB \n\n⚠️ Lưu ý: Không hỗ trợ hoàn tiền nếu bạn nhập sai thông tin Tài khoản. """
  )


##################tài khoản ###############


# Hàm xử lý sau khi nhấp vào các nút game
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query_game(call):
  if call.data == "chienthoi":
    # hiển thị 6 ô vuông
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2,
                                               one_time_keyboard=True,
                                               resize_keyboard=False)
    markup.add("🎲 Danh sách Game", "👤 Tài khoản", "📜 Event", "🥇 Bảng xếp hạng")
    bot.send_message(
        call.message.chat.id,
        "⚠️ Chú ý đề phòng lừa đảo ⚠️\n\nBOT KHÔNG tự nhắn tin cho người dùng được. Vì vậy, tuyệt đối không tin tưởng bất kỳ ai, bất kỳ tài khoản nào có thông tin giống BOT khi nhắn tin cho bạn trước.\n\nNào, bây giờ bạn hãy chọn món theo Menu ở bên dưới nhé 👇👇👇",
        reply_markup=markup)
  elif call.data == "taixiu":
    bot.send_message(
        call.message.chat.id,
        """🎲 TÀI - XỈU 🎲\n\n👉 Khi BOT trả lời mới được tính là đã đặt cược thành công. Nếu BOT không trả lời => Lượt chơi không hợp lệ và không bị trừ tiền trong tài khoản.\n👉 Xúc xắc được quay random bởi Telegram nên hoàn toàn xanh chín.\n\n❗️❗️❗️ Lưu ý: Các biểu tượng Emoji của Telegram click vào có thể tương tác được tránh bị nhầm lẫn các đối tượng giả mạo bằng ảnh gif ❗️❗️❗️\n\n🔖 Thể lệ:\n👍 Kết quả được tính bằng mặt Xúc Xắc Telegram trả về sau khi người chơi đặt cược:\n\n T ➤ x1.9  ➤ Tổng 3 Xúc Xắc: 11-->18 \n\nX ➤x1.9 ➤ Tổng 3 Xúc Xắc: 3-->10"""
    )
  elif call.data == "taixiu2":
    bot.send_message(
        call.message.chat.id,
        """🎲 TÀI - XỈU 2 🎲\n\n👉 Khi BOT trả lời mới được tính là đã đặt cược thành công. Nếu BOT không trả lời => Lượt chơi không hợp lệ và không bị trừ tiền trong tài khoản.\n👉 Xúc xắc được quay random bởi Telegram nên hoàn toàn xanh chín.\n\n✅ TÀI XỈU 2 CHO PHÉP CHÍNH TAY NGƯỜI CHƠI GỬI XÚC XẮC ✅ \n\n❗️❗️❗️ Lưu ý: Các biểu tượng Emoji của Telegram click vào có thể tương tác được tránh bị nhầm lẫn các đối tượng giả mạo bằng ảnh gif ❗️❗️❗️\n\n🔖 Thể lệ:\n👍 Kết quả được tính bằng mặt Xúc Xắc Telegram trả về sau khi người chơi đặt cược:\n\n/tai2 ➤ x1.9  ➤ Xúc XắC: 1-3-5 \n\n/xiu2 ➤x1.9 ➤ Xúc Xắc: 2-4-6 """
    )
  elif call.data == "chanle":
    bot.send_message(
        call.message.chat.id,
        """✌️ CHẴN - LẺ ✌️\n\n👉 Khi BOT trả lời mới được tính là đã đặt cược thành công. Nếu BOT không trả lời => Lượt chơi không hợp lệ và không bị trừ tiền trong tài khoản.\n👉 Timeticks sẽ bằng chính xác thời gian hiện tại (tính đến mili giây) nên hoàn toàn xanh chín nhá ae.\n\n🔖 Thể lệ:\n👍 Kết quả được tính bằng số cuối cùng của Timeticks.\n\nC ➤ x1.95 ➤ Win: 0|2|4|6|8 \n\nL ➤ x1.95 ➤ Win: 1|3|5|7|9 """
    )
  elif call.data == "chanle2":
    bot.send_message(
        call.message.chat.id,
        """🔴 CHẴN - LẺ 2 ⚪️\n\n👉 Khi BOT trả lời mới được tính là đã đặt cược thành công. Nếu BOT không trả lời => Lượt chơi không hợp lệ và không bị trừ tiền trong tài khoản.\n👉 QUÂN VỊ 🔴  ⚪️ RANDOM xanh chín uy tín \n\n🔖 Thể lệ:\n👉 Chẵn : 🔴-🔴-⚪️-⚪️ / 🔴-🔴-🔴-🔴 / ⚪️-⚪️-⚪️-⚪️\n👉 Lẻ : 🔴-🔴-🔴-⚪️ / ⚪️-⚪️-⚪️-🔴.\n\n/chan2 ➤ x1.9  \n\n/le2 ➤ x1.9 """
    )
  elif call.data == "phan3":
    bot.send_message(
        call.message.chat.id,
        """✌️ 1 phần 3 ✌️\n\n👉 Khi BOT trả lời mới được tính là đã đặt cược thành công. Nếu BOT không trả lời => Lượt chơi không hợp lệ và không bị trừ tiền trong tài khoản.\n👉 Timeticks sẽ bằng chính xác thời gian hiện tại (tính đến mili giây) nên hoàn toàn xanh chín nhá ae.\n\n🔖 Thể lệ:\n👍 Kết quả được tính bằng số cuối cùng của Timeticks.\n\nN0 ➤ x5 ➤ Win: 0\n\nN1 ➤ x3 ➤ Win: 1-2-3\n\nN2 ➤ x3 ➤ Win: 4-5-6\n\nN3 ➤ x3 ➤ Win: 7-8-9 """
    )
  elif call.data == "doanso":
    bot.send_message(
        call.message.chat.id,
        """✌️ Đoán Số ✌️\n\n👉 Khi BOT trả lời mới được tính là đã đặt cược thành công. Nếu BOT không trả lời => Lượt chơi không hợp lệ và không bị trừ tiền trong tài khoản.\n👉 Timeticks sẽ bằng chính xác thời gian hiện tại (tính đến mili giây) nên hoàn toàn xanh chín nhá ae.\n\n🔖 Thể lệ:\n👍 Kết quả Là 1 số Timeticks.\n\nD0 ➤ x9 ➤ Win: 0 \nD1 ➤ x9 ➤ Win: 1\nD2 ➤ x9 ➤ Win: 2\nD3 ➤ x9 ➤ Win: 3\nD4 ➤ x9 ➤ Win: 4\nD5 ➤ x9 ➤ Win: 5\nD6 ➤ x9 ➤ Win: 6\nD7 ➤ x9 ➤ Win: 7\nD8 ➤ x9 ➤ Win: 8\nD9 ➤ x9 ➤ Win: 9"""
    )
  elif call.data == "baucua":
    bot.send_message(
        call.message.chat.id,
        """🐯 BẦU CUA 🦐\n\n👉 Khi BOT trả lời mới được tính là đã đặt cược thành công. Nếu BOT không trả lời => Lượt chơi không hợp lệ và không bị trừ tiền trong tài khoản.\n👉 RANDOM 🦧/🦁/🦐/🦀/🐋/🐍 xanh chín uy tín \n\n🔖 Thể lệ:\n👉 RANDOM 3 trong 6 con vật sau để làm kết quả 🦧/🦁/🦐/🦀/🐋/🐍\n\n/baucua ➤ x1.9"""
    )
  pass


# Hàm xử lý khi người dùng gửi lệnh /game
@bot.message_handler(commands=["game"])
@bot.message_handler(func=lambda message: message.text == "🎲 Danh sách Game")
def show_menu_game(msg):
  keyboard = types.InlineKeyboardMarkup()
  taixiu_button = types.InlineKeyboardButton("🎲Tài Xỉu 🎲",
                                             callback_data="taixiu")
  taixiu2_button = types.InlineKeyboardButton("🎲Tài Xỉu 2 🎲",
                                              callback_data="taixiu2")
  chanle_button = types.InlineKeyboardButton("✌️Chẵn Lẻ ✌️",
                                             callback_data="chanle")
  chanle2_button = types.InlineKeyboardButton("🔴 Chẵn Lẻ 2 ⚪️",
                                              callback_data="chanle2")
  phan3_button = types.InlineKeyboardButton("✌️ 1 phần 3 ✌️",
                                            callback_data="phan3")
  doanso_button = types.InlineKeyboardButton("✌️ Đoán Số ✌️",
                                             callback_data="doanso")
  baucua_button = types.InlineKeyboardButton("🐯 Bầu Cua 🦐",
                                             callback_data="baucua")
  keyboard.row(taixiu_button, taixiu2_button)
  keyboard.row(chanle_button, chanle2_button)
  keyboard.row(phan3_button, doanso_button)
  keyboard.row(baucua_button)

  # Đường dẫn tới tệp hình ảnh bạn muốn gửi
  image_path = "menugame.jpg"

  # Gửi hình ảnh và văn bản
  with open(image_path, "rb") as image_file:
    bot.send_photo(msg.chat.id,
                   image_file,
                   caption="Chọn món bạn thích theo menu bên dưới nào 👇 👇 👇",
                   reply_markup=keyboard)
  pass


#################even#####################3
@bot.message_handler(func=lambda message: message.text == "📜 Event")
def even_account_even(msg):
  thongbao_even = "🎊🎊🎊 Chào mừng bạn đến với thiên đường giải trí http://cltx.ct.ws/ 🎊🎊🎊\n\n📢📢📢 Rất nhiều sự kiện hấp dẫn đang chờ đón bạn 📢📢📢"
  bot.reply_to(msg, thongbao_even)


###############tốp ảo ###################
def format_currency(amount):
  return "{:,.0f} VNĐ".format(amount)


# Hàm đọc thông tin từ bảng tops
def read_top_info():
  try:
    # Thực hiện câu truy vấn SELECT để lấy thông tin từ bảng tops
    query = "SELECT telegram_id, total_bet, virtual_money FROM tops"
    db_cursor.execute(query)
    result = db_cursor.fetchall()

    # Xử lý kết quả trả về để tạo nội dung thông tin TOP
    if result:
      content = ""
      for row in result:
        telegram_id = row[0]
        total_bet = format_currency(row[1])
        virtual_money = format_currency(row[2])
        content += f"ID: {telegram_id}\nTổng cược: {total_bet}\nTiền Thưởng: {virtual_money}\n\n"
      return content
    else:
      return "Hiện không có thông tin TOP."

  except Exception as e:
    print("Lỗi khi đọc thông tin từ bảng tops:", e)
    return None


# Hàm xử lý khi người dùng yêu cầu xem bảng xếp hạng
@bot.message_handler(func=lambda message: message.text == "🥇 Bảng xếp hạng")
def xep_account_hang(msg):
  top_info = read_top_info()
  if top_info:
    xephang_even = f"🏆  Top\n\n{top_info}"
  else:
    xephang_even = "Không thể đọc thông tin bảng xếp hạng. Vui lòng thử lại sau."

  bot.reply_to(msg, xephang_even)


# Hàm thông tin tài khoản
@bot.message_handler(func=lambda message: message.text == "👤 Tài khoản")
def show_account_info(msg):
  user_id = msg.from_user.id
  user_name = msg.from_user.first_name
  user_balance = load_balance(user_id)

  formatted_balance = "{:,.0f} đ".format(user_balance)

  account_info = f"👤 Tên tài khoản: {user_name}\n" \
                 f"💳 ID Tài khoản: {user_id}\n" \
                 f"💰 Số dư: {formatted_balance}\n"

  # Thêm nút "NẠP TIỀN" vào bảng phím và gán callback_data="nap"
  nap_button = telebot.types.InlineKeyboardButton("💴 Nạp tiền",
                                                  callback_data="nap")
  rut_button = telebot.types.InlineKeyboardButton("💴 Rút tiền",
                                                  callback_data="rut")
  code_button = telebot.types.InlineKeyboardButton("🎁 Nhập Gifcode",
                                                   callback_data="cod")
  ct_button = telebot.types.InlineKeyboardButton("💴 Chuyển tiền",
                                                 callback_data="c")
  lsnap_button = telebot.types.InlineKeyboardButton("📊 Lịch sử nạp",
                                                    callback_data="lnap")
  lsrut_button = telebot.types.InlineKeyboardButton("📊 Lịch sử rút",
                                                    callback_data="lrut")
  tc_button = telebot.types.InlineKeyboardButton("📝 Tổng cược",
                                                 callback_data="tc")
  keyboard = telebot.types.InlineKeyboardMarkup()
  keyboard.row(nap_button, rut_button)
  keyboard.row(code_button, ct_button)
  keyboard.row(lsnap_button, lsrut_button)
  keyboard.row(tc_button)

  bot.reply_to(msg, account_info, reply_markup=keyboard)


#################menu game  ####################

#tạo code  và  nhập code
# Lưu trạng thái của người dùng và danh sách admin có quyền tạo code
 #  danh sách các ID của admin


# Kiểm tra xem người dùng có phải là admin hay không


# Hàm tạo mã code ngẫu nhiên
def tao_ma_code_ngau_nhien():
  return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', k=6))


# Hàm lưu thông tin mã code và số tiền vào bảng codes
def luu_code_vao_csdl(code, so_tien):
  try:
    # Thực hiện câu truy vấn INSERT để thêm thông tin vào bảng codes
    query = f"INSERT INTO codes (code, amount) VALUES ('{code}', {so_tien})"
    db_cursor.execute(query)
    db_conn.commit()
  except Exception as e:
    print("Lỗi khi lưu thông tin mã code vào cơ sở dữ liệu:", e)


# Hàm kiểm tra xem mã code có tồn tại trong bảng codes hay không
def kiem_tra_ton_tai_code_trong_csdl(code):
  try:
    # Thực hiện câu truy vấn SELECT để kiểm tra mã code trong bảng codes
    query = f"SELECT code FROM codes WHERE code = '{code}'"
    db_cursor.execute(query)
    result = db_cursor.fetchone()
    return result is not None
  except Exception as e:
    print("Lỗi khi kiểm tra mã code trong cơ sở dữ liệu:", e)
    return False


# Hàm lấy số tiền tương ứng với mã code từ bảng codes
def lay_so_tien_tu_csdl(code):
  try:
    # Thực hiện câu truy vấn SELECT để lấy số tiền từ bảng codes
    query = f"SELECT amount FROM codes WHERE code = '{code}'"
    db_cursor.execute(query)
    result = db_cursor.fetchone()

    if result is not None:
      return float(result[0])
    else:
      return None
  except Exception as e:
    print("Lỗi khi lấy số tiền từ cơ sở dữ liệu:", e)
    return None


# Hàm xóa mã code khỏi bảng codes sau khi đã sử dụng
def xoa_code_khoi_csdl(code):
  try:
    # Thực hiện câu truy vấn DELETE để xóa mã code khỏi bảng codes
    query = f"DELETE FROM codes WHERE code = '{code}'"
    db_cursor.execute(query)
    db_conn.commit()
  except Exception as e:
    print("Lỗi khi xóa mã code khỏi cơ sở dữ liệu:", e)
    db_conn.rollback()


# Lệnh /taocode
@bot.message_handler(commands=["taocode"])
def tao_code(msg):
  user_id = msg.from_user.id
  if not la_admin(user_id):
    bot.reply_to(msg, "Bạn không có quyền sử dụng lệnh này.")
    return

  user_state_cd[user_id] = "tao_code_amount"
  bot.reply_to(msg, "Nhập số tiền muốn tạo code:")


# Xử lý khi nhập số tiền muốn tạo code
@bot.message_handler(
    func=lambda message: message.from_user.id in user_state_cd and
    user_state_cd[message.from_user.id] == "tao_code_amount")
def luu_so_tien_tao_code(msg):
  try:
    so_tien = int(msg.text)
    if so_tien <= 0:
      bot.reply_to(msg, "Số tiền phải lớn hơn 0.")
      return

    code = tao_ma_code_ngau_nhien()
    luu_code_vao_csdl(code,
                      so_tien)  # Thêm mã code và số tiền vào cơ sở dữ liệu
    bot.reply_to(
        msg,
        f"Mã code của bạn: {code} với số tiền: {so_tien:,} đ đã được tạo thành công."
    )
    del user_state_cd[
        msg.from_user.id]  # Xoá trạng thái tạo code sau khi đã tạo thành công
  except ValueError:
    pass


# Hàm để lưu lịch sử dùng code vào bảng lichsucode
def luu_lich_su_dung_code(telegram_id, code, so_tien, so_du, thoi_gian):
  db_conn, db_cursor = connect_to_database()
  if not db_conn or not db_cursor:
    return

  try:
    query = "INSERT INTO lichsucode (id,telegram_id, code, so_tien, so_du, thoi_gian) VALUES (0,%s, %s, %s, %s, %s)"
    params = (telegram_id, code, so_tien, so_du, thoi_gian)
    db_cursor.execute(query, params)
    db_conn.commit()

  except mysql.connector.Error as e:
    print(f"Lỗi khi lưu lịch sử dùng code: {e}")
    return


# Lệnh /code (code)
@bot.message_handler(commands=["code"])
def kiem_tra_code(msg):
  try:
    code = msg.text.split()[1]

    if kiem_tra_ton_tai_code_trong_csdl(
        code):  # Kiểm tra mã code trong cơ sở dữ liệu
      so_tien = lay_so_tien_tu_csdl(code)  # Lấy số tiền từ cơ sở dữ liệu
      balance = load_balance(msg.from_user.id)
      balance += so_tien
      save_balance(msg.from_user.id,
                   balance)  # Cộng số tiền vào số dư của người dùng

      # Ghi lại lịch sử dùng code vào bảng lichsucode
      thoi_gian = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      luu_lich_su_dung_code(msg.from_user.id, code, so_tien, balance,
                            thoi_gian)

      bot.reply_to(
          msg,
          f"Code hợp lệ ✅ . Bạn đã được cộng {so_tien:,} đ vào số dư của mình."
      )
      xoa_code_khoi_csdl(code)  # Xoá mã code đã sử dụng khỏi cơ sở dữ liệu
    else:
      bot.reply_to(msg, "Code không hợp lệ hoặc đã được sử dụng.")
  except IndexError:
    bot.reply_to(
        msg, "Vui lòng nhập mã code sau dấu /code (ví dụ: /code TELE333).")


#hàm rút tiền
# Hàm cập nhật số dư trong bảng users
def update_balance(telegram_id, new_balance):
  try:
    # Thực hiện truy vấn UPDATE để cập nhật số dư mới trong bảng users
    query = "UPDATE users SET balance = %s WHERE telegram_id = %s"
    execute_non_select_query(query, (new_balance, telegram_id))

  except Exception as e:
    print("Lỗi khi cập nhật số dư trong bảng users:", e)


# Hàm lưu lịch sử rút tiền vào bảng rutmomo
def save_withdraw_history(telegram_id, momo_account, withdraw_amount):
  try:
    # Thực hiện truy vấn INSERT để lưu lịch sử rút tiền vào bảng rutmomo
    query = "INSERT INTO rutmomo (telegram_id, momo_number, withdrawal_amount, status) VALUES (%s, %s, %s, %s)"
    execute_non_select_query(
        query, (telegram_id, momo_account, withdraw_amount, "Thành công"))

  except Exception as e:
    print("Lỗi khi lưu lịch sử rút tiền:", e)


# Hàm xử lý lệnh /rutmomo
@bot.message_handler(commands=["rutmomo"])
def process_rutmomo(msg):
  try:
    command_parts = msg.text.split()
    momo_account = command_parts[1]
    withdraw_amount = int(command_parts[2])

    # Kiểm tra xem số tiền rút có đủ lớn không (tối thiểu 10,000 đồng)
    if withdraw_amount < 9999:
      bot.reply_to(msg, "Số tiền rút phải lớn hơn hoặc bằng 10,000 đồng.")
      return

    user_balance = load_balance(msg.from_user.id)

    # Kiểm tra xem số dư của người dùng có đủ không
    if withdraw_amount > user_balance:
      bot.reply_to(msg, "Số dư của bạn không đủ để rút số tiền này.")
      return

    # Trừ số tiền rút khỏi số dư của người dùng
    new_balance = user_balance - withdraw_amount
    update_balance(msg.from_user.id, new_balance)

    # Lưu lịch sử rút tiền
    save_withdraw_history(msg.from_user.id, momo_account, withdraw_amount)

    # Gửi thông báo về quá trình rút tiền
    formatted_balance = "{:,.0f} đ".format(new_balance)
    bot.reply_to(
        msg,
        f"Lệnh rút {withdraw_amount:,} đ về {momo_account} đang được hệ thống thanh toán. Số tiền còn lại của bạn: {formatted_balance}"
    )

    # Yêu cầu rút tiền từ bot Telegram khác
    request_message = f"{msg.from_user.first_name} yêu cầu rút {withdraw_amount:,} đ về {momo_account}"
    another_bot_token = "6310695001:AAHecY0B84EmnM_lH8JqnkN2Eyeta20MdXc"
    another_bot_chat_id = "5646550838"
    requests.get(
        f"https://api.telegram.org/bot{another_bot_token}/sendMessage?chat_id={another_bot_chat_id}&text={request_message}"
    )

  except (ValueError, IndexError):
    bot.reply_to(
        msg,
        "Vui lòng nhập đúng định dạng lệnh (ví dụ: /rutmomo 12345678 12234).")


#################################################################


# Hàm xử lý lệnh /lsrut để kiểm tra lịch sử rút tiền
@bot.message_handler(commands=["lsrut"])
def check_withdraw_history(msg):
  try:
    uid = msg.from_user.id

    # Lấy dữ liệu từ bảng rutmomo
    query_rutmomo = "SELECT momo_number, withdrawal_method, FORMAT(withdrawal_amount, 2) as withdrawal_amount, time, status FROM rutmomo WHERE telegram_id = %s"
    params_rutmomo = (uid, )
    rutmomo_data = execute_select_query(query_rutmomo, params_rutmomo)

    # Lấy dữ liệu từ bảng rutbank
    query_rutbank = "SELECT bank_name, account_number, account_holder_name, FORMAT(amount, 2) as amount, time, status FROM rutbank WHERE telegram_id = %s"
    params_rutbank = (uid, )
    rutbank_data = execute_select_query(query_rutbank, params_rutbank)

    # Kết hợp dữ liệu từ cả hai bảng rutmomo và rutbank
    combined_data = rutmomo_data + rutbank_data

    if combined_data:
      # Format dữ liệu thành chuỗi để gửi về cho người dùng
      history_content = "\n".join([
          f"{row[0]} - {row[1]} - {row[2]} - {row[3]} - {row[4]}"
          for row in combined_data
      ])
      bot.reply_to(
          msg,
          "SỐ MOMO RÚT - MOMO - SỐ TIỀN - THỜI GIAN - TRẠNG THÁI\nSTK - NGÂN HÀNG - CTK - SỐ TIỀN - THỜI GIAN - TRẠNG THÁI\n\n"
          + history_content)
    else:
      bot.reply_to(msg, "Bạn chưa có lịch sử rút tiền.")
  except Exception as e:
    bot.reply_to(msg, "Đã xảy ra lỗi khi lấy lịch sử rút tiền.")


##############rút về ngân hàng ###############
# Hàm để lưu lịch sử rút tiền vào bảng rutbank
def save_withdraw_history_bank(uid, bank_info, withdraw_amount):
  try:
    query = "INSERT INTO rutbank (telegram_id, bank_name, account_number, account_holder_name, amount) VALUES (%s, %s, %s, %s, %s)"
    execute_non_select_query(
        query, (uid, bank_info['tên ngân hàng'], bank_info['số tài khoản'],
                bank_info['tên chủ tài khoản'], withdraw_amount))
  except Exception as e:
    print("Lỗi khi lưu lịch sử rút tiền:", e)


# Hàm để cập nhật số dư trong bảng users
def update_balance(telegram_id, new_balance):
  try:
    query = "UPDATE users SET balance = %s WHERE telegram_id = %s"
    execute_non_select_query(query, (new_balance, telegram_id))
  except Exception as e:
    print("Lỗi khi cập nhật số dư trong bảng users:", e)


# Xử lý lệnh /rutbank (số tiền) (tên ngân hàng) (số tài khoản) (tên chủ tài khoản)
@bot.message_handler(commands=["rutbank"])
def withdraw_balance_bank(msg):
  try:
    command_parts = msg.text.split()
    withdraw_amount = int(command_parts[1])
    bank_name = command_parts[2]
    bank_account = command_parts[3]
    account_holder = " ".join(command_parts[4:])

    # Kiểm tra xem số tiền rút có đủ lớn không (tối thiểu 10,000 đồng)
    if withdraw_amount < 19999:
      bot.reply_to(msg, "Số tiền rút phải lớn hơn hoặc bằng 20,000 đồng.")
      return

    user_balance = load_balance(msg.from_user.id)

    # Kiểm tra xem số dư của người dùng có đủ không
    if withdraw_amount > user_balance:
      bot.reply_to(msg, "Số dư của bạn không đủ để rút số tiền này.")
      return

    # Trừ số tiền rút khỏi số dư của người dùng
    new_balance = user_balance - withdraw_amount
    update_balance(msg.from_user.id, new_balance)

    # Lưu lịch sử rút tiền về BANK
    bank_info = {
        "tên ngân hàng": bank_name,
        "số tài khoản": bank_account,
        "tên chủ tài khoản": account_holder
    }
    save_withdraw_history_bank(msg.from_user.id, bank_info, withdraw_amount)

    # Gửi thông báo về quá trình rút tiền
    formatted_balance = "{:,.0f} đ".format(new_balance)
    bot.reply_to(
        msg,
        f"Lệnh rút {withdraw_amount:,} đ về {bank_name} - {bank_account} - {account_holder} đang được hệ thống thanh toán. Số tiền còn lại của bạn: {formatted_balance}"
    )

    # Yêu cầu rút tiền từ bot Telegram khác
    request_message = f"{msg.from_user.first_name} yêu cầu rút {withdraw_amount:,} đ về ngân hàng {bank_name} - {bank_account} - {account_holder}"
    another_bot_token = "7914109458:AAFWgoFEF-mb_ovOX5OAN131NSCA1ekrduA"
    another_bot_chat_id = "-4680613721"  # Thay bằng chat ID phù hợp của bot khác
    requests.get(
        f"https://api.telegram.org/bot{another_bot_token}/sendMessage?chat_id={another_bot_chat_id}&text={request_message}"
    )

  except (ValueError, IndexError):
    bot.reply_to(
        msg,
        "Vui lòng nhập đúng định dạng lệnh (ví dụ: /rutbank (số tiền) (tên ngân hàng) (số tài khoản) (tên chủ tài khoản))."
    )


# Hàm để lấy thông tin người dùng từ bảng users
def load_user_info(telegram_id):
  try:
    query = "SELECT * FROM users WHERE telegram_id = %s"
    result = execute_select_query(query, (telegram_id, ))
    if result:
      return result[0]
    else:
      return None
  except Exception as e:
    print("Lỗi khi lấy thông tin người dùng:", e)
    return None


#hàm lưu lịch sử chuyển tiền


def save_transaction_history(id_tele_chuyen, id_tele_nhan, so_tien, noi_dung,
                             thoi_gian):
  trang_thai = "Thành Công"
  query = "INSERT INTO lichsuct (id_tele_chuyen, id_tele_nhan, so_tien, noi_dung, thoi_gian, trang_thai) VALUES (%s, %s, %s, %s, %s, %s)"
  params = (id_tele_chuyen, id_tele_nhan, so_tien, noi_dung, thoi_gian,
            trang_thai)
  execute_non_select_query(query, params)


# Xử lý khi người dùng nhập /ct (uid) (số tiền) (nội dung)
@bot.message_handler(commands=["ct"])
def chuyen_tien(msg):
  try:
    command_parts = msg.text.split()
    uid_nguoi_nhan = int(command_parts[1])
    ct_amount = int(command_parts[2])
    ct_content = " ".join(command_parts[3:])

    # Kiểm tra xem uid_nguoi_nhan có tồn tại trong bảng users hay không
    user_nguoi_nhan = load_user_info(uid_nguoi_nhan)
    if not user_nguoi_nhan:
      bot.reply_to(msg, "Người nhận không tồn tại trên hệ thống.")
      return

    # Kiểm tra số tiền chuyển (tối thiểu 1000 đồng)
    if ct_amount < 999:
      bot.reply_to(msg, "Số tiền chuyển phải lớn hơn hoặc bằng 1.000 đồng.")
      return

    user_balance = load_balance(msg.from_user.id)

    # Kiểm tra xem số dư của người gửi có đủ không
    if ct_amount > user_balance:
      bot.reply_to(msg, "Số dư của bạn không đủ để chuyển số tiền này.")
      return

    # Kiểm tra xem người gửi có chuyển tiền cho chính mình không
    if msg.from_user.id == uid_nguoi_nhan:
      bot.reply_to(msg, " ❌❌❌ BẠN KHÔNG THỂ CHUYỂN TIỀN CHO CHÍNH MÌNH !!!")
      return

    # Trừ tiền từ số dư của người gửi
    new_balance_nguoi_gui = user_balance - ct_amount
    update_balance(msg.from_user.id, new_balance_nguoi_gui)

    # Cộng tiền vào số dư của người nhận
    user_balance_nguoi_nhan = load_balance(uid_nguoi_nhan)
    new_balance_nguoi_nhan = user_balance_nguoi_nhan + ct_amount
    update_balance(uid_nguoi_nhan, new_balance_nguoi_nhan)

    # Lấy thông tin thời gian hiện tại
    current_time = datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")

    # Lưu thông tin lịch sử chuyển tiền vào bảng lichsuct
    id_tele_chuyen = msg.from_user.id
    id_tele_nhan = uid_nguoi_nhan
    thoi_gian = datetime.datetime.now()  # Lấy thời gian hiện tại
    save_transaction_history(id_tele_chuyen, id_tele_nhan, ct_amount,
                             ct_content, thoi_gian)

    # Gửi thông báo cho người nhận về việc đã nhận tiền
    nguoi_gui = msg.from_user.first_name
    formatted_balance_nguoi_nhan = "{:,.0f} đ".format(new_balance_nguoi_nhan)
    bot.send_message(
        uid_nguoi_nhan, f"┏━━━━━━━━━━━━━┓\n"
        f"┣➤ Tên: {nguoi_gui}\n"
        f"┣➤ Chuyển cho bạn: {ct_amount:,} đ\n"
        f"┣➤ Nội dung: {ct_content}\n"
        f"┣➤ Lúc: ({current_time})\n"
        f"┣➤ Số dư: {formatted_balance_nguoi_nhan}\n"
        f"┗━━━━━━━━━━━━━┛")

    # Gửi thông báo cho người gửi về việc đã chuyển tiền thành công
    formatted_balance_nguoi_gui = "{:,.0f} đ".format(new_balance_nguoi_gui)

    bot.reply_to(
        msg, f"┏━━━━━━━━━━━━━┓\n"
        f"┣➤ Chuyển tiền thành công ✅ \n"
        f"┣➤ Số tiền : {ct_amount:,} đ\n"
        f"┣➤ Đã được chuyển cho người nhận.\n"
        f"┣➤ Số dư mới của bạn: {formatted_balance_nguoi_gui}\n"
        f"┗━━━━━━━━━━━━━┛")

  except (ValueError, IndexError):
    bot.reply_to(
        msg,
        "Vui lòng nhập đúng định dạng lệnh (ví dụ: /ct (uid) (số tiền) (nội dung))."
    )


# Chạy bot
bot.polling()
