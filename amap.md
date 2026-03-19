

https://restapi.amap.com/v3/place/text?keywords=北京大学&city=beijing&offset=20&page=1&key={API_KEY}&extensions=all


"""
| 字段名 | 含义 | 规则说明 |
|--------|------|----------|
| status | 结果状态值 | 值为0或1。0：请求失败；1：请求成功 |
| info | 返回状态说明 | status 为0时，info 返回错误原因，否则返回“OK”。详情参阅 info状态表 |
| count | 搜索方案数目 | |
| suggestion | 城市建议列表 | 当搜索的文本关键字在限定城市中没有返回时会返回建议城市列表 |
| suggestion.keywords | 关键字 | |
| suggestion.cities | 城市列表 | |
| suggestion.cities.name | 名称 | |
| suggestion.cities.num | 该城市包含此关键字的个数 | |
| suggestion.cities.citycode | 该城市的 citycode | |
| suggestion.cities.adcode | 该城市的 adcode | |
| pois | 搜索 POI 信息列表 | |
| pois.poi | POI 信息 | |
| pois.poi.id | 唯一 ID | |
| pois.poi.parent | 父 POI 的 ID | 当前 POI 如果有父 POI，则返回父 POI 的 ID。可能为空 |
| pois.poi.name | 名称 | |
| pois.poi.type | 兴趣点类型 | 顺序为大类、中类、小类，例如：餐饮服务;中餐厅;特色/地方风味餐厅 |
| pois.poi.typecode | 兴趣点类型编码 | 例如：050118 |
| pois.poi.biz_type | 行业类型 | |
| pois.poi.address | 地址 | 例如：东四环中路189号百盛北门 |
| pois.poi.location | 经纬度 | 格式：X,Y |
| pois.poi.distance | 离中心点距离 | 单位：米；仅在周边搜索的时候有值返回 |
| pois.poi.tel | POI的电话 | |
| pois.poi.postcode | 邮编 | extensions=all时返回 |
| pois.poi.website | POI 的网址 | extensions=all时返回 |
| pois.poi.email | POI 的电子邮箱 | extensions=all时返回 |
| pois.poi.pcode | POI 所在省份编码 | extensions=all时返回 |
| pois.poi.pname | POI 所在省份名称 | 若是直辖市的时候，此处直接显示市名，例如北京市 |
| pois.poi.citycode | 城市编码 | extensions=all 时返回 |
| pois.poi.cityname | 城市名 | 若是直辖市的时候，此处直接显示市名，例如北京市 |
| pois.poi.adcode | 区域编码 | extensions=all 时返回 |
| pois.poi.adname | 区域名称 | 区县级别的返回，例如朝阳区 |
| pois.poi.entr_location | POI 的入口经纬度 | extensions=all 时返回，也可用作于 POI 的到达点 |
| pois.poi.exit_location | POI 的出口经纬度 | 目前不会返回内容 |
| pois.poi.navi_poiid | POI 导航 id | extensions=all 时返回 |
| pois.poi.gridcode | 地理格ID | extensions=all 时返回 |
| pois.poi.alias | 别名 | extensions=all 时返回 |
| pois.poi.parking_type | 停车场类型 | 仅在停车场类型 POI 的时候显示该字段，展示停车场类型，包括：地下、地面、路边。extensions=all的时候显示 |
| pois.poi.tag | 该 POI 的特色内容 | 主要出现在美食类 POI 中，代表特色菜，例如“烤鱼,麻辣香锅,老干妈回锅肉”。extensions=all 时返回 |
| pois.poi.indoor_map | 是否有室内地图标志 | 1，表示有室内相关数据；0，代表没有室内相关数据。extensions=all 时返回 |
| pois.poi.indoor_data | 室内地图相关数据 | 当 indoor_map=0时，字段为空。extensions=all 时返回 |
| pois.poi.indoor_data.cpid | 当前 POI 的父级 POI | 如果当前 POI 为建筑物类 POI，则 cpid 为自身 POI ID；如果当前 POI 为商铺类 POI，则 cpid 为其所在建筑物的 POI ID |
| pois.poi.indoor_data.floor | 楼层索引 | 一般会用数字表示，例如8 |
| pois.poi.indoor_data.truefloor | 所在楼层 | 一般会带有字母，例如F8 |
| pois.poi.groupbuy_num | 团购数据 | 此字段逐渐废弃 |
| pois.poi.business_area | 所属商圈 | extensions=all 时返回 |
| pois.poi.discount_num | 优惠信息数目 | 此字段逐渐废弃 |
| pois.poi.biz_ext | 深度信息 | extensions=all 时返回 |
| pois.poi.biz_ext.rating | 评分 | 仅存在于餐饮、酒店、景点、影院类 POI 之下 |
| pois.poi.biz_ext.cost | 人均消费 | 仅存在于餐饮、酒店、景点、影院类 POI 之下 |
| pois.poi.biz_ext.meal_ordering | 是否可订餐 | 仅存在于餐饮相关 POI 之下（此字段逐渐废弃） |
| pois.poi.biz_ext.seat_ordering | 是否可选座 | 仅存在于影院相关 POI 之下（此字段逐渐废弃） |
| pois.poi.biz_ext.ticket_ordering | 是否可订票 | 仅存在于景点相关 POI 之下（此字段逐渐废弃） |
| pois.poi.biz_ext.hotel_ordering | 是否可以订房 | 仅存在于酒店相关 POI 之下（此字段逐渐废弃） |
| pois.poi.photos | 照片相关信息 | extensions=all 时返回 |
| pois.poi.photos.title | 图片介绍 | |
| pois.poi.photos.url | 具体链接 | |
"""

https://restapi.amap.com/v3/place/around?key={API_KEY}&location=116.473168,39.993015&radius=10000&types=011100

"""
| 参数名 | 含义 | 规则说明 | 是否必须 | 缺省值 |
|--------|------|----------|----------|--------|
| key | 请求服务权限标识 | 用户在高德地图官网 申请 Web 服务 API 类型 KEY | 必填 | 无 |
| location | 中心点坐标 | 规则： 经度和纬度用","分割，经度在前，纬度在后，经纬度小数点后不得超过6位 | 必填 | 无 |
| keywords | 查询关键字 | 规则： 只支持一个关键字 | 可选 | 无 |
| types | 查询POI类型 | 多个类型用“|”分割；<br>可选值：分类代码 或 汉字 （若用汉字，请严格按照附件之中的汉字填写） <br>分类代码由六位数字组成，一共分为三个部分，前两个数字代表大类；中间两个数字代表中类；最后两个数字代表小类。<br>若指定了某个大类，则所属的中类、小类都会被显示。<br>例如：010000为汽车服务（大类）<br>010100为加油站（中类）<br>010101为中国石化（小类）<br>010900为汽车租赁（中类）<br>010901为汽车租赁还车（小类）<br>当指定010000，则010100等中类、010101等小类会被包含。<br>当指定010900，则010901等小类会被包含<br>**注意：**返回结果可能会包含中小类POI，但不保证包含所有，如需更精确的信息，推荐输入小类或缩小范围查询<br>下载 POI 分类编码和城市编码表<br>**当 keywords 和 types 均为空的时候，默认指定 types 为050000（餐饮服务）、070000（生活服务）、120000（商务住宅）** | 可选 | |
| city | 查询城市 | 可选值：城市中文、中文全拼、citycode、adcode<br>如：北京/beijing/010/110000<br>当用户指定的经纬度和 city 出现冲突，若范围内有用户指定 city 的数据，则返回相关数据，否则返回为空。<br>如：经纬度指定石家庄，而 city 却指定天津，若搜索范围内有天津的数据则返回相关数据，否则返回为空。 | 可选 | 无（全国范围内搜索） |
| radius | 查询半径 | 取值范围:0-50000。规则：大于50000按默认值，单位：米 | 可选 | 5000 |
| sortrule | 排序规则 | 规定返回结果的排序规则。<br>按距离排序：distance；综合排序：weight | 可选 | distance |
| offset | 每页记录数据 | 强烈建议不超过25，若超过25可能造成访问报错 | 可选 | 20 |
| page | 当前页数 | 当前页数 | 可选 | 1 |
| extensions | 返回结果控制 | 此项默认返回基本地址信息；取值为all返回地址信息、附近 POI、道路以及道路交叉口信息。 | 可选 | base |
| sig | 数字签名 | 请参考 数字签名获取和使用方法 | 可选 | 无 |
| callback | 回调函数 | callback 值是用户定义的函数名称，此参数只在 output=JSON 时有效 | 可选 | 无 |
"""


