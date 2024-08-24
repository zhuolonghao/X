import matplotlib.pyplot as plt
import numpy as np
sector_color = {
    'Information Technology': (0.12156862745098039, 0.4666666666666667, 0.7058823529411765),
    'Consumer Discretionary': (1.0, 0.4980392156862745, 0.054901960784313725),
    'Communication Services': (0.17254901960784313, 0.6274509803921569, 0.17254901960784313),
    'Financials': (0.8392156862745098, 0.15294117647058825, 0.1568627450980392),
    'Health Care': (0.5803921568627451, 0.403921568627451, 0.7411764705882353),
    'Energy': (0.5490196078431373, 0.33725490196078434, 0.29411764705882354),
    'Consumer Staples': (0.8901960784313725, 0.4666666666666667, 0.7607843137254902),
    'Materials': (0.4980392156862745, 0.4980392156862745, 0.4980392156862745),
    'Industrials': (0.7372549019607844, 0.7411764705882353, 0.13333333333333333),
    'Utilities': (0.09019607843137255, 0.7450980392156863, 0.8117647058823529),
    'Real Estate': (0.12156862745098039, 0.4666666666666667, 0.7058823529411765),
    '-999': (1.0, 0.4980392156862745, 0.054901960784313725)
}
exchange_color = {
    'NNM': 'blue',
    'NYSE': 'red', 'AMEX': 'red',
    'BZX': 'k', 'SC': 'k', '-999': 'k'
}
hexagon_vertices = np.array([
    [0, 1],     # Top
    [np.sqrt(3)/2, 0.5],   # Upper right
    [np.sqrt(3)/2, -0.5],  # Lower right
    [0, -1],    # Bottom
    [-np.sqrt(3)/2, -0.5],  # Lower left
    [-np.sqrt(3)/2, 0.5]    # Upper left
])
def _circle(color):
    return  plt.Circle(xy=(0,0), radius=1.0, color=color, fill=False);
def _ticker_chart(k, ticker_data, sector_color, hexagon_vertices):
    ax = fig.add_subplot(5, 4, k)
    ticker = ticker_data['ticker']
    sector = ticker_data['sector']
    color = sector_color[sector]
    exchange = ticker_data['exchange']
    color_ex = exchange_color[exchange]
    ticker_dim = ticker_data[['momentum', 'profitability', 'reversal',  '13F', 'seasonality', 'valuation']]
    # Add the circle to the plot
    circle = _circle(color)
    ax.add_patch(circle)

    hexagon_ticker = hexagon_vertices.copy()
    dimension = ['Momentum', "Profitability", "Reversal", "13F",  "Seasonality", "Valuation"]
    for i, vertex in enumerate(hexagon_vertices):
        plt.text(vertex[0], vertex[1], f'{dimension[i]}', ha='center', va='center', weight='heavy', fontsize=8)
        hexagon_ticker[i] = hexagon_ticker[i] * ticker_dim[i]
    plt.text(0, 0, '+', color=color_ex, ha='center', va='center', weight='normal', fontsize=10)
    ax.fill(hexagon_ticker[:, 0], hexagon_ticker[:, 1], color='cornflowerblue', alpha=0.5)  # Fill the hexagon
    ax.axis('off')
    ax.set_aspect('equal', 'box')
    ax.set_title(f"{ticker} --- {sector}", fontsize=8)
    ax.grid(False)



