import boto3
import streamlit as st
import pandas as pd
import plotly
import plotly.express as px
import openai

# Assuming dynamodb setup and data retrieval remains the same
dynamodb = boto3.resource('dynamodb',
                          region_name='us-east-2',
                          aws_access_key_id=st.secrets['AWS_ACCESS_KEY'],
                          aws_secret_access_key=st.secrets['SECRET_ACCESS_KEY'])

table = dynamodb.Table('product-hunt-keywords')

plotly.io.json.config.default_engine = 'orjson'

response = table.query(
    KeyConditionExpression=boto3.dynamodb.conditions.Key('date').eq('8-2024')
)
items = response['Items']
sorted_items = sorted(items, key=lambda x: float(x['total_score']), reverse=True)

client = openai.OpenAI(api_key=st.secrets['OPEN_AI_KEY'])

prompt = f"""
Generate a product description that incorporates the top keywords provided in the array. The description should be concise, comprising only a couple of sentences, and should inspire a cool and desirable product that you would genuinely want to develop based on the keywords. Avoid creating something overly unconventional or bizarre. Don't end the description with an estimate on when the product will be released. Start the description with something like 'One idea for a product is"
{str(items)}
"""
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ],
)

response_text = response.choices[0].message.content.strip()
# Identify the top keyword and its score for display
top_keyword = sorted_items[0]['word']  # Assuming sorted_items is not empty
top_score = sorted_items[0]['total_score']


# Prepare data for Plotly
data = {
    'Word': [element['word'].upper() if len(element['word']) <= 2 else element['word'].capitalize() for element in sorted_items],
    'Score': [round(float(element['total_score']), 2) for element in sorted_items]
}

df = pd.DataFrame(data)

# Create columns for the top keyword metric and the bar graph
col1, col2 = st.columns([1, 3])

# Use the first column for the top keyword metric
with col1:
    st.metric(label="Top Weekly Keyword",
              value=f"{top_keyword}",
              delta=None)

# Use the second column for the bar graph
with col2:
    # Use Plotly Express to create a bar graph
    fig = px.bar(df, x='Word', y='Score',
                 labels={'Score': 'Total Score', 'Word': 'Keyword'},
                 color='Score',
                 height=400,
                 title='Weekly Trending Product Hunt Keywords')
    # Make the figure more interactive and visually appealing
    fig.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Keyword",
        yaxis_title="Total Score",
        title={
            'text': "Weekly Trending Product Hunt Keywords",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    # Display the Plotly chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Add a header for the product description
st.markdown("**Keyword Curated Product Description**")
st.markdown("A free product idea generated using these top keywords.")

# Create another row for the product description
with st.container():
    st.markdown(
        f'<div style="font-size: smaller;">{response_text}</div>',
        unsafe_allow_html=True
    )
