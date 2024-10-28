from nicegui import ui
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json

# Định nghĩa lớp User để đại diện cho người dùng trong hệ thống
class User:
    def __init__(self, username, fullname, email, birthdate, password=None, password_hash=None):
        self.username = username  # Tên đăng nhập
        self.fullname = fullname  # Họ tên đầy đủ
        self.email = email        # Email người dùng
        self.birthdate = birthdate  # Ngày sinh
        if password:
            self.password_hash = generate_password_hash(password)  # Mã hóa mật khẩu mới
        else:
            self.password_hash = password_hash  # Sử dụng mật khẩu đã mã hóa

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)  # Kiểm tra mật khẩu có khớp không

# Định nghĩa lớp UserDatabase để quản lý dữ liệu người dùng
class UserDatabase:
    def __init__(self, filepath='users.json'):
        self.filepath = filepath  # Đường dẫn file JSON lưu dữ liệu
        self.users = self.load_users()  # Tải dữ liệu người dùng khi khởi tạo

    def add_user(self, user):
        # Kiểm tra username đã tồn tại
        if user.username in self.users:
            return False, "Tên đăng nhập đã tồn tại!"
        
        # Kiểm tra email đã được sử dụng
        for u in self.users.values():
            if u.email == user.email:
                return False, "Email đã được sử dụng!"
            
        # Thêm user mới và lưu vào file
        self.users[user.username] = user
        self.save_users()
        return True, "Đăng ký thành công!"

    def load_users(self):
        # Đọc dữ liệu từ file JSON
        try:
            with open(self.filepath, 'r') as file:
                users_data = json.load(file)
                return {username: User(**user) for username, user in users_data.items()}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}  # Trả về dict rỗng nếu file không tồn tại hoặc lỗi

    def save_users(self):
        # Lưu dữ liệu người dùng vào file JSON
        with open(self.filepath, 'w') as file:
            json.dump({username: user.__dict__ for username, user in self.users.items()}, file)

    def find_user_by_username(self, username):
        # Tìm user theo username
        return self.users.get(username)

    def find_user_by_email(self, email):
        # Tìm user theo email
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    def authenticate_user(self, username, password):
        # Xác thực thông tin đăng nhập
        user = self.find_user_by_username(username) or self.find_user_by_email(username)
        if user and user.check_password(password):
            return True, "Đăng nhập thành công!"
        return False, "Thông tin đăng nhập không hợp lệ!"

# Khởi tạo đối tượng database
user_db = UserDatabase()

# Các hàm tiện ích (utility functions)
def create_centered_container():
    # Tạo container căn giữa màn hình
    return ui.element('div').style('position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 100%; max-width: 400px;')

def redirect(url: str):
    # Chuyển hướng trang
    ui.run_javascript(f'window.location.href = "{url}"')

def get_date_limits():
    # Lấy giới hạn ngày cho input date
    today = datetime.now()
    max_date = today.strftime('%Y-%m-%d')  # Ngày hiện tại
    min_date = (today - timedelta(days=365 * 100)).strftime('%Y-%m-%d')  # 100 năm trước
    return min_date, max_date

# Trang đăng nhập (/)
@ui.page('/')
def login_page():
    # Tạo giao diện đăng nhập
    with create_centered_container():
        with ui.card().classes('w-full p-6'):
            # Tiêu đề
            ui.label('Đăng nhập').classes('text-2xl font-bold text-center mb-6')
            
            with ui.column().classes('w-full gap-4'):
                # Form đăng nhập
                username_input = ui.input('Nhập email tài khoản học').props('outlined required').classes('w-full')
                password_input = ui.input('Nhập mật khẩu').props('outlined required type=password').classes('w-full')
                
                # Link quên mật khẩu
                ui.link('Quên mật khẩu?', '/forgot-password').classes('text-blue-500 text-center hover:text-blue-700 cursor-pointer no-underline')
                
                # Xử lý đăng nhập
                async def handle_login():
                    success, message = user_db.authenticate_user(username_input.value, password_input.value)
                    ui.notify(message, color='positive' if success else 'negative')
                    if success:
                        redirect('/home')

                # Nút đăng nhập
                ui.button('ĐĂNG NHẬP', on_click=handle_login).classes('w-full bg-blue-500 text-white')
                
                # Phần link đăng ký
                with ui.row().classes('w-full justify-center items-center gap-2 mt-4'):
                    ui.label('Chưa có tài khoản?').classes('text-center')
                    ui.link('Tạo tài khoản mới', '/register').classes('text-blue-500 hover:text-blue-700 cursor-pointer no-underline')

# Trang đăng ký (/register)
@ui.page('/register')
def register_page():
    # Lấy giới hạn ngày
    min_date, max_date = get_date_limits()
    
    # Tạo giao diện đăng ký
    with create_centered_container():
        with ui.card().classes('w-full p-6'):
            # Tiêu đề
            ui.label('Đăng ký').classes('text-2xl font-bold text-center mb-6')
            
            with ui.column().classes('w-full gap-4') as form_container:
                # Form đăng ký
                username_input = ui.input('Tên đăng nhập*').props('outlined required').classes('w-full')
                fullname_input = ui.input('Họ&Tên người dùng*').props('outlined required').classes('w-full')
                email_input = ui.input('Email*').props('outlined required type=email').classes('w-full')
                birthdate_input = ui.input('Ngày sinh*').props(f'outlined required type=date min="{min_date}" max="{max_date}"').classes('w-full')
                password_input = ui.input('Mật khẩu*').props('outlined required type=password').classes('w-full')
                confirm_password_input = ui.input('Nhập lại mật khẩu*').props('outlined required type=password').classes('w-full')
                
                # Thông báo
                ui.label('* Vui lòng nhập đúng & ghi nhớ thông tin để lấy lại mật khẩu khi cần thiết').classes('text-red-500 text-sm mb-2')

                # Nút đăng ký
                register_button = ui.button('ĐĂNG KÝ').classes('w-full bg-blue-500 text-white')
                
                # Xử lý đăng ký
                async def validate_and_register():
                    # Kiểm tra ngày sinh
                    if not birthdate_input.value:
                        ui.notify('Vui lòng nhập ngày sinh!', color='negative')
                        return
                    
                    # Kiểm tra định dạng ngày
                    input_date = datetime.strptime(birthdate_input.value, '%Y-%m-%d')
                    min_date_obj = datetime.strptime(min_date, '%Y-%m-%d')
                    max_date_obj = datetime.strptime(max_date, '%Y-%m-%d')

                    # Validate ngày sinh
                    if input_date < min_date_obj or input_date > max_date_obj:
                        birthdate_input.value = min_date
                        ui.notify('Ngày sinh không hợp lệ! Vui lòng nhập đúng ngày sinh.', color='negative')
                        return
                    
                    # Kiểm tra mật khẩu
                    if password_input.value != confirm_password_input.value:
                        ui.notify('Mật khẩu không khớp!', color='negative')
                        return
                    
                    # Kiểm tra email
                    if not '@' in email_input.value:
                        ui.notify('Email không hợp lệ!', color='negative')
                        return
                    
                    # Tạo user mới
                    new_user = User(
                        username=username_input.value,
                        fullname=fullname_input.value,
                        email=email_input.value,
                        birthdate=birthdate_input.value,
                        password=password_input.value
                    )
                    
                    # Thêm user vào database
                    success, message = user_db.add_user(new_user)
                    if success:
                        print(f"User registered: {new_user.__dict__}")

                    ui.notify(message, color='positive' if success else 'negative')
                    if success:
                        register_button.visible = False
                        ui.link('Quay lại đăng nhập', '/').classes('w-full text-center text-blue-500 hover:text-blue-700 cursor-pointer no-underline')

                register_button.on_click(validate_and_register)

# Trang quên mật khẩu (/forgot-password)
@ui.page('/forgot-password')
def forgot_password_page():
    # Tạo giao diện quên mật khẩu
    with create_centered_container():
        with ui.card().classes('w-full p-6'):
            # Tiêu đề
            ui.label('Tìm tài khoản').classes('text-2xl font-bold text-center mb-6')
            
            with ui.column().classes('w-full gap-4'):
                # Thông báo
                ui.label('* Vui lòng nhập email đã đăng ký').classes('text-red-500 text-sm mb-2')
                # Input email
                email_input = ui.input('Nhập email tài khoản').props('outlined required').classes('w-full')
                
                # Xử lý xác minh email
                async def verify_email():
                    if not '@' in email_input.value:
                        ui.notify('Email không hợp lệ!', color='negative')
                        return
                    
                    user = user_db.find_user_by_email(email_input.value)
                    if user:
                        ui.notify('Đã tìm thấy tài khoản! Chuyển đến xác minh thông tin...', color='positive')
                        ui.timer(2.0, lambda: redirect(f'/verify-account/{user.username}'))
                    else:
                        ui.notify('Không tìm thấy tài khoản với email này!', color='negative')

                # Nút tiếp tục
                ui.button('Tiếp tục', on_click=verify_email).classes('w-full bg-blue-500 text-white')
                
                # Link quay lại
                with ui.row().classes('w-full justify-center items-center gap-2 mt-4'):
                    ui.link('Quay lại đăng nhập', '/').classes('text-blue-500 hover:text-blue-700 cursor-pointer no-underline')

# Trang xác minh tài khoản (/verify-account/{username})
@ui.page('/verify-account/{username}')
def verify_account_page(username: str):
    # Lấy giới hạn ngày
    min_date, max_date = get_date_limits()
    
    # Tạo giao diện xác minh
    with create_centered_container():
        with ui.card().classes('w-full p-6'):
            # Tiêu đề
            ui.label('Xác minh thông tin').classes('text-2xl font-bold text-center mb-6')
            
            with ui.column().classes('w-full gap-4'):
                # Thông báo
                ui.label('* Vui lòng nhập chính xác thông tin đã đăng ký').classes('text-red-500 text-sm mb-2')
                # Form xác minh
                fullname_input = ui.input('Họ & Tên người dùng').props('outlined required').classes('w-full')
                birthdate_input = ui.input('Ngày sinh*').props(f'outlined required type=date min="{min_date}" max="{max_date}"').classes('w-full')
                
                # Xử lý xác minh thông tin
                async def verify_info():
                    user = user_db.find_user_by_username(username)
                    if user and user.fullname == fullname_input.value and user.birthdate == birthdate_input.value:
                        ui.notify('Xác minh thành công! Chuyển đến đặt lại mật khẩu...', color='positive')
                        ui.timer(2.0, lambda: redirect(f'/reset-password/{username}'))
                    else:
                        ui.notify('Thông tin không chính xác!', color='negative')

                # Nút xác minh
                ui.button('Xác minh', on_click=verify_info).classes('w-full bg-blue-500 text-white')
                
                # Link quay lại
                with ui.row().classes('w-full justify-center items-center gap-2 mt-4'):
                    ui.link('Quay lại', '/forgot-password').classes('text-blue-500 hover:text-blue-700 cursor-pointer no-underline')

# Định nghĩa trang đặt lại mật khẩu với tham số username
@ui.page('/reset-password/{username}')
def reset_password_page(username: str):
    # Tạo container có căn giữa để hiển thị form
    with create_centered_container():
        # Tạo card chứa form đặt lại mật khẩu
        with ui.card().classes('w-full p-6'):
            # Tiêu đề của form
            ui.label('Đặt lại mật khẩu').classes('text-2xl font-bold text-center mb-6')
            
            # Tạo cột chứa các trường nhập liệu
            with ui.column().classes('w-full gap-4'):
                # Input field cho mật khẩu mới
                new_password = ui.input('Mật khẩu mới*')\
                    .props('outlined required type=password')\
                    .classes('w-full')
                
                # Input field để xác nhận mật khẩu mới
                confirm_password = ui.input('Xác nhận mật khẩu mới*')\
                    .props('outlined required type=password')\
                    .classes('w-full')
                
                # Nút để thực hiện đặt lại mật khẩu
                reset_button = ui.button('Đổi mật khẩu')\
                    .classes('w-full bg-blue-500 text-white')
                
                # Hàm xử lý sự kiện khi nhấn nút đặt lại mật khẩu
                async def reset_password():
                    # Kiểm tra xem hai mật khẩu có khớp nhau không
                    if new_password.value != confirm_password.value:
                        ui.notify('Mật khẩu không khớp!', color='negative')
                        return
                    
                    # Tìm user trong database
                    user = user_db.find_user_by_username(username)
                    if user:
                        # Cập nhật mật khẩu mới đã được mã hóa
                        user.password_hash = generate_password_hash(new_password.value)
                        # Hiển thị thông báo thành công
                        ui.notify('Đổi mật khẩu thành công!', color='positive')
                        # Ẩn nút đặt lại mật khẩu
                        reset_button.visible = False
                        # Hiển thị link quay về trang đăng nhập
                        ui.link('Quay lại đăng nhập', '/')\
                            .classes('w-full text-center text-blue-500 hover:text-blue-700 cursor-pointer no-underline')
                    else:
                        # Hiển thị thông báo lỗi nếu không tìm thấy user
                        ui.notify('Có lỗi xảy ra!', color='negative')
                
                # Gán hàm xử lý sự kiện cho nút đặt lại mật khẩu
                reset_button.on_click(reset_password)

# Định nghĩa trang chủ sau khi đăng nhập
@ui.page('/home')
def home_page():
    # Tạo cột chứa nội dung trang chủ
    with ui.column().classes('w-full items-center p-4'):
        # Hiển thị thông điệp chào mừng
        ui.label('Chào mừng đến trang chủ!')\
            .classes('text-2xl font-bold mb-4')
        # Tạo nút đăng xuất và chuyển hướng về trang đăng nhập
        ui.button('Đăng xuất', on_click=lambda: redirect('/'))\
            .classes('bg-red-500 text-white')

# In ra danh sách người dùng đã đăng kí trước đó
print("Danh sách người dùng:")
for username, user in user_db.users.items():
    print(f"Username: {username}")
    print(f"Fullname: {user.fullname}")
    print(f"Email: {user.email}")
    print(f"Birthdate: {user.birthdate}")
    print("-------------------")

# Khởi chạy ứng dụng
ui.run()