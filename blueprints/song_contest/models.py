from extensions import db

class SongCountry(db.Model):
    __tablename__ = 'songCountry'
    countryID = db.Column(db.SmallInteger, primary_key=True)
    country = db.Column(db.String(60), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(1), default='1', nullable=False)
    display_order = db.Column('display_order', db.SmallInteger, nullable=False, default=0)
    
    song_show_countries = db.relationship('SongShowCountry', back_populates='song_country')

class SongShow(db.Model):
    __tablename__ = 'songShows'
    showID = db.Column(db.Integer, primary_key=True)
    showName = db.Column(db.String(255), nullable=False)
    showDesc = db.Column(db.Text, nullable=True)
    showDate = db.Column(db.Date, nullable=False)
    totalContestants = db.Column(db.Integer, nullable=False)
    # Change TINYINT(1) to SmallInteger (SQLAlchemy-compatible)
    voting_status = db.Column(db.Integer, nullable=False, default=0)  # 0=locked, 1=open, 2=final
    
    def formatted_showDate(self):
        return self.showDate.strftime('%d %B %Y')
    
    songShowCountries = db.relationship('SongShowCountry', back_populates='song_show')

class SongShowCountry(db.Model):
    __tablename__ = 'songShowCountries'
    showID = db.Column(db.Integer, db.ForeignKey('songShows.showID'), primary_key=True)
    countryID = db.Column(db.SmallInteger, db.ForeignKey('songCountry.countryID'), primary_key=True)
    showOrder = db.Column(db.SmallInteger, nullable=False, default=1)
    votesFirst = db.Column(db.SmallInteger, nullable=False, default=0)
    votesSecond = db.Column(db.SmallInteger, nullable=False, default=0)
    votesThird = db.Column(db.SmallInteger, nullable=False, default=0)
    
    song_show = db.relationship('SongShow', back_populates='songShowCountries')
    song_country = db.relationship('SongCountry', back_populates='song_show_countries')

    def __repr__(self):
        return (f"<SongShowCountry(showID={self.showID}, countryID={self.countryID}, "
                f"showOrder={self.showOrder}, votesFirst={self.votesFirst}, "
                f"votesSecond={self.votesSecond}, votesThird={self.votesThird})>")
    
class SongShowVotes(db.Model):
    __tablename__ = 'songShowVotes'
    
    showID = db.Column(db.Integer, db.ForeignKey('songShows.showID'), primary_key=True)
    awarding_countryID = db.Column(db.SmallInteger, db.ForeignKey('songCountry.countryID'), primary_key=True)  # Country giving votes
    recipient_12 = db.Column(db.SmallInteger, db.ForeignKey('songCountry.countryID'), nullable=False)  # 12 points
    recipient_10 = db.Column(db.SmallInteger, db.ForeignKey('songCountry.countryID'), nullable=False)  # 10 points
    recipient_8 = db.Column(db.SmallInteger, db.ForeignKey('songCountry.countryID'), nullable=False)  # 8 points

    awarding_country = db.relationship('SongCountry', foreign_keys=[awarding_countryID])
    recipient_12_country = db.relationship('SongCountry', foreign_keys=[recipient_12])
    recipient_10_country = db.relationship('SongCountry', foreign_keys=[recipient_10])
    recipient_8_country = db.relationship('SongCountry', foreign_keys=[recipient_8])