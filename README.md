## Website Classifier

### Installation

1. Open terminal and run the following command-
   ```bash
   git clone git@github.com:Gardians-Of-Code/Bookmarks.git
   ```
2. Download the model using the following link - https://drive.google.com/drive/folders/1U6kkl18JMemGFXcHiDrEOFH0YbUsk278?usp=sharing
3. Place the model in same directory as the folder containing bookmark.py
4. Run the following command on the terminal to install dependencies-
   ```bash
   pip install -r requirements.txt
   ```
5. Run the following command to install the model-
   ```bash
   python -m spacy download en_core_web_sm
   ```
6. Run the following command to test the classifier-
   ```bash
   python bookmark.py
   ```
7. Start the server by running the following command-
   ```bash
   python server.py
   ```