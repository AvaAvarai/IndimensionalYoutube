import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from pytube import Search

class RandomYouTubePlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Random YouTube Player')
        self.resize(800, 600)

        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Web view to display YouTube videos
        self.web_view = QWebEngineView()
        self.layout.addWidget(self.web_view)

        # Shuffle button
        self.shuffle_button = QPushButton('Shuffle')
        self.shuffle_button.clicked.connect(self.shuffle_video)
        self.layout.addWidget(self.shuffle_button)

        # Load the first video
        self.shuffle_video()

    def shuffle_video(self):
        # Random search term
        search_terms = ['music', 'comedy', 'news', 'sports', 'gaming', 'movies', 'education', 'live', 'nature', 'technology']
        query = random.choice(search_terms)

        # Search YouTube using pytube
        search = Search(query)
        results = search.results

        if results:
            # Randomly select a video from search results
            video = random.choice(results)
            video_id = video.video_id

            # Embed YouTube video in HTML
            html_content = f'''
            <!DOCTYPE html>
            <html>
                <body style="margin:0;">
                    <iframe width="100%" height="100%" src="https://www.youtube.com/embed/{video_id}?autoplay=1" frameborder="0" allowfullscreen></iframe>
                </body>
            </html>
            '''

            # Load HTML content into the web view
            self.web_view.setHtml(html_content)
        else:
            # Handle case when no results are found
            self.web_view.setHtml('<h1>No videos found.</h1>')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = RandomYouTubePlayer()
    player.show()
    sys.exit(app.exec_())
