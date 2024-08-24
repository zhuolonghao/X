import pandas as pd

# Custom formatting function
format_dict = {
    'count': lambda x: '{:.0f}'.format(x),
    'mean': lambda x: '{:.2f}%'.format((x - 1) * 100),
    'std': lambda x: '{:.2f}%'.format(x),
    'min': lambda x: '{:.2f}%'.format((x - 1) * 100),
    '50%': lambda x: '{:.2f}%'.format((x - 1) * 100),
    'max': lambda x: '{:.2f}%'.format((x - 1) * 100),
}
def format_df(df, format_dict=format_dict):
    return df.style \
        .format(format_dict) \
        .set_properties(**{'background-color': 'lightgray'}, subset=pd.IndexSlice[::2, :]) \
        .set_properties(**{'width': '60px', 'text-align': 'right'}) \
        .set_table_styles([{'selector': 'table', 'props': [('width', '100%')]}]) \
        .set_table_attributes('border="1"')

