name: Daily Update Email

on:
  schedule:
    - cron: '0 9 * * *' # Runs every day at 9:00 AM

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Send Email
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: smtp.gmail.com
          server_port: 465
          username: ${{ secrets.EMAIL_USERNAME }}
          password: ${{ secrets.EMAIL_PASSWORD }}
          subject: 'Daily GitHub Update'
          body: 'Here are the latest updates from GitHub...'
"# AI-Based-Satellite-Image-Change-Detection-for-Illegal-Land-Encroachment" 
