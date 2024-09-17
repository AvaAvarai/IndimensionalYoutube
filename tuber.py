import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QObject, pyqtSlot, QUrl
from PyQt5.QtWebChannel import QWebChannel
from pytube import Search

class WebEngineBridge(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    @pyqtSlot()
    def onPlayerError(self):
        print("Player error detected, loading next video...")
        self.parent.shuffle_video()

class RandomYouTubePlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.static_filter = None  # Initialize the static filter before init_ui
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Random YouTube Player')
        self.resize(800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main vertical layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)

        # Web view to display YouTube videos
        self.web_view = QWebEngineView()
        main_layout.addWidget(self.web_view)

        # Set up the WebChannel for communication between JavaScript and Python
        self.bridge = WebEngineBridge(self)
        self.channel = QWebChannel()
        self.channel.registerObject('bridge', self.bridge)
        self.web_view.page().setWebChannel(self.channel)

        # Horizontal layout for buttons at the bottom center
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        # Spacer to center the buttons
        button_layout.addStretch()

        # Shuffle button
        self.shuffle_button = QPushButton('Shuffle')
        self.shuffle_button.clicked.connect(self.shuffle_video)
        button_layout.addWidget(self.shuffle_button)

        # Static Filter button
        self.filter_button = QPushButton('Static Filter')
        self.filter_button.clicked.connect(self.set_static_filter)
        button_layout.addWidget(self.filter_button)

        # Spacer to center the buttons
        button_layout.addStretch()

        # Load the first video
        self.shuffle_video()

    def shuffle_video(self):
        # If a static filter is set, use it; otherwise, use random search terms
        if self.static_filter:
            query = self.static_filter
        else:
            search_terms = ['music', 'comedy', 'news', 'sports', 'gaming', 'movies', 'education', 'live', 'nature', 'technology']
            query = random.choice(search_terms)

        # Search YouTube using pytube
        search = Search(query)
        results = search.results

        if results:
            # Randomly select a video from search results
            video = random.choice(results)
            video_id = video.video_id

            # Embed YouTube video using IFrame API
            html_content = f'''
            <!DOCTYPE html>
            <html>
                <head>
                    <style>
                        html, body {{
                            margin: 0;
                            padding: 0;
                            height: 100%;
                            width: 100%;
                        }}
                        #player {{
                            position: absolute;
                            top: 0;
                            left: 0;
                            width: 100%;
                            height: 100%;
                        }}
                    </style>
                    <!-- YouTube IFrame API -->
                    <script src="https://www.youtube.com/iframe_api"></script>
                    <!-- Qt WebChannel script -->
                    <script type="text/javascript" src="qrc:///qtwebchannel/qwebchannel.js"></script>
                    <script type="text/javascript">
                        var bridge = null;
                        new QWebChannel(qt.webChannelTransport, function(channel) {{
                            bridge = channel.objects.bridge;
                        }});

                        var player;
                        function onYouTubeIframeAPIReady() {{
                            player = new YT.Player('player', {{
                                videoId: '{video_id}',
                                events: {{
                                    'onReady': onPlayerReady,
                                    'onError': onPlayerError
                                }},
                                playerVars: {{
                                    'autoplay': 1,
                                    'controls': 1
                                }}
                            }});
                        }}

                        function onPlayerReady(event) {{
                            // Player is ready
                        }}

                        function onPlayerError(event) {{
                            console.log('Player error occurred:', event.data);
                            if (bridge && bridge.onPlayerError) {{
                                bridge.onPlayerError();
                            }}
                        }}
                    </script>
                </head>
                <body>
                    <div id="player"></div>
                </body>
            </html>
            '''

            # Load HTML content into the web view
            self.web_view.setHtml(html_content, QUrl(''))  # Empty base URL
        else:
            # Handle case when no results are found
            self.web_view.setHtml('<h1>No videos found.</h1>')

    def set_static_filter(self):
        # Open a dialog to set the static filter
        from PyQt5.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, 'Search Keyword', 'Enter search term:')
        if ok and text:
            self.static_filter = text
        else:
            self.static_filter = None  # Reset the filter if no input is provided
        # Shuffle video with the new filter
        self.shuffle_video()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = RandomYouTubePlayer()
    player.show()
    sys.exit(app.exec_())
