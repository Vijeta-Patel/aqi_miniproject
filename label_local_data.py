
import pandas as pd, numpy as np
df=pd.read_csv("my_realtime_data.csv")
col=None
for c in df.columns:
    if "adc" in c.lower() or "mq" in c.lower():
        col=c; break
proxy=df[col].fillna(0).values
bins=[0,70,140,200,280,400,700]
df["label"]=np.digitize(proxy,bins[1:],right=True)
df.to_csv("my_collected_data_labeled.csv",index=False)
print("my_collected_data_labeled.csv created")
