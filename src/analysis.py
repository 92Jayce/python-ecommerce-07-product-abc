"""第07讲 商品ABC与价格带
业务问题：哪些商品贡献收入，哪些商品贡献利润？
全部使用模拟教学数据。"""
from pathlib import Path
import sys
if "__file__" in globals():
    COURSE_ROOT = Path(__file__).resolve().parents[1]
else:
    COURSE_ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "course_common.py").exists())
if str(COURSE_ROOT) not in sys.path:
    sys.path.insert(0, str(COURSE_ROOT))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from course_common import (ROOT, DATA, AS_OF, BLUE, TEAL, ORANGE, load_tables,
    build_facts, positive_orders, rfm_table, safe_divide, outdir, save_table, save_figure, show)

# %% 用SKU行汇总，而不是把订单头金额摊给每个商品
lines,_=build_facts()
sku=lines.groupby(['product_id','product_name','category'],as_index=False).agg(
    net_sales_cents=('net_sales_cents','sum'),net_units=('net_units','sum'),contribution_cents=('contribution_cents','sum'))
sku=sku.sort_values('net_sales_cents',ascending=False).reset_index(drop=True)
sku['share']=sku.net_sales_cents/sku.net_sales_cents.sum()
sku['cumulative_share']=sku.share.cumsum()
# 跨越80%或95%边界的SKU归入前一档，避免边界商品被任意漏掉。
before=sku.cumulative_share-sku.share
sku['abc']=np.select([before<.80,before<.95],['A','B'],default='C')
show(sku,12);save_table(sku,7,'sku_abc')

# %% 帕累托图是排序后的累计贡献，不表示80/20必然成立
fig,ax=plt.subplots(figsize=(9,4));ax.bar(sku.product_id,sku.net_sales_cents/100,color=BLUE)
ax.set(ylabel='Net sales CNY',xlabel='SKU ranked by net sales');ax.tick_params(axis='x',rotation=90)
ax2=ax.twinx();ax2.plot(sku.product_id,sku.cumulative_share*100,color=ORANGE,marker='.',lw=1)
ax2.set(ylabel='Cumulative share (%)',ylim=(0,105));save_figure(fig,7,'sku_pareto')
prices=load_tables()['products'];prices['price_band']=pd.cut(prices.list_price_cents/100,[0,50,100,200,np.inf],right=False)
show(prices[['product_id','list_price_cents','price_band']]);save_table(prices,7,'price_bands')
