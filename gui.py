import random
import dash
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
from pymongo import MongoClient
import dash_daq as daq
import plotly.graph_objects as go

app = Dash(__name__)

external_stylesheets = ['./assets/styles.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, prevent_initial_callbacks='initial_duplicate')


client = MongoClient('localhost', 27017)
db = client['test2']
collection = db['paper']

all_documents = list(collection.find())

df = pd.DataFrame({'Person': [i['person'] for i in all_documents],
                'Latitude': [i['location'][0] + random.uniform(-0.03, 0.03) for i in all_documents],
                'Longitude': [i['location'][1] + random.uniform(-0.03, 0.03) for i in all_documents],
                'Publication': [len(i['article']) for i in all_documents],
                'Publications': [i['article'] for i in all_documents]})

client.close()

all_types = set()
for articles in df['Publications']:
    for article in articles:
        types = article['type'].split('; ')
        for t in types:
            all_types.add(t)
all_types = sorted(list(all_types))

all_languages = set()
for articles in df['Publications']:
    for article in articles:
        all_languages.add(article['language'])
all_languages = sorted(list(all_languages))

print(all_types)
print(all_languages)

max_pub = df['Publication'].max()
df['PublicationRatio'] = (df['Publication'] / max_pub)*100.0


fig = px.scatter_geo(df, lat='Latitude', lon='Longitude', hover_data=['Person', 'Publication', 'PublicationRatio'],
                    size='Publication', size_max=40, color='PublicationRatio', color_continuous_scale='RdBu', scope='world')
fig.update_layout(coloraxis_colorbar=dict(orientation='h', x=0.13, y=0.02, xpad=7, ypad=7, thickness=7, len=0.2, 
                                        lenmode='fraction', title_side='top', bgcolor='white', bordercolor='gray', borderwidth=1.5))
fig.update_traces(hovertemplate='<b>%{customdata[0]}</b><br>Publication Num: %{customdata[1]}<br>Publication Ratio: %{customdata[2]}')

app.layout = html.Div(style={'display': 'block', 'align-items': 'center'}, children=[
    html.Div(id='header', style={"background-color": "#fffefffe","padding-left": "20px", "border-bottom": "2px solid gray", 'display': 'flex', 'align-items': 'center'}, children=[
        dcc.Input(
                id='input-box',
                type='text',
                placeholder='Enter text here...',
                style={'width': '200px'}
            ),
        html.Button("Search", id="search-button"),
        dcc.Dropdown(id='article-type-dropdown', value='all'),
        dcc.Dropdown(id='article-language-dropdown', value='all'),
        daq.BooleanSwitch(id='above-switch'),
        daq.BooleanSwitch(
            id='header-switch',
            on=True,
            vertical=True,
            style={'margin-left': 'auto', 'margin-right': '20px'}
        )
    ]),
    html.Div(className='map-container', children=[
        dcc.Graph(
            id='figure',
            figure=fig,
            style={'width': '95vw', 'height': '90vh'},
            config={'displayModeBar': False}
        ),
    ]),
    html.Div(className='info-container', id='selected-point-info', hidden=True, children=[
        html.Button('×', id='close-button', className='close-button'),
        html.Button('type', id='type-btn', n_clicks=0),
        html.Button('language', id='language-btn', n_clicks=0),
        dcc.Graph(id='graph-display')
    ]),
    html.Div(id='output-message')
])

@app.callback(
    Output('header', 'children'),
    [Input('header-switch', 'on')]
)
def change_header(on):
    if on:
        return [
            html.H3('Institution Around the World', style={'margin-right': '20px'}),
            dcc.Dropdown(
                id='article-type-dropdown',
                options=[{'label': 'All type', 'value': 'all'}] + [{'label': i, 'value': i} for i in all_types],
                value='all',
                style={'width': '200px', 'margin-right': '20px'}
            ),
            dcc.Dropdown(
                id='article-language-dropdown',
                options=[{'label': 'All languages', 'value': 'all'}] + [{'label': i, 'value': i} for i in all_languages],
                value='all',
                style={'width': '200px', 'margin-right': '20px'}
            ),
            daq.BooleanSwitch(
                id='above-switch',
                on=True,
                label="Above/below the mean",
                labelPosition="top"
            ),
            daq.BooleanSwitch(
                id='header-switch',
                on=True,
                vertical=True,
                style={'margin-left': 'auto', 'margin-right': '20px'}
            ),
            dcc.Input(id='input-box',style={'display': 'none'}),
            html.Button(id="search-button", style={'display': 'none'})
        ]
    else:
        return [
            html.H3('Institution Around the World', style={'margin-right': '20px'}),
            dcc.Dropdown(id='article-type-dropdown', value='all', style={'display': 'none'}),
            dcc.Dropdown(id='article-language-dropdown', value='all', style={'display': 'none'}),
            daq.BooleanSwitch(id='above-switch',style={'display': 'none'}),
            dcc.Input(
                id='input-box',
                type='text',
                placeholder='Enter name here...',
                value='',
                style={'width': '200px'}
            ),
            html.Button("Search", id="search-button", n_clicks=0),
            daq.BooleanSwitch(
                id='header-switch',
                on=False,
                vertical=True,
                style={'margin-left': 'auto', 'margin-right': '20px'}
        )]

@app.callback(
    Output("figure", "figure", allow_duplicate=True),
    [Input('article-type-dropdown', 'value'), Input('article-language-dropdown', 'value'), Input('above-switch', 'on')]
)
def change_fig(type_name, language_name, on):
    now_df = df.copy()
    
    # print(type_name, language_name, on)
    if type_name != 'all' and type_name != None:
        filtered_df = now_df[now_df['Publications'].apply(lambda articles: any(type_name in article['type'] for article in articles))].copy()
        filtered_df['Publication'] = filtered_df['Publications'].apply(lambda articles: sum(1 for article in articles if type_name in article['type']))
        now_df = filtered_df
    
    if language_name != 'all' and type_name != None:
        filtered_df = now_df[now_df['Publications'].apply(lambda articles: any(article['language'] == language_name for article in articles))].copy()
        filtered_df['Publication'] = filtered_df['Publications'].apply(lambda articles: sum(1 for article in articles if article['language'] == language_name))
        now_df = filtered_df
        
    max_pub = now_df['Publication'].max()
    now_df['PublicationRatio'] = (now_df['Publication'] / max_pub)*100.0
    
    if not on:
        average_ratio = now_df['PublicationRatio'].mean()
        now_df = now_df[now_df['PublicationRatio'] > average_ratio]
        
    fig = px.scatter_geo(now_df, lat='Latitude', lon='Longitude', hover_data=['Person', 'Publication', 'PublicationRatio'],
                size='Publication', size_max=40, color='PublicationRatio', color_continuous_scale='RdBu', scope='world')
    fig.update_layout(coloraxis_colorbar=dict(orientation='h', x=0.13, y=0.02, xpad=7, ypad=7, thickness=7, len=0.2, 
                                            lenmode='fraction', title_side='top', bgcolor='white', bordercolor='gray', borderwidth=1.5))
    fig.update_traces(hovertemplate='<b>%{customdata[0]}</b><br>Publication Num: %{customdata[1]}<br>Publication Ratio: %{customdata[2]}')
    return fig

@app.callback(
    [Output('selected-point-info', 'children'),
    Output('selected-point-info', 'hidden'),
    Output("figure", "figure")],
    [Input('figure', 'clickData'), Input('close-button', 'n_clicks'), Input('search-button', 'n_clicks'),
    Input('type-btn', 'n_clicks'), Input('language-btn', 'n_clicks')],
    [State('input-box', 'value')]
)
def display_selected_point_info(click_data, n_clicks_close, n_clicks_search, type_clicks, language_clicks, input_value):
    if n_clicks_close:
        click_data = None
        return html.Div([
            html.Button('×', id='close-button', className='close-button'),
            html.Button('type', id='type-btn', n_clicks=0),
            html.Button('language', id='language-btn', n_clicks=0),
            dcc.Graph(id='graph-display')
        ]), True, fig
    if n_clicks_search:
        if input_value is not None:
            result = df[df["Person"] == input_value]
            if not result.empty:
                person = result['Person'].iloc[0]
                publication = result['Publication'].iloc[0]
                publicationRatio = result['PublicationRatio'].iloc[0]
                
                lat = float(result["Latitude"].iloc[0])
                lon = float(result["Longitude"].iloc[0])
                
                fig.update_geos(
                    center=dict(lat=lat, lon=lon+1),
                    projection_scale=50
                )
                
                if type_clicks < language_clicks:
                    graph = display_graph(person, 'language')
                else:
                    graph = display_graph(person, 'type')
                
                return html.Div([
                    html.Button('×', id='close-button', className='close-button'),
                    html.H4(f'Person: {person}'),
                    html.P(f'Publication: {publication}'),
                    html.P(f'Publication Ratio: {publicationRatio}'),
                    html.Button('type', id='type-btn', n_clicks=0),
                    html.Button('language', id='language-btn', n_clicks=0),
                    dcc.Graph(id='graph-display', figure=graph)
                ]), False, fig
    if click_data is not None:
        selected_point = click_data['points'][0]
        person = selected_point['customdata'][0]
        publication = selected_point['customdata'][1]
        mean_score = selected_point['customdata'][2]
        
        lat = selected_point["lat"]
        lon = selected_point["lon"]
        
        fig.update_geos(
            center=dict(lat=lat, lon=lon+1),
            projection_scale=50
        )
        
        if type_clicks < language_clicks:
            graph = display_graph(person, 'language')
        else:
            graph = display_graph(person, 'type')
        
        return html.Div([
            html.Button('×', id='close-button', className='close-button'),
            html.H4(f'Person: {person}'),
            html.P(f'Publication: {publication}'),
            html.P(f'Publication Ratio: {mean_score}'),
            html.Button('type', id='type-btn', n_clicks=0),
            html.Button('language', id='language-btn', n_clicks=0),
            dcc.Graph(id='graph-display', figure=graph)
        ]), False, fig
    return html.Div([
        html.Button('×', id='close-button', className='close-button'),
        html.Button('type', id='type-btn', n_clicks=0),
        html.Button('language', id='language-btn', n_clicks=0),
        dcc.Graph(id='graph-display')
    ]), True, fig

def display_graph(person, which):
    if which == 'type':
        categories = all_types
    else:
        categories = all_languages
    fig = go.Figure()
    
    if which == 'type':
        for type_name in all_types:
            now_df = df.copy()
            filtered_df = now_df[now_df['Publications'].apply(lambda articles: any(type_name in article['type'] for article in articles))].copy()
            filtered_df['Publication'] = filtered_df['Publications'].apply(lambda articles: sum(1 for article in articles if type_name in article['type']))
            now_df = filtered_df
            max_pub = now_df['Publication'].max()
            now_df['PublicationRatio'] = (now_df['Publication'] / max_pub)*100.0
            # print(person, filtered_df.loc[filtered_df['Person'] == person, 'PublicationRatio'].values, filtered_df.loc[filtered_df['Person'] == person, 'Publication'].values)
            fig.add_trace(go.Scatter(
                y=[type_name],
                x=filtered_df.loc[filtered_df['Person'] == person, 'PublicationRatio'].values,
                mode='markers',
                marker=dict(size=filtered_df.loc[filtered_df['Person'] == person, 'Publication'].values * 5, sizemode='diameter'),
                hovertext=filtered_df.loc[filtered_df['Person'] == person, 'Publication'].values,
                hoverinfo='text'
            ))
    else:
        for language_name in all_languages:
            now_df = df.copy()
            filtered_df = now_df[now_df['Publications'].apply(lambda articles: any(article['language'] == language_name for article in articles))].copy()
            filtered_df['Publication'] = filtered_df['Publications'].apply(lambda articles: sum(1 for article in articles if article['language'] == language_name))
            now_df = filtered_df
            max_pub = now_df['Publication'].max()
            now_df['PublicationRatio'] = (now_df['Publication'] / max_pub)*100.0
            # print(filtered_df.loc[filtered_df['Person'] == person, 'PublicationRatio'].values, filtered_df.loc[filtered_df['Person'] == person, 'Publication'].values)
            fig.add_trace(go.Scatter(
                y=[language_name],
                x=filtered_df.loc[filtered_df['Person'] == person, 'PublicationRatio'].values,
                mode='markers',
                marker=dict(size=filtered_df.loc[filtered_df['Person'] == person, 'Publication'].values * 5, sizemode='diameter'),
                hovertext=filtered_df.loc[filtered_df['Person'] == person, 'Publication'].values,
                hoverinfo='text'
            ))
    fig.update_layout(
        xaxis=dict(title='Publication Ratio'),
        yaxis=dict(title='Subject Area', tickvals=categories, ticktext=categories)
    )
    # fig.show()
    return fig

if __name__ == '__main__':
    app.run(debug=True)
