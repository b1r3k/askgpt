## Setup

Get you API KEY form openai.com

## Usage

1. Single question:

   dotenv --dotenv .env poetry run askgpt "Why Amsterdam is known of diamonds?"

1. Single question using docker:

    docker run -it --env-file .env askgpt "Why Amsterdam is known of diamonds?"
   
1. Summarize long text

   cat article5.txt | dotenv --dotenv .env poetry run askgpt --summarize --max-tokens 256

1. Get plaintext from URL:

    docker run -it trafilatura -u "https://roadtoomega.substack.com/p/the-paradigm-of-emergence-a-unifying" > article5.txt

1. Prefix article with question:

    echo -e "Write a concise summary of the following text:\n" | cat - article5.txt | dotenv --dotenv .env poetry run askgpt --max-tokens 500
