import pyvisa

# 初始化資源管理器，使用 pyvisa-py 後端
rm = pyvisa.ResourceManager('@py')

# 列出所有連接的儀器
print("連接的裝置列表:", rm.list_resources())

# 開啟您的 Tektronix 裝置 (請根據上方 list_resources 的輸出修改地址)
# 格式通常類似 'USB0::1689::..."
resource_name = 'USB0::1689::872::C032704::0::INSTR'
resource_name_dec = 'USB0::0x0699::0x0368::C032704::INSTR'

try:
    print(f"嘗試連線至: {resource_name}...")
    #instrument = rm.open_resource(rm.list_resources()[0])
    inst = rm.open_resource(resource_name)
    # 測試連線：詢問型號資訊
    print("儀器識別資訊:", inst.query('*IDN?'))

    # 設定逾時與終止字元
    inst.timeout = 5000

    # 測試連線
    idn = inst.query('*IDN?')
    print(f"連線成功！儀器 IDN: {idn}")
except Exception as e:
    print("連線失敗:", e)
