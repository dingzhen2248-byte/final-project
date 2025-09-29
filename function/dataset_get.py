import pandas as pd
from api import get_request

# 创建种族字段对应字典
race_dict = {
    "B03002_001E": "Total population",
    "B03002_012E": "Hispanic or Latino",
    "B03002_003E": "White alone",
    "B03002_004E": "Black or African American alone",
    "B03002_005E": "American Indian and Alaska Native alone",
    "B03002_006E": "Asian alone",
    "B03002_007E": "Native Hawaiian and Other Pacific Islander alone",
    "B03002_008E": "Some Other Race alone",
    "B03002_009E": "Two or More Races"
}

population_dict = {
    "B01003_001E": "Total population",
    "B01001_001E": "Total Population (Alternative)"
}

# 选择 Census API 基础地址
base_url = "https://api.census.gov/data/2024/acs/acs1"

# 种族变量（总人口、白人、黑人、亚裔等）
variables = list(population_dict.keys())

# 请求参数 - tract 层级
params = {
    "get": "NAME," + ",".join(variables),
    "for": "county subdivision:*",
    "in": "state:25 county:025",   # MA州（25）波士顿县（025）
}
def read_data():
 # 转换为 DataFrame
    data = get_request(base_url,params)
    print("data:", data)
    if data is None:
        print("No data retrieved!")
    df = pd.DataFrame(data[1:], columns=data[0])

    return df


#test area
if __name__ == "__main__":


   data = read_data()