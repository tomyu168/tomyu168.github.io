from telethon.sync import TelegramClient

api_id = '24053889'
api_hash = '8e1a8794cf3c36a56097cd8d3f3775b2'

# 代理设置
proxy = ('socks5', '127.0.0.1', 7890)  # 代理地址和端口需要根据实际情况调整

# 手机号码
phone_number = '+1234567890'  # 替换为你的手机号码

# 登录并创建客户端
with TelegramClient('session_name', api_id, api_hash, proxy=proxy) as client:
    # 检查是否已登录
    if not client.is_user_authorized():
        # 用户未授权，要求输入手机号
        client.send_code_request(phone_number)
        
        # 输入验证码
        client.sign_in(phone_number, input('请输入收到的验证码：'))
    
    # 获取当前登录用户的聊天列表
    dialogs = client.get_dialogs()
    
    # 用于存储未读消息数大于等于35条的频道的 chat_id
    chat_ids = []

    for dialog in dialogs:
        # 只获取频道或群组
        if dialog.is_channel:
            # 获取该频道的未读消息数
            unread_messages = dialog.unread_count
            # 如果未读消息数大于等于35条，将其 chat_id 添加到 chat_ids 列表中
            if unread_messages >= 35:
                chat_ids.append(str(dialog.id))  # 将 chat_id 转为字符串并添加到列表

    # 输出满足条件的频道 chat_ids
    print(f"未读消息数大于等于35条的频道 chat_ids: {chat_ids}")
