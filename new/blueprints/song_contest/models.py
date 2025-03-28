from extensions import db

class SongCountry(db.Model):
    __tablename__ = 'songCountry'
    countryID = db.Column(db.SmallInteger, primary_key=True)
    country = db.Column(db.String(60), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Enum('0', '1'), default='1', nullable=False)
    display_order = db.Column('display_order', db.SmallInteger, nullable=False, default=0)

class SongShow(db.Model):
    __tablename__ = 'songShows'

    showID = db.Column(db.Integer, primary_key=True)  # This is the correct primary key field
    showName = db.Column(db.String(255), nullable=False)
    showDesc = db.Column(db.Text, nullable=True)
    showDate = db.Column(db.Date, nullable=False)
    totalContestants = db.Column(db.Integer, nullable=False)

    def formatted_showDate(self):
        return self.showDate.strftime('%d %B %Y')