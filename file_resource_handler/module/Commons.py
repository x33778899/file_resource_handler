class Commons:

    # 建立網頁驅動
    def createwd():
        chrome_options = Options()
        chrome_options.binary_location = "C:\Program Files\Google\Chrome\Application\chrome.exe"
        driver = WebChrome(chrome_options=chrome_options)
        driver.implicitly_wait(20)
        driver.get(
            "https://apifront.qaz411.com/lx/S004/8.0.15/index.html?ps=qptest-wss.qaz411.com:8031&gameId=0&companyId=5064&theme=S004&agent=1101285&account=1101285_aaa&token=ad87ea4c079f1fc22f73387ab6a7a4139ca38d6ff430768b2f081b2fb6a7963bc165665ed5ef68b6f268d36b97d48f4aa41a46f4efe5fbdf3030fd42a030a8f6fc4deb7da3f75aa882bbed77d0ed90aacbce3cf25c83348801911e404b7cb501e6292a0fb0786fab2cf7f68b8fcaf9c561451e12be40e9ed833fed6f9ff9851c&type=1&platform=1&languageType=zh_cn&sml=0&backgroundUrl=null&title=gfg")
        driver.maximize_window()
        return driver
