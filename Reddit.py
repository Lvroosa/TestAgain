from google import genai
#use reddit api to get posts from a subreddit
import praw
import pandas as pd
import streamlit as st
import altair as alt
import json


#with open('pw.json') as f:
 #   config = json.load(f)


#Password = config['password']
GEMINI_API_KEY = "AIzaSyAKq9tcihQTvaO-qPZ2wVy8F28aci1qZO8"
client = genai.Client(api_key=GEMINI_API_KEY)


reddit = praw.Reddit(
     client_id="tBUSBV7v5JEUasL3p5XERQ",
    client_secret="JIMsy_BAKR8KABBKPvXkd3aucsmZ4A",
    user_agent="MyRedditApp/0.1 by appliedmlproj",
)


#create a streamlit app where you can type in a subreddit and get the top posts from that subreddit
st.title('Reddit Top Posts')
subreddit_name = st.text_input('Enter subreddit name:', 'hiphopheads')
post_limit = st.number_input('Number of posts to retrieve:', min_value=1, max_value=100, value=10)


@st.cache_data
def get_top_posts(subreddit_name, post_limit):
    # Get the subreddit
    subreddit = reddit.subreddit(subreddit_name)
   
    # Get the top posts
    top_posts = []
    for submission in subreddit.top(limit=post_limit):
        top_posts.append([submission.title, submission.score, submission.url, submission.created_utc])
   
    # Create a dataframe to display the posts
    df = pd.DataFrame(top_posts, columns=['Title', 'Score', 'URL', 'Created'])
    df['Created'] = pd.to_datetime(df['Created'], unit='s')
   
    return df
def get_top_posts2(subreddit_name, post_limit):
    # Get the subreddit
    subreddit = reddit.subreddit(subreddit_name)
   
    # Get the top posts
    top_posts = []
    for submission in subreddit.top(limit=post_limit):
        top_posts.append([submission.title, submission.score, submission.url, submission.created_utc])
    return top_posts


def analyze_sentiment(text_to_analyze, subreddit_name):
    sentiment_prompt = (
        "Tell me how the Title of the post relates to "
            f"'{subreddit_name}'.\n"
            "You can find the posts here:\n"
            f"{text_to_analyze}")
    gemini_response = client.models.generate_content(model="gemini-1.5-pro-latest", contents=[sentiment_prompt])
    if gemini_response and hasattr(gemini_response, 'text'):
        text_content = gemini_response.text
    else:
        text_content = "No response from Gemini API."


    return text_content
   


if st.button('Get Top Posts'):
    df = get_top_posts(subreddit_name, post_limit)
    df1 = get_top_posts2(subreddit_name, post_limit)
    text_to_analyze = "\n\n".join(
        [f"Title: {df1[0]}\nDescription: {df1[1]}" for dfs in df]
        )
    sentiment = analyze_sentiment(text_to_analyze, subreddit_name)
   
    # Create a bar chart of the post scores with title in the x axis and score in the y axis
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Title', sort=None),
        y='Score',
        color=alt.Color('Title', legend=None)
    ).properties(
        width=600,
        height=400
    )


    st.altair_chart(chart, use_container_width=True)
   
    # Create a text output of the top posts with the title and score
    st.write(f"### Top {post_limit} Posts On r/{subreddit_name}")
    for index, row in df.iterrows():
        st.markdown(f"###  **[{row['Title']}]({row['URL']})**")
        st.markdown(f"**Score:** {row['Score']:,}")
        st.write(sentiment)
        st.write("---")  # Separator line for readability


    st.write("### Top Posts by Score")
    st.write(df)


    #create a pie chart with the years of the posts in the x axis and the number of posts in the y axis
    df['Year'] = df['Created'].dt.year
    year_counts = df['Year'].value_counts().reset_index()
    year_counts.columns = ['Year', 'Count']
    pie_chart = alt.Chart(year_counts).mark_arc().encode(
        theta='Count',
        color=alt.Color('Year', legend=None),
        tooltip=['Year', 'Count']
    ).properties(
        width=400,
        height=400)

