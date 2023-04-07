import os
import praw
import openai
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def getSecret(name):
    return os.environ.get(name, 'Specified environment variable is not set.')


# Replace with your OpenAI API key
openai.api_key = getSecret("openai_api_key")

# Initialize the Reddit instance
user_agent = "ebaysummary 1.0 by /u/yhsls github.com/vpyati/ebaysummary"
reddit = praw.Reddit(client_id=getSecret("reddit_client_id"), client_secret=getSecret("reddit_client_secret"), user_agent=user_agent)



def send_email(to,subject,content):
    sendgrid_api_key = getSecret("sendgrid_api_key")
    sender_email = 'vikrampyati@gmail.com'

    message = Mail(
        from_email=sender_email,
        to_emails=to,
        subject=subject,
        html_content=content
    )

    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        sg.send(message)
        return 'Email sent successfully'
    except Exception as e:
        return f'Error sending email: {e}'


def get_posts_and_replies(subreddit):
    posts_and_replies = []
    for submission in subreddit.new(limit=5):
        post = {'title': submission.title, 'text': submission.selftext, 'replies': []}
        posts_and_replies.append(post)

    return posts_and_replies

def summarize_posts(posts_and_replies):
    input_texts = []
    for post in posts_and_replies:
        input_texts.append(post['title'] + ". " + post['text'])

    input_text = '.'.join(input_texts)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a assitant which can summarize user's post on eBay subreddit"},
            {"role": "user", "content": f"The following posts are from the eBay subreddit where ebay users discuss their issues. Summarize each post in a separate bullet point with a new line between them and add some hastags as well: {input_text}"}
        ]
    )

    return response.choices[0].message.content.strip()

def summaries(data, context):
    subreddit = reddit.subreddit("Ebay")
    posts_and_replies = get_posts_and_replies(subreddit)
    summaries_data = summarize_posts(posts_and_replies)
    summaries_data = "The summary of some recent posts on Ebay subreddit is as below <br><br>" + summaries_data
    send_email('vikrampyati@gmail.com','Ebay reddit summary',summaries_data)
    return summaries_data

if __name__ == "__main__":
    print(summaries("",""))