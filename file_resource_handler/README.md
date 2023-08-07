[設定值]
config.ini: 
	可以自己修改api key
compression_condition.json:
	修改你要的壓縮條件
		目前有
			圖片大小
			團片寬度
			圖片高度
				功能為壓縮圖片大小

[執行方法]
雙擊 main.exe

[輸出檔案]
image_data.csv: 檔案列表
compressed_image_file: 壓縮後的檔案

----------------------------------
[打包與憑證]
開發人員使用
1. cacert.pem api key為憑證文件
2. 每次修改api請從新打包
3. 在專案目錄開啟 終端機
打包指令:
pyinstaller main.py


[付款級距列表]
3/31
圖片大小	圖片張數			預估金額
0k		29714張			$125.50
10k  		17814張			$102.00
50k	 	 8233張			$68.00
100k   	 6254張			$50.00
200k	 	 2984張			$21.00
500k	  	  978張			$4.00
1000k	  	  325張			Free
