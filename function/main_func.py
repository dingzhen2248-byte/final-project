from dataset_get import read_data_csv
from dataset_clean import clean_data
import seaborn as sns
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # get data
    data = read_data_csv("C:\\Users\\HUANG\\Desktop\\homework\\ALY 6140 Python\\final project\\dataset\\2023.9.csv")

    # clean data
    cleaned_data = clean_data(data)
    print("Cleaned data:\n", cleaned_data.head())

    # 按小时、线路分组并求和
    route_flow = cleaned_data.groupby(['time', 'route_or_line','route_color'])['gated_entries'].sum().reset_index()
    plt.figure(figsize=(12,6))
    sns.lineplot(
        data=route_flow,
        x='time',
        y='gated_entries',
        hue='route_or_line',
        palette=route_flow.set_index('route_or_line')['route_color'].to_dict()
    )

    plt.title('Passenger Flow Over Time by Line')
    plt.xlabel('Time')
    plt.ylabel('Passenger Count')
    plt.legend(title='Route/Line')
    plt.grid(True)
    plt.show()

