import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib
matplotlib.use('WebAgg')

# Create font property object
chinese_font = FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')

# Or specify by family name
# chinese_font = FontProperties(family='Noto Sans CJK SC')

plt.figure(figsize=(10, 6))
plt.plot([1, 2, 3, 4], [1, 4, 2, 3])
plt.title('中文标题测试', fontproperties=chinese_font, fontsize=16)
plt.xlabel('横轴标签', fontproperties=chinese_font)
plt.ylabel('纵轴标签', fontproperties=chinese_font)
plt.show()