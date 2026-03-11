import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pyvisa
import numpy as np
import datetime

rm = pyvisa.ResourceManager('@py')
# 請確保 Resource Name 與之前一致
inst = rm.open_resource('USB0::1689::872::C032704::0::INSTR')
inst.timeout = 10000

def get_waveform(channel):
    try:
        inst.write(f'DATA:SOURCE {channel}')
        inst.write('DATA:WIDTH 1')
        inst.write('DATA:ENCDG RIBINARY')
        
        # 讀取波形參數
        ymult = float(inst.query('WFMPRE:YMULT?'))
        yoff = float(inst.query('WFMPRE:YOFF?'))
        yzero = float(inst.query('WFMPRE:YZERO?'))
        xincr = float(inst.query('WFMPRE:XINCR?'))
        # 增加讀取 XZERO，讓時間軸能對齊示波器的觸發點 (Trigger 0s)
        xzero = float(inst.query('WFMPRE:XZERO?')) 
        
        # 讀取示波器上的顯示設定
        scale = float(inst.query(f'{channel}:SCALE?'))
        pos = float(inst.query(f'{channel}:POSition?'))
        
        data = inst.query_binary_values('CURVE?', datatype='b', is_big_endian=True)
        
        # 計算真實電壓與時間
        volts = np.array([(v - yoff) * ymult + yzero for v in data])
        time = np.arange(0, len(volts)) * xincr + xzero
        
        # 核心修改：計算該點在螢幕上的哪一格 (Divisions)
        # 公式 = (真實電壓 / 每格電壓) + 基準線位移格數
        divs = (volts / scale) + pos
        
        return time, volts, divs, scale, pos
    except Exception as e:
        print(f"Error reading {channel}: {e}")
        return None, None, None, 0.0, 0.0

try:
    t1, v1, d1, s1, p1 = get_waveform('CH1')
    t2, v2, d2, s2, p2 = get_waveform('CH2')
    t3, v3, d3, s3, p3 = get_waveform('CH3')
    t4, v4, d4, s4, p4 = get_waveform('CH4')

    m_scale = float(inst.query('HORizontal:MAIN:SCAle?'))

    # 設定黑色背景主題
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 7), facecolor='#2B2B2B')
    ax.set_facecolor('#1A1A1A')

    # 調整網格線：示波器標準為垂直 8 格，水平 10 格
    ax.grid(True, which='major', color='#555555', linestyle='-', alpha=0.6)
    
    # 強制 Y 軸顯示為 -4 到 +4 格 (示波器螢幕範圍)
    ax.set_ylim(-4.2, 4.2)
    ax.set_yticks(np.arange(-4, 5, 1))

    # 繪製各通道 (這裡改畫 divs 而不是 raw volts)
    if d1 is not None:
        ax.plot(t1, d1, label=f'CH1 RFQ ({s1}V/div)', color='#FFB300', linewidth=1.5) # 橘黃
    if d2 is not None:
        ax.plot(t2, d2, label=f'CH2 DTL ({s2}V/div)', color='#00FFFF', linewidth=1.5) # 青藍
    if d3 is not None:
        ax.plot(t3, d3, label=f'CH3 ({s3}V/div)', color='#FF00FF', linewidth=1.5) # 洋紅
    if d4 is not None:
        # CH4 通常是 50mV，顯示成 mV 比較好讀
        s4_label = f"{s4*1000:.0f}mV" if s4 < 1 else f"{s4}V"
        ax.plot(t4, d4, label=f'CH4 ({s4_label}/div)', color='#00FF00', linewidth=1.5) # 綠色

    plt.title('LINAC oscilloscope from Tektronix TDS 2014B Waveforms (Grid View)')
    plt.xlabel('Time (s)')
    plt.ylabel('Screen Divisions (div)')
    plt.legend(loc='upper right')
    
    # 增加底部邊距，確保文字不會被切掉
    plt.subplots_adjust(bottom=0.15) 

    # 格式化文字 (小於 1V 時顯示 mV)
    ch1_text = f"CH1 {s1}V" if s1 >= 1 else f"CH1 {s1*1000:.0f}mV"
    ch2_text = f"CH2 {s2}V" if s2 >= 1 else f"CH2 {s2*1000:.0f}mV"
    ch3_text = f"CH3 {s3}V" if s3 >= 1 else f"CH3 {s3*1000:.0f}mV"
    ch4_text = f"CH4 {s4}V" if s4 >= 1 else f"CH4 {s4*1000:.0f}mV"

    # 使用 ax.text 將文字定位在圖表左下方 (transform=ax.transAxes 代表以圖表邊界為座標)
    # 第一排 (CH1, CH2)
    ax.text(0.00, -0.08, ch1_text, transform=ax.transAxes, color='#FFB300', fontsize=12, fontweight='bold', ha='left', va='top')
    ax.text(0.15, -0.08, ch2_text, transform=ax.transAxes, color='#00FFFF', fontsize=12, fontweight='bold', ha='left', va='top')
    
    # 第二排 (CH3, CH4)
    ax.text(0.00, -0.12, ch3_text, transform=ax.transAxes, color='#FF00FF', fontsize=12, fontweight='bold', ha='left', va='top')
    ax.text(0.15, -0.12, ch4_text, transform=ax.transAxes, color='#00FF00', fontsize=12, fontweight='bold', ha='left', va='top')

    # 順便把時間刻度 (M) 放在中間旁邊
    m_text = f"M {m_scale*1e6:.1f}us"
    ax.text(0.35, -0.08, m_text, transform=ax.transAxes, color='white', fontsize=12, fontweight='bold', ha='left', va='top')

    # 獲取目前系統時間
    now = datetime.datetime.now()
    time_str = now.strftime("%d-%b-%y   %H:%M") # 格式如：10-Mar-26   14:30:05
    ax.text(0.35, -0.12, time_str, transform=ax.transAxes, color='white', fontsize=12, fontweight='bold', ha='left', va='top')

    output_file = 'tek_triple_channels_fixed'+time_str.replace('   ','-')+'.png'
    plt.savefig(output_file, dpi=150)
    print(f"成功！圖片已儲存至: {output_file}")

finally:
    inst.close()
