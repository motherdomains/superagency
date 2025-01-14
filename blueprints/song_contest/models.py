# blueprints/song_contest/models.py
from extensions import db

# Define the SongCountry model
class SongCountry(db.Model):
    __tablename__ = 'songCountry'
    countryID = db.Column(db.SmallInteger, primary_key=True)
    country = db.Column(db.String(60), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Enum('0', '1'), default='1', nullable=False)
    display_order = db.Column('display_order', db.SmallInteger, nullable=False, default=0)

# Define the SongShow model
class SongShow(db.Model):
    __tablename__ = 'songShows'
    showID = db.Column(db.Integer, primary_key=True)
    showName = db.Column(db.String(255), nullable=False)
    showDesc = db.Column(db.Text, nullable=True)
    showDate = db.Column(db.Date, nullable=False)
    totalContestants = db.Column(db.Integer, nullable=False)

    def formatted_showDate(self):
        return self.showDate.strftime('%d %B %Y')

# Define the SongShowCountry model to create the many-to-many relationship
class SongShowCountry(db.Model):
    __tablename__ = 'songShowCountries'

    showID = db.Column(db.Integer, db.ForeignKey('songShows.showID'), primary_key=True)
    countryID = db.Column(db.SmallInteger, db.ForeignKey('songCountry.countryID'), primary_key=True)

    # Define relationships for easy access
    song_show = db.relationship('SongShow', backref=db.backref('songShowCountries', lazy=True))
    song_country = db.relationship('SongCountry', backref=db.backref('songShowCountries', lazy=True))
