from extensions import db

class SongCountry(db.Model):
    __tablename__ = 'songCountry'
    countryID = db.Column(db.SmallInteger, primary_key=True)
    country = db.Column(db.String(60), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(1), default='1', nullable=False)
    display_order = db.Column('display_order', db.SmallInteger, nullable=False, default='0')

    # You don't need to directly link show_id here, as the relationship is through SongShowCountry

class SongShow(db.Model):
    __tablename__ = 'songShows'
    showID = db.Column(db.Integer, primary_key=True)
    showName = db.Column(db.String(255), nullable=False)
    showDesc = db.Column(db.Text, nullable=True)
    showDate = db.Column(db.Date, nullable=False)
    totalContestants = db.Column(db.Integer, nullable=False)

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
    
    # Relationships
    song_show = db.relationship('SongShow', back_populates='songShowCountries')
    song_country = db.relationship('SongCountry')
    
    def __repr__(self):
        return (f"<SongShowCountry(showID={self.showID}, countryID={self.countryID}, "
                f"showOrder={self.showOrder}, votesFirst={self.votesFirst}, "
                f"votesSecond={self.votesSecond}, votesThird={self.votesThird})>")
